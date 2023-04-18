# imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import re
import random
import pickle
from datetime import datetime

from keys import SLACK_APP_TOKEN, SLACK_BOT_TOKEN


# constants
VERSION = "0.2"

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
REQSETGEO = 11
REQGEO = 12
REQSETSYSTEM = 13
REQSYSTEM = 14
REQSETIMPACT = 15
REQIMPACT = 16
REQSETTITLE = 17
REQTITLE = 18
REQSETUPDATE = 19
REQUPDATE = 20 
REQADDUPDATE = 21
REQSETCURRENT = 22
REQSTATUSALL = 23

DATADIR = "data/"
DATEFORMAT = "%Y-%m-%dZ%H:%M:%S"

INCIDENTCHANNEL = "C053PV8E7E0"

# current incident to work on by user
current = {}

# init
app = App(token=SLACK_BOT_TOKEN)


# functions
def load_current():
  if os.path.exists("current.pickle"):
    with open('current.pickle', 'rb') as handle:
      rc = pickle.load(handle)
  else:
    rc = {}
  return(rc)


def save_current(c):
  with open('current.pickle', 'wb') as handle:
    pickle.dump(c, handle, protocol=pickle.HIGHEST_PROTOCOL)


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


def setattribute(a, id, v, r):
  attributefile = open(DATADIR+"incident-"+str(id)+"/"+a+".txt", "w")
  attributefile.write(v.strip())
  attributefile.close()
  applog("setAttribute " + a + " " + str(id) + " " + v, r)


def attribute(a, id, r):
  try:
    attributefile = open(DATADIR+"incident-"+str(id)+"/"+a+".txt", "r")
    lines = attributefile.readlines()
    attributefile.close()
    statusline = ""
    for line in lines:
      statusline = statusline + line
    applog("Attribute " + a + " " + str(id) + " " + statusline, r)
    return(statusline) 
  except:
    applog("Attribute not available", r)
    return("")


def record_incident(id, m, r):
  incidentstring = "incident-" + str(id)
  os.mkdir(DATADIR+incidentstring)
  setattribute("status", id, "open", user)
  # build a title
  words = m.split()
  title = ""
  for titleword in words[2:]:
     title = title + " " + titleword
  title = title + " by " + r  
  setattribute("title", id, title, user)
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
  id = str(next)
  incidentstring = "incident-" + str(next)
  create_channel(incidentstring, m, requester)
  record_incident(id, m, requester)
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
  print(len(args))
  print(m, args)
  rc = 0
  if len(args) > 2:
    rc = int(args[2])
  return(rc)


def find_value(m):
  args = m.split()
  print(m, args)
  rc = ""
  for arg in args[3:]:
    rc = rc + " " + arg
  return(rc)


def parse_msg(msg):
  m = msg.lower()
  rc = REQSTATUS
  id = 0
  v = ""
  if 'statusall' in m:
    rc = REQSTATUSALL
  elif 'status' in m:
    rc = REQSTATUS
    id = find_id(m)
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
  elif 'setgeo' in m:
    rc = REQSETGEO
    id = find_id(m)
    v = find_value(msg)
  elif 'getgeo' in m:
    rc = REQGEO
    id = find_id(msg)
  elif 'setsystem' in m:
    rc = REQSETSYSTEM
    id = find_id(m)
    v = find_value(msg)
  elif 'getsystem' in m:
    rc = REQSYSTEM
    id = find_id(msg)
  elif 'setimpact' in m:
    rc = REQSETIMPACT
    id = find_id(m)
    v = find_value(msg)
  elif 'getimpact' in m:
    rc = REQIMPACT
    id = find_id(msg)
  elif 'settitle' in m:
    rc = REQSETTITLE
    id = find_id(m)
    v = find_value(msg)
  elif 'gettitle' in m:
    rc = REQTITLE
    id = find_id(msg)
  elif 'setupdate' in m:
    rc = REQSETUPDATE
    id = find_id(m)
    v = find_value(msg)
  elif 'getupdate' in m:
    rc = REQUPDATE
    id = find_id(msg)
  elif 'addupdate' in m:
    rc = REQADDUPDATE
    id = find_id(msg)
    v = find_value(msg)
  elif 'setcurrent' in m:
    rc = REQSETCURRENT
    id = find_id(msg)
  return(rc, id, v)


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
  request, id, value = parse_msg(inmsg)
  applog( "mention" + inmsg, user)
  msg = "Sorry, please repeat"
  now = datetime.utcnow()
  nowstr = now.strftime(DATEFORMAT)
  if request == REQHELP:
    msg = "I can react to help, hello, quote, and status"
  elif request == REQSTATUSALL:
    msg = get_overall_status()
  elif request == REQSTATUS:
    # what is the current status
    if user in current:
      id = current[user]
    else:
      id = current_incident_number() 
    msg = "incident-" + str(id) + "\n"
    m = "title:" + attribute("title",id,user) + "\n"
    msg = msg + m
    m = "status:" + attribute("status",id,user) + "\n"
    msg = msg + m
    m = "system:" + attribute("system", id, user) + "\n"
    msg = msg + m
    m = "geo:" + attribute("geo", id, user)
    msg = msg + m + "\n"
    m = "impact:" + attribute("impact", id, user)
    msg = msg + m + "\n"
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
  elif request == REQSETSYSTEM:
    setattribute("system", id, value, user)
    msg = "Attibute system set"  
  elif request == REQSYSTEM:
    msg = "system:" + attribute("system", id, user)
  elif request == REQSETGEO:
    setattribute("geo", id, value, user)
    msg = "Attibute geo set"  
  elif request == REQGEO:
    msg = "geo:" + attribute("geo", id, user)
  elif request == REQSETIMPACT:
    setattribute("impact", id, value, user)
    msg = "Attibute impact set"  
  elif request == REQIMPACT:
    msg = "impact:" + attribute("impact", id, user)
  elif request == REQSETTITLE:
    setattribute("title", id, value, user)
    msg = "Attibute title set"  
  elif request == REQTITLE:
    msg = "title:" + attribute("title", id, user)
  elif request == REQSETUPDATE:
    setattribute("update", id, value, user)
    msg = "Attribute update set"  
  elif request == REQUPDATE:
    msg = "update:" + nowstr + " " + attribute("update", id, user)
  elif request == REQADDUPDATE:
    m = attribute("update", id, user)
    newm = m + "\n" + nowstr + " " + value
    setattribute("update", id, newm, user)
    msg = "Attribute update added"  
  elif request == REQSETCURRENT:
    current[user] = id
    save_current(current)
    msg = "Current ID set"  
  say(msg)


@app.event("app_wave") 
def mention_handler(body, say):
  say('Hallo World!')


if __name__ == "__main__":
  current = load_current()
  handler = SocketModeHandler(app, SLACK_APP_TOKEN)
  handler.start()
