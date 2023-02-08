import pandas as pd
from sqlalchemy import create_engine


def loadcsv2db(fname, dbname):
    # create new database using csnv.csv
    # fail if there exist old database
    try:
        engine = create_engine(f"sqlite:///{dbname}")
    except Exception:
        print("Can't create 'engine")

    df = pd.read_csv(fname)
    with engine.begin() as connection:
        df.to_sql("src", con=connection, index_label="id", if_exists="fail")
    return df


def appendcsv2db(fname, dbname):
    # append fname.csv to dbname
    try:
        engine = create_engine(f"sqlite:///{dbname}")
    except Exception:
        print("Can't create engine")

    df = pd.read_csv(fname)
    with engine.begin() as connection:
        tab = connection.execute("select event from src")
        tab = [i["Event"] for i in tab]
        df = df[~df.Event.isin(tab)]
        df.index += len(tab)
        df.to_sql("src", con=connection, index_label="id", if_exists="append")
    return df


def db2csv(fname, dbname):
    try:
        engine = create_engine(f"sqlite:///{dbname}")
    except:
        print("Can't create 'engine")
    with engine.begin() as connection:
        sql_query = pd.read_sql_query("select * from src", connection)
    df = pd.DataFrame(sql_query)
    df.to_csv(fname, index=False)


def update(picker_key, picker_list, key, value_list, dbname):
    try:
        engine = create_engine(f"sqlite:///{dbname}")
    except:
        print("Can't create 'engine")
    with engine.begin() as connection:
        for (picker, value) in zip(picker_list, value_list):
            connection.execute(
                f"UPDATE Src SET {key} = {value} WHERE {picker_key}= '{picker}' "
            )
