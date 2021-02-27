import os
import sys
import requests


def list_repos(token, page=1):
    url = 'https://api.github.com/user/repos'
    header = {'Authorization': f'token {token}'}
    params = {'per_page': 30, 'page': page, 'sort': 'updated'}
    r = requests.get(url, headers=header, params=params)
    repos = r.json()
    name_list = []
    url_list = []
    for repo in repos:
        name_list.append(repo['name'])
        url_list.append(repo['html_url'])
    return zip(name_list, url_list)


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


def gen_index(name, info, pagination):
    if os.path.exists(f"{name}.html"):
        os.remove(f"{name}.html")
    exclude_repos = ['img', 'ghcdn.github.io', 'shixian', 'setup', 'JavSub']
    # head of html
    head = """<html lang="zh-CN"><head><meta charset="UTF-8">
           <meta name="viewport" content="width=device-width, initial-scale=1.0">
           <link href="./css/main.css" rel="stylesheet"><title>My Video</title></head><body>
           """
    html = open(f'{name}.html', 'a')
    html.write(head)
    # content of body
    html.write('<div id="content" >')
    for name, url in info:
        if name in exclude_repos:
            continue
        html.write(f'<div id="{name}" class="video_info">')
        r = requests.head(
            f"https://cdn.jsdelivr.net/gh/ghcdn/{name}@latest/img/pic0.jpg")
        if r.status_code == 200:
            html.write(
                f'<img src="https://cdn.jsdelivr.net/gh/ghcdn/{name}@latest/img/pic0.jpg" >')
        else:
            html.write(
                f'<img src="https://cdn.jsdelivr.net/gh/ghcdn/{name}@latest/pic0.jpg" >')
        html.write(
            f'<a href="{url}">{name}</a>  <a href="./page/{name}.html"> Play Now </a>')
        html.write('</div>')
        print(name, "add index!")
        gen_page(name)
    html.write('</div>')
    # index page
    html.write('<div id="pagination_box" class="pagination">')
    html.write('<ul class="pagination">')
    for i in range(1, pagination + 1):
        html.write('<li>')
        html.write(f'<a href="./index{i}.html"> {i} </a>')
        html.write('</li>')
    html.write('</ul>')
    html.write('</div>')
    html.write('</body></html>')
    html.close()
    print(name, "generated!")


if __name__ == '__main__':
    token = sys.argv[1]
    pagination = 4
    info = list_repos(token)
    gen_index('index', info, pagination)
    for i in range(1, pagination + 1):
        info = list_repos(token, i)
        gen_index(f"index{i}", info, pagination)
