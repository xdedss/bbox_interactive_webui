
import numpy as np
import cv2

import os, time, shutil, json, random, threading
import http.server, socketserver

from typing import Sequence

TEMPLATE_DIR = 'template'

class ImageData():

    def __init__(self, img, img_name=None):
        '''
        img: cv2 image(bgr)
        img_name: string or None
        '''
        self.img = img
        self.name = img_name
        self.bboxes = []

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
            'info': info,
        })

        

def get_port_temp_dir(port):
    return f'temp_{port}'

def generate_from_template(data, class_names, class_colors, port):
    
    d = get_port_temp_dir(port)

    if (os.path.exists(d)):
        shutil.rmtree(d)

    shutil.copytree(TEMPLATE_DIR, d)

    # generate imageList json
    img_list = []
    for i, image_data in enumerate(data):
        assert isinstance(image_data, ImageData)
        img = image_data.img
        fname = f'{i:03d}.jpg'
        name = image_data.name
        if (name is None):
            name = f'{i:03d}'
        cv2.imwrite(os.path.join(d, fname), img)
        img_list.append({
            'file': fname,
            'name': name,
            'bbox': image_data.bboxes,
        })

    js_file = os.path.join(d, 'inject.js')
    with open(js_file, 'r', encoding='utf-8') as f:
        s = f.read()
    s = s % (json.dumps(img_list), json.dumps(class_names), json.dumps(class_colors))
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(s)

def serve_blocking(port, http_root):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=http_root, **kwargs)
    handler = Handler
    address = ('', port)
    httpd = socketserver.TCPServer(address, handler)
    httpd.allow_reuse_address = True

    def serve_run():
        httpd.serve_forever()

    print(f"Serving HTTP server on port {port} with root directory '{http_root}'...")
    
    thread = threading.Thread(target=serve_run, daemon=True)
    thread.start()
    try:
        while (True):
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("HTTP server stopped.")
    

def visualize_start_server(data, class_names, class_colors, port):
    '''
    data: list of ImageData
    class_names: list of string
    class_colors: list of [r, g, b] (0-255)
    port: int
    '''


    generate_from_template(data, class_names, class_colors, port)
    serve_blocking(port, get_port_temp_dir(port))
    shutil.rmtree(get_port_temp_dir(port))
    


def test():
    data = []
    tags = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    classes = ['dog', 'cat', 'person', 'car', 'plane']
    colors = [
        [255, 80, 80],      # Brighter Red
        [80, 255, 80],      # Brighter Green
        [80, 80, 255],      # Brighter Blue
        [255, 255, 100],    # Brighter Yellow
        [255, 80, 255]      # Brighter Magenta
    ]
    for i in range(5):
        img = np.clip(np.random.randn(256, 256, 3) * 0.2 * 255, 0, 255).astype(np.uint8)
        img_data = ImageData(img)
        for j in range(10):
            cx, cy = np.random.uniform(0, img.shape[1]), np.random.uniform(0, img.shape[0])
            w, h = np.exp(np.random.uniform(np.log(5), np.log(200))), np.exp(np.random.uniform(np.log(5), np.log(200)))
            img_data.add_bbox((cx - w/2, cy - h/2), (cx + w/2, cy + h/2), random.randint(0, len(classes) - 1), random.sample(tags, 2))
            cv2.ellipse(img, (int(cx), int(cy)), (int(w/2), int(h/2)), 0, 0, 360, color=np.random.randint(0, 255, 3).tolist(), thickness=-1)
        data.append(img_data)
    visualize_start_server(data, classes, colors, 8080)

test()


