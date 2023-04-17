# imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import re
import random
from datetime import datetime

from keys import SLACK_APP_TOKEN, SLACK_BOT_TOKEN


# constants
VERSION = "0.1"

REQHELP = 0
REQVERSION = 1
REQHELLO = 2
REQSTATUS = 3
REQQUOTE = 4 
REQCREATE = 5
REQRESOLVE = 6 
REQLOG = 7 
REQSHOWLOG = 8 
REQCLOSE = 9  
REQCLEAN = 10  

DATADIR = "data/"
DATEFORMAT = "%Y-%m-%dZ%H:%M:%S"

INCIDENTCHANNEL = "C053PV8E7E0"


# init
app = App(token=SLACK_BOT_TOKEN)


# functions
def current_incident_number():
  incidentfile = open(DATADIR+'incidents.txt', 'r')
  incidents = incidentfile.readlines()
  return(int(incidents[0]))


def inc_incident_number():
  current = current_incident_number()
  current = current + 1
  incidentfile = open(DATADIR+'incidents.txt', 'w')
  incidentfile.write(str(current))
  incidentfile.close()


def applog(msg,r):
  logfile = open("applog.txt", "a")
  now = datetime.utcnow()
  nowstr = now.strftime(DATEFORMAT)
  logfile.write(nowstr)
  logfile.write(" ")
  logfile.write(str(r))
  logfile.write(" ")
  logfile.write(str(msg).strip())
  logfile.write("\n")
  logfile.close()


def log(id, r, msg):
  if isinstance(id,int):
    incidentid = "incident-"+str(id)
  else:
    incidentid = id
  incidentfile = open(DATADIR+incidentid+'/log.txt', 'a')
  now = datetime.utcnow()
  nowstr = now.strftime(DATEFORMAT)
  incidentfile.write(nowstr)
  incidentfile.write(" ")
  incidentfile.write(r)
  incidentfile.write(" ")
  incidentfile.write(msg.strip())
  incidentfile.write("\n")
  incidentfile.close()


def showlog(id,requester):
  incidentid = "incident-"+str(id)
  applog("show " + incidentid, requester)
  incidentfile = open(DATADIR+incidentid+'/log.txt', 'r')
  lines = incidentfile.readlines()
  incidentfile.close()
  newline = "Log " + incidentid + "\n"
  for line in lines:
    newline = newline + line
  return(newline)


def record_incident(incidentid, m, r):
  os.mkdir(DATADIR+incidentid)
  incidentfile = open(DATADIR+incidentid+'/status.txt', 'w')
  incidentfile.write("open")
  incidentfile.close()
  incidentfile = open(DATADIR+incidentid+'/title.txt', 'w')
  # build a title
  words = m.split()
  title = ""
  for titleword in words[2:]:
     title = title + " " + titleword
  title = title + " by " + r  
  incidentfile.write(title)
  incidentfile.close()
  log(incidentid, r, "open")
  log(incidentid, r, "title set to "+title)
  applog(incidentid + " open", r)
  applog(incidentid + " title set to " + title, r)


def resolve_incident(incidentid, r):
  incidentfile = open(DATADIR+incidentid+'/status.txt', 'w')
  incidentfile.write("resolved")
  incidentfile.close()
  log(incidentid, "resolved")
  applog(incidentid + " resolved", r)


def close_incident(incidentid, r):
  incidentfile = open(DATADIR+incidentid+'/status.txt', 'w')
  incidentfile.write("closed")
  incidentfile.close()
  log(incidentid, r, "closed")
  applog(incidentid + " closed", r)


def append_overall_status(incidentid, status, r):
  # overall status file update
  now = datetime.utcnow()
  nowstr = now.strftime(DATEFORMAT)
  incidentfile = open(DATADIR+'status.txt', 'a')
  incidentfile.write(status+" "+incidentid+" "+r+" "+nowstr+"\n")
  incidentfile.close()


def create_channel(id, m, r):
  # create channel
  try:
    # Call the conversations.create method using the WebClient
    # conversations_create requires the channels:manage bot scope
    result = app.client.conversations_create(name=id)
    channelid = result['channel']['id']
    applog(result,r)
    applog(channelid,r)
  except Exception as e:
    applog("Error creating conversation: {}".format(e), r)

  # add the requester
  try:
    result = app.client.conversations_invite(channel=channelid, users=r)
    applog(result,r)
  except Exception as e:
    applog("Error creating conversation: {}".format(e), r)

  # set the topic
  words = m.split()
  title = ""
  for titleword in words[2:]:
     title = title + " " + titleword
  title = title + " by " + r  
  try:
    result = app.client.conversations_setTopic(channel=channelid, topic=title)
    applog(result,r)
  except Exception as e:
    applog("Error creating conversation: {}".format(e), r)
  try:
    result = app.client.conversations_setPurpose(channel=channelid, purpose=title)
    applog(result,r)
  except Exception as e:
    applog("Error creating conversation: {}".format(e), r)
  
  # add new incident into the generic channel
  notice = "A new incident has been opened: #" + id + " regarding: " + m
  try:
    results = app.client.chat_postMessage(channel=INCIDENTCHANNEL, text=notice)
    applog(result,r)
  except Exception as e:
    applog("Error creating conversation: {}".format(e), r)
   


