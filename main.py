import config
import time
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from yt_dlp import YoutubeDL
from os import listdir, remove, replace, path, makedirs
from os.path import isfile, join
import random
import subprocess
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx
import yt_api

import re
import os

DOWNLOAD_NAME = 'downloaded_video.mp4'  # Имя файла будет сразу с расширением .mp4
DOWNLOAD_PATH = 'videos/downloaded'
PROCESSED_PATH = 'videos/processed'
TO_POST_PATH = 'videos/to_post'
RESIZED_PATH = 'videos/resized'  # New path for resized videos
POSTED_PATH = 'videos/posted'


path_list = [DOWNLOAD_PATH, PROCESSED_PATH, TO_POST_PATH, RESIZED_PATH, POSTED_PATH]


# Create all needed folders
for path_to_check in path_list:
    if not path.exists(path_to_check):
        makedirs(path_to_check)


def sanitize_filename(filename):
    # Remove the directory path if present
    filename = os.path.basename(filename)
    
    # Remove the query string (everything after and including '?')
    filename = filename.split('?')[-1]
    
    # Remove or replace special characters
    filename = re.sub(r'[^\w\-_\. ]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    filename = filename.replace('=', '')
    
    # Remove any leading or trailing periods or spaces
    filename = filename.strip('. ')
    
    # Ensure the filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    # If filename doesn't have an extension, add .mp4
    if not os.path.splitext(filename)[1]:
        filename += '.mp4'
    
    return filename


# def process_video_with_blur(input_path, output_path, output_resolution=(1080, 1920)):
#     # Load the video
#     video = VideoFileClip(input_path)
    
#     # Calculate scaling factor to fit video width to output width
#     scale_factor = output_resolution[0] / video.w
    
#     # Resize the main video
#     main_video = video.(width=output_resolution[0])
    
#     # Create a blurred background
#     # background = (video
#     #               .resize(height=output_resolution[1])
#     #               .crop(x1=0, y1=(output_resolution[1]-video.h*scale_factor)/2, 
#     #                     x2=video.w, y2=(output_resolution[1]+video.h*scale_factor)/2)
#     #               .resize(output_resolution)
#     #               .fx(vfx.blur, 3))  # Adjust blur intensity as needed
    
#     # Compose the final video
#     # final_video = CompositeVideoClip([background, main_video.set_position("center")])
#     final_video = main_video.set_duration(video.duration)
    
#     # Write the result
#     final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
#     # Close the clips
#     video.close()
#     final_video.close()
#     print(f"Framing applied: {output_path}")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def resize_video(input_path, output_path, output_resolution=(1080, 1920)):
    with VideoFileClip(input_path) as video:
        # Resize the video
        resized_video = video.resize(height=output_resolution[1])
        
        # If the width is larger than 1080, crop it
        if resized_video.w > output_resolution[0]:
            resized_video = resized_video.crop(width=output_resolution[0], height=output_resolution[1], 
                                               x_center=resized_video.w/2, y_center=resized_video.h/2)
        
        # Write the result
        resized_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    print(f"Video resized: {output_path}")


async def cut(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not context.args:
            await update.message.reply_text("Please provide a YouTube link after the /cut command.")
            return

        link = context.args[0]
        
        await update.message.reply_text(f'Loading {link} with minimum clip length of {config.min_length_s} seconds')
        print(f'Loading {link} with minimum clip length of {config.min_length_s} seconds')

        filename = sanitize_filename(link)

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}/{filename}',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        video_path = f'{DOWNLOAD_PATH}/{filename}'
        print(f"Downloaded.")
        await update.message.reply_text(f"Video downloaded. Processing...")

        # Resize the video
        resized_video_path = f'{RESIZED_PATH}/{filename}'
        resize_video(video_path, resized_video_path)

        scene_list = detect(resized_video_path, AdaptiveDetector())
        split_video_ffmpeg(resized_video_path, scene_list, output_dir=PROCESSED_PATH, show_progress=True)

        processed_files = [f for f in listdir(PROCESSED_PATH) if isfile(join(PROCESSED_PATH, f))]
        
        # Filter and keep only videos longer than min_length_s
        kept_files = []
        for file in processed_files:
            file_path = join(PROCESSED_PATH, file)
            remove = False
            with VideoFileClip(file_path) as clip:
                if clip.duration >= config.min_length_s:
                    kept_files.append(file)
                else:
                    remove = True
                    print(f"Removed {file} (duration: {clip.duration}s)")
            
            if remove:
                os.remove(file_path)

        await update.message.reply_text(f'Video {link} processed. {len(kept_files)} scenes extracted (minimum length: {config.min_length_s}s).')

    except Exception as e:
        error_message = f'An error occurred: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data.split('_')
    
    try:
        if data[0] == "show":
            action = data[1]
            filename = '_'.join(data[2:])  # Rejoin the filename in case it contained underscores
            path_to_process = f'{PROCESSED_PATH}/{filename}'
            
            if action == "0":
                if path.exists(path_to_process):
                    remove(path_to_process)
                    await query.edit_message_caption(caption='❌ Removed.')
                else:
                    await query.edit_message_caption(caption='⚠️ Cannot find the file to delete.')
            elif action == "1":
                replace(path_to_process, f'{TO_POST_PATH}/{filename}')
                await query.edit_message_caption(caption='✅ Saved for later post.')
        else:
            # Handle the original button logic
            path_to_delete = f'{PROCESSED_PATH}/{query.message.effective_attachment.file_name}'
            if query.data == "0":
                if path.exists(path_to_delete):
                    remove(path_to_delete)
                    await query.edit_message_caption(caption='❌ Removed.')
                else:
                    await query.edit_message_caption(caption='⚠️ Cannot find the file to delete.')
            elif query.data == '1':
                replace(f'{PROCESSED_PATH}/{query.message.effective_attachment.file_name}',
                        f'{TO_POST_PATH}/{query.message.effective_attachment.file_name}')
                await query.edit_message_caption(caption='✅ Saved for later post.')
        
        await query.answer()

    except Exception as e:
        await query.message.reply_text(f'An error occurred: {str(e)}')


async def show_something(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Get a list of all video files in the PROCESSED_PATH
        video_files = [f for f in listdir(PROCESSED_PATH) if isfile(join(PROCESSED_PATH, f))]
        
        if not video_files:
            await update.message.reply_text("No processed videos available to show.")
            return
        
        # Select a random video file
        random_video = random.choice(video_files)
        video_path = join(PROCESSED_PATH, random_video)
        
        # Create the inline keyboard
        keyboard = [
            [InlineKeyboardButton("✅", callback_data=f"show_1_{random_video}"),
             InlineKeyboardButton("❌", callback_data=f"show_0_{random_video}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the video with the inline keyboard
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, reply_markup=reply_markup)
        
    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')


bot = Bot(config.tg_bot_token)
app = ApplicationBuilder().token(config.tg_bot_token).build()

app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("cut", cut))
app.add_handler(CommandHandler("show_something", show_something))

# resize_video('videos/processed/vJMgZb_q-pRQ-Scene-046.mp4', 'videos/processed/00000.mp4', output_resolution=(1080, 1920))

app.run_polling()
