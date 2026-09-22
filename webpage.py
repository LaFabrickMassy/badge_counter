HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Statistiques du FabLab</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; }
        table {
            border-collapse: collapse;
            table-layout: fixed;
            width: 100%;
            max-width: 700px;
        }
        th, td {
            box-sizing: border-box;
            padding: 0.6rem;
            border-bottom: 1px solid #ddd;
            text-align: left;
            vertical-align: top;
            overflow-wrap: break-word;
        }
        th:nth-child(1), td:nth-child(1) { width: 25%; }
        th:nth-child(2), td:nth-child(2) { width: 25%; }
        th:nth-child(3), td:nth-child(3) { width: 50%; }
    </style>
</head>
<body>
    <h1>Attendance statistics</h1>
    <p><a href="/admin">Administration du lecteur</a></p>

    <p>Total visits: <strong id="total-visits">...</strong></p>
    <p>Unique visitors: <strong id="unique-visitors">...</strong></p>

    <table>
        <thead>
            <tr>
                <th>Month</th>
                <th>Visits</th>
                <th>Unique visitors</th>
            </tr>
        </thead>
        <tbody id="monthly-data"></tbody>
    </table>

    <script>
        async function loadStatistics() {
            const response = await fetch("/api/stats");
            const stats = await response.json();

            document.getElementById("total-visits").textContent =
                stats.total_visits;

            document.getElementById("unique-visitors").textContent =
                stats.unique_visitors;

            document.getElementById("monthly-data").innerHTML =
                stats.monthly.map(function (item) {
                    return `<tr>
                        <td>${item.month}</td>
                        <td>${item.visits}</td>
                        <td>${item.unique_visitors}</td>
                    </tr>`;
                }).join("");
        }

        loadStatistics();
        setInterval(loadStatistics, 10000);
    </script>
</body>
</html>
"""

ADMIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Administration du lecteur</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; max-width: 40rem; }
        form { display: grid; gap: 1rem; max-width: 24rem; }
        input, button { box-sizing: border-box; font: inherit; padding: 0.6rem; }
        button { cursor: pointer; }
        #message { min-height: 1.5rem; }
    </style>
</head>
<body>
    <h1>Administration</h1>
    <p><a href="/">Retour aux statistiques</a></p>
    <form id="rtc-form">
        <label for="rtc-datetime">Date et heure du module RTC</label>
        <input id="rtc-datetime" name="datetime" type="datetime-local" step="1" required>
        <button type="submit">Enregistrer l'heure</button>
        <button id="sync-clock" type="button">Régler avec l'heure du navigateur</button>
    </form>
    <p id="message" role="status"></p>

    <h2>Fichiers de la carte SD</h2>
    <p><a href="/admin/download/data">Télécharger data.txt</a></p>
    <p><a href="/admin/download/stats">Télécharger stats.csv</a></p>
    <h2>Remplacer le fichier de log</h2>
    <p><strong>Avertissement :</strong> l'envoi d'un fichier remplacera <code>/sd/data.txt</code> et conservera l'ancienne version dans un fichier daté, par exemple <code>/sd/data.txt.2026-09-18_12-00-00.bak</code>.</p>
    <form id="upload-form" enctype="multipart/form-data">
        <label for="data-file">Fichier data.txt</label>
        <input id="data-file" name="file" type="file" accept=".txt,text/plain" required>
        <button type="submit">Remplacer data.txt</button>
    </form>

    <script>
        const input = document.getElementById("rtc-datetime");
        const message = document.getElementById("message");

        async function loadRtc() {
            const response = await fetch("/api/rtc");
            const data = await response.json();
            input.value = data.datetime;
        }

        function getBrowserDateTime() {
            const now = new Date();
            const pad = value => String(value).padStart(2, "0");

            return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}` +
                `T${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
        }

        async function synchronizeClock() {
            const datetime = getBrowserDateTime();
            input.value = datetime;

            const response = await fetch("/api/rtc", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ datetime: datetime })
            });
            const data = await response.json();
            message.textContent = data.ok ? "Heure du serveur synchronisée." : data.error;
        }

        document.getElementById("rtc-form").addEventListener("submit", async function (event) {
            event.preventDefault();
            const response = await fetch("/api/rtc", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ datetime: input.value })
            });
            const data = await response.json();
            message.textContent = data.ok ? "Heure enregistrée." : data.error;
        });

        document.getElementById("sync-clock").addEventListener("click", synchronizeClock);

        document.getElementById("upload-form").addEventListener("submit", async function (event) {
            event.preventDefault();
            if (!confirm("Attention : ce fichier va remplacer /sd/data.txt. L'ancienne version sera sauvegardée dans un fichier daté. Continuer ?")) {
                return;
            }
            const response = await fetch("/admin/upload/data", {
                method: "POST",
                body: new FormData(event.target)
            });
            const data = await response.json();
            message.textContent = data.ok ? "data.txt a été remplacé et l'ancienne version sauvegardée." : data.error;
        });

        loadRtc();
    </script>
</body>
</html>
"""