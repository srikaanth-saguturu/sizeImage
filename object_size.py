# USAGE
# python object_size.py --image images/example_01.png --width 0.955
# python object_size.py --image images/example_02.png --width 0.955
# python object_size.py --image images/example_03.png --width 3.5

# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import numpy as np
import argparse
import imutils
import cv2
import os
import base64
import json

app = Flask(__name__)
api = Api(app)
#app.config["DEBUG"] = true
#@app.route('/imageSizeApi', methods=['POST'])

class imageSizeApi(Resource):
    
	def midpoint(ptA, ptB):
		return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

	def post(self):
		###path = r"C:\Srikaanth\Container Crush\sizeImage-master\sizeImage-master\images\example.png"
		#r"Object-s-Size-measurement-in-an-image-using-openCV4.0-and-imutils-master\images\example.png"
		#width = request.json['width']
		width = request.form['width']
		###width = 5
		imageString = base64.b64decode(request.form['img'])     
		nparr = np.fromstring(imageString, np.uint8)
		image = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR);
		#image = cv2.imread(os.path.join(path,"example.png")
		###image = cv2.imread(path) 
		json_def = {"responseCode" : "", "responseMessage" : "", "itemDimension" : "", "dimension" : []}
		counter = 0        
#Get the parameters via API
# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--image", required=True,
	#help="path to the input image")
#ap.add_argument("-w", "--width", type=float, required=True,
	#help="width of the left-most object in the image (in inches)")
#args = vars(ap.parse_args())

# load the image, convert it to grayscale, and blur it slightly
	#image = cv2.imread(args["image"])
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges
		edged = cv2.Canny(gray, 50, 100)
		edged = cv2.dilate(edged, None, iterations=1)
		edged = cv2.erode(edged, None, iterations=1)

# find contours in the edge map
		cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)

# sort the contours from left-to-right and initialize the
# 'pixels per metric' calibration variable
		(cnts, _) = contours.sort_contours(cnts)
		pixelsPerMetric = None

# loop over the contours individually
		for c in cnts:
	# if the contour is not sufficiently large, ignore it
			if cv2.contourArea(c) < 100:
				continue

	# compute the rotated bounding box of the contour
			orig = image.copy()
			box = cv2.minAreaRect(c)
			box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
			box = np.array(box, dtype="int")

	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
			box = perspective.order_points(box)
			cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

	# loop over the original points and draw them
			for (x, y) in box:
				cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
			(tl, tr, br, bl) = box
			(tltrX, tltrY) = imageSizeApi.midpoint(tl, tr)
			(blbrX, blbrY) = imageSizeApi.midpoint(bl, br)

	# compute the midpoint between the top-left and top-right points,
	# followed by the midpoint between the top-righ and bottom-right
			(tlblX, tlblY) = imageSizeApi.midpoint(tl, bl)
			(trbrX, trbrY) = imageSizeApi.midpoint(tr, br)

	# draw the midpoints on the image
			cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
			cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
			cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
			cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

	# draw lines between the midpoints
			cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
				(255, 0, 255), 2)
			cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
				(255, 0, 255), 2)

	# compute the Euclidean distance between the midpoints
			dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
			dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

	# if the pixels per metric has not been initialized, then
	# compute it as the ratio of pixels to supplied metric
	# (in this case, inches)
			if pixelsPerMetric is None:
				#pixelsPerMetric = dB / args["width"]
				pixelsPerMetric = dB / int(width)

	# compute the size of the object
			dimA = dA / pixelsPerMetric
			dimB = dB / pixelsPerMetric

	# commenting Mani   
	# draw the object sizes on the image
	#cv2.putText(orig, "{:.1f}in".format(dimA),
		#(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
		#0.65, (255, 255, 255), 2)
	#cv2.putText(orig, "{:.1f}in".format(dimB),
		#(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
		#0.65, (255, 255, 255), 2)

	# show the output image
	#cv2.imshow("Image", orig)
	#cv2.waitKey(0)
	# commenting Mani   
			print("Length:",dimA,"Width:",dimB)  
			counter = counter + 1 
			if (counter==2):        
				json_def["itemDimension"] = {"length" : dimA, "width" : dimB}   
			json_def["dimension"].append({"length" : dimA, "width" : dimB})              
		#return {'length': dimA, 'width': dimB}
		if (0<=counter<=1):
			json_def["responseCode"] = 10  
			json_def["responseMessage"] = "No Objects detected"
		elif counter>=3:
			json_def["responseCode"] = 20 
			json_def["responseMessage"] = "More than 2 objects detected"
		else:
			json_def["responseCode"] = 0 
			json_def["responseMessage"] = "Successful"
   
		print(json_def)
		#return json.dumps(json_def)
		return jsonify(json_def)
    
api.add_resource(imageSizeApi, '/imageSizeApi') # API Path

if __name__ == '__main__':
     app.run(port='5005')
