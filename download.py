#!/usr/bin/env python

import requests, re
import cern_sso

s = requests.Session()

domain = 'https://indico.cern.ch/'

print "Getting cookies"
s.cookies = cern_sso.krb_sign_on(domain+'category/6142/')

name_re = re.compile(r'.*/(.*)$')

with open('slides.txt') as f:
    for url in f:
        url = url.strip()
        url = domain + url
        r = s.get(url,stream=True)
        r.raise_for_status()
        name = 'slides/'+name_re.sub(r'\1',url)
        print name
        with open(name,'wb') as f:
            for block in r.iter_content(1024):
                f.write(block)

