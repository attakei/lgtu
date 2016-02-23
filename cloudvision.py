# -*- coding:utf8 -*-
"""Google Cloud Vision API calling wrapper
"""
from __future__ import (absolute_import, unicode_literals)


__version__ = '0.0.1'
__author__ = 'attakei'


from urllib.parse import urlencode
import json
import base64
import requests


class API(object):
    API_URL_BASE = 'https://vision.googleapis.com/v1'
    
    def __init__(self, api_key, features=None):
        self.api_key = api_key
        self.features = features

    @property
    def url(self):
        url_path = '/images:annotate'
        get_query = {'key': self.api_key}
        return '{}{}?{}'.format(
            self.API_URL_BASE,
            url_path,
            urlencode(get_query)
        )

    @classmethod
    def get_default_features(cls):
        return [
            'TEXT_DETECTION',
        ]

    @classmethod
    def encode_image(cls, image_path):
        with open(image_path, 'rb') as fp:
            encoded = base64.urlsafe_b64encode(fp.read())
        return encoded.decode('ascii')

    @classmethod
    def build_request_unit(cls, image, features, max_results):
        unit = {
            'image': image.payload(),
            'features': []
        }
        for feature in features:
            unit['features'].append({'type': feature, 'maxResults': max_results})
        return unit

    def _call(self, image, features=None, max_results=1):
        payload = {
            'requests': []
        }
        if features is not None:
            pass
        elif self.features is not None:
            features = self.features
        else:
            features = self.get_default_features()
        request_unit = {}
        payload['requests'].append(self.build_request_unit(image, features, max_results))
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(self.url, headers=headers, data=json.dumps(payload))
        return Response(resp.json())


class ImageRequest(object):
    def __init__(self, path):
        self.path = path
        self._cache = None

    def payload(self):
        if self._cache is None:
            self.get_image()
        return {'content': self._cache}

    def get_image(self):
        if self.path.startswith('http://') or self.path.startswith('https://'):
            self._cache = self.encode_from_http()
        else:
            self._cache = self.encode_from_local()

    def encode_from_http(self):
        resp = requests.get(self.path)
        return base64.urlsafe_b64encode(resp.content).decode('ascii')

    def encode_from_local(self):
        with open(self.path, 'rb') as fp:
            encoded = base64.urlsafe_b64encode(fp.read())
        return encoded.decode('ascii')


class Response(object):
    def __init__(self, response):
        response_ = response['responses'][0]
        self.error = response_.get('error', None)
        """API error message"""
        self.text = [Entity(**annotation) for annotation in response_.get('textAnnotations', [])]
        """List of text annotations"""
        self.logo = [Entity(**annotation) for annotation in response_.get('logoAnnotations', [])]
        """List of logo annotations"""
        self.label = [Entity(**annotation) for annotation in response_.get('labelAnnotations', [])]
        """List of logo annotations"""
        self.face = [Entity(**annotation) for annotation in response_.get('faceAnnotations', [])]
        """List of face annotations"""


# Tahnks to http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
class Entity(object):
    def __init__(self, **entries): 
        self.__dict__.update(entries)


if __name__ == '__main__':
    vision = CloudVision('none')
    print(vision.url)
    