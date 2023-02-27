import time
import json
import hashlib
import hmac
import base64
import requests

class API:
    __base_url = 'https://api.switch-bot.com'

    def __init__(self, token, secret, nonce):
        self.__token = token
        self.__secret = secret
        self.__nonce = nonce

    def __gen_header(self):
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(self.__token, t, self.__nonce)
        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(self.__secret, 'utf-8')
        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

        headers = {
            'Content-type': 'application/json; charset=utf8',
            'Authorization': self.__token,
            'sign': str(sign, 'utf-8'),
            't': str(t),
            'nonce': self.__nonce
        }

        return headers

    def get(self, target_url):
        url = self.__base_url + target_url
        headers = self.__gen_header()
        r = requests.get(url = url, headers = headers)
        if r.status_code == requests.codes.ok:
            r_dict = r.json()
            if 'body' in r_dict:
                return True, r_dict['body']
        return False, {}

    def post(self, target_url, payload):
        url = self.__base_url + target_url
        headers = self.__gen_header()
        r = requests.post(url = url, headers = headers, data = json.dumps(payload))
        if r.status_code == requests.codes.ok:
            return True
        else:
            return False

class DeviceManager:
    __url_get_list = '/v1.1/devices'
    __url_get_status = '/v1.1/devices/{}/status'
    __url_ctrl = '/v1.1/devices/{}/commands'

    def __init__(self, api):
        self.__api = api

    def get_all(self):
        target_url = self.__url_get_list
        ret, resp = self.__api.get(target_url)
        if ret and 'deviceList' in resp:
            return resp['deviceList']
        return []

    def get_by_name(self, dev_name):
        devices = []
        for device in self.get_all():
            if 'deviceName' in device and device['deviceName'] == dev_name:
                devices.append(device)
        return devices

    def get_by_type(self, dev_type):
        devices = []
        for device in self.get_all():
            if 'deviceType' in device and device['deviceType'] == dev_type:
                devices.append(device)
        return devices

    def get_status(self, device_id):
        target_url = self.__url_get_status.format(device_id)
        return self.__api.get(target_url)

    def ctrl(self, device_id, type, cmd, param):
        target_url = self.__url_ctrl.format(device_id)
        payload = {
            'commandType': type,
            "command": cmd,
            "parameter": param
        }
        return self.__api.post(target_url, payload)

class Bot:
    pass

class CeilingLight:
    __device_type = 'Ceiling Light'

    def __init__(self, device_manager, device_id):
        self.__device_manager = device_manager
        self.__device_id = device_id

    def device_id(self):
        return self.__device_id

    def get_power(self):
        ret, resp = self.__device_manager.get_status(self.__device_id)
        if ret and 'power' in resp:
            return resp['power']
        return "unknow"

    def get_brightness(self):
        ret, resp = self.__device_manager.get_status(self.__device_id)
        if ret and 'brightness' in resp:
            return resp['brightness']
        return 0

    def get_color_temp(self):
        ret, resp = self.__device_manager.get_status(self.__device_id)
        if ret and 'brightness' in resp:
            return resp['brightness']
        return 0

    def turn_on(self):
        return self.__device_manager.ctrl(
            self.__device_id,
            'command',
            'turnOn',
            'default')

    def turn_off(self):
        return self.__device_manager.ctrl(
            self.__device_id,
            'command',
            'turnOff',
            'default')

    def toggle(self):
        return self.__device_manager.ctrl(
            self.__device_id,
            'command',
            'toggle',
            'default')

    def set_brightness(self, brightness):
        if brightness < 1 or brightness > 100:
            return
        return self.__device_manager.ctrl(
            self.__device_id,
            'command',
            'setBrightness',
            brightness)

    def set_color_temp(self, color_temp):
        if color_temp < 2700 or color_temp > 6500:
            return
        return self.__device_manager.ctrl(
            self.__device_id,
            'command',
            'setColorTemperature',
            color_temp)

CeilingLightPro = CeilingLight