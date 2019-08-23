from copy import deepcopy
from importlib import resources


def clean(data):
    data = deepcopy(data)

    if isinstance(data, dict):
        for key, value in tuple(data.items()):
            new = key.lower().replace(' ', '_').replace('-', '_')
            data.pop(key)
            data[new] = clean(value)
    elif isinstance(data, str):
        data = data.strip()

        try:
            if ',' in data:
                #: for string sizes
                data = [float(part) for part in data.split(',')]
            else:
                data = float(data)
        except Exception:
            if '" /' in data:
                #: convert measurement to only inches
                data = float(data.split('"')[0].strip())
            elif data in ['N/A', 'None']:
                data = None
            elif data == 'right-handed':
                data = 'R'
            elif data == 'left-handed':
                data = 'L'
            elif data.startswith('$'):
                data = float(data[1:].replace(',', ''))

    return data
