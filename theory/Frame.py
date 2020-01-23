#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import json
from pylorenzmie.theory.Feature import Feature
from pylorenzmie.theory.LMHologram import LMHologram


class Frame(object):

    def __init__(self, data=None, features=None,
                 framenumber=None, info=None, model=None):
        if model is None:
            self.model = LMHologram()
        self._data = data
        self._framenumber = framenumber
        self._features = []
        if features is not None:
            for feature in features:
                if isinstance(feature, dict):
                    f = Feature(info=feature)
                    self._features.append(f)
                elif type(feature) is Feature:
                    f = feature
                    self._features.append(f)
                else:
                    msg = "Features must be list of Features or deserializable Features"
                    raise(TypeError(msg))
        if info is not None:
            self.deserialize(info)

    @property
    def framenumber(self):
        return self._framenumber

    @framenumber.setter
    def framenumber(self, idx):
        self._framenumber = idx

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def features(self):
        return self._features

    def serialize(self, filename=None, omit=[], omit_feat=[]):
        features = []
        for feature in self.features:
            feature.data = None
            out = feature.serialize(exclude=omit_feat)
            features.append(out)
        if self.data is not None:
            shape = (int(self.data.shape[0]), int(self.data.shape[1]))
            data = self.data.flatten().tolist()
        else:
            shape = None
            data = self.data
        info = {'data': data,
                'shape': shape,
                'features': features,
                'framenumber': str(self.framenumber)}
        for k in omit:
            if k in info.keys():
                info.pop(k)
                if k == 'data':
                    info.pop('shape')
        if filename is not None:
            with open(filename, 'w') as f:
                json.dump(info, f)
        return info

    def deserialize(self, info):
        if info is None:
            return
        if isinstance(info, str):
            with open(info, 'rb') as f:
                info = json.load(f)
        if 'data' in info.keys():
            self.data = np.array(info['data'])
            if 'shape' in info.keys():
                self.data.reshape(info['shape'])
        if 'features' in info.keys():
            features = info['features']
            self._features = []
            for d in features:
                self._features.append(Feature(model=self.model, info=d))
        if 'framenumber' in info.keys():
            self.framenumber = int(info['framenumber'])
        else:
            self.framenumber = None

    def optimize(self, report=True, **kwargs):
        for idx, feature in enumerate(self.features):
            result = feature.optimize(**kwargs)
            if report:
                print(result)
