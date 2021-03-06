#!/usr/bin/python3

# This module is used to configure what metrics the Telegraf agent should
# collect over and above it's base config

from urllib.request import Request,urlopen
import urllib.parse
import json
import maas_conf
import time


# Main function to control actions to take with this page
def collect(args,form):

  # HTML Header
  content = "<html><head><link rel='stylesheet' type='text/css' href='/static/dark.css'></head>"
  content += "<h1><A style='text-decoration:none' HREF='/'>Host Monitoring Configuration Management</a></h1>"
  content += "<hr>"

  api_url = maas_conf.conf['api']['url']

  # Two modes, view and edit.  view is the default
  try:
    mode = args['mode']
  except:
    mode = "view"

  ########### EDIT
  if mode == "edit":

    # If entityname and config data was passed to this page then
    # we just want to write that to the Elastic backend
    if 'config' in form and 'entity' in form :
      entity = form['entity']
      config = form['config']
  
      # Get the platform for this host
      req = Request(api_url + "/entity?entity=" + entity,method='GET')
      platform = json.loads(json.load(urlopen(req)))[0]['platform']

      # Now post the new config via the API
      params = {"entity":entity,"platform":platform,"config":config}
      data = str(json.dumps(params)).encode("utf-8")
      req = Request(api_url + "/config/entity",data=data)
      req.add_header('Content-Type','application/json')
      resp = str(urlopen(req).read(),'utf-8')
   
      # Check the API Response and write an appropriate message out
      if resp == "created" or resp == "updated" : 
        # The API update was successful so now let's rebuild the Telegraf 
        # configuration with the latest customisations so that the agent
        # pulls it at next startup

        # Bug fix :
        # Sleep for 1 second to allow config to be properly written to Elastic
        # otherwise the reload might pull in old config
        time.sleep(1)

        telegraf_url = maas_conf.conf['www']['url'] + "/telegraf-configure?host=" + entity + "&os=" + platform + "&reset=true"
        urllib.request.urlopen(telegraf_url)
        content += "<h2>Config written, view <A HREF='/collect?mode=view&entity=" + entity + "'>here</A></h2>"
        content += "<h5>Agent needs to be retarted to pick up new config</h5>"
        content += "<h3>Click <A HREF='/telegraf-configure?host=" + entity + "'>here</A> to see Telgraf config</h3>"
      else :
        content += "<h5>ERROR writing new config</h5><BR>"
        content += resp

    # Only a entity passed, so try and read existing config and then show form
    elif 'entity' in args :
      entity = args['entity']
      try :
        req = Request(api_url + "/config/entity?mode=custom&entity=" + entity,method='GET')
        config = json.loads(json.load(urlopen(req)),strict=False)[0]['config']
      except :
        config = ""

      content += """
<html>
Configure metric collection for a entity
<FORM ACTION="/collect?mode=edit" METHOD="POST">
<TABLE>
 <TR>
  <TD>Hostname</TD>
  <TD>
    <input name="entity" id="entity" value=""" + entity + """></input>
  </TD>
  <TD>&nbsp;&nbsp;&nbsp;</TD>
  <TD> </TD>
 </TR>
 <TR>
  <TD>Content</TD>
  <TD>
    <textarea rows=10 cols=40 id="config" name="config">""" + config + """</textarea>
  </TD>
  <TD></TD>
  <TD align=center>
<B>Supported Monitors</B><BR>
process=<I>process_name</I><BR>
service=<I>win_service</I><BR>
filesystem=<I>mount_point</I><BR>
http=<I>url</I><BR>
template=<I>pre-configured-component-template</I><BR>
  </TD>
 </TR>
 <TR>
  <TD COLSPAN=2 ALIGN=CENTER>
   <input type="submit"></input>
  </TD>
 </TR>
  

</TABLE>

</FORM>
<BR><BR>

"""
    # No fields passed so show inventory of existing entitys
    else :
      content += "<h2>Monitored Host Inventory</h2>"
      content += "<TABLE class='blueTable'><TR><TH>Host<TH>Action</TR>"
      try : 
        req = Request(api_url + "/entity",method='GET')
        all_entities = json.loads(json.load(urlopen(req)))
        records = sorted(all_entities,key=lambda i: i['entity'] )
      except :
        records = {}
      for r in records:
        entity = r['entity'] 
        content += "<TR><TD>" + entity + "<TD><A HREF='/collect?entity=" + entity + "&mode=edit'>Edit Config</A></TR>"
      content += "</TABLE>"

   
  #################### VIEW
  elif mode == "view":
    # If an entity was supplied then show that individual config
    if "entity" in args: 
      entity = args['entity']
      try:
        # Try and get config via API
        req = Request(api_url + "/config/entity?mode=custom&entity=" + entity,method='GET')
        conf = json.loads(json.load(urlopen(req)),strict=False)[0]['config'].split()

        content += "<h2>Showing custom collection for entity " + entity + "</h2>"
        # Print out each entry found in a table
        content += "<TABLE class='blueTable'><TR><TH>Monitor Type</TH><TH>Instance</TH></TR>"
        for line in conf:
          x = line.split("=")
          content += "<TR><TD>" + x[0] + "</TD><TD>" + x[1] + "</TD></TR>"
        content += "</TABLE>"

        # Option to edit config or view full blown Telegraf agent conf
        content += "<h3><A HREF='/collect?mode=edit&entity=" + entity + "'>Edit Custom Config</A></h3>"
        content += "<h3><A HREF='/telegraf-configure?host=" + entity + "'>View Full Config</A></h3>"
      except:
        content += "<h3>No Custom Configuration found for entity %s</h3>" %  (entity)
        content += "<h4><A HREF='/collect?mode=edit&entity=" + entity + "'>Add New Configuration here </A></h4>"

    else :
      # No parameters passed so list inventory of agents and indicator 
      # showing whether there is a custom config applied

      # Get list of all hosts from API call
      try :
        req = Request(api_url + "/entity",method='GET')
        all_entities = json.loads(json.load(urlopen(req)))
        all_entities = sorted(all_entities,key=lambda i: i['entity'] )
      except:
        all_entities = {}

      # Get list of all hosts with custom monitors 
      try:
        req = Request(api_url + "/config/entity?mode=custom",method='GET')
        custom_entities = json.loads(json.load(urlopen(req)),strict=False)
        # Now build a dictionary of custom hosts so we can reference later
        custom = {}
        for r in custom_entities:
          entity = r['entity']
          custom[entity] = True
      except:
        custom = {}

      # Build the output table of entities
      content += """
    <TABLE class='blueTable'>
    <TR><TH COLSPAN=3 ALIGN=CENTER>Configured Hosts</TH></TR>
    <TR><TH>Platform<TH>Full Config<TH>Custom Config</TR>
"""
      for r in all_entities:
        entity = r['entity']
        platform = r['platform']
        full_url = "<A HREF='/telegraf-configure?host=" + entity + "'>" + entity + "</A>"
        custom_url = "<A HREF='/collect?mode=edit&entity=" + entity + "'><FONT COLOR=RED>Create New</FONT></A>"
        if entity in custom:
          custom_url = "<A HREF='/collect?mode=view&entity=" + entity + "'><FONT COLOR=GREEN>View Existing</FONT></A>"
        content+= "<TR><TD>" + platform + "<TD ALIGN=CENTER>" + full_url + "</TD><TD>" + custom_url + "</TD></TR>"
      content += "</TABLE>"
      content += "<h5>Append &entity=xxx to the URL to jump directly to a entity config</h5>"
      content += "<h3><A HREF='/collect?mode=edit'>Add Configuration for New Host</A></h3>"
      
  return content
