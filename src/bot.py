import fnmatch
import json
import os
import re
import time
from datetime import datetime, timedelta

import facebook

sep = os.sep

# Loading configuration from JSON
with open('config.json', 'r') as json_config:
    print('Loading config')
    config = json.load(json_config)
    ANHS_ACCESS_TOKEN = config['anhs_access_token']
    TEST_ACCESS_TOKEN = config['test_access_token']
    time_start = datetime.fromtimestamp(config['time_start'])
    time_delta = config['time_delta']
    image_directory = config['image_directory']
    print('\tANHS Token:', ANHS_ACCESS_TOKEN)
    print('\tTest Token:', TEST_ACCESS_TOKEN)
    print('\tTime start:', time_start)
    print('\tTime delta:', time_delta)
    print('\tImage directory:', image_directory)

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
            file = os.path.join(image_directory, file)
            if (os.path.isfile(file)) and is_image(file):
                print('Adding file: ', file)
                image_files.append(file)
        if len(image_files) > 0:
            print('Image files:', image_files)
            process_images(image_files)
    except FileNotFoundError as exception:
        print(exception)


def process_images(image_files):
    for image_file in image_files:
        print('------------------------')
        print('Image file: ', image_file)
        file_name = image_file.split(sep)[-1]
        manga_name = re.search('(.+?) - ', image_file).group(1).split(sep)[-1].replace('_', ' ')
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


def is_image(file):
    return (
            fnmatch.fnmatch(file, '*.png')
            or fnmatch.fnmatch(file, '*.jpeg')
            or fnmatch.fnmatch(file, '*.jpg')
            or fnmatch.fnmatch(file, '*.webp')
            or fnmatch.fnmatch(file, '*.gif')
    )


bot_job()
