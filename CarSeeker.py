import os
import sys
import numpy
import math
import cv2

from darkflow.net.build import TFNet


options = {"model":"./cfg/yolo.cfg","load": "./yolo.weights", "threshold": 0.38,"gpu":1.0}
tfnet = TFNet(options)
KIGOU = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
THRESHOLD_DISTANCE = 150
THRESHOLD_SIZE = 150


def main():
    #path = arg1 
    case1 = CarSeeker()
    case1.nodamethod('./images/test/IMG_20180116_135746.jpg')


class CarSeeker():
    def __init__(self):
        #self.path = path
        pass


    def setup(self):
        path_output = os.path.join(self.path, 'output/')
        if os.path.exists(path_output) == False:
            print("出力フォルダがありません．新たに作成してもいいですか？[y/n]")
            ans = input('>>')
            if ans == 'y':
                os.mkdir(path_output)
                print("出力フォルダを作成しました．%s" % path_output)
            else:
                print("やめます")
                sys.exit(1)
    

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
                    min_distance = THRESHOLD_DISTANCE + 1
                else:
                    for point in list_center:
                        distance = self._distance(center[0], center[1], point[0], point[1])
                        list_distance.append(distance)
                    min_distance = min(list_distance)
                if min_distance > THRESHOLD_DISTANCE and size > THRESHOLD_SIZE:
                    num_of_points += 1
                    list_center.append(center)
                    d_center = {"{}".format(KIGOU[num_of_points-1]):{
                                    "x":center[0],
                                    "y":center[1],
                                    "size":size
                                    }
                               }
                    output_dict[filename].update(d_center)
        output_dict[filename]["num_of_points"] = num_of_points
        print(output_dict)
                
                        
    def _distance(self, x1, y1, x2, y2):
        xd = x2 - x1
        yd = y2 - y1 
        distance = math.sqrt(pow(xd,2)+pow(yd,2))
        return distance


if __name__ == '__main__':
    #arg = sys.argv
    main()