import contextlib
import functools
import json
import textwrap

import psycopg2


def connect():
    with open('db_credentials.json') as fp:
        conn_kwargs = json.load(fp)

    conn = psycopg2.connect(conn_kwargs)
    return conn


def create_table(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tablename = func.__name__
        schema = func(*args, **kwargs).strip('\n')
        table = '''
        CREATE TABLE IF NOT EXISTS {tablename}
        (
        {schema}
        );
        ''' 
        table = textwrap.dedent(table).strip()
        table = table.format(tablename=tablename, schema=schema)
        with contextlib.closing(connect()) as conn:
            with conn:
                with conn.cursor() as curs:
                    curs.execute(table)
    return wrapper


@create_table
def models(): 
    return '''
    model_id        INTEGER         PRIMARY KEY
    , name          VARCHAR(75)     NOT NULL
    , headline      VARCHAR(75)
    , description   TEXT
    '''


@create_table
def bodies():
    return '''
    model_id            INTEGER         PRIMARY KEY     REFERENCES models(model_id)         -- 1 to 1 relationship
    , back_material_id  INTEGER                         REFERENCES materials(material_id)
    , body_material_id  INTEGER                         REFERENCES materials(material_id)
    , side_material_id  INTEGER                         REFERENCES materials(material_id)
    , top_material_id   INTEGER                         REFERENCES materials(material_id)
    , finsih_id         INTEGER                         REFERENCES finishes(finish_id)
    , binding           VARCHAR(75)
    , binding_style     VARCHAR(75)
    , body_shape        VARCHAR(75)
    , bracing           VARCHAR(75)
    , centerblock       VARCHAR(75)
    , weight_relief     VARCHAR(75)
    '''


@create_table
def electronics():
    return '''
    model_id                    INTEGER         PRIMARY KEY     REFERENCES models(model_id)     -- 1 to 1 relationship
    , bridge_pickup_id          INTEGER                         REFERENCES pickups(pickup_id)
    , middle_pickup_id          INTEGER                         REFERENCES pickups(pickup_id)
    , neck_pickup_id            INTEGER                         REFERENCES pickups(pickup_id)
    , under_saddle_pickup_id    INTEGER                         REFERENCES pickups(pickup_id)
    , controls                  VARCHAR(150)
    '''


@create_table
def hardwares():
    return '''
    model_id                INTEGER         PRIMARY KEY     REFERENCES models(model_id)         -- 1 to 1 relationship
    , finsih_id             INTEGER                         REFERENCES finsihes(finish_id)
    , saddle_material_id    INTEGER                         REFERENCES materials(material_id)
    , bridge                VARCHAR(75)
    , bridge_pins           VARCHAR(75)
    , control_knobs         VARCHAR(75)
    , jack_plate            VARCHAR(75)
    , pick_guard            VARCHAR(75)
    , switch_tip            VARCHAR(75)
    , switch_washer         VARCHAR(75)
    , tailpiece             VARCHAR(75)
    , truss_rod_cover       VARCHAR(75)
    , tuner_plating         VARCHAR(75)
    , tuners                VARCHAR(75)
    '''


@create_table
def necks():
    return '''
    model_id                    INTEGER         PRIMARY KEY     REFERENCES models(model_id)         -- 1 to 1 relationship
    , fingerboard_material_id   INTEGER                         REFERENCES materials(material_id)
    , neck_material             INTEGER                         REFERENCES materials(material_id)
    , nut_material              INTEGER                         REFERENCES materials(material_id)
    , end_of_board_width        FLOAT           -- inches
    , fingerboard_radius        FLOAT           -- inches
    , frets                     VARCHAR(75)
    , inlays                    VARCHAR(75)
    , neck_profile              VARCHAR(75)
    , number_of_frets           INTEGER
    , nut_width                 FLOAT           -- inches
    , scale_length              FLOAT           -- inches
    '''


@create_table
def miscs():
    return '''
    model_id        INTEGER         PRIMARY KEY     REFERENCES models(model_id)     -- 1 to 1 relationship
    , case          VARCHAR(75)     NOT NULL
    , accessories   VARCHAR(200)
    , strings       FLOAT[]
    '''


@create_table
def materials():
    return '''
    material_id     INTEGER         PRIMARY KEY
    , material      VARCHAR(150)    NOT NULL
    '''


@create_table
def versions():
    return '''
    version_id      INTERGER    PRIMARY KEY
    , price         FLOAT       NOT NULL        -- US dollars
    , handedness    CHAR(1)     NOT NULL        CHECK (handedness IN ('L', 'R'))
    , finish_id     INTEGER     NOT NULL        REFERENCES finishes(finish_id)
    , model_id      INTEGER     NOT NULL        REFERENCES models(model_id)
    '''


@create_table
def finishes():
    return '''
    finish_id   INTEGER         PRIMARY KEY
    , finish    VARCHAR(150)    NOT NULL
    '''


@create_table
def pickups():
    return '''
    pickup_id   INTEGER         PRIMARY KEY
    , pickup    VARCHAR(150)    NOT NULL
    '''


@create_table
def images():
    return '''
    image_id        INTEGER         PRIMARY KEY
    , url           VARCHAR(100)    NOT NULL
    , version_id    INTEGER         NOT NULL        REFERENCES versions(version_id)
    '''


@create_table
def related():
    return '''
    model_id        INTEGER     NOT NULL    REFERENCES models(model_id)
    , related_id    INTEGER     NOT NULL    REFERENCES models(model_id)
    , CHECK (model_id != related_id)
    , PRIMARY KEY (model_id, related_id)    -- junction table
    '''
