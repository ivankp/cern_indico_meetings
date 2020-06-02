#!/bin/bash

if [[ $# != 2 ]]; then
  echo "usage: $0 category event"
  exit 1
fi

./meetings.py $1 $2 last

mv "${1}.yml" "${1}-0.yml"

cat "${1}-1.yml" <(awk \
    "{ if(i>1){print}else{ if(i==0){ if(/^- - '$2'/){i=1} }else{ if(/^- - '[0-9]+'/){i=2; print} } } }" \
    "${1}-0.yml" \
  ) > "${1}.yml"

