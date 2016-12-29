from flask import Flask
import numpy as np
from matplotlib import pyplot as plt
import cv2
import copy
from os import listdir
from os.path import isfile, join

class Object(object):
    pass

app = Flask(__name__)

@app.route('/')
def homepage():
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    imageSourcePath = "imageSource"
    imageOutputPath = "imageOutputs"
    imageSources = [f for f in listdir(imageSourcePath) if isfile(join(imageSourcePath, f))]

    params = Object()
    #gaussianParams
    params.gKernelX = 3
    params.gKernelY = 3
    params.sigmaX = 0
    #threshParams
    params.tThresh = 100
    params.tMaxVal = 255
    params.tType = cv2.THRESH_BINARY_INV
    #cannyParams
    params.cMinVal = 100
    params.cMaxVal = 50
    #houghParams
    params.hResolutionScale = 1
    params.hMinCircDist = 100
    params.hAccum = 15 #Higher means less circles detected
    params.hMinRadius = 5
    #growingCircleParams
    params.gcIters = 1
    #lightThreshParams
    params.ltThresh = 200
    params.ltMaxVal = 255
    params.ltType = cv2.THRESH_BINARY
    #lightCannyParams
    params.lcMinVal = 100
    params.lcMaxVal = 50
    #lightHoughParams
    params.lhResolutionScale = 1
    params.lhMinCircDist = 1000
    params.lhAccum = 3 #Higher means less circles detected
    #lightGaussianParams
    params.glKernelX = 5
    params.glKernelY = 5
    params.glSigmaX = 0



    img = cv2.imread("test.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(gray)
    length = len(eyes)
    eyeCollection = []
    eyeNum = 0
    eyeCenter = []
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(img,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        eye = img[ey:ey+eh, ex:ex+ew];

        grayeye = cv2.GaussianBlur(cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY),(params.gKernelX,params.gKernelY),params.sigmaX)
        ret, thresh1 = cv2.threshold(grayeye,params.tThresh,params.tMaxVal,params.tType)
        canny = cv2.Canny(thresh1, params.cMinVal, params.cMaxVal)
        circles = cv2.HoughCircles(thresh1,cv2.cv.CV_HOUGH_GRADIENT,params.hResolutionScale,params.hMinCircDist, param1=params.cMinVal, param2=params.hAccum, minRadius=params.hMinRadius)
        try:
            circles = np.uint16(np.around(circles))
        except Exception as e:
            print str(e)
            continue
        try:
            print circles

            for i in circles[0,:]:
                cv2.circle(img,(i[0],i[1]),i[2],(255,0,0),2) #Default circles
                cv2.circle(img,(i[0],i[1]),2,(255,0,0),2) #Default circles
                cv2.circle(canny,(i[0],i[1]),i[2],(255,255,255),1) #Default circles
                cv2.circle(canny,(i[0],i[1]),2,(255,255,255),1) #Default circles

                print i[0]
                testXLeft = copy.deepcopy(i[0]) - int(0.5*i[2])
                testXRight = copy.deepcopy(i[0]) + int(0.5*i[2])
                testY = copy.deepcopy(i[1])
                tempRadius = 0
                for m in range(params.gcIters):

                    while(True):
                        while canny[testY, testXLeft] == 0:
                            #print testX
                            testXLeft = testXLeft - 1;
                        while canny[testY, testXRight] == 0:
                            #print testX
                            testXRight = testXRight + 1;
                        if int((testXRight - testXLeft)/2) > tempRadius:
                            tempRadius = int((testXRight - testXLeft)/2)
                            testY = testY + 1
                        else:
                            break
                    while(True):
                        testY = testY - 1
                        while canny[testY, testXLeft] == 0:
                            #print testX
                            testXLeft = testXLeft - 1;
                        while canny[testY, testXRight] == 0:
                            #print testX
                            testXRight = testXRight + 1;
                        if int((testXRight - testXLeft)/2) > tempRadius:
                            tempRadius = int((testXRight - testXLeft)/2)
                        else:
                            break
                    xpoint = int((testXLeft + testXRight)/2)
                    cv2.circle(canny,(xpoint, testY),tempRadius,(255,255,255),1)
                    # cv2.circle(canny,(testX, testY + m),2,(255,255,255),3)
                    # #print i[0]-i[2]
                    # #print testX + 1
                    # if(i[0]-i[2] != testX + 1 ):
                    #     i[0] = i[0] - int(( i[0] - i[2] - testX - 1)/2)
                    #     i[2] = i[2] - int(( i[0] - i[2] - testX - 1)/2)
                    #
                    # testX = copy.deepcopy(i[0]) + int(0.5*i[2])
                    # testY = copy.deepcopy(i[1])
                    # while canny[testY, testX] == 0:
                    #     #print testX
                    #     testX = testX + 1;
                    # cv2.circle(canny,(testX, testY + m),2,(255,255,255),3)
                    # #print i[0]+i[2]
                    # #print testX - 1
                    # if(i[0]+i[2] != testX - 1 ):
                    #     i[0] = i[0] + int((testX - 1 - i[0] - i[2])/2)
                    #     i[2] = i[2] - int((testX - 1 - i[0] - i[2])/2)
                    cv2.circle(canny,(i[0], i[1]),i[2],(255,255,255),1)
                    cv2.circle(canny,(i[0], i[1]),2,(255,255,255),1)

                cv2.circle(eye,(xpoint,testY),tempRadius,(0,255,0),1)
                cv2.circle(eye,(xpoint, testY),2,(0,0,255),3)
                print i[0]
                eyeCenter.append(i[2]);
                grayeye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
                grayeye = cv2.GaussianBlur(grayeye,(params.glKernelX,params.glKernelY),params.glSigmaX)

                ret, threshLight = cv2.threshold(grayeye,params.ltThresh,params.ltMaxVal,params.ltType)
                cannyLight = cv2.Canny(threshLight, params.lcMinVal, params.lcMaxVal)
                #cv2.imshow('a', cannyLight)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                circles = cv2.HoughCircles(threshLight,cv2.cv.CV_HOUGH_GRADIENT,params.lhResolutionScale,params.lhMinCircDist, param1=params.lcMinVal, param2=params.lhAccum, minRadius=1)
                circles = np.uint16(np.around(circles))

                for j in circles[0,:]:
                    cv2.circle(eye,(j[0],j[1]),2,(255,0,0),3)
        except Exception as e:
             print e
        # cv2.imshow('a',eye)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        eyeCollection.append(copy.deepcopy(thresh1))
        eyeCollection.append(copy.deepcopy(canny))
        eyeCollection.append(copy.deepcopy(eye))
        eyeNum = eyeNum + 3
    return img
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
