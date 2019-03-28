import fnmatch
import os
import pprint
from apscheduler.schedulers.blocking import BlockingScheduler

import facebook

# PATO_ID = 365219843638526
# ANHS_ID = 1456333264610651
PATO_ACCESS_TOKEN = 'EAACVS6jUj0QBAG2n9qdrga7ZBjytXpaCdkDfNPscmtQDzmDWoMFqnHFApvQtrYjv2ycQhno7u7Fp8fB7EZC2tzlHj3rIIRTIZAKlFZA71DaJZAQyecMdNul0QkMR8Ryy6fhclYAaxUXWsqiAKHZAqu43Lk3JFYltQJLPHnJLOZB57ZCzDluoRD8YBO42VInFGckZD'
ANHS_ACCESS_TOKEN = 'EAACVS6jUj0QBABAyhEcutQYUVZAnjq55BAYrAt5VzAzabAhn5x8KOmxZBrWB9cpNcIvQanOpMMfQCN3ZBLZACAlZC7ccs7hcwVTMTmbkTsdvhomhSIShzFn19DUajPV2syfYOQwjOrmN13nq7wLguoPTgbOmIClsh1wRU8LAAeEuNbbdYHX5b'

sched = BlockingScheduler()


def main():
    token = ANHS_ACCESS_TOKEN

    files = os.listdir()
    image_files = []
    for file in files:
        if (os.path.isfile(file)) and is_image(file):
            image_files.append(file)

    pprint.pprint(image_files)
    pprint.pprint(files)

    graph = facebook.GraphAPI(
        access_token=token,
        version="3.1"
    )

    pprint.pprint(graph)

    post_caption = 'Perhaps\nBot test by Metroid'
    post_id = graph.put_photo(
        image=open('asdimg.png', 'rb'),
        message=post_caption
    )

    pprint.pprint(post_id)


def is_image(file):
    return (
        fnmatch.fnmatch(file, '*.png')
        or fnmatch.fnmatch(file, '*.jpeg')
        or fnmatch.fnmatch(file, '*.jpg')
    )


@sched.scheduled_job('interval', seconds=5)
def bot_job():
    print('This job is run every 5 seconds.')
    file = os.listdir()[0]
    print(file)
    if not(os.path.isdir(file)):
        if file == 'bot.py':
            file = os.listdir()[1]
            print(file)
        os.remove(file)

    # main()


sched.start()
