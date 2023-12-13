import time
import datetime 

def wait_until_15_to_25_minutes():
    while True:
        current_time = datetime.datetime.now()
        if 15 <= current_time.minute < 25:
            print(f"It's {current_time.strftime('%H:%M')}, within the 15-24 minute range. Waiting until the next full 25-minute mark.")
            total_wait_time = (25 - current_time.minute) * 60 - current_time.second
            while total_wait_time > 0:
                print(f"Waiting for {total_wait_time} more seconds.")
                wait_time = min(30, total_wait_time)  # Wait for 30 seconds or the remaining time, whichever is smaller
                time.sleep(wait_time)
                total_wait_time -= wait_time
            break
        else:
            print(f"It's not yet in the 15-24 minute range. Current time: {current_time.strftime('%H:%M')}")
            return