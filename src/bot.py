import fnmatch
import io
import json
import os
import re
import time
import urllib
from datetime import datetime, timedelta

import facebook

# Loading configuration from JSON
with open('config.json', 'r') as json_config:
    print('Loading config')
    config = json.load(json_config)
    ANHS_ACCESS_TOKEN = config['anhs_access_token']
    TEST_ACCESS_TOKEN = config['test_access_token']
    latest_tomo_chapter = config['latest_tomo_chapter']
    time_start = datetime.fromtimestamp(config['time_start'])
    time_delta = config['time_delta']
    image_directory = config['image_directory'] + '\\'
    draft_tomo = config['draft_tomo']
    print('\tANHS Token:', ANHS_ACCESS_TOKEN)
    print('\tTest Token:', TEST_ACCESS_TOKEN)
    print('\tLatest Tomo chapter:', latest_tomo_chapter)
    print('\tTime start:', time_start)
    print('\tTime delta:', time_delta)
    print('\tImage directory:', image_directory)
    print('\tTomo posts as draft?:', draft_tomo)

# Set FB Access Token
token = ANHS_ACCESS_TOKEN
print('Connected with token:', token[0:10] + '...')

# Connect to the FB API
graph = facebook.GraphAPI(
    access_token=token,
    version="3.1"
)


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
            process_tomo()
    except FileNotFoundError as exception:
        print(exception)
        process_tomo()


def process_images(image_files):
    for image_file in image_files:
        print('------------------------')
        print('Image file: ', image_file)
        file_name = image_file.split('\\')[-1]
        manga_name = re.search('(.+?) - ', image_file).group(1).split('\\')[-1]
        print('Final name:', manga_name)

        global time_start
        scheduled_time = int((time_start + timedelta(hours=time_delta)).timestamp())
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
            time_start = time_start + timedelta(hours=time_delta)
        except facebook.GraphAPIError as exception:
            print('Couldn\'t post image:', exception)
            image.close()
            failed_directory = image_directory + 'failed'
            if not os.path.isdir(failed_directory):
                os.mkdir(failed_directory)
            destination = failed_directory + '\\' + file_name
            print('Failed, moving file to:', destination)
            os.rename(image_file, destination)
    with open('config.json', 'r+') as json_config_time:
        print('Writing latest time:', time_start)
        config_time = json.load(json_config_time)
        config_time['time_start'] = int(datetime.timestamp(time_start))
        json_config_time.seek(0)
        json.dump(config_time, json_config_time)
        json_config_time.truncate()


def process_tomo():
    print('------------------------')
    global latest_tomo_chapter
    now = datetime.now()

    tomo_chapter = str(latest_tomo_chapter + 1)
    print('Searching for chapter', tomo_chapter)

    tomo_url = 'https://dropoutmanga.files.wordpress.com/' + str(now.year) + '/' + str(now.month).zfill(2)
    tomo_url += '/dropout-tomo-chan-wa-onna-no-ko-page-' + tomo_chapter + '.png'
    print('Trying URL:', tomo_url)
    found_chapter = False
    while not found_chapter:
        try:
            tomo_url_file = urllib.request.urlopen(tomo_url)
            tomo_file = io.BytesIO(tomo_url_file.read())

            post_caption = 'Manga: Tomo-chan wa Onnanoko ' + tomo_chapter + '\n\n-Bottroid'
            try:
                graph.put_photo(
                    image=tomo_file,
                    message=post_caption,
                    published=draft_tomo
                )
                print('Chapter posted succesfully')

                with open('config.json', 'r+') as json_config_tomo:
                    print('Writing latest Tomo chapter:', tomo_chapter)
                    config_tomo = json.load(json_config_tomo)
                    config_tomo['latest_tomo_chapter'] = int(tomo_chapter)
                    json_config_tomo.seek(0)
                    json.dump(config_tomo, json_config_tomo)
                    json_config_tomo.truncate()

                found_chapter = True
            except facebook.GraphAPIError as exception:
                print('Couldn\'t post chapter:', exception)
        except urllib.error.HTTPError as exception:
            print('No chapter found:', exception)
            time.sleep(300)
    process_tomo()


def is_image(file):
    return (
            fnmatch.fnmatch(file, '*.png')
            or fnmatch.fnmatch(file, '*.jpeg')
            or fnmatch.fnmatch(file, '*.jpg')
            or fnmatch.fnmatch(file, '*.webp')
            or fnmatch.fnmatch(file, '*.gif')
    )


bot_job()
