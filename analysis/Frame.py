#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from .Feature import Feature

class Frame(object):
"""
    Object representation of an experimental video frame. Frames can have an image (data), a framenumber, an instrument for fitting, a list of Feature objects
    and a corresponding list of bounding boxes. Features can be added in two ways: 
      1) If the frame has an image (data), then Features are added by specifying a bbox (via a dict) in deserialize . The bbox specifies x_p and y_p, and 
         Feature data (cropped image) is obtained by using the bbox to crop the Frame data. Optionally, the dict can also pass other feature info 
         (like z_p, a_p, etc.)  through a dict 'bbox_info'
      2) Feature objects can be passed directly. Their corresponding bbox will be 'none' and are serialized individually (under 'features') with their own data.
   
"""
    def __init__(self, features=None, instrument=None, 
                 data=None, framenumber=None, info=None):
        self._instrument = instrument
        self._framenumber = framenumber
        self._data = data
        self._bboxes = []
        self._features = []
        if features is not None:
            self.add(features)
        if info is not None:
            self.deserialize(info)
    
    @property
    def instrument(self):
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        self._instrument = instrument

    @property
    def framenumber(self):
        return self._framenumber

    @framenumber.setter
    def framenumber(self, idx):
        self._framenumber = idx

    @property
    def features(self):
        return self._features
    
    @property
    def bboxes(self):
        return self._bboxes
    
    def add(self, features): 
        if type(features) is Feature:
            features = [features] 
        for feature in features:
            if self.instrument is not None:
                feature.model.instrument = self.instrument
            if type(feature) is Feature:
                self._features.append(feature)
                self._bboxes.append(None)
            else:
                msg = "features must be list of Features"
                msg += " or deserializable Features"
                raise(TypeError(msg))
                
    def add_bbox(self, bboxes, info=None):
        info = info or [None for bbox in bboxes]
        for i, bbox in enumerate(bboxes):
            feature = Feature(data=self.crop(bbox))
            feature.x_p = bbox[0]
            feature.y_p = bbox[1]
            feature.deserialize(info[i])
            self._features.append(feature)
            self._bboxes.append(bbox)         

    def crop(self, center, cropshape):
        cropped, corner = crop_center(self.data, center, cropshape)
        return cropped
    
    def optimize(self, report=True, **kwargs):
        for idx, feature in enumerate(self.features):
            result = feature.optimize(**kwargs)
            if report:
                print(result)

    def serialize(self, filename=None, omit=[], omit_feat=[]):
        info = {}
        features = []
        bboxes = []
        bbox_info = []
        if 'features' not in omit:
            for i, feature in enumerate(self.features):
                if self.bbox[i] is None:
                    features.append(feature.serialize( exclude=omit_feat ))
                else:
                    bbox.append(self.bbox[i])
                    bbox_info.append(feature.serialize( exclude=['data', 'x_p', 'y_p', 'shape'].extend(omit_feat) ))
                  
        info['features'] = features
        info['bboxes'] = bboxes
        info['bbox_info'] = [(x if len(x.keys()) > 0 else None) for x in bbox_info]                              
        if self.framenumber is not None:
            info['framenumber'] = str(self.framenumber)
        for k in omit:
            if k in info.keys():
                info.pop(k)
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
        if 'features' in info.keys():          #### Add any features passed in serial form
            self.add(info['features'])
        if 'bboxes' in info.keys():            #### Add any features specified by bboxes
            bboxes = info['bboxes']
            if 'bbox_info' in info.keys():
                self.add_bbox(bboxes, info=info['bbox_info'])
            else:
                self.add_bbox(bboxes)
        if 'framenumber' in info.keys():
            self.framenumber = int(info['framenumber']) if self.framenumber is None else self.framenumber
        else:
            self.framenumber = None

                  
                                  
#### Static helper method. Literally copy-pasted from Lauren Altman's crop_feature - can probably just import it instead in the future                                 
def crop_center(img_local, center, cropshape):
    (xc, yc) = center
    (crop_img_rows, crop_img_cols) = cropshape
    (img_cols, img_rows) = img_local.shape[:2]
    if crop_img_rows % 2 == 0:
        right_frame = left_frame = int(crop_img_rows/2)
    else:
        left_frame = int(np.floor(crop_img_rows/2.))
        right_frame = int(np.ceil(crop_img_rows/2.))
    xbot = xc - left_frame
    xtop = xc + right_frame
    if crop_img_cols % 2 == 0:
        top_frame = bot_frame = int(crop_img_cols/2.)
    else:
        top_frame = int(np.ceil(crop_img_cols/2.))
        bot_frame = int(np.floor(crop_img_cols/2.))
    ybot = yc - bot_frame
    ytop = yc + top_frame
    if xbot < 0:
        xbot = 0
        xtop = crop_img_rows
    if ybot < 0:
        ybot = 0
        ytop = crop_img_cols
    if xtop > img_rows:
        xtop = img_rows
        xbot = img_rows - crop_img_rows
    if ytop > img_cols:
        ytop = img_cols
        ybot = img_cols - crop_img_cols
    cropped = img_local[ybot:ytop, xbot:xtop]
    corner = (xbot, ybot)
    return cropped, corner
                                  
                               
            
