from geopy.point import Point
import requests
import json
import os


def _get_arg_from_env_or_json(arg_name, default=None):
    value = os.getenv(arg_name)
    if value is None or not value.strip():
        # Try loading from setting.json
        try:
            with open('settings.json', 'r', encoding='utf-8') as fp:
                value = json.load(fp)[arg_name]
        except Exception:
            value = default
    return value


def get_routes():
    route_url = 'https://sport.fudan.edu.cn/sapi/route/list'
    params = {'userid': _get_arg_from_env_or_json('USER_ID'),
              'token': _get_arg_from_env_or_json('FUDAN_SPORT_TOKEN')}
    response = requests.get(route_url, params=params)
    data = json.loads(response.text)
    try:
        route_data_list = filter(lambda route: route['points'] is not None and len(route['points']) == 1,
                                 data['data']['list'])
        return [FudanRoute(route_data) for route_data in route_data_list]
    except:
        print(f"ERROR: {data['message']}")
        exit(1)


class FudanAPI:
    def __init__(self, route):
        self.route = route
        self.user_id = _get_arg_from_env_or_json('USER_ID')
        self.token = _get_arg_from_env_or_json('FUDAN_SPORT_TOKEN')
        self.system = _get_arg_from_env_or_json('PLATFORM_OS', 'iOS 2016.3.1')
        self.device = _get_arg_from_env_or_json('PLATFORM_DEVICE', 'iPhone|iPhone 13<iPhone14,5>')
        self.run_id = None

    def start(self):
        start_url = 'https://sport.fudan.edu.cn/sapi/run/start'
        params = {'userid': self.user_id,
                  'token': self.token,
                  'route_id': self.route.id,
                  'route_type': self.route.type,
                  'system': self.system,
                  'device': self.device,
                  'lng': self.route.start_point.longitude,
                  'lat': self.route.start_point.latitude}
        response = requests.get(start_url, params=params)
        data = json.loads(response.text)
        try:
            self.run_id = data['data']['run_id']
        except:
            print(f"ERROR: {data['message']}")
            exit(1)

    def update(self, point):
        update_url = 'https://sport.fudan.edu.cn/sapi/run/point'
        params = {'userid': self.user_id,
                  'token': self.token,
                  'run_id': self.run_id,
                  'lng': point.longitude,
                  'lat': point.latitude}
        response = requests.get(update_url, params)
        try:
            data = json.loads(response.text)
            return data['message']
        except:
            return response.text

    def finish(self, point):
        finish_url = 'https://sport.fudan.edu.cn/sapi/run/finish'
        params = {'userid': self.user_id,
                  'token': self.token,
                  'run_id': self.run_id,
                  'system': self.system,
                  'device': self.device,
                  'lng': point.longitude,
                  'lat': point.latitude}
        response = requests.get(finish_url, params)
        data = json.loads(response.text)
        return data['message']


class FudanRoute:
    def __init__(self, data):
        self.id = data['route_id']
        self.name = data['name']
        self.type = data['types'][0]
        self.start_point = Point(data['points'][0]['lat'],
                                 data['points'][0]['lng'])

    def pretty_print(self):
        print(f"#{self.id}: {self.name}")
