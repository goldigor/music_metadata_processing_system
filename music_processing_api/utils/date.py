from datetime import timedelta

def milliseconds_to_time(milliseconds: int):
    seconds = milliseconds / 1000

    duration = timedelta(seconds=seconds)

    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_time = f"{minutes}:{seconds:02d}"
    if hours:
        formatted_time = f"{hours}:{minutes:02d}:{seconds:02d}"

    return formatted_time
