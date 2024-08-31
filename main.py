import config
import time
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from yt_dlp import YoutubeDL
from os import listdir, remove, replace, path, makedirs
from os.path import isfile, join

DOWNLOAD_NAME = 'downloaded_video.mp4'  # Имя файла будет сразу с расширением .mp4
DOWNLOAD_PATH = 'videos/downloaded'
PROCESSED_PATH = 'videos/processed'
TO_POST_PATH = 'videos/to_post'

path_list = [DOWNLOAD_PATH, PROCESSED_PATH, TO_POST_PATH]

for path_to_check in path_list:
    if not path.exists(path_to_check):
        makedirs(path_to_check)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def cut(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print(f'Loading {context.args[0]}')
        link = context.args[0]
        filename = link.split('=')[-1].replace('-', '')

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}/{filename}',
            'format': 'bestvideo+bestaudio/best',  # Выбирает лучшее качество видео и аудио
            'merge_output_format': 'mp4',  # Задает формат файла после объединения
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Используем скачанный mp4 файл для дальнейшей обработки
        video_path = f'{DOWNLOAD_PATH}/{filename}.mp4'
        print(video_path)
        scene_list = detect(video_path, AdaptiveDetector())
        split_video_ffmpeg(video_path, scene_list, output_dir=PROCESSED_PATH, show_progress=True)

        onlyfiles = [f for f in listdir(PROCESSED_PATH) if isfile(join(PROCESSED_PATH, f))]

        for file in onlyfiles:
            keyboard = [
                [InlineKeyboardButton("✅", callback_data="1"),
                 InlineKeyboardButton("❌", callback_data="0")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(f'{PROCESSED_PATH}/{file}', 'rb') as video_file:
                await bot.send_video(config.test_chat_id, video=video_file, reply_markup=reply_markup)
                time.sleep(10)

        await update.message.reply_text(f'Loaded {context.args[0]}')

    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    path_to_delete = f'{PROCESSED_PATH}/{query.message.effective_attachment.file_name}'

    try:
        if query.data == "0":
            if path.exists(path_to_delete):
                remove(path_to_delete)
                await query.edit_message_caption(caption='❌ Removed.')
            else:
                await query.edit_message_caption(caption='⚠️ ??? Can not find the file to delete.')
                # await query.delete_message()
        elif query.data == '1':
            replace(f'{PROCESSED_PATH}/{query.message.effective_attachment.file_name}',
                    f'{TO_POST_PATH}/{query.message.effective_attachment.file_name}')
            await query.edit_message_caption(caption='✅ Saved for later post.')
        await query.answer()

    except Exception as e:
        await query.message.reply_text(f'An error occurred: {str(e)}')

bot = Bot(config.tg_bot_token)
app = ApplicationBuilder().token(config.tg_bot_token).build()

app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("cut", cut))

app.run_polling()
