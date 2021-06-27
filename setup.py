import os
import sys
import requests
from bs4 import BeautifulSoup


def list_repos(token, page=1):
    url = 'https://api.github.com/user/repos'
    header = {'Authorization': f'token {token}'}
    params = {'per_page': 30, 'page': page, 'sort': 'updated'}
    r = requests.get(url, headers=header, params=params)
    repos = r.json()
    name_list = []
    for repo in repos:
        name_list.append(repo['name'])
    return name_list


def gen_page(name):
    if os.path.exists(f'./page/{name}.html'):
        os.remove(f'./page/{name}.html')
    hls = open('hls.html', 'r')
    page = open(f'./page/{name}.html', 'a')
    content = hls.read().replace('{name}', name)
    page.write(content)
    hls.close()
    page.close()
    print(name, 'page generated!')


def gen_new_tag(href, img_src, title):
    soup = BeautifulSoup("<li class=\"card\"></li>", "html.parser")
    original_tag = soup.li
    style = f"background-image: url({img_src});"
    card_img_tag = soup.new_tag("a", attrs={
                                "class": "card-image", "href": href, "target": "_blank", "style": style})
    desc_tag = soup.new_tag(
        "a", attrs={"class": "card-description", "href": href, "target": "_blank"})
    text_tag = soup.new_tag("p")
    text_tag.string = title
    desc_tag.append(text_tag)
    original_tag.append(card_img_tag)
    original_tag.append(desc_tag)
    return original_tag

def gen_index(name, info):
    if os.path.exists(f"{name}.html"):
        os.remove(f"{name}.html")
    exclude_repos = ['img', '', 'FFmpeg', 'ghcdn.github.io', 'shixian', 'setup', 'JavSub']
    # head of html
    html = open(f"{name}.html", "wb")
    homepage = open("home.html", "r")
    soup = BeautifulSoup(homepage.read(), "html.parser")
    card_list = soup.body.ul
    # content of body
    for video_id in info:
        if video_id in exclude_repos:
            continue
        r = requests.head(f"https://raw.githubusercontent.com/ghcdn/{video_id}/master/img/pic0.jpg")
        if r.status_code == 200:
            img = f"https://cdn.chan.im/video/{video_id}/online/img/pic0.jpg"
        else:
            img = f"https://cdn.chan.im/video/{video_id}/online/pic0.jpg"
        new_item = gen_new_tag(f"./page/{video_id}.html", img, video_id)
        card_list.append(new_item)
        print(video_id, "add index!")
        gen_page(video_id)
    # index page
    html.write(soup.encode("utf-8"))
    html.close()
    homepage.close()
    print(f"{name}.html", "generated!")


if __name__ == '__main__':
    token = sys.argv[1]
    info = list_repos(token)
    gen_index('index', info)
