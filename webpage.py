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