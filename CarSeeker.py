import os
import sys
import numpy
import math
import glob
import cv2
import sqlite3
import json

from darkflow.net.build import TFNet

options = {"model":"./cfg/yolo.cfg","load": "./yolo.weights", "threshold": 0.38,"gpu":1.0}
tfnet = TFNet(options)


class CarSeeker():
    KIGOU = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    THRESHOLD_DISTANCE = 150
    THRESHOLD_SIZE = 150

    def __init__(self, path):
        self.path = path
        self.outputpath = ''
        self.labelname = 'label.db'
        self.outputfilename = 'output.json'
        self.result_dict = {}


    def test_method(self):
        self.setup()
        self.matomete(self.path)
        self.save(self.result_dict)


    def setup(self):
        self.outputpath = os.path.join(self.path, 'output/')
        if os.path.exists(self.outputpath) == False:
            print("出力フォルダがありません．新たに作成してもいいですか？[y/n]")
            ans = input('>>')
            if ans == 'y':
                os.mkdir(self.outputpath)
                print("出力フォルダを作成しました．%s" % self.outputpath)
            else:
                print("やめます")
                sys.exit(1)
        
    
    def matomete(self, inputpath):
        targets = glob.glob(os.path.join(inputpath, '*.jpg'))
        num_of_images = len(targets)
        print("{}枚の画像があります．．．".format(num_of_images))
        for image in targets:
            self.nodamethod(image)
            print(image)


    def save(self, result_dict):
        outputfilepath = os.path.join(self.outputpath, self.outputfilename)
        with open(outputfilepath, 'w') as f:
            json.dump(result_dict, f, indent=4, separators=(',',':'))


    def nodamethod(self, input_image):
        img = cv2.imread(input_image)
        filename = os.path.basename(input_image)
        height, width = img.shape[:2]
        output_dict = {filename:{
                           "label":0,
                           "width":width,
                           "height":height,
                           "num_of_points":0,
                           }
                      }
        result = tfnet.return_predict(img)
        num_of_points = 0
        list_center = []
        #print(result)
        for item in result:
            label = item['label']
            if label == 'car' or label == 'bus' or label == 'truck':
                topleft_x = item['topleft']['x']
                topleft_y = item['topleft']['y']
                bottomright_x = item['bottomright']['x']
                bottomright_y = item['bottomright']['y']
                confidence = item['confidence']
                center = [int(topleft_x+(bottomright_x-topleft_x)/2),
                          int(topleft_y+(bottomright_y-topleft_y)/2)]
                size = self._distance(topleft_x, topleft_x, bottomright_x, bottomright_y)
                list_distance = []
                if num_of_points == 0:
                    min_distance = CarSeeker.THRESHOLD_DISTANCE + 1
                else:
                    for point in list_center:
                        distance = self._distance(center[0], center[1], point[0], point[1])
                        list_distance.append(distance)
                    min_distance = min(list_distance)
                if min_distance > CarSeeker.THRESHOLD_DISTANCE and size > CarSeeker.THRESHOLD_SIZE:
                    num_of_points += 1
                    list_center.append(center)
                    d_center = {"{}".format(CarSeeker.KIGOU[num_of_points-1]):{
                                    "x":center[0],
                                    "y":center[1],
                                    "size":int(size)
                                    }
                               }
                    output_dict[filename].update(d_center)
                    text = label + " {0:.2f}".format(confidence)
                    k = [img,
                         topleft_x, topleft_y,
                         bottomright_x, bottomright_y,
                         center, text]
                    self._writein(*k)
        output_dict[filename]["num_of_points"] = num_of_points
        output_dict[filename]["label"] = self._getlabel(filename)
        cv2.imwrite(os.path.join(self.outputpath, filename), img)
        self.result_dict.update(output_dict)


    def _distance(self, x1, y1, x2, y2):
        xd = x2 - x1
        yd = y2 - y1 
        distance = math.sqrt(pow(xd, 2)+pow(yd, 2))
        return distance

    def _writein(self, img, x1, y1, x2, y2, center, text):
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 5)
        cv2.rectangle(img, (x1, y1-15), (x1+100, y1+5), (0,0,255), -1)
        cv2.putText(img, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
        cv2.circle(img, (center[0], center[1]), 15, (255, 255, 0), -1)

    def _getlabel(self, filename):
        #DBに登録が無かったときには警告を出さないと(´･_･`)
        labelpath = os.path.join('./', self.labelname)
        conn = sqlite3.connect(labelpath)
        c = conn.cursor()
        sql = "select * from images where filename = '%s'" % filename
        c.execute(sql)
        for raw in c:
            label = raw[1]
        conn.close
        return label 


def main(arg0):
    path = arg0 
    case1 = CarSeeker(path)
    case1.test_method()


if __name__ == '__main__':
    arg = sys.argv
    main(arg[1])