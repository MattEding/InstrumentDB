from instruments.transform.clean import clean


def test_clean():
    input = dict(
        outer=dict(
            null_na='N/A',
            null_none='None',
            inner=dict(
                inches='12" / 304.8mm',
            ),
            char='c',
            string='Text',
        ),
        frets='10',
        string_sizes='.009, .011, .016, .026, .036, .046',
        key={
            'w_x Y-Z': '',
        },
        price='$3,799.00',
        left='left-handed',
        right='right-handed',
    )
    
    expected = dict(
        outer=dict(
            null_na=None,
            null_none=None,
            inner=dict(
                inches=12.0,
            ),
            char='c',
            string='Text',
        ),
        frets=10.0,
        string_sizes=[0.009, 0.011, 0.016, 0.026, 0.036, 0.046],
        key={
            'w_x_y_z': ''
        },
        price=3799.0,
        left='L',
        right='R',
    )

    assert clean(input) == expected
