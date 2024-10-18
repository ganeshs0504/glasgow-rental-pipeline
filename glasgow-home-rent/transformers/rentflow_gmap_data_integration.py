from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader, ConfigKey, EnvironmentVariableLoader
import pandas as pd
from os import path
import googlemaps
from datetime import datetime, date

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



def get_gmaps_direction(gmaps, origin, dest='Glasgow Central', dep_time=datetime(date.today().year, date.today().month, date.today().day, 9, 0, 0), mode='transit'):
    response = gmaps.directions(
        origin = origin,
        destination = dest,
        mode = mode,
        transit_mode = 'rail',
        region = 'uk',
        departure_time = dep_time,
        units = 'metric'
    )
    return response 


@transformer
def transform(df, *args, **kwargs):

    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'gmap_dev'
    config = ConfigFileLoader(config_path, config_profile)
    API_KEY = config.get('API_KEY')

    gmaps = googlemaps.Client(key=API_KEY)

    train_journey_time_ = []
    number_of_trains_ = []
    total_number_of_stops_ = []
    walking_time_ = []
    walking_distance_ = []
    origin_lat_ = []
    origin_lng_ = []
    total_time_ = []
    total_dist_ = []

    for i, row in df.iterrows():
        try:
            train_journey_time = 0
            number_of_trains = 0
            total_number_of_stops = 0
            walking_time = 0
            walking_distance = 0
            origin_lng = 0
            origin_lat = 0
            total_time = 0
            total_dist = 0
        
            response = get_gmaps_direction(gmaps, row['station_1']+', Glasgow')
                
            legs = response[0]['legs'][0]
        
            origin_lat = legs['start_location']['lat']
            origin_lng = legs['start_location']['lng']
        
            total_time = legs['duration']['value'] / 60
            total_dist = legs['distance']['value']
        
            for step in legs['steps']:
                if step['travel_mode'] == 'TRANSIT':
                    number_of_trains += 1
                    total_number_of_stops += step['transit_details']['num_stops']
                    train_journey_time += step['duration']['value']
                elif step['travel_mode'] == 'WALKING':
                    walking_distance += step['distance']['value']
                    walking_time += step['duration']['value'] / 60
        except Exception as e:
            print(e, row['station_1'])
            # train_journey_time = 0
            # number_of_trains = 0
            # total_number_of_stops = 0
            # walking_time = 0
            # walking_distance = 0
            # origin_lat = 0
            # origin_lng = 0
            # total_time = 0
            # total_dist = 0
        
        train_journey_time_.append(train_journey_time)
        number_of_trains_.append(number_of_trains)
        total_number_of_stops_.append(total_number_of_stops)
        walking_time_.append(walking_time)
        walking_distance_.append(walking_distance)
        origin_lat_.append(origin_lat)
        origin_lng_.append(origin_lng)
        total_time_.append(total_time)
        total_dist_.append(total_dist)

    df['train_journey_time'] = train_journey_time_
    df['number_of_trains'] = number_of_trains_
    df['total_number_of_stops'] = total_number_of_stops_
    df['walking_time'] = walking_time_
    df['walking_distance'] = walking_distance_
    df['origin_lat'] = origin_lat_
    df['origin_lng'] = origin_lng_
    df['total_time'] = total_time_
    df['total_dist'] = total_dist_
    


    return df


@test
def test_output(output, *args) -> None:
    assert len(output[output['origin_lat']==0]['station_1'].unique()) == 1, 'Error finding some stations'
