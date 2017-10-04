#!flask/bin/python


# note that on EC2, the python log should be located here:  /var/log/httpd/error_log
# also, deployment logs should be checked here:             /var/log/eb-activity.log


from __future__ import print_function

import os
import sys
import socket
import json
import datetime
import signal
import pytz
import tzlocal

import threading

# import logging
import dateutil
import dateutil.parser
# import pandas
# import httplib2
# import argparse


# needed for Amazon AWS S3 stuff
import boto3            # as bt3
import botocore         # as bc
import boto3.session    # as bsess
# from botocore.exceptions import ClientError as ce
import botocore.exceptions



# from apiclient import discovery
# from oauth2client import client
# from oauth2client import tools
# from oauth2client.file import Storage

#import apiclient
import oauth2client
import oauth2client.file
# import com.google.api.services.calendar.Calendar
import oauthlib.oauth2


import flask
import flask_bootstrap
import flask_bootstrap.nav
import flask_appconfig
import flask_nav
import flask_nav.elements as fne
import flask_session
import flask_oauthlib
import flask_oauthlib.client
import flask_login
# import flask_sqlalchemy
# import flaskrun
# import flask_oauth2_login     # this was previously flask-googlelogin, and wouldn't pip install
#                               # but this version now works, and extends requests_oauthlib.OAuth2Session
# import flask_oauth
# import flask.ext.session      # depreciated
# import flask_social
# import flask_sqlalchemy_session

import multiprocessing
import ssl

import requests
# import requests.exceptions
import requests_oauthlib
# import requests_exceptions


# import markupsafe
# import urllib3.exceptions
# import werkzeug.wrappers



import pymysql




# Uncomment for detailed oauthlib logs
# import logging
# import sys
# log = logging.getLogger('oauthlib')
# log.addHandler(logging.StreamHandler(sys.stdout))
# log.setLevel(logging.DEBUG)








myHostName = socket.gethostname()

print("\n\n\n")
print("**************************************")
print("Beginning of application.py")
print("**************************************\n\n")
print("myHostName = " + myHostName + "\n\n")
sys.stdout.flush()



def get_google_auth(state=None, token=None):
    if token:
        return requests_oauthlib.OAuth2Session(GOOGLE_CLIENT_ID, token=token)
    if state:
        return requests_oauthlib.OAuth2Session(
            GOOGLE_CLIENT_ID,
            state=state,
            redirect_uri=REDIRECT_URI)
    oauth = requests_oauthlib.OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=GOOGLE_CLIENT_SCOPE)
    return oauth




# type(myCalendarEvents['kind'])                 = <class 'str'>
# type(myCalendarEvents['etag'])                 = <class 'str'>
# type(myCalendarEvents['summary'])              = <class 'str'>
# type(myCalendarEvents['updated'])              = <class 'str'>
# type(myCalendarEvents['timeZone'])             = <class 'str'>
# type(myCalendarEvents['accessRole'])           = <class 'str'>
# type(myCalendarEvents['defaultReminders'])     = <class 'list'>
# type(myCalendarEvents['nextPageToken'])        = <class 'str'>
# type(myCalendarEvents['items'])                = <class 'list'>

def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print (k)
                dumpclean(v)
            else:
                print ('%s : %s' % (k, v))
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print (v)
    else:
        print (obj)




def dumpclean_str(obj):
    tempstr = ""
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                tempstr = tempstr + str(k) + "<br>\n"
                dumpclean(v)
            else:
                tempstr = tempstr + str(k) + " : " + str(v) + "<br>\n"

    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                tempstr = tempstr + str(v) + "<br>\n"
    else:
        tempstr = tempstr + str(obj) + "<br>\n"

    return tempstr







GLOBAL_LIST_OF_LOCAL_HOSTNAMES = [ "DESKTOP-MIRI5VU", "chi-ghalt2.cnvr.conversantmedia.com" ]


REDIRECT_URI = 'https://code.plantter.net/oauth2callback'
REDIRECT_URI_RELATIVE = '/oauth2callback'
AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

# USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
# CALENDAR_INFO = 'https://www.googleapis.com/calendar/v3/users/me'

GOOGLE_BASE_URL='https://www.googleapis.com/oauth2/v1/'
GOOGLE_CLIENT_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar',
    ]

# SECRET_KEY = 'development'
# SECRET_KEY = 'development3'     # need to change this periodically to reset prior sessions
# SECRET_KEY = 'development4'
SECRET_KEY = 'development5'
# SESSION_TYPE = 'redis'
SESSION_TYPE = 'filesystem'
DEBUG = True




# figure out how to make this not hard-coded in the application!






print ("REDIRECT_URI = " + REDIRECT_URI)
if any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
    REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback'
    print ("updated REDIRECT_URI = " + REDIRECT_URI)
sys.stdout.flush()






frontend = flask.Blueprint('frontend', __name__)


application = flask.Flask(__name__)
mySess = flask_session.Session()

# We use Flask-Appconfig here, but this is not a requirement
flask_appconfig.AppConfig(application)


# Install our Bootstrap extension
flask_bootstrap.Bootstrap(application)


application.register_blueprint(frontend)


application.config['BOOTSTRAP_SERVE_LOCAL'] = True


application.config['SSL'] = True


# Check Configuration section for more details
application.secret_key = SECRET_KEY
application.config['SESSION_TYPE'] = SESSION_TYPE

mySess.init_app(application)
# flask_session.Session(application)


login_manager = flask_login.LoginManager()
login_manager.init_app(application)


myApplicationContext = application.app_context()
myApplicationContext.push()



nav = flask_nav.Nav()

nav.init_app(application)



@nav.navigation()
def top_nav_default():
    items = [
        fne.View('planTTer',           '.index'),
        fne.View('Login',              '.login'),
        # fne.View('Home',               '.index'),
        # fne.View('About',              '.about'),
        # fne.View('Contact',            '.contact'),
        # fne.Link('Blog',               'http://blog.plantter.net/'),
        # fne.View('Shop',               '.shop'),
        # fne.View('Help & Feedback',    '.help')
        ]
    return fne.Navbar('', *items)


@nav.navigation()
def top_nav_user_loggedin():
    items = [
        fne.View('planTTer',           '.index'),
        fne.View('Logout',             '.logout'),
        fne.View('Stats',              '.debugstats'),
        # fne.View('Home',               '.index'),
        # fne.View('About',              '.about'),
        # fne.View('Contact',            '.contact'),
        # fne.Link('Blog',               'http://blog.plantter.net/'),
        # fne.View('Shop',               '.shop'),
        # fne.View('Help & Feedback',    '.help')
        ]
    return fne.Navbar('', *items)


nav.register_element('frontend_top_default', top_nav_default())


nav.register_element('frontend_top_user_loggedin', top_nav_user_loggedin())







# from https://stackoverflow.com/questions/36505091/flask-nav-bootstrap-navbar-dynamic-construction-align-some-element-to-the-righ
# Custom Navbar Renderer to render after certain bootstrap navbars templates

class CustomRenderer(flask_bootstrap.nav.BootstrapRenderer):
    def visit_Navbar(self, node):
        nav_tag = super(CustomRenderer, self).visit_Navbar(node)
        nav_tag['class'] = 'navbar navbar-default navbar-fixed-top'
        return nav_tag


# register renderer to app
flask_nav.register_renderer(application, 'custom', CustomRenderer)













print ("REDIRECT_URI = " + REDIRECT_URI + "\n")
sys.stdout.flush()




# oauth = flask_oauth.OAuth()
oauth = flask_oauthlib.client.OAuth(application)

