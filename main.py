from fastapi import FastAPI
from typing import Optional, List
import requests
import textwrap
import os
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from fastapi.responses import StreamingResponse, FileResponse
import tempfile

temp_dir = tempfile.TemporaryDirectory()
app = FastAPI()


def GetLinkData(url: str) -> str:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    description = soup.find("meta", property="og:description").get("content")
    title = soup.find("meta", property="og:title").get("content")
    return title, description


def drawImage(title, description, sfurl, url):
    st_time = time.time()
    wrapper = textwrap.TextWrapper(width=45)
    word_list = wrapper.wrap(text=description)
    caption_new = ""
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + "\n"
    caption_new += word_list[-1]
    img = Image.open("bg-black.png")
    draw = ImageDraw.Draw(img)
    print(len(title))
    draw.text((107,222), url.strip("https://").split("/")[0], "aqua", font=ImageFont.truetype("jb.ttf", 45))
    if len(title) > 30:
        draw.text((92,410), title, "white", font=ImageFont.truetype("ps.ttf", 70))
    else:
        draw.text((92,410), title, "white", font=ImageFont.truetype("ps.ttf", 100))
    draw.text((92,590), caption_new, "orange", font=ImageFont.truetype("fira.ttf", 60))
    rgb_im = img.convert("RGB")
    rgb_im.save(f"{temp_dir.name}/{sfurl}.jpeg", "JPEG", quality=100, progressive=True)
    img_io = BytesIO()
    rgb_im.save(img_io, "JPEG", quality=100, progressive=True)
    img_io.seek(0)
    print(f"Image Gen: {time.time()-st_time}")
    return img_io


def checkImageinDir(url):
    for _, _, f in os.walk(temp_dir.name):
        for _file in f:
            print(f)
            if url in _file:
                print("Kitti", _file)
                return True
        else:
            print("Illa")
            return False


@app.get("/")
def getHey():
    return {"message": "Hello World"}


@app.get("/img")
async def getUrlData(url: Optional[str] = None):
    start = time.time()
    try:
        sufUrl = url.strip("https://").split("/")[1]
    except IndexError:
        sufUrl = url.strip("https://")
    if checkImageinDir(sufUrl) is True:
        print(f"Temp File Find exec time {time.time()-start}")
        return FileResponse(f"{temp_dir.name}/{sufUrl}.jpeg")
    else:
        siteData = GetLinkData(url)
        title = siteData[0]
        description = siteData[1]
        img = drawImage(title, description, sufUrl, url)
        print(f"Image Gen Response time {time.time()-start}")
        return StreamingResponse(
            img,
            media_type="image/jpeg",
            headers={"Content-Disposition": 'inline; filename="Image.jpeg"'},
        )
