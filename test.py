from Tiktok_uploader import uploadVideo

session_id = "54623f0213b22464eb6c0020ca5d75bc"
file = "my_video.mp4"
title = "MY SUPER TITLE"
tags = ["Funny", "Joke", "fyp"]
schedule_time = 1672592400

# Publish the video
uploadVideo(session_id, file, title, tags, verbose=True)
# Schedule the video
uploadVideo(session_id, file, title, tags, schedule_time, verbose=True)