oauth.init_app(application)








@application.route('/', methods=['GET','POST'])
# @flask_login.login_required
def index():
    print("\n\n")
    print("inside of index...\n\n")
    sys.stdout.flush()

    if 'google_token' in flask.session:
        tempUserName = flask.session['user_given_name']
        print("flask.session['user_given_name'] = " + flask.session['user_given_name'] + "\n\n")
        sys.stdout.flush()

        if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
            if flask.request.url.startswith('http://'):
                return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
            elif flask.request.url.startswith('https://'):
                return flask.render_template('index.html', username=tempUserName)
            abort(500)
        else:
            return flask.render_template('index.html', username=tempUserName)

    else:
        myGoogle = get_google_auth()

        auth_url, state = myGoogle.authorization_url(
            AUTH_URI,
            access_type='offline',
            # approval_prompt="force"
            # approval_prompt="auto"
            # approval_prompt="select_account"
            prompt="select_account"
            )

        # State is used to prevent CSRF, keep this for later.
        flask.session['oauth_state'] = state
        flask.session['oauth_auth_url'] = auth_url

        print("auth_url = " + auth_url)
        print("state = " + state)
        sys.stdout.flush()

        if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
            if flask.request.url.startswith('http://'):
                return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
            elif flask.request.url.startswith('https://'):
                return flask.render_template('index.html', auth_url=auth_url)
            abort(500)
        else:
            return flask.render_template('index.html', auth_url=auth_url)

    if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
        if flask.request.url.startswith('http://'):
            return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
        elif flask.request.url.startswith('https://'):
            return flask.render_template('index.html')
        abort(500)
    else:
        return flask.render_template('index.html')






@application.route('/login')
def login():
    print("\n\n")
    print("inside of login...\n\n")
    sys.stdout.flush()

    return flask.redirect(flask.url_for('google_oauth2'))




@application.route('/logout')
def logout():
    print("\n\n")
    print("inside of logout...\n\n")
    sys.stdout.flush()

    myTempKeys = list(flask.session.keys())

    print("myTempKeys = " + str(myTempKeys) + "\n\n")
    sys.stdout.flush()

    if myTempKeys:
        for key in myTempKeys:
            flask.session.pop(key, None)

    flask.session.clear()
    return flask.redirect(flask.url_for('index'))









@application.route('/forceclear')
def forceclear():
    print("\n\n")
    print("inside of forceclear...\n\n")
    sys.stdout.flush()
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


@application.route('/killapp', methods=['GET', 'POST'])
def killapp():
    print("\n\n")
    print("inside of killapp...\n\n")
    sys.stdout.flush()
    flask.session.clear()
    shutdown_server()
    return 'Server shutting down...'


@application.route('/sys-exit', methods=['GET', 'POST'])
def exitSys():
    print("\n\n")
    print("inside of sys-exit...\n\n")
    sys.stdout.flush()
    flask.session.clear()
    return sys.exit(0)


@application.route('/terminate', methods=['GET', 'POST'])
def terminate():
    print("\n\n")
    print("inside of terminate...\n\n")
    sys.stdout.flush()
    flask.session.clear()
    os.kill(os.getpid(), signal.SIGTERM)
    return 'Killing this process via os.kill(os.getpid(), signal.SIGTERM)...'


@application.route('/pythonkill', methods=['GET', 'POST'])
def pythonkill():
    print("\n\n")
    print("inside of pythonkill...\n\n")
    sys.stdout.flush()
    flask.session.clear()
    os.system("killall -KILL python")
    return 'Killing this process via killall -KILL python...'








@application.route('/index.html')
def redirecttobase():
    print("\n\n")
    print("inside of redirecttobase...\n\n")
    sys.stdout.flush()
    return flask.redirect(flask.url_for('index'))




@application.route('/google_oauth2')
def google_oauth2():
    print("\n\n")
    print("inside of google_oauth2...\n\n")
    sys.stdout.flush()

    myGoogle = get_google_auth()

    auth_url, state = myGoogle.authorization_url(
        AUTH_URI,
        access_type='offline',
        approval_prompt="force")

    flask.session['oauth_state'] = state
    flask.session['oauth_auth_url'] = auth_url

    print("auth_url = " + auth_url)
    print("state = " + state)
    sys.stdout.flush()

    return flask.redirect(auth_url)







