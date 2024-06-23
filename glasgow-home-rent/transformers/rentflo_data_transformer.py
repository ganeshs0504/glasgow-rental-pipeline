import pandas as pd
from datetime import datetime, timedelta
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def convert_pricing(str):
    if pd.isna(str) or (str is None):
        return None
    return float(str.split()[0].replace(',', '').replace('£', ''))

def convert_distance(str):
    if pd.isna(str) or (str is None):
        return None
    return float(str.split()[0])

def convert_datetime(str):
    if pd.isna(str) or (str is None):
        return pd.NaT
    str = str.lower()
    if str == 'now' or str == 'today':
        return datetime.today().date()
    elif str == 'yesterday':
        return (datetime.today() - timedelta(days=1)).date()
    else:
        return pd.to_datetime(str, format='%d/%m/%Y').date()


@transformer
def transform(df, *args, **kwargs):
    
    df = df.drop_duplicates(ignore_index=True)

    df['price'] = df['price'].apply(convert_pricing)

    df['deposit'] = df['deposit'].replace('Ask agent', None)
    df['deposit'] = df['deposit'].apply(convert_pricing)

    df['station_1_dist'] = df['station_1_dist'].apply(convert_distance)
    df['station_2_dist'] = df['station_2_dist'].apply(convert_distance)
    df['station_3_dist'] = df['station_3_dist'].apply(convert_distance)

    df['furnish_type'] = df['furnish_type'].replace('Ask agent', None).replace('Now', None)

    df['date_added'] = df['date_added'].replace('Ask agent', None)
    df['available_date'] = df['available_date'].replace('Ask agent', None)

    df['date_added'] = df['date_added'].apply(convert_datetime)
    df['available_date'] = df['available_date'].apply(convert_datetime)
    df['date_added'] = pd.to_datetime(df['date_added'])
    df['available_date'] = pd.to_datetime(df['available_date'])

    df['beds'] = df['beds'].fillna(0.0).astype(int)
    df['bath'] = df['bath'].fillna(0.0).astype(int)

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
