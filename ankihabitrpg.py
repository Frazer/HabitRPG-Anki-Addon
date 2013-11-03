#Author: Pherr <pherr@pherr.net>
#License: MIT License <http://opensource.org/licenses/MIT>

import urllib2, urllib,  os, sys, json
from anki.hooks import wrap
from aqt.reviewer import Reviewer
from anki.sync import Syncer
from aqt import *

config ={}
rate = 5
conffile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".habitrpg.conf")
conffile = conffile.decode(sys.getfilesystemencoding())
Syncer.active = False
Syncer.correct_answers = 0

def card_answered(self, ease):  # Cache number of correct answers
    if Syncer.active == True:
        if ease > 1:
            Syncer.correct_answers += 1

def habit_sync(x):              # Call API once for every correct answer during Ankiweb sync
    if Syncer.active == True:
        while Syncer.correct_answers >= rate:
            urllib2.urlopen(Syncer.url,urllib.urlencode(Syncer.headers))
            Syncer.correct_answers -= rate
        config['score'] = Syncer.correct_answers
        json.dump( config, open( conffile, 'w' ) )
        

def setup():
    user_id, ok = utils.getText("Enter your user ID:")
    if ok == True:
        api_token, ok = utils.getText('Enter your API token:')
        if ok == True:          # Create config file and save values
            api_token = str(api_token)
            user_id = str(user_id)
            config = {'token' : api_token, 'user' : user_id, 'score' : Syncer.correct_answers}
            json.dump( config, open( conffile, 'w' ) )
            Syncer.active = True
            Syncer.url = 'https://habitrpg.com/v1/users/%s/tasks/Anki/up' % user_id
            Syncer.headers = {"apiToken":api_token}
            utils.showInfo("The add-on has been setup.")


if os.path.exists(conffile):    # Load config file
    config = json.load(open(conffile, 'r'))
    api_token = config['token']
    user_id = config['user']
    Syncer.correct_answers = config['score']
    Syncer.url = 'https://habitrpg.com/v1/users/%s/tasks/Anki/up' % user_id
    Syncer.headers = {"apiToken":api_token}
    Syncer.active = True


#Add Setup to menubar
action = QAction("Setup HabitRPG", mw)
mw.connect(action, SIGNAL("triggered()"), setup)
mw.form.menuTools.addAction(action)

#Wrap funtions to Anki
Reviewer._answerCard = wrap(Reviewer._answerCard, card_answered)
Syncer.sync = wrap(Syncer.sync, habit_sync)
