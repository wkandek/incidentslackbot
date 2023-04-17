# imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import re
import random

from keys import SLACK_APP_TOKEN, SLACK_BOT_TOKEN


# constants
VERSION = "0.1"

REQHELP = 0
REQVERSION = 1
REQHELLO = 2
REQSTATUS = 3
REQQUOTE = 4 
REQCREATE = 5

DATADIR = "data/"


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


def record_incident(incidentid):
  # make a directory, put a status file, create a channel
  os.mkdir(DATADIR+incidentid)
  incidentfile = open(DATADIR+incidentid+'/status.txt', 'w')
  incidentfile.write("open")
  incidentfile.close()


def resolve_incident(incidentid):
  # make a directory, put a status file, create a channel
  incidentfile = open(DATADIR+incidentid+'/status.txt', 'w')
  incidentfile.write("resolve")
  incidentfile.close()


def append_overall_status(incidentid, status):
  # overall status file update
  incidentfile = open(DATADIR+'status.txt', 'a')
  incidentfile.write(status+" "+incidentid+"\n")
  incidentfile.close()


def update_overall_status(incidentid, status):
  # overall status file update
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  newline = ""
  for line in lines:
    if incidentid in line:
      newline = newline+status+incidentid+"\n"
    else:
      newline = newline + line
  incidentfile.close()
  incidentfile = open(DATADIR+'status.txt', 'w')
  incidentfile.write(newline)
  incidentfile.close()


def get_overall_status():
  # overall status file 
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  statusline = ""
  for line in lines:
    statusline = statusline + line
  return(statusline) 


def create():
  # create an incidnet
  # get the last incident #
  inc_incident_number()
  next = current_incident_number()
  incidentstring = "incident-"+str(next)
  # channel
  record_incident(incidentstring)
  append_overall_status(incidentstring,"open")
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


def parse_msg(m):
  m = m.lower()
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
  else:
    rc = REQSTATUS
  return(rc)


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
  inmsg = body['event']['text']
  request = parse_msg(inmsg)
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
    msg = create()

  say(msg)
  #client.chat_postMessage(
  #  channel=body["event"]["channel"],
  #  thread_ts=body["event"]["thread_ts"],
  #  text=f"Yes <@{body['event']['user']}>.",
  #)


@app.event("app_wave") 
def mention_handler(body, say):
  say('Hallo World!')


if __name__ == "__main__":
  handler = SocketModeHandler(app, SLACK_APP_TOKEN)
  handler.start()