@application.route(REDIRECT_URI_RELATIVE, methods=['GET', 'POST'])
def authorized():
    print("\n\n")
    print("inside of authorized...\n\n")
    sys.stdout.flush()

    myGoogle2 = get_google_auth(state=flask.session['oauth_state'])

    try:
        token = myGoogle2.fetch_token(
        TOKEN_URI,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=flask.request.url)
    except requests.exceptions.HTTPError:
        return 'HTTPError occurred.'

    flask.session['google_token'] = token

    myGoogle3 = get_google_auth(token=token)

    myGoogle5 = requests_oauthlib.OAuth2Session(GOOGLE_CLIENT_ID, token=flask.session['google_token'])

    myUserinfo = myGoogle5.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

    for x in myUserinfo:
        print (x)

    # id
    # email
    # verified_email
    # name
    # given_name
    # family_name
    # link
    # picture
    # gender
    # locale

    dumpclean(myUserinfo)
    print("\n\n\n")

    print("\n\n\n")
    if ('id' in myUserinfo.keys()) :
        print("myUserinfo['id']                 = " + myUserinfo['id'])
    if ('email' in myUserinfo.keys()) :
        print("myUserinfo['email']              = " + myUserinfo['email'])
    if ('verified_email' in myUserinfo.keys()) :
        print("myUserinfo['verified_email']     = " + str(myUserinfo['verified_email']))
    if ('name' in myUserinfo.keys()) :
        print("myUserinfo['name']               = " + myUserinfo['name'])
    if ('given_name' in myUserinfo.keys()) :
        print("myUserinfo['given_name']         = " + myUserinfo['given_name'])
    if ('family_name' in myUserinfo.keys()) :
        print("myUserinfo['family_name']        = " + myUserinfo['family_name'])
    if ('link' in myUserinfo.keys()) :
        print("myUserinfo['link']               = " + myUserinfo['link'])
    if ('picture' in myUserinfo.keys()) :
        print("myUserinfo['picture']            = " + myUserinfo['picture'])
    if ('gender' in myUserinfo.keys()) :
        print("myUserinfo['gender']             = " + myUserinfo['gender'])
    if ('locale' in myUserinfo.keys()) :
        print("myUserinfo['locale']             = " + myUserinfo['locale'])
    print("\n\n\n")

    sys.stdout.flush()


    flask.session['user_given_name'] = myUserinfo['given_name']

    print("we made it here 002\n\n")
    sys.stdout.flush()

    dumpclean(myUserinfo)
    print("\n\n\n")

    print("we made it here 005\n\n")
    sys.stdout.flush()

    myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary').json()
    # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/glenn.strycker%40gmail.com').json()
    # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/glenn.strycker@gmail.com').json()
    # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/src=glenn.strycker%40gmail.com').json()

    print("we made it here 007\n\n")
    sys.stdout.flush()

    if myCalendarinfo:
        for x in myCalendarinfo:
            print (x)

    print("we made it here 008\n\n")
    sys.stdout.flush()

    dumpclean(myCalendarinfo)
    print("\n\n\n")

    print("we made it here 009\n\n")
    sys.stdout.flush()


    currentDateTime = datetime.datetime.now()

    print("currentDateTime = " + currentDateTime.isoformat('T') + "\n\n")
    sys.stdout.flush()

    # currentDateTime = 2017-09-19T18:51:56.530280
    # currentDateTime = 2017-09-19T21:53:01.677419


    modifiedMinTime = currentDateTime.replace(hour=0, minute=0, second=0, microsecond=0)

    print("modifiedMinTime (original) = " + modifiedMinTime.isoformat('T') + "\n\n")
    sys.stdout.flush()

    # see https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python

    # try:
    #     modifiedMinTime = modifiedMinTime.replace(year = modifiedMinTime.year - 1)
    # except ValueError:
    #     return modifiedMinTime + (date(modifiedMinTime.year - 1, 1, 1) - date(modifiedMinTime.year, 1, 1))

    # modifiedMinTime = modifiedMinTime - dateutil.relativedelta.relativedelta(years=1)

    print("modifiedMinTime (minus a year) = " + modifiedMinTime.isoformat('T') + "\n\n")
    sys.stdout.flush()


    # modifiedMinTime = 2017-09-19T00:00:00


    myLocalTimeZone = tzlocal.get_localzone()
    print("myLocalTimeZone = " + str(myLocalTimeZone) + "\n\n")
    sys.stdout.flush()


    # myLocalTimeZone = local       -- when I ran on localhost
    # myLocalTimeZone = UTC         -- when I ran on Amazon AWS EC2 server on actual code.plantter.net


    # modifiedMinTimeUTCstr = myLocalTimeZone.localize(modifiedMinTime).isoformat('T')
    modifiedMinTimeUTCstr = myLocalTimeZone.localize(modifiedMinTime).isoformat('T').replace('+00:00', 'Z')
    print("modifiedMinTimeUTCstr = " + modifiedMinTimeUTCstr + "\n\n")
    sys.stdout.flush()


    # modifiedMinTimeUTCstr = 2017-09-19T00:00:00-05:00
    # modifiedMinTimeUTCstr = 2017-09-20T00:00:00+00:00


    flask.session['modified_MinTime_UTC'] = modifiedMinTimeUTCstr



    # print("type(myGoogle5) = " + str(type(myGoogle5)) + "\n\n")
    # sys.stdout.flush()


    # myCalendarEvents = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary/events').json()
    # myCalendarEvents = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=%s' % currentDateTime.isoformat('T') ).json()
    # myCalendarEvents = myGoogle5.get(url='https://www.googleapis.com/calendar/v3/calendars/primary/events', timeMin=currentDateTime.isoformat('T') ).json()
    # myCalendarEvents = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=%s' % modifiedMinTimeUTCstr ).json()
    # myCalendarEvents = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=5&timeMin=%s' % modifiedMinTimeUTCstr ).json()
    # myCalendarEvents = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=20&timeMin=%s' % flask.session['modified_MinTime_UTC'] ).json()

    print("we made it here 0071a\n\n")
    sys.stdout.flush()


    # numberOfEventsToPull = 20
    numberOfEventsToPull = 30
    # numberOfEventsToPull = 50
    # numberOfEventsToPull = 100
    # numberOfEventsToPull = 500
    # numberOfEventsToPull = 3000


    if 'modified_MinTime_UTC' in flask.session:
        print("flask.session['modified_MinTime_UTC'] = " + str(flask.session['modified_MinTime_UTC']) + "\n\n")
        sys.stdout.flush()
        # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=20&timeMin=' + str(flask.session['modified_MinTime_UTC'])
        # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=' + str(flask.session['modified_MinTime_UTC'])
        # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=' + str(flask.session['modified_MinTime_UTC']) + '&'
        # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=2017-09-20T00:00:00Z'
        calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=' + str(numberOfEventsToPull) + '&timeMin=' + str(flask.session['modified_MinTime_UTC'])
    else:
        print("flask.session['modified_MinTime_UTC'] = NOT FOUND\n\n")
        sys.stdout.flush()
        # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20'
        # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=2017-09-20T00:00:00Z'
        calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=' + str(numberOfEventsToPull)


    print("calendarAPIurl = " + calendarAPIurl + "\n\n")
    sys.stdout.flush()

    print("we made it here 0071b\n\n")
    sys.stdout.flush()


    myCalendarEvents = myGoogle5.get(calendarAPIurl).json()


    print("we made it here 0072\n\n")
    sys.stdout.flush()

    # if myCalendarEvents:
    #     for x in myCalendarEvents:
    #         print (x)

    print("\n\n\n\n")
    sys.stdout.flush()


    print("we made it here 0082\n\n")
    sys.stdout.flush()

    # dumpclean(myCalendarEvents)
    # print("\n\n\n")

    print("we made it here 0092\n\n")
    sys.stdout.flush()




    print("\n\n\n")
    sys.stdout.flush()


    #print("myCalendarinfo['id']                 = " + myCalendarinfo['id'])

    if ('kind' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['kind'])                 = " + str(type(myCalendarEvents['kind'])))
    if ('etag' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['etag'])                 = " + str(type(myCalendarEvents['etag'])))
    if ('summary' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['summary'])              = " + str(type(myCalendarEvents['summary'])))
    if ('updated' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['updated'])              = " + str(type(myCalendarEvents['updated'])))
    if ('timeZone' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['timeZone'])             = " + str(type(myCalendarEvents['timeZone'])))
    if ('accessRole' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['accessRole'])           = " + str(type(myCalendarEvents['accessRole'])))
    if ('defaultReminders' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['defaultReminders'])     = " + str(type(myCalendarEvents['defaultReminders'])))
    if ('nextPageToken' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['nextPageToken'])        = " + str(type(myCalendarEvents['nextPageToken'])))
    if ('items' in myCalendarEvents.keys()) :
        print("type(myCalendarEvents['items'])                = " + str(type(myCalendarEvents['items'])))
    print("\n\n")

    print("\n\n\n")

    if ('kind' in myCalendarEvents.keys()) :
        print("myCalendarEvents['kind']               = " + myCalendarEvents['kind'])
    if ('etag' in myCalendarEvents.keys()) :
        print("myCalendarEvents['etag']               = " + myCalendarEvents['etag'])
    if ('summary' in myCalendarEvents.keys()) :
        print("myCalendarEvents['summary']            = " + myCalendarEvents['summary'])
    if ('updated' in myCalendarEvents.keys()) :
        print("myCalendarEvents['updated']            = " + myCalendarEvents['updated'])
    if ('timeZone' in myCalendarEvents.keys()) :
        print("myCalendarEvents['timeZone']           = " + myCalendarEvents['timeZone'])
    if ('kind' in myCalendarEvents.keys()) :
        print("myCalendarEvents['accessRole']         = " + myCalendarEvents['accessRole'])
    if ('defaultReminders' in myCalendarEvents.keys()) :
        print("myCalendarEvents['defaultReminders']   = " + str(myCalendarEvents['defaultReminders']))
    if ('nextPageToken' in myCalendarEvents.keys()) :
        print("myCalendarEvents['nextPageToken']      = " + myCalendarEvents['nextPageToken'])
    # print("myCalendarEvents['items']              = " + str(myCalendarEvents['items']) + "\n\n")
    print("\n\n")


    print("\n\n\n")


    if ('items' in myCalendarEvents.keys()) :
        itemNum = 0
        for myItem in myCalendarEvents['items']:
            itemNum += 1

            if ('summary' in myItem.keys()) :
                if ('plantter' in str(myItem['summary']).lower()) :
                    print("\n\n\n")
                    print("itemNum = " + str(itemNum))
                    if ('kind' in myItem.keys()) :
                        print("myItem['kind']               = " + myItem['kind'])
                    print("myItem['etag']               = " + myItem['etag'])
                    print("myItem['id']                 = " + myItem['id'])
                    print("myItem['status']             = " + myItem['status'])
                    print("myItem['htmlLink']           = " + myItem['htmlLink'])
                    print("myItem['created']            = " + myItem['created'])
                    print("myItem['updated']            = " + myItem['updated'])
                    print("myItem['summary']            = " + myItem['summary'])
                    print("myItem['creator']            = " + str(myItem['creator']))
                    print("myItem['organizer']          = " + str(myItem['organizer']))
                    print("myItem['start']              = " + str(myItem['start']))
                    print("myItem['end']                = " + str(myItem['end']))
                    if ('recurrence' in myItem.keys()) :
                        print("myItem['recurrence']         = " + str(myItem['recurrence']))
                    if ('transparency' in myItem.keys()) :
                        print("myItem['transparency']       = " + str(myItem['transparency']))
                    print("myItem['iCalUID']            = " + str(myItem['iCalUID']))
                    print("myItem['sequence']           = " + str(myItem['sequence']))
                    print("myItem['reminders']          = " + str(myItem['reminders']))
                    print("\n\n\n")
                else:
                    tempStart = datetime.datetime(1980, 1, 1, 0, 0)
                    tempEnd = datetime.datetime(2999, 12, 31, 0, 0)
                    if ('start' in myItem.keys()) :
                        if ('dateTime' in myItem['start']) :
                            tempStart = dateutil.parser.parse(myItem['start']['dateTime'])
                        elif ('date' in myItem['start']) :
                            tempStart = dateutil.parser.parse(myItem['start']['date'])
                    if ('end' in myItem.keys()) :
                        if ('dateTime' in myItem['end']) :
                            tempEnd = dateutil.parser.parse(myItem['end']['dateTime'])
                        elif ('date' in myItem['end']) :
                            tempEnd = dateutil.parser.parse(myItem['end']['date'])
                    print("itemNum = " + str(itemNum) + "      start = " + tempStart.isoformat('T') + "      end = " + tempEnd.isoformat('T'))
            else:
                tempStart = datetime.datetime(1980, 1, 1, 0, 0)
                tempEnd = datetime.datetime(2999, 12, 31, 0, 0)
                if ('start' in myItem.keys()) :
                    if ('dateTime' in myItem['start']) :
                        tempStart = dateutil.parser.parse(myItem['start']['dateTime'])
                    elif ('date' in myItem['start']) :
                        tempStart = dateutil.parser.parse(myItem['start']['date'])
                if ('end' in myItem.keys()) :
                    if ('dateTime' in myItem['end']) :
                        tempEnd = dateutil.parser.parse(myItem['end']['dateTime'])
                    elif ('date' in myItem['end']) :
                        tempEnd = dateutil.parser.parse(myItem['end']['date'])

                print("itemNum = " + str(itemNum) + "      start = " + tempStart.isoformat('T') + "      end = " + tempEnd.isoformat('T'))


    print("\n\n\n")

    sys.stdout.flush()

    #flask.session['user_given_name'] = myCalendarinfo['given_name']



    print("we made it here 0100\n\n")
    sys.stdout.flush()




    # s3resource = boto3.resource('s3')

    print("we made it here 0101\n\n")
    sys.stdout.flush()


    # s3client = boto3.client('s3')

    s3client = boto3.client(
        's3',
        # Hard coded strings as credentials, not recommended.
        aws_access_key_id='',
        aws_secret_access_key=''
        )

    print("we made it here 0102\n\n")
    sys.stdout.flush()

    s3session = boto3.Session(
        aws_access_key_id='',
        aws_secret_access_key=''
        )

    print("we made it here 0103\n\n")
    sys.stdout.flush()


    # s3resource = boto3.resource('s3')
    s3resource = s3session.resource('s3')

    print("we made it here 0104\n\n")
    sys.stdout.flush()




    for bucket in s3resource.buckets.all():
        print(bucket.name)

    print("\n\n\n")


    # all-other-emails
    # aws-codestar-us-west-2-924186898717
    # aws-codestar-us-west-2-924186898717-plantter-code-pipeline
    # aws-codestar-us-west-2-924186898717-plantter-flask1-pipeline
    # aws-website-plantter-27zb3
    # elasticbeanstalk-us-west-2-924186898717
    # emails-to-admin
    # plantter-aws-billing
    # plantter-logs
    # plantter-sns-forwarder



    print("we made it here 0105\n\n")
    sys.stdout.flush()




    # Get handle for IAM client
    iamClient = boto3.client(
        'iam',
        aws_access_key_id='',
        aws_secret_access_key=''
        )

    print("we made it here 0108\n\n")
    sys.stdout.flush()

    paginator = iamClient.get_paginator('list_users')
    for response in paginator.paginate():
        print(response)

    print("\n\n\n")


    print("we made it here 0109\n\n")
    sys.stdout.flush()




    # see http://boto3.readthedocs.io/en/latest/guide/migrations3.html for very helpful tips!!


    response1 = s3client.list_buckets()

    print("we made it here 0110\n\n")
    sys.stdout.flush()


    buckets1 = [bucket['Name'] for bucket in response1['Buckets']]

    print("we made it here 0111\n\n")
    sys.stdout.flush()


    # if 'plantter-user-profiles' not in s3resource.buckets.all():
    # if 'plantter-user-profiles' not in list(s3resource.buckets.all()):
    if 'plantter-user-profiles' not in [x.name for x in list(s3resource.buckets.all())]:
        print('plantter-user-profiles is not in the AWS buckets... creating...')
        sys.stdout.flush()

        s3client.create_bucket(
            Bucket='plantter-user-profiles',
            # CreateBucketConfiguration={'LocationConstraint': 'us-west-1'}
            )

        print("we made it here 0112\n\n")
        sys.stdout.flush()

        # bucketLocation = s3client.getBucketLocation(new GetBucketLocationRequest(bucketName));
        # print("bucket location = " + bucketLocation);

        result2 = s3client.get_bucket_acl(Bucket='plantter-user-profiles')

        print("we made it here 0113\n\n")
        sys.stdout.flush()

        print(result2)
        print("\n\n")


        # {'ResponseMetadata': {'RequestId': '93E4EAA235A4E6F4', 'HostId': 'DT/oKn1nxBbEYBJ6CC54kXiop3sWABHzpx2XNrUGTlgAH4fHpXzoFjYuhqRxlmGLXIJcES2d2Cs=',
        # 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': 'DT/oKn1nxBbEYBJ6CC54kXiop3sWABHzpx2XNrUGTlgAH4fHpXzoFjYuhqRxlmGLXIJcES2d2Cs=',
        # 'x-amz-request-id': '93E4EAA235A4E6F4', 'date': 'Thu, 28 Sep 2017 21:43:43 GMT', 'content-type': 'application/xml',
        # 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0},
        # 'Owner': {'DisplayName': 'mitka_karamazov', 'ID': '1283c150ff9488b377422eb3d4d257194d61032a0013dfd040ab7e81e39ef5f7'},
        # 'Grants': [{'Grantee': {'DisplayName': 'mitka_karamazov', 'ID': '1283c150ff9488b377422eb3d4d257194d61032a0013dfd040ab7e81e39ef5f7',
        # 'Type': 'CanonicalUser'}, 'Permission': 'FULL_CONTROL'}]}

        # {'ResponseMetadata': {'RequestId': '23AEDE644450A632', 'HostId': 'tGVYT7bYuA0CN56PCSOflpKIDMHQcOppdwN0AVi1O+KyCNblWot0oS8iWhaxECb71rT8AwA7ySE=',
        # HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': 'tGVYT7bYuA0CN56PCSOflpKIDMHQcOppdwN0AVi1O+KyCNblWot0oS8iWhaxECb71rT8AwA7ySE=',
        # 'x-amz-request-id': '23AEDE644450A632', 'date': 'Thu, 28 Sep 2017 22:07:36 GMT', 'content-type': 'application/xml',
        # 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0},
        # 'Owner': {'DisplayName': 'mitka_karamazov', 'ID': '1283c150ff9488b377422eb3d4d257194d61032a0013dfd040ab7e81e39ef5f7'},
        # 'Grants': [{'Grantee': {'DisplayName': 'mitka_karamazov', 'ID': '1283c150ff9488b377422eb3d4d257194d61032a0013dfd040ab7e81e39ef5f7',
        # 'Type': 'CanonicalUser'}, 'Permission': 'FULL_CONTROL'}]}

        print("we made it here 0114\n\n")
        sys.stdout.flush()


        #        s3resource = s3session.resource('s3')
        #
        #        print("we made it here 0114b\n\n")
        #        sys.stdout.flush()


    else:
        print('plantter-user-profiles exists in the AWS buckets... ready to load...')
        sys.stdout.flush()




    # if 'plantter-user-profiles' not in s3resource.buckets.all():
    # if 'plantter-user-profiles' not in list(s3resource.buckets.all()):
    if 'plantter-user-profiles' not in [x.name for x in list(s3resource.buckets.all())]:
        print('plantter-user-profiles is STILL not in the AWS buckets... ERROR!\n')
        sys.stdout.flush()
    else:
        print('loading plantter-user-profiles bucket from AWS...\n\n')
        sys.stdout.flush()


        print("we made it here 0115\n\n")
        sys.stdout.flush()

        result2 = s3client.get_bucket_acl(Bucket='plantter-user-profiles')

        print("we made it here 0116\n\n")
        sys.stdout.flush()

        print(result2)
        print("\n\n")

        print("we made it here 0117\n\n")
        sys.stdout.flush()


        plantterBucket = s3resource.Bucket('plantter-user-profiles')


        print("we made it here 0118\n\n")
        sys.stdout.flush()

        exists = True
        error_code = -1
        try:
            s3resource.meta.client.head_bucket(Bucket='plantter-user-profiles')
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                exists = False

        print("plantter-user-profiles exists = " + str(exists))
        if not exists:
            print("error_code = " + str(error_code))

        print("\n\n")
        sys.stdout.flush()


        # Call to S3 to retrieve the policy for the given bucket
        try:
            result = s3client.get_bucket_policy(Bucket='plantter-user-profiles')

            print("we made it here 0118c\n\n")
            sys.stdout.flush()

            print(result)

            # {'ResponseMetadata': {'RequestId': '674413A88F292DC9', 'HostId': 'yuVF/4n9ZIDstUTc8/Niiyukxc3QqSP1cJE5xXTZDoXMaByCzVH9/IMcFUPGW6u9Y4qdZcBoBzA=',
            # 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': 'yuVF/4n9ZIDstUTc8/Niiyukxc3QqSP1cJE5xXTZDoXMaByCzVH9/IMcFUPGW6u9Y4qdZcBoBzA=',
            # 'x-amz-request-id': '674413A88F292DC9', 'date': 'Fri, 29 Sep 2017 17:34:02 GMT', 'content-type': 'application/json',
            # 'content-length': '164', 'server': 'AmazonS3'}, 'RetryAttempts': 0},
            # 'Policy': '{"Version":"2012-10-17","Statement":[{
            # "Sid":"AddPerm","Effect":"Allow","Principal":"*","Action":"s3:GetObject",
            # "Resource":"arn:aws:s3:::plantter-user-profiles/*"}]}'}

            print("we made it here 0118d\n\n")
            sys.stdout.flush()
        except:
            print("There is no bucket policy in place!  Setting a new bucket policy...\n\n")
            sys.stdout.flush()

            bucket_name = "plantter-user-profiles"

            # Create the bucket policy
            bucket_policy = {
                'Version': '2012-10-17',
                'Statement': [{
                    'Sid': 'AddPerm',
                    'Effect': 'Allow',
                    'Principal': '*',
                    'Action': ['s3:GetObject'],
                    'Resource': "arn:aws:s3:::%s/*" % bucket_name
                }]
            }

            # Convert the policy to a JSON string
            bucket_policy = json.dumps(bucket_policy)


            print("New bucket policy attempt = " + str(bucket_policy) + "\n\n")
            sys.stdout.flush()


            # Set the new policy on the given bucket
            s3client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

            print("we made it here 0118e\n\n")
            sys.stdout.flush()

            try:
                result2 = s3client.get_bucket_policy(Bucket='plantter-user-profiles')

                print("we made it here 0118f\n\n")
                sys.stdout.flush()

                print(result2)

                print("we made it here 0118g\n\n")
                sys.stdout.flush()
            except:
                print("There is STILL no bucket policy in place!\n\n")
                sys.stdout.flush()



        print("we made it here 0119\n\n")
        sys.stdout.flush()

        tempObjectCollection = plantterBucket.objects.all()
        tempKeysList = list(tempObjectCollection)

        print("Number of entries in plantter-user-profiles:   len(tempKeysList) = " + str(len(tempKeysList)) + "\n\n")
        sys.stdout.flush()

        for key in plantterBucket.objects.all():
            print(key.key)

        print("\n\n\n")

        print("we made it here 0120\n\n")
        sys.stdout.flush()



    print("we made it here 0121\n\n")
    sys.stdout.flush()




    myConnection = pymysql.connect(RDS_HOST, user=RDS_DB_USER, port=RDS_PORT, passwd=RDS_DB_PASSWORD, db=RDS_DB_NAME)

    print("we made it here 0122\n\n")
    sys.stdout.flush()


    mySQLcursor = myConnection.cursor()

    print("we made it here 0122\n\n")
    sys.stdout.flush()


    # select the database
    mySQLcursor.execute("USE plantterdb")

    print("we made it here 0123\n\n")
    sys.stdout.flush()


    mySQLcursor.execute("SHOW TABLES")

    print("we made it here 0124\n\n")
    sys.stdout.flush()


    # return data from last query
    # tempTables = mySQLcursor.fetchall()

    print("\n\n")
    print("Show tables:\n")
    for (table_name,) in mySQLcursor:
        print(table_name)
    print("\n\n\n")
    sys.stdout.flush()




    print("we made it here 0126\n\n")
    sys.stdout.flush()



    print("end of function authorized()\n\n")
    sys.stdout.flush()


    return flask.redirect(flask.url_for('index'))










