from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
import numpy as np
import urllib
import json
import cv2
import os
import copy
from os import listdir
from os.path import isfile, join
import math
import base64
import subprocess
from math import pi, sqrt, exp
import time

# define the path to the face detector
EYE_DETECTOR_PATH = "{base_path}/haarcascade_eye.xml".format(
	base_path=os.path.abspath(os.path.dirname(__file__)))

@csrf_exempt
def detect(request):
	username = request.POST.get("username", None)
	print(username)
	# check to see if this is a post request
	if request.method == "POST":
		# check to see if an image was uploaded
		if request.FILES.get("image", None) is not None:
			# grab the uploaded image
			image = _grab_image(stream=request.FILES["image"])

		# otherwise, assume that a URL was passed in
		else:
			# grab the URL from the request
			url = request.POST.get("url", None)
			image = _grab_image(url=url)

		ret = analyze(image)
		data = ret[0]
		image_base64 = ret[1]
        print(data)
        print(image_base64)
        return HttpResponse("Success", content_type="text/plain")


def _grab_image(path=None, stream=None, url=None):
	# if the path is not None, then load the image from disk
	if path is not None:
		image = cv2.imread(path)

	# otherwise, the image does not reside on disk
	else:
		# if the URL is not None, then download the image
		if url is not None:
			resp = urllib.urlopen(url)
			data = resp.read()

		# if the stream is not None, then the image has been uploaded
		elif stream is not None:
			print("image data found")
			data = stream.read()

		if stream is None:
			print("no data found")

		# convert the image to a NumPy array and then read it into
		# OpenCV format
		image = np.asarray(bytearray(data), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)

	# return the image
	return image

class Object(object):
	pass

def analyze(img):

	start_time = time.time()
	eye_cascade = cv2.CascadeClassifier(EYE_DETECTOR_PATH)

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
	params.lhAccum = 3
	#lightGaussianParams
	params.glKernelX = 5
	params.glKernelY = 5
	params.glSigmaX = 0

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	eyes = eye_cascade.detectMultiScale(gray)
	length = len(eyes)
	eyeCollection = []
	eyeNum = 0
	outString = ""
	eyeCenter = []

	for (ex,ey,ew,eh) in eyes:
		eyeNum = eyeNum + 1
		cv2.rectangle(img,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
		eye = img[ey:ey+eh, ex:ex+ew];

		grayeye = cv2.GaussianBlur(cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY),(params.gKernelX,params.gKernelY),params.sigmaX)
		ret, thresh1 = cv2.threshold(grayeye,params.tThresh,params.tMaxVal,params.tType)
		canny = cv2.Canny(thresh1, params.cMinVal, params.cMaxVal)


		try:
			cv2.imwrite(join(imageOutputPath, imageSource) + str(eyeNum) + ".jpg", grayeye)
			circParam = thresh(join(imageOutputPath, imageSource) + str(eyeNum) + ".jpg", 30, 100)
			cv2.circle(eye,(circParam[1],circParam[0]),circParam[2],(255,0,0),1)
			cv2.circle(eye,(circParam[1],circParam[0]),1,(255,0,0),2)
			lightReflexEyeO = grayeye[circParam[0] - circParam[2]:circParam[0]+circParam[2], circParam[1] - circParam[2]:circParam[1]+circParam[2]]
			lightReflexEye = cv2.GaussianBlur(lightReflexEyeO,(params.glKernelX,params.glKernelY),params.glSigmaX)
			ret, threshLight = cv2.threshold(lightReflexEye,params.ltThresh,params.ltMaxVal,params.ltType)
			cannyLight = cv2.Canny(threshLight, params.lcMinVal, params.lcMaxVal)
			circles = cv2.HoughCircles(threshLight,cv2.cv.CV_HOUGH_GRADIENT,params.lhResolutionScale,params.lhMinCircDist, param1=params.lcMinVal, param2=params.lhAccum, minRadius=1)
			circles = np.uint16(np.around(circles))
			for j in circles[0,:]:
				cv2.circle(lightReflexEyeO,(j[0],j[1]),1,(0,0,0),1)
				cv2.circle(eye,(circParam[1] - circParam[2] + j[0], circParam[0] - circParam[2] + j[1]),1,(0,0,255),2)
				outString = outString + '{Light reflex parameters: ' + str(circParam[1] - circParam[2] + j[0]) + ' ' + str(circParam[0] - circParam[2] + j[1]) + "},"
			outString = outString + '{Iris parameters: ' + str(circParam[1]) + ' ' + str(circParam[0]) + ' '  + str(circParam[2]) + "},"
			outString = outString +  '{Distance: ' + str(((circParam[1]- (circParam[1] - circParam[2] + j[0]))**2 + (circParam[0] - (circParam[0] - circParam[2] + j[1]))**2)**0.5) + "},"
			outString = outString +  '{Angle: ' + str(math.atan2((circParam[0] - (circParam[0] - circParam[2] + j[1])),(circParam[1]- (circParam[1] - circParam[2] + j[0]))) * 180 / 3.14) + "},"

		except Exception as e:
			print e

	png = cv2.imencode('.png', img)[1]
	jpeg_base64 = base64.encodestring(png)

	elapsedTime = time.time() - start_time
	outString = outString +  '{Total Elapsed Time: ' + str(elapsedTime) + "}"
	return [outString, jpeg_base64]
