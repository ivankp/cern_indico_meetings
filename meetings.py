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

print "Getting previous events"
before = 'data-event-list-before'
before = page.xpath('//*[@'+before+']')[0].get(before)
before = s.get(
    url+('' if url.endswith('/') else '/')+'event-list?before='+before
).content
before = html.fromstring( json.loads(before)['html'] )

for event in before.xpath('//*[@class="list-name"]/a'):
    add_event(event)

print len(events), "events"

import pprint
pp = pprint.PrettyPrinter(indent=2)

def person(a): # affiliation node
    return [ a.getprevious().text, a.xpath('.//*[@class="text"]')[0].text ]

def people(aa):
    return [ person(a) for a in aa ]

# for e in events:
for e in [next(e for e in events if e[0]==sys.argv[2])]:
    print e
    page = html.fromstring(
      s.get('https://indico.cern.ch/event/'+e[0]+'/').content )

    talks = [ ]
    for t in page.xpath('//*[@class="meeting-timetable"]/*'):
        talks.append({
          'title': t.xpath('.//*[@class="timetable-title "]')[0].text,
          'speakers': people(t.xpath(
            './/*[@class="speaker-list"]//*[@class="affiliation"]')),
          'material': [ a.get('href') for a in t.xpath(
            './/*[@class="material-list"]//a') ]
        })

    e.append({
      'time': page.xpath('//*[@class="event-date"]//time')[0].get('datetime'),
      'vidyo': page.xpath('//*[@class="event-service-title"]')[0].text,
      'chairs': people(page.xpath(
        '//*[@class="chairperson-list"]//*[@class="affiliation"]')),
      'talks': talks,
      'minutes': [ a.get('href') for a in page.xpath(
          '//*[@class="event-note-section"]//a[@target="_blank"]') ] + \
        [ a.get('href') for a in page.xpath(
          '//*[@class="event-sub-header"]//*[@class="folder "]//a[@target="_blank"]') ],
      'location': page.xpath(
        '//*[@class="event-location"]//*[@class="text"]')[0].text
    })

    # print e
    # pp.pprint(e)
    break

import yaml

with open('meetings.yml','w') as f:
    yaml.dump(events, f)

