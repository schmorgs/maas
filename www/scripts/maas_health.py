#!/usr/bin/python3

# This module tests the health of one or more agents

from urllib.request import Request,urlopen
import json
import datetime
import maas_conf
import sys

def health(args):

  # Set some variables from this
  api_url = maas_conf.conf['api']['url']

  # If "entities" param was provided, then lets use that in the query
  entities = "*"
  if 'entities' in args :
    entities = args['entities']

  # HTML Header
  content = "<html><head><link rel='stylesheet' type='text/css' href='/static/dark.css'></head>"
  content += "<h1><A style='text-decoration:none' HREF='/'>Agent Health</a></h1>"
  content += "<hr>"

  # Build Elastic query to return all records which match the supplied tag
  try:
    req = Request(api_url + "/entity?entity=" + entities,method='GET')
    records = json.loads(json.load(urlopen(req)))
    records = sorted(records,key=lambda i: i['entity'])
  except:
    return content + "<h3>Unable to get any nodes</h3>"

  content += "<H2>Last Reboot Measurement for Hosts</h2>"

  # Build a table for each host we know about along with last reboot/measurement
  content += "<TABLE class='blueTable'><TR><TH>Hostname<TH>Last Reboot<TH>Last Measurement</TR>"
  
  status = {}  # Dictionary used to store the overall monitors and status
  for r in records :
    entity = r['entity']
    metric_class = "system"
    metric_name = "uptime"

    # Query influx to get last measurement of uptime via API
    params = "entity=%s&metric_class=%s&metric_name=%s" % ( entity,metric_class,metric_name)
    req = Request(api_url + "/metric/last?" + params,method='GET')

    # Get the value returned and the last measurement
    value, metric_timestamp = str(urlopen(req).read(),'utf-8').split(' ')
    # Default colour for status cell
    color = "GREEN"
    # It looks like we have data so lets compare it
    if metric_timestamp != "NA" and metric_timestamp != "NULL" :
      try:
        value = float(value)
      except:
        value = 0

      # Work out last reboot based on uptime
      reboot = datetime.datetime.utcnow() - datetime.timedelta(seconds=value)
      reboot = reboot.strftime("%Y-%m-%d %H:%M:%S")

      # Reformat the time stamp field
      metric_timestamp = metric_timestamp.replace("T"," ").replace("Z","")
      metric_timestamp = datetime.datetime.strptime(metric_timestamp,"%Y-%m-%d %H:%M:%S")
      metric_age = datetime.datetime.utcnow() - metric_timestamp
      metric_age = int(metric_age.total_seconds())
      # Data is older than two mins to mark as stale
      if metric_age > 120 :
        color = "RED"
    else:
      # No data was returned to bad
      value = 0
      color = "RED"
      reboot = "NA"
      metric_age = "NA"

    content += "<TR><TD>%s<TD>%s<TD><FONT COLOR='%s'><p title='%s seconds'>%s</p></FONT></TR>" % (entity,reboot,color,metric_age,metric_timestamp) 

  content += "</TABLE>"
  content += "<h5>Note - Last Reboot time will vary if you constantly refresh the page.  This is because it is calculated by subtracting the last received metric of system uptime from 'now'</h5>"

  content += "</html>"

  return content
