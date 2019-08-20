import json
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
                # for string sizes
                data = [float(part) for part in data.split(',')]
            else:
                data = float(data)
                
        except Exception:
            if '" /' in data:
                # convert measurement to only inches
                data = float(data.split('"')[0].strip())
            elif data == 'N/A':
                data = None

    return data


with resources.path('instruments.data.gibson.json', '') as json_path:
    pass

with open(json_path / 'model.json') as old, open(json_path / 'clean.json') as new:
    for line in old.readlines():
        data = json.loads(line)
        data = clean(data)

        json.dump(data, new)
        new.write('\n')


if __name__ == "__main__":
    test = dict(
        a=dict(
            b='N/A',
            c=dict(
                d='12" / 304.8mm',
            ),
            e='D',
        ),
        f='10',
        g='.009, .011, .016, .026, .036, .046',
        h={
            'w_x Y-Z': '',
        },
    )
    
    expected = dict(
        a=dict(
            b=None,
            c=dict(
                d=12.0,
            ),
            e='D',
        ),
        f=10.0,
        g=[0.009, 0.011, 0.016, 0.026, 0.036, 0.046],
        h={
            'w_x_y_z': ''
        },
    )

    assert test == clean(expected)