@application.route('/about.html', methods=['GET','POST'])
def about():
    if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
        if flask.request.url.startswith('http://'):
            return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
        elif flask.request.url.startswith('https://'):
            if 'google_token' in flask.session and 'user_given_name' in flask.session:
                return flask.render_template('about.html', username=flask.session['user_given_name'])
            else:
                return flask.render_template('about.html')
        abort(500)
    else:
        if 'google_token' in flask.session and 'user_given_name' in flask.session:
            return flask.render_template('about.html', username=flask.session['user_given_name'])
        else:
            return flask.render_template('about.html')
        return flask.render_template('about.html')
    return flask.render_template('about.html')



@application.route('/contact.html', methods=['GET','POST'])
def contact():
    if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
        if flask.request.url.startswith('http://'):
            return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
        elif flask.request.url.startswith('https://'):
            if 'google_token' in flask.session and 'user_given_name' in flask.session:
                return flask.render_template('contact.html', username=flask.session['user_given_name'])
            else:
                return flask.render_template('contact.html')
        abort(500)
    else:
        if 'google_token' in flask.session and 'user_given_name' in flask.session:
            return flask.render_template('contact.html', username=flask.session['user_given_name'])
        else:
            return flask.render_template('contact.html')
        return flask.render_template('contact.html')
    return flask.render_template('contact.html')



