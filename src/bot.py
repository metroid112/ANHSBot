import fnmatch
import os
import re
from typing import Dict, Any

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import urllib
import io
import json

import facebook

with open('config.json') as json_config:
    print('Loading config')
    config = json.load(json_config)
    for conf in config['config']:
        ANHS_ACCESS_TOKEN = conf['anhs_access_token']
        PATO_ACCESS_TOKEN = conf['pato_access_token']
        latest_tomo_chapter = conf['latest_tomo_chapter']
        image_directory = conf['image_directory'] + '\\'
        print('\tANHS Token:', ANHS_ACCESS_TOKEN)
        print('\tPato Token:', PATO_ACCESS_TOKEN)
        print('\tLatest Tomo chapter:', latest_tomo_chapter)
        print('\tImage directory:', image_directory)
        print('------------------------')
now = datetime(2019, 4, 7, 13, 42)
graph = facebook.GraphAPI(
    access_token=ANHS_ACCESS_TOKEN,
    version="3.1"
)

print('Running every 1 hour')
sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=20)
def bot_job():
    print('------------------------')
    print('Connected with token:', PATO_ACCESS_TOKEN)

    global graph

    files = os.listdir(image_directory)
    print('Files:', files)
    image_files = []
    for file in files:
        file = image_directory + file
        if (os.path.isfile(file)) and is_image(file):
            image_files.append(file)

    if len(image_files) > 0:
        x = 1
        process_images(image_files, files)
    else:
        x = 2
        # process_tomo()


def process_images(image_files, files):
    image_file = image_files[0]
    print('Image files:', image_files)
    print('Image file: ', image_file)
    manga_name = re.search('(.+?) - ', image_file).group(1).split('\\')[-1]
    print('Name before fix:', manga_name)
    manga_name = manga_name.replace('_', ' ')
    print('Final name:', manga_name)
    post_caption = 'Manga: ' + manga_name + '\n\n-Bottroid'
    global now
    scheduled_time = int((now + timedelta(hours=3)).timestamp())
    print(scheduled_time)
    image = open(image_file, 'rb')
    try:
        post_id = graph.put_photo(
            image=image,
            message=post_caption,
            published='false',
            scheduled_publish_time=scheduled_time
        )
        image.close()

        print('Manga posted succesfully')
        if post_id != '':
            print('Moving file to processed:', image_file)
            processed_directory = image_directory + 'processed'
            if not os.path.isdir(processed_directory):
                os.mkdir(processed_directory)
            destination = processed_directory + '\\' + files[0]
            try:
                os.rename(image_file, destination)
                print('Processed')
                now = now + timedelta(hours=3)
            except FileExistsError:
                print('File exists, renaming...')
                os.rename(image_file, destination + '_1')
                print('Renamed')
    except facebook.GraphAPIError:
        print('Couldn\'t post image, trying with the next')
        image.close()
        failed_directory = image_directory + 'failed'
        if not os.path.isdir(failed_directory):
            os.mkdir(failed_directory)
        destination = failed_directory + '\\' + files[0]
        os.rename(image_file, destination)


def process_tomo():
    print('No files to process, It\'s Tomo time')
    global now
    print('Time:', now)

    global latest_tomo_chapter
    tomo_chapter = str(latest_tomo_chapter + 1)
    print('Searching for chapter', tomo_chapter)

    tomo_url = 'https://dropoutmanga.files.wordpress.com/' + str(now.year) + '/' + str(now.month).zfill(
        2) + '/dropout-tomo-chan-wa-onna-no-ko-page-' + tomo_chapter + '.png'
    print('Trying URL:', tomo_url)
    try:
        tomo_url_file = urllib.request.urlopen(tomo_url)
        tomo_file = io.BytesIO(tomo_url_file.read())

        post_caption = 'Manga: Tomo-chan wa Onnanoko ' + tomo_chapter + '\n\n-Bottroid'
        try:
            graph.put_photo(
                image=tomo_file,
                message=post_caption
            )
            print('Chapter posted succesfully')

            latest_tomo_chapter += 1
        except facebook.GraphAPIError:
            print('Couldn\'t post chapter')
    except urllib.error.HTTPError:
        print('No chapter found')


def is_image(file):
    return (
            fnmatch.fnmatch(file, '*.png')
            or fnmatch.fnmatch(file, '*.jpeg')
            or fnmatch.fnmatch(file, '*.jpg')
            or fnmatch.fnmatch(file, '*.webp')
            or fnmatch.fnmatch(file, '*.gif')
    )


bot_job()
sched.start()
