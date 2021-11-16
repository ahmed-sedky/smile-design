import message as Message
import os
import io
import cv2
from google.cloud import vision
from PIL import Image
from PIL import ImageFilter

import numpy as np

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"setup/config.json"
mouthImagePath = "cached/mouth.png"


def mouthDetection(imagePath):
    client = vision.ImageAnnotatorClient()

    with io.open(imagePath, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.face_detection(image=image)
    face = response.face_annotations[0]

    upper_lip_index = 8
    mouth_left_index = 10
    lower_lip_index = 9
    mouth_right_index = 11

    left = face.landmarks[mouth_left_index].position.x
    top = face.landmarks[upper_lip_index].position.y
    right = face.landmarks[mouth_right_index].position.x
    bottom = face.landmarks[lower_lip_index].position.y

    mouthCrop(imagePath, (left, top, right, bottom))
    mouthEnhance()


def mouthCrop(imagePath, area):
    image = Image.open(imagePath).crop(area).filter(ImageFilter.SMOOTH_MORE)

    if not os.path.exists("cached"):
        os.makedirs("cached")
    image.save(mouthImagePath)


def mouthEnhance():
    basewidth = 300
    image = Image.open(mouthImagePath)

    wpercent = basewidth / float(image.size[0])
    hsize = int((float(image.size[1]) * float(wpercent)))

    image = image.resize((basewidth, hsize), Image.ANTIALIAS)
    image.save(mouthImagePath)


def checkDiscoloration(self):
    image = cv2.imread(mouthImagePath)

    bgr = [216, 248, 243]
    threshold = 70

    minBGR = np.array([bgr[0] - threshold, bgr[1] - threshold, bgr[2] - threshold])
    maxBGR = np.array([bgr[0] + threshold, bgr[1] + threshold, bgr[2] + threshold])

    maskBGR = cv2.inRange(image, minBGR, maxBGR)
    resultBGR = cv2.bitwise_and(image, image, mask=maskBGR)

    yellowCount = 0
    blackCount = 0
    rows, cols, _ = image.shape
    for i in range(rows):
        for j in range(cols):
            pixel = resultBGR[i, j]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                blackCount += 1
            elif pixel[0] < 180:
                yellowCount += 1

    ratio = yellowCount / ((rows * cols) - blackCount)

    # print(ratio)
    # print(yellowCount)
    # print(((rows * cols) - blackCount))

    discolorationResult = ""
    if ratio > 0.5:
        discolorationResult = "There is discoloration"
    else:
        discolorationResult = "There is no discoloration"
    Message.info(self, discolorationResult)