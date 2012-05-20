import json
import csv
from django.template.defaultfilters import slugify
from mappings import *

MTC_TYPE_REVERSE_MAP = {
   'Ordinary': 'ORD',
   'Night Service': 'NGT',
   'LSS': 'LSS',
   'M-Route': 'MSVC',
   'Delux': 'DLX',
   'Air Condition': 'AC',
   'Express': 'EXP'
}


def resolve_route_name(name):
    display_name = name
    dlx_flag = False
    ac_flag = False
    for p in PREFIX_LIST:
        if display_name.startswith(p):
            if not p in PREFIX_KEEPERS:
               display_name = display_name.lstrip(p)
            if p == 'Z':
               ac_flag = True
               display_name = display_name.rstrip('V')
            if p == 'S':
               dlx_flag = True
            break
    slug = slugify(display_name)
    for s in SUFFIX_LIST:
        if display_name.endswith(s):
            if not s in SUFFIX_KEEPERS: display_name = display_name.rstrip(s)
            slug = slugify(display_name)
            if s in EXT_ALIASES: display_name = display_name.replace(s," Ext")
            if s in CUT_ALIASES: display_name = display_name.replace(s," Cut")
            break
    if dlx_flag:
        display_name = display_name + " Dlx"
        slug = "s" + slug
    if ac_flag:
        display_name = display_name + " AC"
        slug = "w" + slug
    return (display_name, slug)


def main():
    c = csv.DictWriter(open('data.csv', 'w'), [
            'route',
            'stops',
            'types'
        ])
    c.writeheader()
    data = {}
    rds = json.load(open('routes_detail.json', 'r'))
    for mtc_name in rds:
        display_name, slug = resolve_route_name(mtc_name)
        rd = rds[mtc_name]
        if rd['source'] is None:
            print 'Source is empty for ' + mtc_name
            continue
        if rd['destination'] is None:
            print 'Destination is empty for ' + mtc_name
            continue
        if len(rd['stages']) == 0:
            print 'Stages is empty for ' + mtc_name
            continue
        service_type = rd['service_type']
        s_type = MTC_TYPE_REVERSE_MAP.get(service_type, 'ORD')

        if slug in data:
            data[slug]['types'].append(s_type)
        else:
            data[slug] = {
                'route': display_name,
                'stops': ','.join(rd['stages']),
                'types': [s_type]
            }

    json.dump(data, open('data.json', 'w'), indent=4)
    for row in data.values():
        row['types'] = ','.join(row['types'])
        c.writerow(row)
main()
