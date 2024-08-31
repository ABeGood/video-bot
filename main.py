import config
import time

from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from pytube import YouTube
from os import listdir, remove, replace, path, makedirs
from os.path import isfile, join


DOWNLOAD_NAME = 'downloaded_video.mp4'

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
    print(f'Loading {context.args[0]}')
    link = context.args[0]
    video = YouTube(link)
    video.streams.filter(progressive = True, file_extension = "mp4").first().download(output_path = DOWNLOAD_PATH, filename = DOWNLOAD_NAME)

    scene_list = detect(f'{DOWNLOAD_PATH}/{DOWNLOAD_NAME}', AdaptiveDetector())
    split_video_ffmpeg(f'{DOWNLOAD_PATH}/{DOWNLOAD_NAME}', scene_list, output_dir=PROCESSED_PATH, show_progress=True)

    onlyfiles = [f for f in listdir(PROCESSED_PATH) if isfile(join(PROCESSED_PATH, f))]

    for file in onlyfiles:
        keyboard = [
            [
                InlineKeyboardButton("✅", callback_data="1"),
                InlineKeyboardButton("❌", callback_data="0"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(f'{PROCESSED_PATH}/{file}', 'rb') as file:
            await bot.send_video(config.test_chat_id, video=file, reply_markup=reply_markup, filename=f'{PROCESSED_PATH}/{file}')
            time.sleep(0.2)

    remove(f'{DOWNLOAD_PATH}/{DOWNLOAD_NAME}')
    # for file in onlyfiles:
    #     remove(f'{PROCESSED_PATH}/{file}')

    await update.message.reply_text(f'loaded {context.args[0]}')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    # print(update.message.video.file_name)
    query = update.callback_query

    path_to_delete = (f'{PROCESSED_PATH}/{query.message.effective_attachment.file_name}')

    if query.data == "0":
        if path.exists(path_to_check): 
            remove(path_to_delete)
        await query.delete_message()
    elif query.data == '1':
        replace(f'{PROCESSED_PATH}/{query.message.effective_attachment.file_name}', f'{TO_POST_PATH}/{query.message.effective_attachment.file_name}')
        await query.edit_message_caption(caption='✅ Saved for later post.')

    await query.answer()

    # await query.edit_message_text(text=f"Selected option: {query.data}")


bot = Bot(config.tg_bot_token)

app = ApplicationBuilder().token(config.tg_bot_token).build()

app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("cut", cut))

app.run_polling()