def update_overall_status(incidentid, status, r):
  # overall status file update
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  incidentfile.close()
  now = datetime.utcnow()
  nowstr = now.strftime(DATEFORMAT)
  newline = ""
  for line in lines:
    if incidentid in line:
      logline = status + " " + incidentid + " " + r + " " + nowstr + "\n"
      newline = newline + logline + "\n"
    else:
      newline = newline + line
  incidentfile = open(DATADIR+'status.txt', 'w')
  incidentfile.write(newline)
  incidentfile.close()
  applog("update " + logline, r)


def get_overall_status():
  # overall status file 
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  statusline = ""
  for line in lines:
    statusline = statusline + line
  return(statusline) 


def clean(requester):
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  incidentfile.close()
  now = datetime.utcnow()
  nowstr = now.strftime(DATEFORMAT)
  newline = ""
  logline = ""
  for line in lines:
    if "close" not in line:
      newline = newline + line
    else:
      logline = logline + line.strip()
  incidentfile = open(DATADIR+'status.txt', 'w')
  incidentfile.write(newline)
  incidentfile.close()
  applog("clean " + logline, requester)


def create(m, requester):
  # create an incident
  # get the last incident #
  inc_incident_number()
  next = current_incident_number()
  incidentstring = "incident-" + str(next)
  create_channel(incidentstring, m, requester)
  record_incident(incidentstring, m, requester)
  append_overall_status(incidentstring, "open", requester)
  return(incidentstring)
  
 
def resolve(id, requester):
  # resolve an incidnet
  incidentstring = "incident-"+str(id)
  # channel
  resolve_incident(incidentstring, requestor)
  update_overall_status(incidentstring,"resolved",requester)
  return(incidentstring)
  
 
def close(id, requester):
  # close an incidnet
  incidentstring = "incident-"+str(id)
  # channel
  close_incident(incidentstring, requester)
  update_overall_status(incidentstring,"closed", requester)
  return(incidentstring)
  
 
def get_quote():
  # read lines - only line with a " are a quote, if it does not end in a " it is a multiline quote
  quotes = open('quotes.txt', 'r')
  lines = quotes.readlines()
  while 1:
    lineselected = random.randint(0,len(lines)-1)
    print(lineselected)
    line = lines[lineselected]
    if '“' in line:
      quote = line
      while '”' != line[len(line)-2]:
        lineselected = lineselected + 1
        line = lines[lineselected]
        quote = quote + line
      return((quote[1:len(quote)-2]))


def find_id(m):
  args = m.split()
  print(m, args)
  rc = int(args[2])
  return(rc)


def parse_msg(m):
  m = m.lower()
  rc = REQSTATUS
  id = 0
  if 'status' in m:
    rc = REQSTATUS
  elif 'version' in m:
    rc = REQVERSION
  elif 'hello' in m:
    rc = REQHELLO
  elif 'quote' in m:
    rc = REQQUOTE
  elif 'help' in m:
    rc = REQHELP
  elif 'create' in m:
    rc = REQCREATE
  elif 'resolve' in m:
    # needs an id
    rc = REQRESOLVE
    id = find_id(m)
  elif 'showlog' in m:
    rc = REQSHOWLOG
    id = find_id(m)
  elif 'log' in m:
    rc = REQLOG
    id = find_id(m)
  elif 'clean' in m:
    rc = REQCLEAN
  elif 'close' in m:
    rc = REQCLOSE
    id = find_id(m)
  return(rc, id)


@app.message(re.compile("(hello|hi)", re.I))
def say_hello_regex(say, context):
    greeting = context["matches"][0]
    say(f"{greeting}, <@{context['user_id']}>, how are you?")


@app.message(re.compile(""))
def catch_all(say, context):
    """A catch-all message."""
    say(f"I didn't get that, <@{context['user_id']}>.")


@app.event("app_mention") 
def mention_handler(body, client, say):
  print(body)
  user = body['event']['user']
  inmsg = body['event']['text']
  request, id = parse_msg(inmsg)
  applog( "mention" + inmsg, user)
  msg = "Sorry, please repeat"
  if request == REQHELP:
    msg = "I can react to help, hello, quote, and status"
  elif request == REQSTATUS:
    msg = get_overall_status()
  elif request == REQVERSION:
    msg = VERSION 
  elif request == REQHELLO:
    msg = "Hello yourself"
  elif request == REQQUOTE:
    msg = get_quote()
  elif request == REQCREATE:
    msg = create(inmsg, user)
  elif request == REQRESOLVE:
    msg = resolve(id, user)
  elif request == REQCLOSE:
    msg = close(id, user)
  elif request == REQLOG:
    log(id,user,inmsg)
    msg = "Message logged"
  elif request == REQSHOWLOG:
    msg = showlog(id, user)
  elif request == REQCLEAN:
    clean(user)
    msg = "Log cleaned"  


@app.event("app_wave") 
def mention_handler(body, say):
  say('Hallo World!')


if __name__ == "__main__":
  handler = SocketModeHandler(app, SLACK_APP_TOKEN)
  handler.start()
