
import numpy as np
import cv2

import os, time, shutil, json

from typing import Sequence

TEMPLATE_DIR = 'template'

class ImageData():

    def __init__(self, img):
        '''
        img: cv2 image(bgr)
        '''
        self.img = img
        self.bboxes = []
    
    def to_json(self):
        pass

    def add_bbox(
            self, 
            top_left_xy: tuple[float, float], 
            bottom_right_xy: tuple[float, float], 
            class_id: int, 
            tags: Sequence[str]=[], 
            info: str='no additional info'):
        x1, y1 = top_left_xy
        x2, y2 = bottom_right_xy
        tags = [str(tag) for tag in tags]
        self.bboxes.append({
            'classId': class_id,
            'tags': tags,
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
        })

        

def get_port_temp_dir(port):
    return f'temp_{port}'

def generate_from_template(data, class_names, class_colors, port):
    d = get_port_temp_dir(port)
    shutil.copytree(TEMPLATE_DIR, d)
    js_file = os.path.join(d, 'inject.js')
    with open(js_file, 'r', encoding='utf-8') as f:
        s = f.read()
    s = s % (data, json.dumps(class_names), json.dumps(class_colors))

    

def visualize_start_server(data, class_names, class_colors, port):
    '''
    data: [
        
    ]
    class_names: list of string
    class_colors: list of [r, g, b] (0-255)
    '''

