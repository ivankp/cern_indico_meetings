#!/usr/bin/env python3

import sys

if len(sys.argv)!=3:
    print("usage:", sys.argv[0], "file speaker")
    sys.exit(1)

import sys, yaml, re

with open(sys.argv[1],'r') as f:
    meetings = yaml.load(f, Loader=yaml.SafeLoader)

for m in meetings:
    if len(m)>2:
        for t in m[2]['talks']:
            for s in t['speakers']:
                if sys.argv[2] in s[0]:
                    print(re.sub('T.*','',m[2]['time']))
                    print(t['title'])
                    for x in t['material']:
                        print(x)
                    print()
                    break

