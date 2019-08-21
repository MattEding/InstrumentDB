import textwrap

import pytest

from instruments.extract.webscrape import (
    get_driver,
    get_header,
    get_versions,
    get_specifications,
)


@pytest.fixture(scope='session')
def driver(request):
    d = get_driver()
    url = 'https://www.gibson.com/Guitar/CUSGFA436/1958-Les-Paul-Junior-Double-Cut-Reissue'
    d.get(url)
    yield d
    d.quit()


def test_header(driver):
    output = get_header(driver)

    name = '1958 Les Paul Junior Double Cut Reissue'

    headline = 'The Junior Gets Its Wings'
    
    description = '''
    1958 was a monumental year for Gibson in which a whole new lineup of 
    now-famous models were introduced. One of them was the redesigned 
    "double cutaway" Les Paul Junior, which has since found its place in 
    music history as a favorite of hard rock musicians. The extra fret access 
    of the double-cut construction allows upper octave leads while the 
    "simple is better" single-pickup setup projects only thick, heavy tone. 
    Gibson Custom Shop has proudly revived the original recipe from 1958 for 
    this Historic Reissue, from the solid mahogany and hide glue construction 
    to the vintage-style wiring. It is an accurate and faithful replica in 
    every possible way.
    '''

    expected = dict(
        product_name=name,
        headline=textwrap.dedent(headline).replace('\n', ''),
        description=textwrap.dedent(description).replace('\n', ''),
    )
    assert output == expected


def test_versions(driver):
    output = tuple(get_versions(driver))

    expected_1 = dict(
        handedness='right-handed',
        finish='Cherry Red',
        price='$3,799.00',
        images=[
            'https://static.gibson.com/product-images/Custom/CUSGFA436/Cherry%20Red/front-banner-1600_900.png',
            'https://static.gibson.com/product-images/Custom/CUSGFA436/Cherry%20Red/beauty-1600_900.png',
            'https://static.gibson.com/product-images/Custom/CUSGFA436/Cherry%20Red/back-banner-1600_900.png',
        ],
    )

    expected_2 = dict(
        handedness='left-handed',
        finish='TV Yellow',
        price='$3,799.00',
        images=[
            'https://static.gibson.com/product-images/Custom/CUSGFA436/TV%20Yellow/front-banner-1600_900.png',
            'https://static.gibson.com/product-images/Custom/CUSGFA436/TV%20Yellow/beauty-1600_900.png',
            'https://static.gibson.com/product-images/Custom/CUSGFA436/TV%20Yellow/side-banner-1600_900.png',
            'https://static.gibson.com/product-images/Custom/CUSGFA436/TV%20Yellow/back-banner-1600_900.png',
            'https://static.gibson.com/product-images/Custom/CUSGFA436/TV%20Yellow/neck-side-1600_900.png',
        ],
    )

    assert len(output) == 4
    assert expected_1 in output
    assert expected_2 in output


def test_specifications(driver):
    output = get_specifications(driver)
    
    expected = dict(
        Body={
            'Body Material': '1-Piece Solid Mahogany',
            'Weight Relief': 'None',
            'Finish': 'Nitrocellulose VOS (Vintage Patina)',
        },
        Neck={
            'Neck Material': 'Solid Mahogany',
            'Neck Profile': 'Chunky C-Shape',
            'Scale Length': '24.75" / 62.865cm',
            'Fingerboard Material': 'Indian Rosewood, Hide Glue Fit',
            'Fingerboard Radius': '12" / 304.8mm',
            'Number of Frets': '22',
            'Frets': 'Authentic Medium-Jumbo',
            'Nut Material': 'Nylon',
            'Nut Width': '1.687" / 42.85mm',
            'End-of-Board Width': '2.24" / 56.89mm',
            'Inlays': 'Pearloid Dots',
        },
        Hardware={
            'Finish': 'Nickel',
            'Bridge': 'Wraparound',
            'Tailpiece': 'Wraparound',
            'Pick Guard': '1-Ply Tortoiseshell Celluloid',
            'Truss Rod Cover': 'Single-ply Black',
            'Control Knobs': 'Gold Top Hats',
            'Switch Tip': 'Amber',
            'Jack Plate': 'Black',
        },
        Electronics={
            'Bridge Pickup': 'Custom Dog-Ear P90',
            'Controls': 'CTS 500K Audio Taper Potentiometers, Paper-in-Oil Capacitors',
        },
        Miscellaneous={
            'Strings': '.010, .013, .017, .026, .036, .046',
            'Case': 'Custom Shop Hardshell',
            'Included Accessories': 'Certificate of Authenticity Booklet',
        },
    )

    assert output == expected
