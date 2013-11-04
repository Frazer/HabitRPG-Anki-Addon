#Author: Pherr <pherr@pherr.net>
#License: MIT License <http://opensource.org/licenses/MIT>

import urllib2, urllib,  os, sys, json
from anki.hooks import wrap
from aqt.reviewer import Reviewer
from anki.sync import Syncer
from aqt import *

config ={}
rate = 5
correct_answers = 0
active = False
url = 'https://habitrpg.com/api/v1/user/task/Anki/up'

configpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "habitrpg.config")
configpath = configpath.decode(sys.getfilesystemencoding())

def card_answered(self, ease):  # Cache number of correct answers
    if active == True:
        if ease > 1:
            correct_answers += 1

def habit_sync(x):              # Call API once for every correct answer during Ankiweb sync
    if active == True:
        while correct_answers >= rate:
            urllib2.urlopen(url,urllib.urlencode(Syncer.headers))
            correct_answers -= rate
        config['score'] = correct_answers
        json.dump( config, open( configpath, 'w' ) )
        

def setup():
    user_id, ok = utils.getText("Enter your user ID:")
    if ok == True:
        api_token, ok = utils.getText('Enter your API token:')
        if ok == True:          # Create config file and save values
            api_token = str(api_token)
            user_id = str(user_id)
            config = {'token' : api_token, 'user' : user_id, 'score' : correct_answers}
            json.dump( config, open( configpath, 'w' ) )
            active = True
            Syncer.headers = {"x-api-key":api_token, "x-api-user":user_id}
            utils.showInfo("The add-on has been setup.")


if os.path.exists(configpath):    # Load config file
    config = json.load(open(configpath, 'r'))
    api_token = config['token']
    user_id = config['user']
    correct_answers = config['score']
    Syncer.headers = {"x-api-key":api_token, "x-api-user":user_id}
    active = True


#Add Setup to menubar
action = QAction("Setup HabitRPG", mw)
mw.connect(action, SIGNAL("triggered()"), setup)
mw.form.menuTools.addAction(action)

#Wrap funtions to Anki
Reviewer._answerCard = wrap(Reviewer._answerCard, card_answered)
Syncer.sync = wrap(Syncer.sync, habit_sync)
