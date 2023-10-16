class ContributionMixin:
    def serialize_data(self, tips, examples):
        """
        {
            "user_id_1": [
                {
                    date: Date | String,
                    tips: Number,
                    examples: Number,
                },
                {
                ...
                }
            ],
            "user_id_2": [
                {
                    date: Date | String,
                    tips: Number,
                    examples: Number,
                },
                {
                ...
                }
            ],
        }
        """
        user_dates_data = {}

        for tip in tips:
            user_id = tip["added_by"]
            created_date = tip["date"].strftime("%Y-%m-%d")
            count = tip["count"]

            if user_id not in user_dates_data:
                user_dates_data[user_id] = {}

            user_dates_data[user_id][created_date] = {"tips": 0, "examples": 0}
            user_dates_data[user_id][created_date]["tips"] = count

        for example in examples:
            user_id = example["added_by"]
            created_date = example["date"].strftime("%Y-%m-%d")
            count = example["count"]

            if user_id not in user_dates_data:
                user_dates_data[user_id] = {}

            if created_date not in user_dates_data[user_id]:
                user_dates_data[user_id][created_date] = {
                    "tips": 0,
                    "examples": 0,
                }
            user_dates_data[user_id][created_date]["examples"] = count

        data = {}
        for user_id, user_data in user_dates_data.items():
            dates_data = []
            for created_date, date_data in user_data.items():
                date_data = {
                    "date": created_date,
                    "tips": date_data["tips"],
                    "examples": date_data["examples"],
                }
                dates_data.append(date_data)
            data[user_id] = dates_data

        return data
