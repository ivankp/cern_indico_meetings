#!/usr/bin/env python

# https://github.com/cerndb/cern-sso-python

import sys

if len(sys.argv)==1:
    print "usage:", sys.argv[0], "URL"
    sys.exit(1)
url = sys.argv[1]

import requests, json, re
import cern_sso
from lxml import html, etree

s = requests.Session()

print "Getting cookies"
s.cookies = cern_sso.krb_sign_on(url)

print "Fetching", url
page = html.fromstring( s.get(url).content )

events = [ ]

get_num_re = re.compile('\d+')
def add_event(e):
    events.append([
        get_num_re.findall(e.get('href'))[0],
        event.text.strip()
    ])

for event in page.xpath(
'//*[@class="event-list"]//*[@class="list-name"]/a'
):
    add_event(event)

# print "Getting previous events"
# before = 'data-event-list-before'
# before = page.xpath('//*[@'+before+']')[0].get(before)
# before = s.get(
#     url+('' if url.endswith('/') else '/')+'event-list?before='+before
# ).content
# before = html.fromstring( json.loads(before)['html'] )
#
# for event in before.xpath('//*[@class="list-name"]/a'):
#     add_event(event)

print len(events), "events"

for e in events:
    print e
    page = html.fromstring(
        s.get('https://indico.cern.ch/event/'+e[0]+'/').content )
    d = { }
    d['time'] = page.xpath('//*[@class="event-date"]//time')[0].get('datetime')
    e.append(d)

    print e
    break

