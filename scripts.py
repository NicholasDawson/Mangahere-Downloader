import requests
from bs4 import BeautifulSoup
import os
import urllib.request
from urllib.request import Request
import PySimpleGUI as sg


def new_folder(directory, folder_name):
    # Don't forget to include a '/' after the directory!
    dir = directory + '/' + folder_name + '/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def save_image(directory, image_url, image_name):
    # Don't forget to include a '/' after the directory!
    req = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)  # store the response
    f = open(directory + str(image_name) + '.jpg', 'wb')  # wb means write binary
    f.write(response.read())
    f.close()


def connect_to_link(link):
    # Input: Website Address
    # Output: HTML of that website
    page = requests.get(link)
    while page.status_code != 200:
        print("Connection error, reconnecting to URL...")
        page = requests.get(link)
    return BeautifulSoup(page.content, 'html.parser')


def get_manga_title(html):
    title = html.find('h1', class_='title')
    return title.text


def get_chapter_list(html):
    chapter_list_html = html.find_all('div', class_='detail_list')
    chapter_list_text = []

    for tag in chapter_list_html:
        td_tags = tag.find_all('a', class_='color_0077')
        for element in td_tags:
            to_append = element.text
            to_append = to_append.replace('\n', '')
            to_append = to_append[:-1]
            chapter_list_text.append(to_append)
    return chapter_list_text[::-1]


def get_image_link(chapter_link):
    html = connect_to_link(chapter_link)
    img_code = html.find('img', id="image")
    return img_code['src']


def get_chapter_link_list(html):
    chapter_link_list_html = html.find_all('div', class_='detail_list')
    chapter_link_list_text = []

    for tag in chapter_link_list_html:
        td_tags = tag.find_all('a', class_='color_0077')
        for element in td_tags:
            to_append = element['href']
            to_append = to_append[2:]
            chapter_link_list_text.append(to_append)
    return chapter_link_list_text[::-1]


def get_chapter_pages(url):
    pages_list = []
    html = connect_to_link('http://' + url)
    html = html.find('select', class_='wid60')
    html = html.text
    html = html.split('\n')
    html = html[1:-2]
    for num in html:
        pages_list.append(int(num))
    return int(max(pages_list))


def save_chapter(url, directory, name):
    page_num = 1
    chap_dir = new_folder(directory, name)
    pages = get_chapter_pages(url)

    print('Downloading ' + name + '...', "Pages:", pages)

    for page in range(pages):
        page_url = url + str(page_num) + '.html'
        img_link = get_image_link('http://' + page_url)
        save_image(chap_dir, img_link, page)
        page_num += 1


def download_all_chapters(chapter_list, chapter_link_list, manga_dir, manga_title):
    quit_application = False
    manga_chapters = len(chapter_list)

    # make layout
    layout = [
        [sg.Text('', key='manga_text', size=(30, 1))],
        [sg.ProgressBar(manga_chapters, orientation='h', size=(30, 20), key='manga_progress')],
        [sg.Text('-' * 80)],
        [sg.Text('', key='chapter_text', size=(30, 1))],
        [sg.ProgressBar(0, orientation='h', size=(30, 20), key='chapter_progress')],
        [sg.Cancel()]
    ]

    # create window and progress bars
    window = sg.Window('Downloading ' + manga_title).Layout(layout)
    manga_progress = window.FindElement('manga_progress')
    chapter_progress = window.FindElement('chapter_progress')
    manga_text = window.FindElement('manga_text')
    chapter_text = window.FindElement('chapter_text')

    event, values = window.Read(timeout=0)

    for x in range(manga_chapters):
        if quit_application:
            break
        url = chapter_link_list[x]
        directory = manga_dir
        name = chapter_list[x]
        page_num = 1
        chap_dir = new_folder(directory, name)
        pages = get_chapter_pages(url)
        manga_progress.UpdateBar(x)
        chapter_progress.UpdateBar(max=pages, current_count=0)
        manga_text.Update(str(x) + ' of ' + str(manga_chapters) + ' chapters downloaded')
        for page in range(pages):
            chapter_progress.UpdateBar(page)
            chapter_text.Update(str(page+1) + ' of ' + str(pages) + ' pages downloaded')
            page_url = url + str(page_num) + '.html'
            img_link = get_image_link('http://' + page_url)
            save_image(chap_dir, img_link, page)
            page_num += 1
            event, values = window.Read(timeout=0)
            if event == 'Cancel' or event is None:
                quit_application = True
                break
    window.Close()
        













