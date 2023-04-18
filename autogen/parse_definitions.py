import json
import glob
import traceback
from collections import OrderedDict

from bs4 import BeautifulSoup


def parse_html(file: str):
    with open(file) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    edefinitions = soup.body.find('operation-details').find('div').findAll('type-definition', recursive=False)
    definitions = []
    for definition in edefinitions:
        name = definition.h4.text.strip()
        eheader, eparams = definition.div.findAll('div', recursive=False)
        params = []
        for eparam in eparams.findAll('div', recursive=False):
            epname, erequired, etype, edescription = eparam.findAll('div', recursive=False)
            params.append({'name': epname.text.strip(), 'required': erequired.text.strip(), 'type': etype.text.strip(), 'description': edescription.text.strip()})
        definitions.append({'name': name, 'params': params})
    return definitions


api_definitions = {}

for file in glob.glob('*.htm'):
    try:
        for definition in parse_html(file):
            name = definition['name']
            if name in api_definitions:
                if definition != api_definitions[name]:
                    raise RuntimeError(f'Conflicting definition: {definition} - {api_definitions[name]}')
            api_definitions[name] = definition
    except:
        print(f'ERROR: failed to parse "{file}"')
        traceback.print_exc()

blacklist = ['APIError','LocalizedErrorDetail', 'ApiV3TripsGet200ApplicationJsonResponse']
for item in blacklist:
    if item in api_definitions:
        del api_definitions[item]


with open('reisinformatie.json', 'wt') as f:
    spec = [(name, api_definitions[name]) for name in sorted(api_definitions.keys())]
    json.dump(OrderedDict(spec), f, indent=1)
