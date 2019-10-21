#!/usr/bin/env python

import yaml

with open('6142.yml','r') as f:
    meetings = yaml.load(f)

for m in meetings:
    if len(m)>2:
        for t in m[2]['talks']:
            for s in t['speakers']:
                if 'Rachel' in s[0]:
                    print t['title']
                    for x in t['material']:
                        print x
                    print ''

