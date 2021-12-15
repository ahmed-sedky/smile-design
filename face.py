
from numpy.lib.type_check import imag
import message as Message
import helper as Helper
import cv2
import cv2
import dlib
import numpy as np
from PIL import Image, ImageDraw

import numpy as np

from skimage.io import imread, imshow
from skimage.filters import prewitt_h, prewitt_v

mouthImagePath = "cached/mouth.png"
midlineImagePath = "cached/midline.png"
teethColorImagePath = "cached/teethColor.png"
coloredTeethImagePath = "cached/coloredTeeth.png"


def mouthDetection():
    global mouthPoints
    global mouth_left_x
    global mouth_right_x
    global mouth_center_x
    global mouth_center_y
    global eyes_center_x
    global eyes_center_y
    global img

    img = cv2.imread(Helper.filePath)

    detector = dlib.get_frontal_face_detector()

    predetector = dlib.shape_predictor(
        "setup/shape_predictor_68_face_landmarks.dat")

    dets = detector(img, 1)
    for k, d in enumerate(dets):
        shape = predetector(img, d)
        xmouthpoints = [shape.part(x).x for x in range(60, 68)]
        ymouthpoints = [shape.part(x).y for x in range(60, 68)]

    eyes_center_x = shape.part(27).x
    eyes_center_y = shape.part(27).y
    mouth_center_x = shape.part(62).x
    mouth_center_y = shape.part(62).y
    mouth_left_x = shape.part(48).x
    mouth_right_x = shape.part(54).x

    pts = []
    for i in range(0, 8):
        pts.append([xmouthpoints[i], ymouthpoints[i]])

    mouthPoints = np.array(pts)
    mouthCrop()
    mouthEnhance()


def mouthCrop():
    global mouthPoints

    rect = cv2.boundingRect(mouthPoints)
    x, y, w, h = rect
    croped = img[y: y + h, x: x + w].copy()

    mouthPoints = mouthPoints - mouthPoints.min(axis=0)

    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [mouthPoints], -1, (255, 255, 255), -1, cv2.LINE_AA)

    dst = cv2.bitwise_and(croped, croped, mask=mask)

    cv2.imwrite(mouthImagePath, dst)


def mouthEnhance():
    basewidth = 300
    image = Image.open(mouthImagePath)

    wpercent = basewidth / float(image.size[0])
    hsize = int((float(image.size[1]) * float(wpercent)))

    image = image.resize((basewidth, hsize), Image.ANTIALIAS)
    image.save(mouthImagePath)


def drawMidline(self):
    global results

    ratio = int(mouth_right_x - int(mouth_left_x))
    ratio = int(ratio / 6)

    midline = []
    final_midlines = []
    shiftFlag = True
    img = cv2.imread(Helper.filePath)
    image = cv2.line(
        img,
        (eyes_center_x, eyes_center_y - 150),
        (eyes_center_x, eyes_center_y + 400),
        color=(255, 255, 255),
        thickness=2,
    )
    for i in range(-1 * ratio, ratio):
        bgr = np.array(image[mouth_center_y][mouth_center_x + i])
        midline.append([bgr[0], mouth_center_x + i])

    midline.sort()

    for idx, x in enumerate(midline):
        for elem in midline[idx + 1:]:
            if (elem[1] < x[1] + 10) and (elem[1] > x[1] - 10):
                midline.remove(elem)

    for i in range(0, 2):
        if abs(midline[i][1] - eyes_center_x) < 4:
            final_midlines.clear()
            shiftFlag = False
            break
        final_midlines.append(midline[i])

    for x in final_midlines:
        image = cv2.line(
            img,
            (x[1], mouth_center_y - 200),
            (x[1], mouth_center_y + 100),
            color=(0, 0, 255),
            thickness=2,
        )

    if shiftFlag:
        results += "A midline shift found\n"
    else:
        results += "Facial and Dental midline are almost identical. No shift found\n"

    cv2.imwrite(midlineImagePath, image)


def checkMidline(self):
    drawMidline(self)
    Helper.plotImage(self, midlineImagePath)


