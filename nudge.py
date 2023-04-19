# imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from datetime import datetime

from keys import SLACK_APP_TOKEN, SLACK_BOT_TOKEN


# constants
VERSION = "0.1"

DATADIR = "data/"
DATEFORMAT = "%Y-%m-%dZ%H:%M:%S"

# periodic update channel
CURRENTINCIDENTCHANNEL = "C053KBTDSVC"

# init
app = App(token=SLACK_BOT_TOKEN)


# functions
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


def attribute(a, id, r):
  if "incident" in str(id):
    attributefilename = DATADIR+str(id)+"/"+a+".txt"
  else:
    attributefilename = DATADIR+"incident-"+str(id)+"/"+a+".txt"
  try:
    attributefile = open(attributefilename, "r")
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


def post_notice(c, i, n, m, r):
  # add new incident into the generic channel
  notice = n + str(i) + " regarding: " + m
  try:
    results = app.client.chat_postMessage(channel=c, text=notice)
    applog(result,r)
  except Exception as e:
    applog("Error creating conversation: {}".format(e), r)

   
def count_open_status(r):
  # overall status file update
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  incidentfile.close()

  count = 0
  for line in lines:
    if "open" in line:
      count = count + 1
  
  applog("count_open_status" + str(count), r)
  return(count)


def update_open_status(r):
  # overall status file update
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  incidentfile.close()

  newline = ""
  for line in lines:
    if "open" in line:
      le = line.split()
      id = le[1]
      title = attribute("title", id, r)
      post_notice(CURRENTINCIDENTCHANNEL, id, "Open Incident: ", title, r)
      newline = newline + line
  
  logline = newline.replace("\n","")
  applog("update_open_status" + logline, r)

def nudge_open_status(r):
  # overall status file update
  incidentfile = open(DATADIR+'status.txt', 'r')
  lines = incidentfile.readlines()
  incidentfile.close()

  newline = ""
  for line in lines:
    if "open" in line:
      le = line.split()
      id = le[1]
      title = attribute("title", id, r)
      owner = attribute("owner", id, r)
      update = attribute("update", id, r)
      priority = attribute("priority", id, r)
      msg = "This incident: " + id + " will be autoupdated soon.\nThe following status will be posted:\n"
      msg = msg + "  Owner: " + owner + "\n"
      msg = msg + "  Priority: " + priority + "\n"
      msg = msg + "  Title: " + title + "\n"
      msg = msg + "  Update: " + update + "\n"
      msg = msg + "You can change the status using the setupdate and settitle, etc commands"
      results = app.client.chat_postMessage(channel=owner, text=msg)
      newline = newline + line
  
  logline = newline.replace("\n","")
  applog("nudge_open_status" + logline, r)


if __name__ == "__main__":
  if count_open_status("") > 0:
    nudge_open_status("nudge_batch")
