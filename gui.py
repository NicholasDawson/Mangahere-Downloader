import PySimpleGUI as sg
import pickle
import os
import scripts

# Get save folder
if os.path.isfile('user_data'):
    save_folder = pickle.load(open('user_data', 'rb'))
else:
    save_folder = sg.PopupGetFolder('Choose a save destination for downloaded manga.', 'Select Folder')
    pickle.dump(save_folder, open('user_data', 'wb'))

# Get manga link
layout = [
    [sg.Text('Enter Mangahere link:'), sg.InputText()],
    [sg.Button('Download'), sg.Quit()]
]

window = sg.Window('Mangahere Downloader').Layout(layout)
button, (manga_link,) = window.Read()
window.Close()

manga_page = scripts.connect_to_link(manga_link)
manga_title = scripts.get_manga_title(manga_page)
manga_dir = scripts.new_folder(save_folder, manga_title)
chapter_list = scripts.get_chapter_list(manga_page)
chapter_link_list = scripts.get_chapter_link_list(manga_page)

scripts.download_all_chapters(chapter_list, chapter_link_list, manga_dir, manga_title)