@application.route('/blog.html', methods=['GET','POST'])
def blog():
    return flask.redirect("http://blog.plantter.net", code=302)



@application.route('/shop.html', methods=['GET','POST'])
def shop():
    if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
        if flask.request.url.startswith('http://'):
            return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
        elif flask.request.url.startswith('https://'):
            if 'google_token' in flask.session and 'user_given_name' in flask.session:
                return flask.render_template('shop.html', username=flask.session['user_given_name'])
            else:
                return flask.render_template('shop.html')
        abort(500)
    else:
        if 'google_token' in flask.session and 'user_given_name' in flask.session:
            return flask.render_template('shop.html', username=flask.session['user_given_name'])
        else:
            return flask.render_template('shop.html')
        return flask.render_template('shop.html')
    return flask.render_template('shop.html')



@application.route('/help.html', methods=['GET','POST'])
def help():
    if not any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
        if flask.request.url.startswith('http://'):
            return flask.redirect(flask.request.url.replace('http', 'https', 1).replace('080', '443', 1))
        elif flask.request.url.startswith('https://'):
            if 'google_token' in flask.session and 'user_given_name' in flask.session:
                return flask.render_template('help.html', username=flask.session['user_given_name'])
            else:
                return flask.render_template('help.html')
        abort(500)
    else:
        if 'google_token' in flask.session and 'user_given_name' in flask.session:
            return flask.render_template('help.html', username=flask.session['user_given_name'])
        else:
            return flask.render_template('help.html')
        return flask.render_template('help.html')
    return flask.render_template('help.html')






