import message as Message
import helper as Helper
import os
import io
import cv2
from google.cloud import vision
from PIL import Image, ImageFilter,ImageDraw,ImageQt

import numpy as np

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"setup/config.json"
mouthImagePath = "cached/mouth.png"
midlineImagePath = "cached/midline.png"
teethColorImagePath = "cached/teethColor.png"


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
    eyes_center_index = 6
    mouth_center_index = 12

    left = face.landmarks[mouth_left_index].position.x
    top = face.landmarks[upper_lip_index].position.y
    right = face.landmarks[mouth_right_index].position.x
    bottom = face.landmarks[lower_lip_index].position.y

    mouth_x = int(face.landmarks[mouth_center_index].position.x)
    mouth_y = int(face.landmarks[mouth_center_index].position.y)
    eyes_x = int(face.landmarks[eyes_center_index].position.x)
    eyes_y = int(face.landmarks[eyes_center_index].position.y)
    
    drawMidline(imagePath,mouth_x,mouth_y,eyes_x,eyes_y)
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

def drawMidline(imagePath,mouth_x,mouth_y,eyes_x,eyes_y):
    midline = []
    img = cv2.imread(imagePath)
    image = cv2.line(img, (eyes_x, eyes_y-150),
                     (eyes_x, eyes_y+400), color=(255, 255, 255), thickness=2)
    for i in range(-18, 18):
        bgr = np.array(image[mouth_y][mouth_x+i])
        midline.append([bgr[0], mouth_x+i])
    midline.sort()
    image = cv2.line(img, (midline[0][1], mouth_y-200),
                     (midline[0][1], mouth_y+100), color=(0, 0, 255), thickness=2)
    image = cv2.line(img, (midline[1][1], mouth_y-200),
                     (midline[1][1], mouth_y+100), color=(0, 0, 255), thickness=2)
    cv2.imwrite(midlineImagePath, image)

def checkMidline(self):
    Helper.plotImage(self,midlineImagePath)

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
    createTeethColorImage((255,0,0))
    Helper.plotTeethColor(self)
    self.palette.setVisible(True)
    Message.info(self, discolorationResult)
    
def createTeethColorImage(rgb):
    w, h = 50, 50
    shape = [(0, 0), (w , h)]
    img = Image.new("RGB", (w, h))

    img1 = ImageDraw.Draw(img)
    img1.rectangle(shape, fill=rgb)
    img.save(teethColorImagePath)

