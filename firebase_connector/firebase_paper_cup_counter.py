__author__ = 'Nate Waddington'
__email__ = 'nathan.waddington@akqa.com'

from firebase import firebase

def firebase_post(json):
    _firebase = firebase.FirebaseApplication('https://papercup22.firebaseio.com', None)

    result = _firebase.post('/paper_cup_count', json)
    if debug: print result
