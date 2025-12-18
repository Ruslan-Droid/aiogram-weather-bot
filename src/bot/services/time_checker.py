def is_valid_time(time: str) -> bool:
    if len(time) == 5 and time[2] == ":":
        try:
            hours, minutes = map(int, time.split(":"))

            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except ValueError:

            return False
    return False
