import fnmatch
import os
import re
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import urllib
import io

import facebook

# PATO_ID = 365219843638526
# ANHS_ID = 1456333264610651
PATO_ACCESS_TOKEN = 'EAACVS6jUj0QBAG2n9qdrga7ZBjytXpaCdkDfNPscmtQDzmDWoMFqnHFApvQtrYjv2ycQhno7u7Fp8fB7EZC2tzlHj3rIIRTIZAKlFZA71DaJZAQyecMdNul0QkMR8Ryy6fhclYAaxUXWsqiAKHZAqu43Lk3JFYltQJLPHnJLOZB57ZCzDluoRD8YBO42VInFGckZD'
ANHS_ACCESS_TOKEN = 'EAACVS6jUj0QBABAyhEcutQYUVZAnjq55BAYrAt5VzAzabAhn5x8KOmxZBrWB9cpNcIvQanOpMMfQCN3ZBLZACAlZC7ccs7hcwVTMTmbkTsdvhomhSIShzFn19DUajPV2syfYOQwjOrmN13nq7wLguoPTgbOmIClsh1wRU8LAAeEuNbbdYHX5b'

latest_tomo_chapter = 911 # read latest chapter

graph = facebook.GraphAPI(
    access_token=PATO_ACCESS_TOKEN,
    version="3.1"
)

print('Running every 1 minute')
sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def bot_job():
    print('------------------------')
    print('Connected with token:', PATO_ACCESS_TOKEN)

    global graph

    files = os.listdir()
    print('Files:', files)
    image_files = []
    for file in files:
        if (os.path.isfile(file)) and is_image(file):
            print('Appending file:', file)
            image_files.append(file)

    if len(image_files) > 0:
        image_file = image_files[0]
        print('Image files:', image_files)
        print(image_file)
        manga_name = re.search('(.+?) - ', image_file).group(1)
        print('Name before fix:', manga_name)
        manga_name = manga_name.replace('_', ' ')
        print('Final name:', manga_name)

        post_caption = 'Manga: ' + manga_name + '\n\n-Bottroid'
        post_id = graph.put_photo(
            image=open(image_file, 'rb'),
            message=post_caption
        )

        print('Manga posted succesfully')
        if post_id != '':
            print('Moving file to processed:', image_file)
            if not os.path.isdir('processed'):
                os.mkdir('processed')
            destination = 'processed/' + image_file
            os.rename(image_file, destination)
    else:
        print('No files to process, It\'s Tomo time')
        now = datetime.datetime.now()
        print('Time:', now)

        global latest_tomo_chapter
        tomo_chapter = str(latest_tomo_chapter + 1)
        print('Searching for chapter', tomo_chapter)

        tomo_url = 'https://dropoutmanga.files.wordpress.com/' + str(now.year) + '/' + str(now.month).zfill(2) + '/dropout-tomo-chan-wa-onna-no-ko-page-' + tomo_chapter + '.png'
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
    )


sched.start()
