from fastapi import FastAPI
from typing import Optional
import requests
import textwrap
from io import BytesIO
from PIL import Image,ImageDraw, ImageFont
from bs4 import BeautifulSoup
from fastapi.responses import StreamingResponse

app = FastAPI()

def GetLinkData(url:str)->str:
    soup = BeautifulSoup(requests.get(url).content,"html.parser")
    description = soup.find("meta", property="og:description").get('content')
    title = soup.find("meta", property="og:title").get('content')
    return title, description

def drawImage(title,description,url):
    pass
@app.get("/")
def getHey():
    return {"message": "Hello World"}

@app.get("/img")
async def getUrlData(url: Optional[str] = None):
    siteData=GetLinkData(url)
    baseurl = url.strip("https://").split("/")
    title = siteData[0]
    description =siteData[1]
    burl = baseurl[0]
    wrapper = textwrap.TextWrapper(width=70) 
    word_list = wrapper.wrap(text=description)
    caption_new = ''
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + '\n'
    caption_new += word_list[-1]
    img = Image.open('bg-1.png')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("ibm.ttf",21)

    w,h = draw.textsize(caption_new, font=font)
    W,H = img.size
    print(len(title))
    draw.text((39,69),burl,"#e6e7eb",font=ImageFont.truetype("ibm.ttf",14))
    if len(title) > 30:
        draw.text((31,116),title,"white",font=ImageFont.truetype("ibm.ttf",24))
    else:
        draw.text((31,116),title,"white",font=ImageFont.truetype("ibm.ttf",28))
    draw.text((31,196),caption_new,"tomato",font=ImageFont.truetype("ibm.ttf",18))
    rgb_im=img.convert('RGB')
    img_io = BytesIO()
    rgb_im.save(img_io, 'JPEG', quality=100, progressive=True)
    img_io.seek(0)
    return StreamingResponse(img_io, media_type="image/jpeg",
    headers={'Content-Disposition': 'inline; filename="Image.jpeg"'})