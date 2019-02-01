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

# content = requests.get(url, cookies=cookies).content
# with open('meetings.txt','wb') as f:
#     f.write(content)

events = [ ]

get_num_re = re.compile('\d+')
def event_num(element):
    return get_num_re.findall(element.get('href'))[0];

for event in page.xpath(
'//*[@class="event-list"]//*[@class="list-name"]/a'
):
    # print event.text.strip()
    events.append([event_num(event),event.text.strip()])

print "Getting previous events"
before = 'data-event-list-before'
before = page.xpath('//*[@'+before+']')[0].get(before)
before = s.get(
    url+('' if url.endswith('/') else '/')+'event-list?before='+before
).content
before = html.fromstring( json.loads(before)['html'] )

for event in before.xpath('//*[@class="list-name"]/a'):
    # print event.text.strip(), event.get('href')
    events.append([event_num(event),event.text.strip()])

print len(events), "events"

for event in events:
    print event

# import re
#
# dir_name = re.match('.+/([^/]+)/thread/([^/]+)',url)
# if not dir_name:
#     print "Bad url:",url
#     sys.exit(1)
# dir_name = '_'.join(str(x) for x in dir_name.groups())
#
# from lxml import html
# import requests, os
#
# def mkdir(d):
#     if not os.path.isdir(d): os.makedirs(d)
#
# mkdir(dir_name)
#
# print "Fetching", url
# for post in html.fromstring(requests.get(url).content).xpath(
# '//div[contains(@class,"postContainer")]//a[@class="fileThumb"]'):
#     href = post.get('href')
#     name = dir_name+'/'+re.match('.+/(.+)',href).group(1)
#     print name
#     r = requests.get('http:'+href)
#     if r.status_code == 200:
#         with open(name,'wb') as f:
#             f.write(r.content)
#
#
