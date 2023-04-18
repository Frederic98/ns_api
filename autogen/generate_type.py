import json

def json2py(infile: str, outfile: str):
    with open(infile) as f:
        spec = json.load(f)
    with open(outfile, 'wt') as f:
        f.write('import typing\nimport datetime\n\nfrom . import NSData\n')
        for name, obj in spec.items():
            f.write('\n\n')
            f.write(f'class {name}(NSData):\n')
            for attr in obj['params']:
                dtype = decode_dtype(attr["type"])
                if attr['required'].lower() != 'true':
                    dtype = f'typing.Optional[{dtype}]'
                description = attr['description'].strip()
                comment = f'  # {description}' if len(description) > 0 else ''
                f.write(f'    {attr["name"]}: {dtype}{comment}\n')


def decode_dtype(dtype: str):
    if dtype.endswith('[]'):
        return f'list[{decode_dtype(dtype[:-2])}]'
    if dtype == 'string':
        return 'str'
    if dtype == 'boolean':
        return 'bool'
    if dtype.startswith('int'):
        return 'int'
    if dtype in ('double', 'number'):
        return 'float'
    if dtype == 'date-time':
        return 'datetime.datetime'
    if dtype == 'date':
        return 'datetime.date'
    if dtype in ('url', 'uri'):
        return 'str'
    return f'"{dtype}"'

json2py('reisinformatie.json', '../nsapi/dtypes/travel_information.py')