def checkDiscoloration(self):
    global results

    image = cv2.imread(mouthImagePath)

    minBGR = np.array([120, 140, 140])
    maxBGR = np.array([255, 255, 255])

    maskBGR = cv2.inRange(image, minBGR, maxBGR)
    resultBGR = cv2.bitwise_and(image, image, mask=maskBGR)
    # cv2.imshow("Masked Image",resultBGR)
    yellowCount = 0
    blackCount = 0
    count = 0
    cleanArr = []
    rows, cols, _ = image.shape
    for i in range(rows):
        for j in range(cols):
            pixel = resultBGR[i, j]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                blackCount += 1
            else:
                cleanArr.append(pixel)
                if pixel[0] < 180:
                    yellowCount += 1
    std = np.std(cleanArr)

    # print(np.mean(cleanArr, axis=0))
    upper = np.mean(cleanArr, axis=0) + std
    # print(upper)
    lower = np.mean(cleanArr, axis=0) - std
    # print(lower)
    index = 0
    for pixel in cleanArr:
        if (
            (pixel[0] < lower[0] or pixel[0] > upper[0])
            and (pixel[1] < lower[1] or pixel[1] > upper[1])
            and (pixel[2] < lower[2] or pixel[2] > upper[2])
        ):
            cleanArr.pop(index)
            count += 1
        index += 1

    # print(np.median(cleanArr, axis=0))
    # print(np.mean(cleanArr, axis=0))
    # print(blackCount, rows*cols)
    mean = np.mean(cleanArr, axis=0)
    createTeethColorImage((int(mean[2]), int(mean[1]), int(mean[0])))
    ratio = yellowCount / ((rows * cols) - blackCount)

    # print(ratio)
    # print(count)
    # print(yellowCount)
    # print(((rows * cols) - blackCount))

    if ratio > 0.5:
        results += "There is a discoloration\n"
    else:
        results += "There is no discoloration\n"
    self.colorsWidget.setVisible(True)
    Helper.plotTeethColor(self)


def checkGummySmile(self):
    global results
    image = cv2.imread(mouthImagePath)

    # cv2.imshow("Masked Image",resultBGR)
    redCount = 0
    blackCount = 0
    rows, cols, _ = image.shape
    for i in range(rows):
        for j in range(cols):
            pixel = image[i, j]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                blackCount += 1
            else:
                if pixel[0] < 150 and pixel[1] < 150 and pixel[2] > 200:
                    redCount += 1

    ratio = redCount / ((rows * cols) - blackCount)

    # print(ratio)
    # print(((rows * cols) - blackCount))
    # print(redCount)
    # print(((rows * cols) - blackCount))

    if ratio > 0.05:
        results += "There is a gummy smile"
    else:
        results += "There is no gummy smile"
    self.colorsWidget.setVisible(True)
    Helper.plotTeethColor(self)


def createTeethColorImage(rgb):
    w, h = 55, 55
    shape = [(0, 0), (w, h)]
    img = Image.new("RGB", (w, h))

    img1 = ImageDraw.Draw(img)
    img1.rectangle(shape, fill=rgb)
    img.save(teethColorImagePath)


def teethColoring(self):
    image = cv2.imread(mouthImagePath)
    
    if results.find("There is no gummy smile")==-1:
        minBGR = np.array([140, 170, 140])  # 120,140,140 (#140, 170, 140 for gummy smile)
        maxBGR = np.array([255, 255, 248])  # 255, 255, 248 for gummy smile
    else:
        minBGR = np.array([140, 140, 140])  
        maxBGR = np.array([255, 255, 255])     
    mask = cv2.inRange(image, minBGR, maxBGR)
    #  invert mask
    # cv2.imwrite("mask.jpg", mask)

    mask = 255 - mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    result = image.copy()
    result[mask == 0] = (205, 219, 225)
    cv2.imwrite(coloredTeethImagePath, result)
    # cv2.imshow("result", result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def checkAll(self):
    global results
    results = ""
    checkDiscoloration(self)
    # checkMidline(self)
    checkGummySmile(self)
    teethColoring(self)
    Message.info(self, results)
