from fastapi import FastAPI
from typing import Optional
import requests
import textwrap
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from fastapi.responses import StreamingResponse,FileResponse
import tempfile

temp_dir = tempfile.TemporaryDirectory()
app = FastAPI()


def GetLinkData(url: str) -> str:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    description = soup.find("meta", property="og:description").get("content")
    title = soup.find("meta", property="og:title").get("content")
    return title, description


def drawImage(title, description, url):
    wrapper = textwrap.TextWrapper(width=60)
    word_list = wrapper.wrap(text=description)
    caption_new = ""
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + "\n"
    caption_new += word_list[-1]
    img = Image.open("bg-1.png")
    draw = ImageDraw.Draw(img)
    print(len(title))
    draw.text((39, 69), url, "#e6e7eb", font=ImageFont.truetype("ibm.ttf", 14))
    if len(title) > 30:
        draw.text((31, 116), title, "white", font=ImageFont.truetype("ibm.ttf", 26))
    else:
        draw.text((31, 116), title, "white", font=ImageFont.truetype("ibm.ttf", 28))
    draw.text((31, 196), caption_new, "tomato", font=ImageFont.truetype("fira.ttf", 18))
    rgb_im = img.convert("RGB")
    rgb_im.save(f"{temp_dir.name}/{url}.jpeg", "JPEG", quality=100, progressive=True)
    img_io = BytesIO()
    rgb_im.save(img_io, "JPEG", quality=100, progressive=True)
    img_io.seek(0)
    return img_io


def checkImageinDir(url):
    for _, _, f in os.walk(temp_dir.name):
        for file in f:
            if url in file:
                print("Kitti",file)
                return True
            else:
                print("Illa")
                return False


@app.get("/")
def getHey():
    return {"message": "Hello World"}


@app.get("/img")
async def getUrlData(url: Optional[str] = None):
    siteData = GetLinkData(url)
    title = siteData[0]
    description = siteData[1]
    try:
        sufUrl = url.strip("https://").split("/")[1]
    except IndexError:
        sufUrl = url.strip("https://")
    if checkImageinDir(sufUrl) is True:
        return FileResponse(f"{temp_dir.name}/{sufUrl}.jpeg")
    else:
        img = drawImage(title, description, sufUrl)
        return StreamingResponse(
            img,
            media_type="image/jpeg",
            headers={"Content-Disposition": 'inline; filename="Image.jpeg"'},
        )
