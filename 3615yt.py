#!/usr/bin/env python

import encoding
import time
import subprocess
import glob
import minitel
import yt_dlp
from mt_graphics import bytes_from_image
from youtube_search import YoutubeSearch
from vlc_controller import VLCController
from mt_elements import (
    ProgressBar,
    UpdatableText,
)


def search_screen(mt=MT):
    mt.clear_screen()
    mt.cursor_on(False)

    # Draw logo
    b = bytes_from_image('assets/logo.png', (10, 6))
    mt.write_bytes(b)

    # Title
    mt.move_cursor((9, 19))
    b = minitel.ESC + b'\x4f' + encoding.encode('3615-YouTube')
    mt.write_bytes(b)
    mt.move_cursor((1, 20))
    mt.write_text('Mots-clés : ')

    # Input field
    query = b''
    while not query:
        mt.move_cursor((13, 20))
        query, exit_key = mt.input(40*3 - 12)
        if exit_key == b'\x13B':
            return (None, exit_key)
    return query, exit_key


def results_screen(query, mt=MT):
    mt.clear_screen()
    mt.cursor_on(False)

    b = minitel.ESC + b'\x5d'
    mt.write_bytes(b)
    mt.write_text(f"Recherche: {query.decode('utf-8')}")
    mt.move_cursor((1, 2))
    mt.write_bytes(minitel.ESC + b'\x42')
    mt.write_text('_' * 40)

    print('Query: ' + query.decode('utf-8'))
    results = YoutubeSearch(query, max_results=7).to_dict()

    for i, r in enumerate(results):

        y = 2+i*3
        mt.move_cursor((1, y))
        mt.write_text('_' * 40)
        mt.move_cursor((1, y+1))
        mt.write_bytes(minitel.ESC + b'\x5d')
        mt.write_text(f'{i+1}')
        mt.move_cursor((3, y+1))
        mt.write_text(encoding.clean(r['title'][:37]))
        mt.move_cursor((3, y+2))
        mt.write_bytes(minitel.ESC + b'\x45')
        mt.write_text(encoding.clean(r['channel'][:20]))
        mt.write_text(' (')
        mt.write_text(encoding.clean(r['duration']))
        mt.write_text(')')

    number = b''
    while not number:
        mt.move_cursor((1, 24))
        mt.write_text('Entrez votre choix (1 à 7) ')
        number, exit_key = mt.input(1)
        if exit_key in [minitel.ESC, b'\x13\x42']:
            # Go back to search screen
            return (None, exit_key)
        elif number not in b'1234567':
            mt.move_cursor((1, 24))
            mt.write_text('Entrée invalide' + ' ' * 24)
            time.sleep(3)
            number = b''

    chosen = results[int(number)-1]
    return chosen, exit_key


def download_screen(chosen, mt=MT, vlc=VLC):
    url = 'https://youtube.com' + chosen['url_suffix']
    raw_duration = chosen['duration']
    # Parsing duration
    duration_parts = [int(p) for p in raw_duration.split(':')]
    if len(duration_parts) == 3:  # H:M:S
        h, m, s = duration_parts
    else:  # M:S
        h = 0
        m, s = duration_parts
    duration = 3600*h + 60*m + s

    mt.clear_screen()
    mt.cursor_on(False)
    mt.write_text(encoding.clean(chosen['title'][:80]))
    mt.write_text('\n\r')
    mt.write_bytes(minitel.ESC + b'\x45')
    mt.write_text(encoding.clean(chosen['channel'][:35]))

    b = bytes_from_image('assets/vhs.png', (9, 6))
    mt.write_bytes(b)
    mt.move_cursor((1, 18))
    mt.write_text('Téléchargement : ')
    dl_progressbar = ProgressBar(mt, (18, 18), 12)
    dl_percent = UpdatableText(mt, (32, 18), 8)

    # Fetching video with yt-dlp
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d['downloaded_bytes'] / d['total_bytes']
            dl_progressbar.update(p)
            dl_percent.update(f'{p:.2%}')

    ydl_opts = {
        'format': 'best[height<=1080][fps<=30]',
        'progress_hooks': [progress_hook],
        'outtmpl': 'downloaded.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)

    # PLAYBACK
    def format_time(raw):
        hours = raw // 3600
        rest = raw % 3600
        minutes = rest // 60
        seconds = rest % 60

        if hours:
            return f'{hours}:{minutes:0>2d}:{seconds:0>2d}'
        elif minutes:
            return f'{minutes}:{seconds:0>2d}'
        else:
            return f'{seconds}s'

    vlc.add(glob.glob('downloaded*')[0])
    vlc.stop()
    mt.move_cursor((1, 19))
    mt.write_bytes(b'Enregistrement : ')
    rec_progressbar = ProgressBar(mt, (18, 19), 12)
    rec_percent = UpdatableText(mt, (32, 19), 8)
    print('Recording started')

    subprocess.run(['irsend', 'SEND_ONCE', 'LG_VCR_REMOTE', 'KEY_RECORD'])
    time.sleep(2)  # Delay for the VCR to start
    vlc.play()
    start_time = time.time()
    while vlc.is_playing() or time.time() - start_time < duration*0.5:
        elapsed, length = vlc.get_progress()
        if length > 0:
            p = elapsed/length
            r = length - elapsed
            rec_progressbar.update(p)
            rec_percent.update(format_time(r))

    print('Recording stoped')
    subprocess.run(
        ['irsend', 'SEND_ONCE', 'LG_VCR_REMOTE', 'KEY_STOP']
    )  # Stopping VCR

    subprocess.run(['rm',  glob.glob('downloaded*')[0]])  # Removing file


def main():

    VLC = VLCController()
    MT = minitel.Minitel(baudrate=4800)
    MT.echo_on(False)
    print('Connected to Minitel')

    state = 0
    query = ''
    choice = None
    while True:
        if state == 0:
            query, key = search_screen(MT)
            if key == b'\x13B':  # Quitting
                break
            else:
                state = 1
        elif state == 1:
            choice, key = results_screen(query, MT)
            if key == b'\x13B':  # Return to home page
                choice = None
                query = ''
                state = 0
            else:
                state = 2
        elif state == 2:
            download_screen(choice, MT, VLC)
            query = ''
            choice = None
            state = 0

    MT.clear_screen()
    MT.conn.close()
    VLC.quit()
