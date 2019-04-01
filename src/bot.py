import fnmatch
import io
import json
import os
import re
import urllib
from datetime import datetime, timedelta

import facebook

# Loading configuration from JSON
with open('config.json') as json_config:
    print('Loading config')
    config = json.load(json_config)
    for conf in config['config']:
        ANHS_ACCESS_TOKEN = conf['anhs_access_token']
        PATO_ACCESS_TOKEN = conf['pato_access_token']
        latest_tomo_chapter = conf['latest_tomo_chapter']
        time_delta = conf['time_delta']
        image_directory = conf['image_directory'] + '\\'
        print('\tANHS Token:', ANHS_ACCESS_TOKEN)
        print('\tPato Token:', PATO_ACCESS_TOKEN)
        print('\tLatest Tomo chapter:', latest_tomo_chapter)
        print('\tTime delta:', time_delta)
        print('\tImage directory:', image_directory)
# Set starting time
now = datetime(2019, 5, 4, 14, 00)

# Connect to the FB API
graph = facebook.GraphAPI(
    access_token=ANHS_ACCESS_TOKEN,
    version="3.1"
)
print('Connected with token:', PATO_ACCESS_TOKEN)


def bot_job():
    global graph

    try:
        files = os.listdir(image_directory)
        print('Files:', files)
        image_files = []
        for file in files:
            file = image_directory + file
            if (os.path.isfile(file)) and is_image(file):
                image_files.append(file)
        if len(image_files) > 0:
            print('Image files:', image_files)
            process_images(image_files)
        else:
            print('Tomo')
            # process_tomo()
    except FileNotFoundError as exception:
        print(exception)


def process_images(image_files):
    for image_file in image_files:
        print('------------------------')
        print('Image file: ', image_file)
        file_name = image_file.split('\\')[-1].replace('_', ' ').replace('"', ' ')
        manga_name = re.search('(.+?) - ', image_file).group(1).split('\\')[-1].replace('_', ' ').replace('"', ' ')
        print('Final name:', manga_name)

        global now
        scheduled_time = int((now + timedelta(hours=time_delta)).timestamp())
        print('Scheduled time:', scheduled_time)

        post_caption = 'Manga: ' + manga_name + '\n\n-Bottroid'
        image = open(image_file, 'rb')
        try:
            graph.put_photo(
                image=image,
                message=post_caption,
                published='false',
                scheduled_publish_time=scheduled_time
            )
            image.close()

            print('Manga posted succesfully')
            processed_directory = image_directory + 'processed'
            if not os.path.isdir(processed_directory):
                os.mkdir(processed_directory)
            destination = processed_directory + '\\' + file_name
            print('Processed, moving file to:', destination)
            os.rename(image_file, destination)
            print('Processed')
            now = now + timedelta(hours=time_delta)
        except facebook.GraphAPIError as exception:
            print('Couldn\'t post image:', exception)
            image.close()
            failed_directory = image_directory + 'failed'
            if not os.path.isdir(failed_directory):
                os.mkdir(failed_directory)
            destination = failed_directory + '\\' + file_name
            print('Failed, moving file to:', destination)
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
