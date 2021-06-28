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
    r = requests.head(f"https://raw.githubusercontent.com/ghcdn/{name}/master/img/thumb01.jpg")
    if r.status_code == 200:
        hls_name = "hls-thumb.html"
    else:
        hls_name = "hls.html"
    hls = open(hls_name, 'r')
    page = open(f'./page/{name}.html', 'a')
    content = hls.read().replace('{name}', name)
    page.write(content)
    hls.close()
    page.close()
    print(name, 'page generated!')


def gen_card_tag(href, img_src, title):
    soup = BeautifulSoup("<li class=\"card\"></li>", "html.parser")
    original_tag = soup.li
    style = f"background-image: url({img_src});"
    card_img_tag = soup.new_tag("a", attrs={"class": "card-image", "href": href, "target": "_blank", "style": style})
    img_tag = soup.new_tag("img", attrs={"src": img_src, "alt": title})
    desc_tag = soup.new_tag("a", attrs={"class": "card-description", "href": href, "target": "_blank"})
    text_tag = soup.new_tag("p")
    text_tag.string = title
    card_img_tag.append(img_tag)
    desc_tag.append(text_tag)
    original_tag.append(card_img_tag)
    original_tag.append(desc_tag)
    return original_tag

def gen_index(index_num, info, total_page):
    html_name = f"index{index_num}.html"
    exclude_repos = ['img', '', 'FFmpeg', 'ghcdn.github.io', 'shixian', 'setup', 'JavSub']
    html = open(html_name, "wb")
    homepage = open("home.html", "r")
    soup = BeautifulSoup(homepage.read(), "html.parser")
    # add iterm to card-list
    card_list = soup.body.ul
    for video_id in info:
        if video_id in exclude_repos:
            continue
        if requests.head(f"https://raw.githubusercontent.com/ghcdn/{video_id}/master/img/pic0.jpg").status_code == 200:
            img = f"https://cdn.chan.im/video/{video_id}/online/img/pic0.jpg"
        elif requests.head(f"https://raw.githubusercontent.com/ghcdn/{video_id}/master/pic0.jpg").status_code == 200:
            img = f"https://cdn.chan.im/video/{video_id}/online/pic0.jpg"
        else:
            img = "https://cdn.chan.im/video/FFmpeg/online/breach.jpg"
        new_item = gen_card_tag(f"./page/{video_id}.html", img, video_id)
        card_list.append(new_item)
        print(video_id, "had added to index!")
        gen_page(video_id)
    # pagination
    page_list = soup.find("div",{"class": "pagination"}).ul
    # prev
    page_tag = soup.new_tag("li")
    page_num = index_num - 1 if index_num - 1 > 0 else index_num
    page_name = f"index{page_num}.html"
    href_tag = soup.new_tag("a", attrs={"href": page_name})
    page_tag.append(href_tag)
    page_list.append(page_tag)
    # page num
    for i in range(1, total_page + 1):
        if i == index_num:
            page_tag = soup.new_tag("li", attrs={"class": "active"})
        else:
            page_tag = soup.new_tag("li")
        page_name = f"index{i}.html"
        href_tag = soup.new_tag("a", attrs={"href": page_name})
        page_tag.append(href_tag)
        page_list.append(page_tag)
    # next
    page_tag = soup.new_tag("li")
    page_num = index_num + 1 if index_num + 1 <= total_page else index_num
    page_name = f"index{page_num}.html"
    href_tag = soup.new_tag("a", attrs={"href": page_name})
    page_tag.append(href_tag)
    page_list.append(page_tag)
    # save html
    html.write(soup.encode("utf-8"))
    # if index1.html, add extra index.html
    if index_num == 1:
        with open("index.html", "wb") as f:
            f.write(soup.encode("utf-8"))
    html.close()
    homepage.close()
    print(html_name, "generated!")


if __name__ == '__main__':
    token = sys.argv[1]
    total_page = 4
    for i in range(1, total_page + 1):
        info = list_repos(token, i)
        gen_index(i, info, total_page)

