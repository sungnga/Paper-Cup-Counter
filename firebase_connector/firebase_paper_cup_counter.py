__author__ = 'Nate Waddington'
__email__ = 'nathan.waddington@akqa.com'

import requests
from firebase import firebase
import datetime

def firebase_post(json):
    try:
        _firebase = firebase.FirebaseApplication('https://papercup22.firebaseio.com', None)

        today = datetime.datetime.now()
        url = '/paper_cup_count/' + str(today).split(' ')[0]
        result = _firebase.post(url, json)

        url = '/paper_cup_count/' + str(today).split(' ')[0] + '/' +  str(today).split(' ')[1].split(':')[0]
        result = _firebase.post(url, json)

    except requests.exceptions.ConnectionError or requests.exceptions.Timeout as e:
        print str(e)
