import facebook
import pprint

ANHS_ACCESS_TOKEN = 'EAACVS6jUj0QBABAyhEcutQYUVZAnjq55BAYrAt5VzAzabAhn5x8KOmxZBrWB9cpNcIvQanOpMMfQCN3ZBLZACAlZC7ccs7hcwVTMTmbkTsdvhomhSIShzFn19DUajPV2syfYOQwjOrmN13nq7wLguoPTgbOmIClsh1wRU8LAAeEuNbbdYHX5b'
ANHS_ID = 1456333264610651

PATO_ACCESS_TOKEN = 'EAACVS6jUj0QBAG2n9qdrga7ZBjytXpaCdkDfNPscmtQDzmDWoMFqnHFApvQtrYjv2ycQhno7u7Fp8fB7EZC2tzlHj3rIIRTIZAKlFZA71DaJZAQyecMdNul0QkMR8Ryy6fhclYAaxUXWsqiAKHZAqu43Lk3JFYltQJLPHnJLOZB57ZCzDluoRD8YBO42VInFGckZD'
PATO_ID = 365219843638526


def main():
    token = PATO_ACCESS_TOKEN

    graph = facebook.GraphAPI(
        access_token=token,
        version="3.1"
    )

    post_id = graph.put_photo(
        image=open('img.jpg', 'rb'),
        message='Look at this cool photo!'
    )

    pprint.pprint(post_id)


if __name__ == '__main__':
    main()
