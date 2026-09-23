from attendance_api import AttendanceApi
from webpage import ADMIN_PAGE, HTML_PAGE
import ujson


class WebService:
    def __init__(self, model, socket_server):
        self.api = AttendanceApi(model)
        self.socket_server = socket_server

    def handle_request(self, request):
        first_line = request.split("\r\n")[0]
        path = first_line.split(" ")[1]

        if path == "/":
            return self.http_response(
                "text/html",
                HTML_PAGE,
            )

        if path == "/admin":
            return self.http_response(
                "text/html",
                ADMIN_PAGE,
            )

        if path == "/api/stats":
            return self.http_response(
                "application/json",
                self.api.stats(),
            )

        if path == "/api/rtc":
            if request.startswith("POST "):
                try:
                    body = request.split("\r\n\r\n", 1)[1]
                    payload = ujson.loads(body)
                    self.set_rtc(payload["datetime"])
                    return self.http_response(
                        "application/json",
                        ujson.dumps({"ok": True}),
                    )
                except (KeyError, ValueError, IndexError, TypeError):
                    return self.http_response(
                        "application/json",
                        ujson.dumps({"ok": False, "error": "Invalid date"}),
                        status="400 Bad Request",
                    )

            return self.http_response(
                "application/json",
                ujson.dumps({"datetime": self.get_rtc()}),
            )

        if path == "/admin/upload/data" and request.startswith("POST "):
            try:
                self.upload_data_file(request)
                return self.http_response(
                    "application/json",
                    ujson.dumps({"ok": True}),
                )
            except (KeyError, ValueError, IndexError, OSError):
                return self.http_response(
                    "application/json",
                    ujson.dumps({"ok": False, "error": "Upload invalide"}),
                    status="400 Bad Request",
                )

        if path == "/admin/download/data":
            return self.download_file(
                self.api.model.datafilename,
                "data.txt",
                "text/plain",
            )

        if path == "/admin/download/stats":
            return self.download_file(
                "/sd/stats.csv",
                "stats.csv",
                "text/csv",
            )

        return self.http_response(
            "text/plain",
            "Not found",
            status="404 Not Found",
        )

    def download_file(self, path, filename, content_type):
        try:
            with open(path, "r") as file:
                content = file.read()
        except OSError:
            return self.http_response(
                "text/plain",
                "File not found",
                status="404 Not Found",
            )

        return self.http_response(
            content_type,
            content,
            headers="Content-Disposition: attachment; filename=\"{}\"\r\n".format(filename),
        )

    def upload_data_file(self, request):
        header_text, body = request.split("\r\n\r\n", 1)
        content_type = self.get_header(header_text, "Content-Type")
        boundary = content_type.split("boundary=", 1)[1].strip('"')
        delimiter = "--" + boundary

        for part in body.split(delimiter):
            if 'name="file"' not in part:
                continue
            part_headers, content = part.split("\r\n\r\n", 1)
            if content.endswith("\r\n"):
                content = content[:-2]
            datafilename = self.api.model.datafilename
            try:
                with open(datafilename, "r") as file:
                    previous_content = file.read()
            except OSError:
                previous_content = None
            if previous_content is not None:
                backup_datetime = self.get_rtc().replace("T", "_").replace(":", "-")
                backup_filename = "{}.{}.bak".format(datafilename, backup_datetime)
                with open(backup_filename, "w") as file:
                    file.write(previous_content)
            with open(datafilename, "w") as file:
                file.write(content)
            return

        raise ValueError("Missing file")

    def get_header(self, headers, name):
        for line in headers.split("\r\n"):
            if line.lower().startswith(name.lower() + ":"):
                return line.split(":", 1)[1].strip()
        raise KeyError(name)

    def get_rtc(self):
        current = self.api.model.rtc.datetime()
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            current.year,
            current.month,
            current.day,
            current.hour,
            current.minute,
            current.second,
        )

    def set_rtc(self, value):
        date_part, time_part = value.split("T")
        year, month, day = [int(part) for part in date_part.split("-")]
        time_parts = [int(part) for part in time_part.split(":")]
        if len(time_parts) == 2:
            hour, minute = time_parts
            second = 0
        elif len(time_parts) == 3:
            hour, minute, second = time_parts
        else:
            raise ValueError("Invalid time")
        if not (1 <= month <= 12):
            raise ValueError("Invalid date")
        days_in_month = (31, 29 if year % 4 == 0 and
                         (year % 100 != 0 or year % 400 == 0) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        if not (1 <= day <= days_in_month[month - 1]):
            raise ValueError("Invalid date")
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError("Invalid time")

        century = year // 100
        year_in_century = year % 100
        weekday = (day + (13 * (month + 1)) // 5 + year_in_century +
                   year_in_century // 4 + century // 4 + 5 * century + 5) % 7
        self.api.model.rtc.datetime((
            year, month, day, weekday, hour, minute, second, 0,
        ))

    def http_response(self, content_type, body, status="200 OK", headers=""):
        return (
            "HTTP/1.1 {}\r\n"
            "Content-Type: {}\r\n"
            "{}"
            "Connection: close\r\n"
            "\r\n"
            "{}"
        ).format(status, content_type, headers, body)
        
    def poll(self):
        try:
            client, address = self.socket_server.accept()
        except OSError as error:
            if error.args and error.args[0] == 11:
                return
            raise

        try:
            client.setblocking(True)
            client.settimeout(2)
            request_data = self.receive_request(client)
            if not request_data:
                return

            response = self.handle_request(request_data)
            client.send(response.encode())
        finally:
            client.close()

    def receive_request(self, client):
        request_data = b""
        content_length = None
        while True:
            chunk = client.recv(1024)
            if not chunk:
                break
            request_data += chunk
            header_end = request_data.find(b"\r\n\r\n")
            if header_end >= 0 and content_length is None:
                header_text = request_data[:header_end].decode()
                try:
                    content_length = int(self.get_header(header_text, "Content-Length"))
                except KeyError:
                    content_length = 0
            if (content_length is not None and
                    len(request_data) >= header_end + 4 + content_length):
                break
        return request_data.decode()