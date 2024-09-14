import schedule
import time
from datetime import datetime
from os import listdir, remove, replace, path, makedirs
from os.path import isfile, join
import random
import yt_api

TO_POST_PATH = 'videos/to_post'
POSTED_PATH = 'videos/posted'

def trigger_function():
    print(f"Function triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get a list of all video files in the PROCESSED_PATH
    video_files = [f for f in listdir(TO_POST_PATH) if isfile(join(TO_POST_PATH, f))]
    

    # Select a random video file
    random_video = random.choice(video_files)
    video_path = join(TO_POST_PATH, random_video)
    yt_api.upload(video_path=video_path, video_name=f'Meme no {random.randint(1, 100)}')

    replace(video_path, f'{TO_POST_PATH}/{random_video}')
    print(f'Upload done, video moved from {video_path} to {TO_POST_PATH}/{random_video}')



def main():
    # Schedule the trigger_function to run at 2:30 PM every day
    schedule.every().day.at("16:51").do(trigger_function)
    schedule.every().day.at("16:53").do(trigger_function)
    schedule.every().day.at("16:55").do(trigger_function)

    print("Scheduler started. Waiting for scheduled time...")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()