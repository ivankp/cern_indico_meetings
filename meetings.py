#!/usr/bin/env python2

# https://github.com/cerndb/cern-sso-python

import sys

if len(sys.argv)==1:
    print "usage:", sys.argv[0], "category-URL [event-id [single|last]]"
    sys.exit(1)
url = sys.argv[1]

import requests, json, re, yaml, glob
import cern_sso
from lxml import html, etree

s = requests.Session()

print "Getting cookies"
s.cookies = cern_sso.krb_sign_on(url)

print "Fetching", url
page = html.fromstring( s.get(url).text )

events = [ ]

get_num_re = re.compile('\d+')
def add_event(e):
    events.append([
        get_num_re.findall(e.get('href'))[0],
        event.text.strip()
    ])

for event in page.xpath(
'//*[@class="event-list"]//*[@class="list-name"]//a'
):
    add_event(event)

print "Getting previous events"
before = 'data-event-list-before'
before = page.xpath('//*[@'+before+']')[0].get(before)
before = s.get(
    url+('' if url.endswith('/') else '/')+'event-list?before='+before
).text
before = html.fromstring( json.loads(before)['html'] )

for event in before.xpath('//*[@class="list-name"]//a'):
    add_event(event)

print len(events), "events"

def safe_text(x):
    try:
        return x[0].text
    except IndexError:
        return ''

def people(aa): # affiliation nodes
    return [
      [ a.getprevious().text, safe_text(a.xpath('.//*[@class="text"]')) ]
      for a in aa ]

def index_of(xs,f):
    i = 0
    for x in xs:
        if f(x): break
        i += 1
    return i

single = False
last = False
if len(sys.argv)>2:
    if len(sys.argv)<4 or sys.argv[3]=='single': single = True
    elif sys.argv[3]=='last': last = True

if single:
    events = [next(e for e in events if e[0]==sys.argv[2])]
elif last:
    events = events[:index_of(events, lambda e: e[0]==sys.argv[2])+1]

for e in events:
    print '%s: %s' % (e[0],e[1])
    page = html.fromstring(
      s.get('https://indico.cern.ch/event/'+e[0]+'/').text )

    if page.xpath('(//*[@class="main"])[1]/div/div')[0].get('class')!='event-wrapper':
        continue

    talks = [ ]
    for t in page.xpath('//*[@class="meeting-timetable"]/*'):
        talks.append({
          'title': safe_text(t.xpath('.//*[@class="timetable-title "]')),
          'speakers': people(t.xpath(
            './/*[@class="speaker-list"]//*[@class="affiliation"]')),
          'material': [ a.get('href') for a in t.xpath(
            './/*[@class="material-list"]//a') ]
        })

    e.append({
      'time': page.xpath('//*[@class="event-date"]//time')[0].get('datetime'),
      'vidyo': safe_text(page.xpath('//*[@class="event-service-title"]')),
      'chairs': people(page.xpath(
        '//*[@class="chairperson-list"]//*[@class="affiliation"]')),
      'talks': talks,
      'minutes': [ a.get('href') for a in page.xpath(
          '//*[@class="event-note-section"]//a[@target="_blank"]') ] + \
        [ a.get('href') for a in page.xpath(
          '//*[@class="event-sub-header"]//*[@class="folder "]//a[@target="_blank"]'
        ) ],
      'location': safe_text(page.xpath(
        '//*[@class="event-location"]//*[@class="text"]'))
    })

if single:
    print yaml.dump(events)
else:
    name = get_num_re.findall(url)[-1]
    files = glob.glob(name+'*.yml')
    if len(files)>0:
        name += '-' + str(max(
            int(re.match(name+'(?:-(\d+))?', x).group(1) or 0) for x in files
        ) + 1 )
    name += '.yml'

    with open(name,'w') as f:
        yaml.dump(events, f)

