import requests
import config
import json
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes
from telegram import Update


# TODO: One text with multiple messages, maybe will need to switch to tg lib from REST API

def post(message: str, channels: list, image_path=None):

    get_post_type = {
        str: 'text',
        tuple: 'media'
    }

    for channel in channels:
        if image_path is not None:
            if get_post_type[type(image_path)] == 'photo':
                url = f"https://api.telegram.org/bot{config.tg_bot_token}/sendPhoto"
                files = {'photo': open(image_path, 'rb')}
                data = {'chat_id': channel, 'caption': message}

            elif get_post_type[type(image_path)] == 'media':
                url = f"https://api.telegram.org/bot{config.tg_bot_token}/sendMediaGroup"
                files = {}
                media = []
                for i, attachment in enumerate(image_path):
                    files[f'image{i}'] = open(attachment, 'rb')

                    media.append(
                        {'type': 'photo', 'media': f'attach://image{i}', 'caption': f'Caption for image {i+1}'}
                    )

                data = {'chat_id': channel, 'media': json.dumps(media)}

        else:
            url = f"https://api.telegram.org/bot{config.tg_bot_token}/sendMessage"
            files = None
            data = {'chat_id': channel, 'text': message, 'parse_mode': 'HTML'}

        response = requests.post(url, files=files, data=data)

        # Check if the request was successful
        if response.status_code == 200:
            print("Post sent successfully")
        else:
            print(f"Failed to send photo. Status code: {response.status_code}")


async def respond_post(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    print('Got message...')
    # link = update.effective_message.text.split(' ')[-1]
    # print(f'Link: {link}')
    # # bot replies to the message sending a string with the username
    # column = scrapper.scrap_post(link)
    # print(f'Column scrapped')
    # processed_text = gpt.process_text_with_gpt(column['text'])['choices'][0]['message']['content']
    # processed_text = processed_text.removeprefix("'").removesuffix("'")
    # column_text = json.loads(processed_text)
    # print(f'Text processed')
    # img_links = ', '.join(column['img_links'])
    # image_link = gpt.send_images_and_get_relevance(processed_text=processed_text, images=img_links)['choices'][0]['message']['content']
    # image_link = f'<a href="{image_link}">⁠</a>'
    # print(f'Image ink: {image_link}')
    # post_text = f'<b>{column_text['title']}</b>\n\n{column_text['text']}\n{image_link}'

    # # logger.save_post(column_text['title'], post_text)
    # # post_text = f'<b>{column_text['title']}</b>\n\n{column_text['text']}\n\nИсточник: {link}\n{image_link}'
    # # extension = image_link.split('.')[-1]
    # # with open(f'posts/img/img.{extension}', "wb") as f:
    # #     f.write(requests.get(image_link).content)

    # post(message=post_text, channels=[config.test_chat_id])
    # os.remove("posts/img/img.jpg")

# post(message='Media group', channels=[config.test_chat_id], image_path=('fans.png', 'match.png'))

# bot = Application.builder().token(config.token).build()
# bot.add_handler(CommandHandler("post", respond_post))

# # start and poll for updates, press CRTL+C to stop
# bot.run_polling()