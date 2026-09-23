import ujson


class AttendanceApi:
    def __init__(self, model):
        self.model = model

    def stats(self):
        monthly = []

        for month in sorted(self.model.monthly_line_counts):
            monthly.append({
                "month": month,
                "visits": self.model.monthly_line_counts[month],
                "unique_visitors": len(
                    self.model.monthly_unique_ids[month]
                ),
            })

        return ujson.dumps({
            "total_visits": len(self.model.log),
            "unique_visitors": len(self.model.last_visits),
            "monthly": monthly,
        })