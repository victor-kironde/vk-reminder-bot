from datetime import datetime
import pytz


class DatetimeHelper:
    @staticmethod
    def format_datetime(_dtime):
        _datetime = pytz.utc.localize(
            datetime.strptime(_dtime.replace("T", " "), "%Y-%m-%d %H:%M:%S")
        )
        timezone = pytz.timezone("Africa/Nairobi")
        local_time = _datetime.astimezone(timezone)
        return local_time
