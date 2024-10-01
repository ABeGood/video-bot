import schedule
import time
from datetime import datetime
from os import listdir, remove, rename, path, makedirs
from os.path import isfile, join
import random
import yt_api
import posts_config

TO_POST_PATH = 'videos/to_post'
POSTED_PATH = 'videos/posted'

last_video_num = posts_config.last_video_number

def trigger_function():
    global last_video_num
    last_video_num += 1

    print(f"Function triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get a list of all video files in the PROCESSED_PATH
    video_files = [f for f in listdir(TO_POST_PATH) if isfile(join(TO_POST_PATH, f))]
    
    # Select a random video file
    random_video = random.choice(video_files)
    video_path = join(TO_POST_PATH, random_video)
    yt_api.upload(video_path=video_path, video_name=f'{random.choice(posts_config.youtube_shorts_titles_short)} No. {last_video_num}')
    

    rename(video_path, f'{POSTED_PATH}/{random_video}')
    print(f'Upload done, video moved from {video_path} to {POSTED_PATH}/{random_video}')



def main():
    # Schedule the trigger_function to run at 2:30 PM every day
    schedule.every().day.at("07:06").do(trigger_function)

    schedule.every().day.at("12:17").do(trigger_function)
    schedule.every().day.at("12:43").do(trigger_function)

    schedule.every().day.at("16:55").do(trigger_function)
    schedule.every().day.at("17:15").do(trigger_function)
    schedule.every().day.at("19:21").do(trigger_function)


    print("Scheduler started. Waiting for scheduled time...")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()