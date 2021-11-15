import os
import io
import cv2
from google.cloud import vision
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter

import numpy as np

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"ServiceAccountToken.json"

client = vision.ImageAnnotatorClient()

file_name = "Dental-Implants-All-on-4-Before-and-After.jpg"
image_path = f".\{file_name}"

img = Image.open(image_path)
with io.open(image_path, "rb") as image_file:
    content = image_file.read()

image = vision.Image(content=content)
response = client.face_detection(image=image)
faceAnnotations = response.face_annotations

upper_lip_index = 8
mouth_left_index = 10
lower_lip_index = 9
mouth_right_index = 11

for face in faceAnnotations:
    left = face.landmarks[mouth_left_index].position.x
    top = face.landmarks[upper_lip_index].position.y
    right = face.landmarks[mouth_right_index].position.x
    bottom = face.landmarks[lower_lip_index].position.y

    image_res = img.crop((left, top, right, bottom)) #image.crop((left, top, right, bottom))
    image_smooth = image_res.filter(ImageFilter.SMOOTH_MORE)

image_smooth.save(f"mouth.png")
image = cv2.imread('mouth.png', cv2.IMREAD_UNCHANGED)

scale_percent = 500  # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)

# resize image

# resized_image = cv2.resize(image, (100, 50)) 
# set the base width of the result
basewidth = 300
image = Image.open('mouth.png')
# determining the height ratio
wpercent = (basewidth/float(image.size[0]))
hsize = int((float(image.size[1])*float(wpercent)))
# resize image and save
image = image.resize((basewidth,hsize), Image.ANTIALIAS)
image.save('mouth_resized.png') 

resized2 = cv2.resize(image, dim, interpolation=cv2.INTER_NEAREST)

cv2.imwrite("mouth_resized.png", resized2)


image = cv2.imread("mouth_resized.png")


# 216 ,248 ,243 rgb(171, 158, 115) // 162, 148, 122 // 226, 195, 168
bgr = [216, 248, 243]
threshr = 70  # 70
threshg = 70
threshb = 70

minBGR = np.array([bgr[0] - threshb, bgr[1] - threshg, bgr[2] - threshr])
maxBGR = np.array([bgr[0] + threshb, bgr[1] + threshg, bgr[2] + threshr])

maskBGR = cv2.inRange(image, minBGR, maxBGR)
resultBGR = cv2.bitwise_and(image, image, mask=maskBGR)


kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
opened_mask = cv2.morphologyEx(maskBGR, cv2.MORPH_OPEN, kernel)
masked_img = cv2.bitwise_and(resultBGR, resultBGR, mask=opened_mask)

# check only
thresh = 40
min_col = np.array([bgr[0] - thresh, bgr[1] - thresh, bgr[2] - thresh])
max_col = np.array([bgr[0] + thresh, bgr[1] + thresh, bgr[2] + thresh])
check_img = cv2.inRange(image, min_col, max_col)
resultBGR2 = cv2.bitwise_and(image, image, mask=check_img)

count = 0
countb = 0
rows, cols, _ = image.shape
x = 0
# for pixel in resultBGR[0:rows, 0:cols]:
#     # print (pixel)
#     x +=1
# print (x)
# print (len(resultBGR) ,len(resultBGR[0]))

for i in range(rows):
    for j in range(cols):
        k = resultBGR[i, j]
        if k[0] == 0 and k[1] == 0 and k[2] == 0:
            countb += 1
        elif k[0] < 230 and k[1] < 230 and k[2] < 230:
            count += 1

ratio = count / ((rows * cols) - countb)
print(f"{ratio*100}%")
print(count)
print((rows * cols) - countb)
if (ratio > 0.5):
    print("There Is Discoloration")
else:
    print("There Is No Discoloration")