# incidentslackbot

Python slack bot for Incidents

After installing the pre requisties modules (slack-bolt), creating the necessary setup in your Slack application (edit keys.py) , creating the referenced meta channels "incidents" and  "current-incidents" (edit app.py) and creating a local "data" diretcory where the incidnet information is stored, the bot shoudl be ready to run with "python3 app.py"

It will create incidents and the associated slack channels, notify other slack channels, resolve incidnets and close them, show status, etc.

For example: @BotOne create Outage in EMEA creates a new incident and informs its number. Part of the creation is a dedicated slack channel for it and notfication of generic slack channels. The idea is that people interested in incidents can just monitor "#incidents" (only create/resolve and updates every 24 hours) and "#current-incidents" (create/resolve, updates every 30 minutes) while the channel itself has ongoing troubleshooting information, specualation and monitoring results in it.

The incidnet can further be annotated with updates, a title, a geography, a system name, etc.

Progress:
- status - done
- create, update, resolve, close, status - done
  - “website abc down”
  - New incident in Filesystem/DB/Opsgenie - done
    - Filesystem
- slack channel creation and updates - 1/2 done
  - New Slack channel #incident-123) - done
  - Notification in Status Channel (#current-incidents) - done, will get status every 30 minutes (automated?)
  - Notification in Meta Channel (#incidents) - not done, will get open/resolve - every 24 hours status
- To do
  - Look up user and channel names
  - Periodic Status post reminder or auto post
  - Better Parsing

Initial start and setup of Slack - https://kubiya.ai/blog/how-to-build-a-slackbot-with-python/
Tested at kandek.slack.com

authentication variables needed for slack are conatined in the keys.py file, included variables are for illustration only.
