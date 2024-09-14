# youtube upload api: https://github.com/pillargg/youtube-upload?tab=readme-ov-file
# https://github.com/FujiwaraChoki/MoneyPrinter/blob/main/Backend/youtube.py
from youtube_upload.client import YoutubeUploader
from config import client_id, client_secret

uploader = YoutubeUploader(client_id=client_id, client_secret=client_secret)

uploader.authenticate()

hashtags = [
    "#MemeLaughs",
    "#FunnyMemeMayhem",
    "#ChuckleMemes",
    "#MemeGoneWild",
    "#HumorMeMemes",
    "#LaughOutLoudMemes",
    "#MemeMadness",
    "#HilariousMemeMoments",
    "#MemeComedyCentral",
    "#RoflMemeZone",
    "#LMAOMemeParty",
    "#EpicMemes",
    "#ComedyGold",
    "#LOL",
    "#Shorts",
    "#ViralVideo",
    "#MemeFails",
    "#MemeReaction",
    "#FunnyMoments",
    "#InstantLaughs"
]

def upload(video_path:str, video_name:str, tags:str|None=None, description:str=''):
    # Video options
    options = {
        "title" : f"{video_name}", # The video title
        # "title" : f"Hello-3?#shorts", # The video title
        "description" : f"{description}\n#shorts", # The video description
        "tags" : hashtags,
        "categoryId" : "23",
        "privacyStatus" : "public", # Video privacy. Can either be "public", "private", or "unlisted"
        "kids" : False, # Specifies if the Video if for kids or not. Defaults to False.
        # "thumbnailLink" : "image.png" # Optional. Specifies video thumbnail.
    }

    # upload video
    print(f'Uploading {video_path} as {video_name}')
    uploader.upload(video_path, options) 