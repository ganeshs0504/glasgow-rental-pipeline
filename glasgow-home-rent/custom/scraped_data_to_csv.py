if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom(*args, **kwargs):
    # df = output['data']

    # df['date_added'] = output['date_added']
    # df['available_date'] = output['available_date']
    # df['deposit'] = output['deposit']
    # df['furnish_type'] = output['furnish_type']
    # df['property_type'] = output['property_type']
    # df['station_1'] = output['station_1']
    # df['station_1_dist'] = output['station_1_dist']
    # df['station_2'] = output['station_2']
    # df['station_2_dist'] = output['station_2_dist']
    # df['station_3'] = output['station_3']
    # df['station_3_dist'] = output['station_3_dist']

    # df.to_csv('output.csv', index=False, encoding='utf-8')

    return "Successfully written"