@application.route('/debugstats/', methods=['GET'])
def debugstats():
    print("\n\n")
    print("inside of debugstats...\n\n")
    sys.stdout.flush()

    cwd = os.getcwd()

    # msg = '{"Output":"Hello World 34"}<br>'

    msg = '<html lang="en">\n'
    msg = msg + "<head>\n"
    msg = msg + '<meta charset="utf-8">\n'
    msg = msg + '<meta http-equiv="X-UA-Compatible" content="IE=edge">\n'
    msg = msg + '<title>planTTer</title>\n'
    msg = msg + '<meta name="description" content="planTTer social platform">\n'
    msg = msg + "</head>\n"
    msg = msg + "<body>\n"
    msg = msg + '{"Output":"Hello World 35"}<br>\n'
    msg = msg + "current path cwd =" + cwd + "<br>\n"

    isSSL = application.config.get("SSL")
    isSecure = flask.request.is_secure
    serverName = application.config.get("SERVER_NAME")
    appRoot = application.config.get("app_ROOT")

    if isSSL:
        if isSecure:
            msg = msg + "We are using SSL, and it is a secure HTTPS connection<br>\n"
        else:
            msg = msg + "We are attempting to use SSL, but it does NOT appear to be secure<br>\n"
    else:
        if isSecure:
            msg = msg + "This appears to be a secure HTTPS connection, but application.config.get(\"SSL\") is False<br>\n"
        else:
            msg = msg + "We do not appear to be attempting to use SSL at all<br>\n"

    if serverName:
        msg = msg + "SERVER_NAME = " + str(serverName) + "<br>\n"
    else:
        msg = msg + "Server name unavailable<br>\n"

    if appRoot:
        msg = msg + "app_ROOT = " + str(appRoot) + "<br>\n"
    else:
        msg = msg + "app_ROOT unavailable<br>\n"

    if myHostName:
        msg = msg + "myHostName = " + str(myHostName) + "<br>\n"

    if 'oauth_state' in flask.session:
        msg = msg + "<br>" + "flask.session[oauth_state]        = " + flask.session['oauth_state'] + "<br>\n"

    if 'oauth_auth_url' in flask.session:
        msg = msg + "<br>" + "flask.session[oauth_auth_url]     = " + flask.session['oauth_auth_url'] + "<br>\n"

    if 'user_given_name' in flask.session:
        msg = msg + "<br>" + "flask.session[user_given_name]    = " + flask.session['user_given_name'] + "<br>\n"

    if 'google_token' in flask.session:
        msg = msg + "<br><br>\n"
        # msg = msg + "flask.session[google_token] is present!<br><br>\n"
        msg = msg + "flask.session[google_token]        = " + json.dumps(flask.session['google_token']) + "<br><br>\n"
        # msg = msg + "flask.session[google_token]        = " + str(flask.session['google_token']) + "<br><br>\n"

        ## myTempToken = flask.session['google_token']
        #myGoogle6 = requests_oauthlib.OAuth2Session(GOOGLE_CLIENT_ID, token=flask.session['google_token'])
        #myUserinfo = myGoogle6.get(GOOGLE_BASE_URL + 'userinfo')

        myTempToken = flask.session['google_token']
        myGoogle3 = get_google_auth(token=myTempToken)
        myGoogle5 = requests_oauthlib.OAuth2Session(GOOGLE_CLIENT_ID, token=myTempToken)
        myUserinfo = myGoogle5.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

        msg = msg + "myUserinfo['id']                 = " + myUserinfo['id'] + "<br>\n"
        msg = msg + "myUserinfo['email']              = " + myUserinfo['email'] + "<br>\n"
        msg = msg + "myUserinfo['verified_email']     = " + str(myUserinfo['verified_email']) + "<br>\n"
        msg = msg + "myUserinfo['name']               = " + myUserinfo['name'] + "<br>\n"
        msg = msg + "myUserinfo['given_name']         = " + myUserinfo['given_name'] + "<br>\n"
        msg = msg + "myUserinfo['family_name']        = " + myUserinfo['family_name'] + "<br>\n"
        # msg = msg + "myUserinfo['link']               = " + myUserinfo['link'] + "<br>\n"
        msg = msg + "myUserinfo['picture']            = " + myUserinfo['picture'] + "<br>\n"
        # msg = msg + "myUserinfo['gender']             = " + myUserinfo['gender'] + "<br>\n"
        msg = msg + "myUserinfo['locale']             = " + myUserinfo['locale'] + "<br>\n"
        msg = msg + "<br><br>\n"


        print("we made it here 020\n\n")
        sys.stdout.flush()

        msg = msg + "<font color='blue'><b>\n"
        msg = msg + dumpclean_str(myUserinfo)
        msg = msg + "</font></b>\n"
        print("\n\n\n")

        print("we made it here 020b\n\n")
        sys.stdout.flush()





        # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/calendarId').json()
        myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary').json()
        # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/glenn.strycker%40gmail.com').json()
        # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/glenn.strycker@gmail.com').json()
        # myCalendarinfo = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/src=glenn.strycker%40gmail.com').json()


        #        print("we made it here 021\n\n")
        #        sys.stdout.flush()
        #
        #        print("myCalendarinfo = " + str(myCalendarinfo) + "\n\n")
        #        sys.stdout.flush()
        #
        #        print("we made it here 022\n\n")
        #        sys.stdout.flush()


        print("\n\n\n")
        sys.stdout.flush()

        msg = msg + "<br><br>\n"
        msg = msg + "<br><br>\n"

        msg = msg + "myCalendarinfo['kind']         = " + myCalendarinfo['kind'] + "<br>\n"
        msg = msg + "myCalendarinfo['etag']         = " + myCalendarinfo['etag'] + "<br>\n"
        msg = msg + "myCalendarinfo['id']           = " + myCalendarinfo['id'] + "<br>\n"
        msg = msg + "myCalendarinfo['summary']      = " + myCalendarinfo['summary'] + "<br>\n"
        msg = msg + "myCalendarinfo['timeZone']     = " + myCalendarinfo['timeZone'] + "<br>\n"
        msg = msg + "<br><br>\n"

        msg = msg + "<br><br>\n"
        msg = msg + "<br><br>\n"
        msg = msg + "<br><br>\n"





        # numberOfEventsToPull = 20
        numberOfEventsToPull = 30
        # numberOfEventsToPull = 50
        # numberOfEventsToPull = 100
        # numberOfEventsToPull = 500
        # numberOfEventsToPull = 3000


        # myCalendarEvents = myGoogle5.get('https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=20&timeMin=%s' % flask.session['modified_MinTime_UTC'] ).json()

        if 'modified_MinTime_UTC' in flask.session:
            msg = msg + "<br>" + "flask.session[modified_MinTime_UTC] = " + str(flask.session['modified_MinTime_UTC']) + "<br>\n"
            # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=' + str(flask.session['modified_MinTime_UTC'])
            # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=' + str(flask.session['modified_MinTime_UTC']) + '&'
            # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=2017-09-20T00:00:00Z'
            calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=' + str(numberOfEventsToPull) + '&timeMin=' + str(flask.session['modified_MinTime_UTC'])
        else:
            msg = msg + "<br>" + "flask.session[modified_MinTime_UTC] = NOT FOUND<br>\n"
            # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20'
            # # calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=20&timeMin=2017-09-20T00:00:00Z'
            calendarAPIurl = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?singleEvents=true&orderBy=startTime&maxResults=' + str(numberOfEventsToPull)


        msg = msg + "<br>" + "calendarAPIurl = " + calendarAPIurl + "<br>\n"
        print("calendarAPIurl = " + calendarAPIurl + "\n\n")
        sys.stdout.flush()


        print("we made it here 0171b\n\n")
        sys.stdout.flush()


        myCalendarEvents = myGoogle5.get(calendarAPIurl).json()


        print("we made it here 0171c\n\n")
        sys.stdout.flush()

        # dumpclean(myCalendarEvents)
        # print("\n\n\n")

        print("we made it here 0171d\n\n")
        sys.stdout.flush()

        # msg = msg + "<font color='blue'><b>\n"
        # msg = msg + dumpclean_str(myCalendarEvents)
        # msg = msg + "</font></b>\n"
        # print("\n\n\n")

        print("we made it here 0171e\n\n")
        sys.stdout.flush()



        # msg = msg + "type(myCalendarEvents['kind'])                 = " + str(type(myCalendarEvents['kind'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['etag'])                 = " + str(type(myCalendarEvents['etag'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['summary'])              = " + str(type(myCalendarEvents['summary'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['updated'])              = " + str(type(myCalendarEvents['updated'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['timeZone'])             = " + str(type(myCalendarEvents['timeZone'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['accessRole'])           = " + str(type(myCalendarEvents['accessRole'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['defaultReminders'])     = " + str(type(myCalendarEvents['defaultReminders'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['nextPageToken'])        = " + str(type(myCalendarEvents['nextPageToken'])) + "<br>\n"
        # msg = msg + "type(myCalendarEvents['items'])                = " + str(type(myCalendarEvents['items'])) + "<br>\n"
        # msg = msg + "<br><br>\n"


        msg = msg + "<br><br>\n"
        msg = msg + "<br><br>\n"

        if ('kind' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['kind']               = " + myCalendarEvents['kind'] + "<br>\n"
        if ('etag' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['etag']               = " + myCalendarEvents['etag'] + "<br>\n"
        if ('summary' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['summary']            = " + myCalendarEvents['summary'] + "<br>\n"
        if ('updated' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['updated']            = " + myCalendarEvents['updated'] + "<br>\n"
        if ('timeZone' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['timeZone']           = " + myCalendarEvents['timeZone'] + "<br>\n"
        if ('accessRole' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['accessRole']         = " + myCalendarEvents['accessRole'] + "<br>\n"
        if ('defaultReminders' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['defaultReminders']   = " + str(myCalendarEvents['defaultReminders']) + "<br>\n"
        if ('nextPageToken' in myCalendarEvents.keys()) :
            msg = msg + "myCalendarEvents['nextPageToken']      = " + myCalendarEvents['nextPageToken'] + "<br>\n"
        # msg = msg + "myCalendarEvents['items']              = " + str(myCalendarEvents['items']) + "<br>\n"
        msg = msg + "<br><br>\n"
        msg = msg + "<br><br>\n"



        # myItem['summary'] = planTTer -- open and available for meeting up with a friend

        if ('items' in myCalendarEvents.keys()) :
            itemNum = 0
            for myItem in myCalendarEvents['items']:
                itemNum += 1

                # msg = msg + "itemNum = " + str(itemNum) + "<br><br>\n"
                # msg = msg + "itemNum = " + str(itemNum) + "<br>\n"

                if ('summary' in myItem.keys()) :
                    if ('plantter' in str(myItem['summary']).lower()) :

                        msg = msg + "<br><br>\n"
                        msg = msg + "<br><br>\n"
                        msg = msg + "itemNum = " + str(itemNum) + "<br>\n"

                        if ('kind' in myItem.keys()) :
                            msg = msg + "myItem['kind']               = " + myItem['kind'] + "<br>\n"
                        msg = msg + "myItem['etag']               = " + myItem['etag'] + "<br>\n"
                        msg = msg + "myItem['id']                 = " + myItem['id'] + "<br>\n"
                        msg = msg + "myItem['status']             = " + myItem['status'] + "<br>\n"
                        msg = msg + "myItem['htmlLink']           = " + myItem['htmlLink'] + "<br>\n"
                        msg = msg + "myItem['created']            = " + myItem['created'] + "<br>\n"
                        msg = msg + "myItem['updated']            = " + myItem['updated'] + "<br>\n"
                        # msg = msg + "myItem['summary']            = " + myItem['summary'] + "<br>\n"
                        msg = msg + "<font color='red'><b>myItem['summary']            = " + myItem['summary'] + "</b></font><br>\n"
                        msg = msg + "myItem['creator']            = " + str(myItem['creator']) + "<br>\n"
                        msg = msg + "myItem['organizer']          = " + str(myItem['organizer']) + "<br>\n"
                        msg = msg + "myItem['start']              = " + str(myItem['start']) + "<br>\n"
                        msg = msg + "myItem['end']                = " + str(myItem['end']) + "<br>\n"
                        if ('recurrence' in myItem.keys()) :
                            msg = msg + "myItem['recurrence']         = " + str(myItem['recurrence']) + "<br>\n"
                        if ('transparency' in myItem.keys()) :
                            msg = msg + "myItem['transparency']       = " + str(myItem['transparency']) + "<br>\n"
                        msg = msg + "myItem['iCalUID']            = " + str(myItem['iCalUID']) + "<br>\n"
                        msg = msg + "myItem['sequence']           = " + str(myItem['sequence']) + "<br>\n"
                        msg = msg + "myItem['reminders']          = " + str(myItem['reminders']) + "<br>\n"
                        msg = msg + "<br><br>\n"
                        msg = msg + "<br><br>\n"

                        # msg = msg + "<font color='blue'><b>\n"
                        # msg = msg + dumpclean_str(myItem)
                        # msg = msg + "</font></b>\n"
                        # print("\n\n\n")
                    else:
                        # msg = msg + "itemNum = " + str(itemNum) + "<br>\n"
                        tempStart = datetime.datetime(1980, 1, 1, 0, 0)
                        tempEnd = datetime.datetime(2999, 12, 31, 0, 0)
                        if ('start' in myItem.keys()) :
                            # print("type(myItem['start'])        = " + str(type(myItem['start'])))
                            # print("myItem['start']              = " + str(myItem['start']))
                            # # print("myItem['start']              = " + str(myItem['start']['dateTime']))
                            # # tempStart = dateutil.parser.parse(myItem['start']['dateTime'])
                            # # tempStart = dateutil.parser.parse((myItem['start'])['dateTime'])
                            # # tempStart = dateutil.parser.parse(myItem['start'])
                            if ('dateTime' in myItem['start']) :
                                # print("myItem['start']['dateTime']  = " + str(myItem['start']['dateTime']))
                                tempStart = dateutil.parser.parse(myItem['start']['dateTime'])
                            elif ('date' in myItem['start']) :
                                # print("myItem['start']['date']      = " + str(myItem['start']['date']))
                                tempStart = dateutil.parser.parse(myItem['start']['date'])

                        if ('end' in myItem.keys()) :
                            # print("type(myItem['end'])          = " + str(type(myItem['end'])))
                            # print("myItem['end']                = " + str(myItem['end']))
                            # # print("myItem['end']                = " + str(myItem['end']['dateTime']))
                            # # # tempEnd = dateutil.parser.parse(myItem['end']['dateTime'])
                            # # tempEnd = dateutil.parser.parse((myItem['end'])['dateTime'])
                            # # # tempEnd = dateutil.parser.parse(myItem['end'])
                            if ('dateTime' in myItem['end']) :
                                # print("myItem['end']['dateTime']    = " + str(myItem['end']['dateTime']))
                                tempEnd = dateutil.parser.parse(myItem['end']['dateTime'])
                            elif ('date' in myItem['end']) :
                                # print("myItem['end']['date']        = " + str(myItem['end']['date']))
                                tempEnd = dateutil.parser.parse(myItem['end']['date'])

                        # msg = msg + "itemNum = " + str(itemNum) + "         start = " + tempStart.isoformat('T') + "    end = " + tempEnd.isoformat('T') + "<br>\n"
                        msg = msg + "itemNum = " + str(itemNum) + " &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; start = " + tempStart.isoformat('T') + " &nbsp; &nbsp; &nbsp; &nbsp; end = " + tempEnd.isoformat('T') + "<br>\n"

                else:
                    #msg = msg + "itemNum = " + str(itemNum) + "<br>\n"

                    tempStart = datetime.datetime(1980, 1, 1, 0, 0)
                    tempEnd = datetime.datetime(2999, 12, 31, 0, 0)
                    if ('start' in myItem.keys()) :
                        # print("type(myItem['start'])        = " + str(type(myItem['start'])))
                        # print("myItem['start']              = " + str(myItem['start']))
                        # # print("myItem['start']              = " + str(myItem['start']['dateTime']))
                        # # tempStart = dateutil.parser.parse(myItem['start']['dateTime'])
                        # # tempStart = dateutil.parser.parse((myItem['start'])['dateTime'])
                        # # tempStart = dateutil.parser.parse(myItem['start'])
                        if ('dateTime' in myItem['start']) :
                            # print("myItem['start']['dateTime']  = " + str(myItem['start']['dateTime']))
                            tempStart = dateutil.parser.parse(myItem['start']['dateTime'])
                        elif ('date' in myItem['start']) :
                            # print("myItem['start']['date']      = " + str(myItem['start']['date']))
                            tempStart = dateutil.parser.parse(myItem['start']['date'])

                    if ('end' in myItem.keys()) :
                        # print("type(myItem['end'])          = " + str(type(myItem['end'])))
                        # print("myItem['end']                = " + str(myItem['end']))
                        # # print("myItem['end']                = " + str(myItem['end']['dateTime']))
                        # # # tempEnd = dateutil.parser.parse(myItem['end']['dateTime'])
                        # # tempEnd = dateutil.parser.parse((myItem['end'])['dateTime'])
                        # # # tempEnd = dateutil.parser.parse(myItem['end'])
                        if ('dateTime' in myItem['end']) :
                            # print("myItem['end']['dateTime']    = " + str(myItem['end']['dateTime']))
                            tempEnd = dateutil.parser.parse(myItem['end']['dateTime'])
                        elif ('date' in myItem['end']) :
                            # print("myItem['end']['date']        = " + str(myItem['end']['date']))
                            tempEnd = dateutil.parser.parse(myItem['end']['date'])

                    # msg = msg + "itemNum = " + str(itemNum) + "         start = " + tempStart.isoformat('T') + "    end = " + tempEnd.isoformat('T') + "<br>\n"
                    msg = msg + "itemNum = " + str(itemNum) + " &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; start = " + tempStart.isoformat('T') + " &nbsp; &nbsp; &nbsp; &nbsp; end = " + tempEnd.isoformat('T') + "<br>\n"


                # msg = msg + "<br><br>\n"
                # msg = msg + "<br><br>\n"


    msg = msg + "<br><br><br><br><br>\n"

    msg = msg + "</body>\n"
    msg = msg + "</html>\n"

    return msg




@application.route('/.well-known/acme-challenge/Cy_Jy5nOi6Au8NMLdGE5BW9bXOFGwRfDbO44vyp1sTA', methods=['GET','POST'])
def sslVerification():
    return 'Cy_Jy5nOi6Au8NMLdGE5BW9bXOFGwRfDbO44vyp1sTA.Dvl4vg2zdoaQgGwzzn1f3egJgeHNELy3kQ5-0z_0U1o'




def https_app():
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('/etc/letsencrypt/live/code.plantter.net/fullchain.pem', '/etc/letsencrypt/live/code.plantter.net/privkey.pem')
    # sess.init_app(application)
    # application.debug = DEBUG
    application.run(port=443, ssl_context=context)



if any(myHostName in s for s in GLOBAL_LIST_OF_LOCAL_HOSTNAMES):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'     # use this to disable requiring SSL for OAuth 2
    if __name__ == "__main__":
        # sess.init_app(application)
        # application.debug = DEBUG
        application.run(port=8000)
        #print("user agent = " + flask.request.headers.get('User-Agent') + "\n\n")
        #sys.stdout.flush()
        #print("application name = " + flask.current_app.name + "\n\n")
        #sys.stdout.flush()
        #print("flask.session[google_token] = " + json.dumps(flask.session['google_token']) + "\n\n")
        #print("flask.session[google_token] = " + json.dumps(flask.session.get('google_token')) + "\n\n")
        #sys.stdout.flush()
else:
    if __name__ == "__main__":
        # REDIRECT_URI = 'https://code.plantter.net:8000/oauth2callback'
        # application.config.set
        # print ("updated REDIRECT_PATH = " + application.config.get('REDIRECT_PATH'))
        # print ("updated REDIRECT_URI = " + REDIRECT_URI)
        multiprocessing.Process(target=https_app, daemon=True).start()
        # sess.init_app(application)
        # application.debug = DEBUG
        application.run(port=443)



