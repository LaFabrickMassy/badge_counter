from attendance_api import AttendanceApi
from webpage import HTML_PAGE


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

        if path == "/api/stats":
            return self.http_response(
                "application/json",
                self.api.stats(),
            )

        return self.http_response(
            "text/plain",
            "Not found",
            status="404 Not Found",
        )

    def http_response(self, content_type, body, status="200 OK"):
        return (
            "HTTP/1.1 {}\r\n"
            "Content-Type: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "{}"
        ).format(status, content_type, body)
        
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
            request_data = client.recv(1024)
            if not request_data:
                return

            request = request_data.decode()
            response = self.handle_request(request)
            client.send(response.encode())
        finally:
            client.close()