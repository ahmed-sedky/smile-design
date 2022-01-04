import message as Message
import helper as Helper
import cv2
import cv2
import dlib
import numpy as np
from PIL import Image, ImageDraw
from PyQt5 import QtCore

import numpy as np

from skimage.io import imread, imshow
from skimage.filters import prewitt_h, prewitt_v

mouthImagePath = "cached/mouth.png"
finalImagePath = "cached/final.png"
teethColorImagePath = "cached/teethColor.png"
coloredTeethImagePath = "cached/coloredTeeth.png"
templatePath = {"Square": "cached/square.png","Rectangle": "cached/rectangle.png","Triangle": "cached/triangle.png","Oval": "cached/oval.png"}
imagePath = "cached/image.png"
imagePath2 = "cached/diastema.png"
templateImagePath = "cached/template.png"


def mouthDetection():
    global mouthPoints
    global mouth_left_x
    global mouth_right_x
    global mouth_center_x
    global mouth_center_y
    global mouth_center_y2
    global mouth_center_y3
    global eyes_center_x
    global eyes_center_y
    global img
    global mouth_center_y3

    img = cv2.imread(Helper.filePath)
    detector = dlib.get_frontal_face_detector()

    predetector = dlib.shape_predictor("setup/data.dat")

    dets = detector(img, 1)
    for k, d in enumerate(dets):
        shape = predetector(img, d)
        xmouthpoints = [shape.part(x).x for x in range(60, 68)]
        ymouthpoints = [shape.part(x).y for x in range(60, 68)]

    eyes_center_x = shape.part(27).x
    eyes_center_y = shape.part(27).y
    mouth_center_x = shape.part(62).x
    mouth_center_y = int((shape.part(66).y - shape.part(62).y) / 2) + shape.part(62).y
    mouth_center_y2 = shape.part(62).y
    mouth_center_y3 = shape.part(66).y
    mouth_left_x = shape.part(48).x
    mouth_right_x = shape.part(54).x
    mouth_center_y3 = shape.part(66).y

    pts = []
    for i in range(0, 8):
        pts.append([xmouthpoints[i], ymouthpoints[i]])

    mouthPoints = np.array(pts)
    mouthCrop()
    cv2.imwrite(imagePath, img)


def mouthCrop():
    global mouthPoints
    global x
    global y
    global h
    global w

    rect = cv2.boundingRect(mouthPoints)
    x, y, w, h = rect
    croped = img[y : y + h, x : x + w].copy()

    mouthPoints = mouthPoints - mouthPoints.min(axis=0)

    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [mouthPoints], -1, (255, 255, 255), -1, cv2.LINE_AA)

    dst = cv2.bitwise_and(croped, croped, mask=mask)

    cv2.imwrite(mouthImagePath, dst)


def checkMidline():
    global results
    global incisor_width
    global final_midline
    global incisors_lower_edge

    ratio = int(mouth_right_x - int(mouth_left_x))
    ratio = int(ratio / 6)

    midline = []
    final_midlines = []
    shiftFlag = True
    img = cv2.imread(imagePath)
    
    for i in range(-1 * ratio, ratio):
        bgr = np.array(img[mouth_center_y][mouth_center_x + i])
        midline.append([bgr[0], mouth_center_x + i])
        # cv2.circle(img,(mouth_center_x + i,mouth_center_y), 1 ,(0,255,0),-1)

    midline.sort()

    for idx, x in enumerate(midline):
        for elem in midline[idx + 1 :]:
            if (elem[1] < x[1] + 10) and (elem[1] > x[1] - 10):
                midline.remove(elem)
    for i in range(0, 3):
        final_midlines.append(midline[i])
    final_midlines.sort(key=lambda x: x[1])

    distances = []
    for i in range(1, 3):
        distances.append(abs(final_midlines[i][1] - final_midlines[i - 1][1]))

    incisor_width = 0
    if abs(distances[0] - distances[1]) <= 5:
        incisor_width = distances[0]
        final_midline = final_midlines[1][1]
    elif distances[0] > distances[1]:
        final_midline = final_midlines[0][1]
        incisor_width = distances[0]
    else:
        final_midline = final_midlines[2][1]
        incisor_width = distances[1]

    if abs(final_midline - eyes_center_x) <= 8:
        shiftFlag = False
    else:
        shiftFlag = True

    if shiftFlag:
        results += "A midline shift found\n"
    else:
        results += "Facial and Dental midline are almost identical. No shift found\n"

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Blur the image for better edge detection
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
    # Canny Edge Detection
    edges = cv2.Canny(
        image=img_blur, threshold1=100, threshold2=200
    )  # Canny Edge Detection
    pixel = edges[mouth_center_y][final_midline + int(incisor_width / 2)]

    up = 0
    while int(pixel) == 0:
        up += 1
        pixel = edges[mouth_center_y + up][final_midline + int(incisor_width / 2)]

    incisors_lower_edge = mouth_center_y + up - int(1.25 * incisor_width)
    global incisor 
    incisor=  mouth_center_y + up
    #cv2.imwrite(midlineImagePath, image)


def templateMatching(shape):
    im1 = Image.open(imagePath)
    im2 = Image.open(templatePath[shape])
    
    mouth_width = mouth_right_x - mouth_left_x
    im2 = im2.resize((int (mouth_width*0.8), int(1.25 * incisor_width)))  # 50
    im2.save(templateImagePath)
    offset = QtCore.QPointF(final_midline - int(im2.size[0]) / 2,incisors_lower_edge)
    return Helper.createPixmapItem(templateImagePath, im2.size, offset)
    # im1.paste(im2, (final_midline - int(im2.size[0] / 2),
    #             incisors_lower_edge), im2)
    # im1.save(finalImagePath, quality=95)


def checkDiscoloration(self):
    global results
    global mean
    minBGR = np.array([120, 140, 140])
    maxBGR = np.array([255, 255, 255])

    maskBGR = cv2.inRange(mouthImage, minBGR, maxBGR)
    resultBGR = cv2.bitwise_and(mouthImage, mouthImage, mask=maskBGR)
    # cv2.imshow("Masked mouthImage",resultBGR)
    # cv2.imshow("Masked mouthImage",resultBGR)
    yellowCount = 0
    blackCount = 0
    count = 0
    cleanArr = []
    rows, cols, _ = mouthImage.shape
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

    upper = np.mean(cleanArr, axis=0) + std
    lower = np.mean(cleanArr, axis=0) - std

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
    mean = np.mean(cleanArr, axis=0)

    matchTeethColor(self, mean)

    createTeethColorImage((int(mean[2]), int(mean[1]), int(mean[0])))
    ratio = yellowCount / ((rows * cols) - blackCount)

    if ratio > 0.5:
        results += "There is a discoloration\n"
        Helper.enableTeethColoration(self)
    else:
        results += "There is no discoloration\n"
        Helper.disableTeethColoration(self)
    Helper.plotTeethColor(self)


def checkGummySmile():
    global results
    global mouthImage

    mouthImage = cv2.imread(mouthImagePath)
    # cv2.imshow("Masked Image", image)
    redCount = 0
    blackCount = 0
    rows, cols, _ = mouthImage.shape
    for i in range(rows):
        for j in range(cols):
            pixel = mouthImage[i, j]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                blackCount += 1
            else:
                if pixel[0] < 150 and pixel[1] < 150 and pixel[2] > 200:
                    redCount += 1

    ratio = redCount / ((rows * cols) - blackCount)
    global gummy_smile
    if ratio > 0.07: 
        results += "There is a gummy smile\n"
        gummy_smile = True
    else:
        results += "There is no gummy smile\n"
        gummy_smile = False


def createTeethColorImage(rgb):
    w, h = 55, 55
    shape = [(0, 0), (w, h)]
    img2 = Image.new("RGB", (w, h))

    img1 = ImageDraw.Draw(img2)
    img1.rectangle(shape, fill=rgb)
    img2.save(teethColorImagePath)


def teethColoring(text):
    global img

    img = cv2.imread(imagePath)
    if results.find("There is no gummy smile") == -1:
        # 120,140,140 (#140, 170, 140 for gummy smile)
        minBGR = np.array([50, 180, 30])  # ([100, 180, 100])
        maxBGR = np.array([255, 255, 248])  # 255, 255, 248 for gummy smile
    else:
        minBGR = np.array([50, 140, 30])  # ([100, 140, 100)
        maxBGR = np.array([255, 255, 255])
    mask2 = cv2.inRange(mouthImage, minBGR, maxBGR)

    low_red = np.array([84, 155, 161])  # ([161, 155, 84])
    high_red = np.array([255, 255, 179])  # ([179, 255, 255])
    mask0 = cv2.inRange(mouthImage, low_red, high_red)

    # join my masks
    mask = mask2 - mask0

    mask = 255 - mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    result = mouthImage.copy()

    newColor = ()
    if text == "A1":
        newColor = (220, 220, 220)
    elif text == "B1":
        newColor = (205, 219, 255)

    result[mask == 0] = newColor
    cv2.imwrite(coloredTeethImagePath, result)

    for i in range(len(result)):
        for j in range(len(result[0])):
            pixel = np.array(result[i][j])
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                continue
            pixel2 = np.array(img[y + i][x + j])
            flag = False
            for k in range(3):
                if pixel[k] != pixel2[k]:
                    flag = True
                    break
            if flag:
                img[y + i][x + j] = result[i][j]

    cv2.imwrite(finalImagePath, img)


def checkDiastema():
    global results
    global img
    global incisor

    
    img5 = cv2.imread(Helper.filePath , 0)
    img6 = img5
    gap = 0
    row=0
    for i in range(0, 10):
        if gummy_smile:
            for j in range(-5,5):
               pixel_color = np.array(img6[mouth_center_y2 + 16 + i][mouth_center_x + j])
             
               if mouth_center_y2 + 16 + i > incisor:
                   break
               #cv2.circle(img6,(mouth_center_x + j,mouth_center_y2 + 16 + i), 1 ,(0,0,255),-1)
               if pixel_color < 120:
                  gap += 1
            if gap > 2 :
                row +=1
                gap=0

        else:
            for j in range(-5,5):
               pixel_color = np.array(img6[mouth_center_y2 + int((mouth_center_y3-mouth_center_y2 ) /4) + i ][mouth_center_x + j])
               if mouth_center_y2 + int((mouth_center_y3-mouth_center_y2 ) /4) + i > incisor:
                   break
               print(pixel_color)
               #cv2.circle(img6,(mouth_center_x + j , mouth_center_y2 + 10 + i), 1 ,(0,0,255),-1)
            # and pixel_color[1]<=120 and pixel_color[2]<=120:
               if pixel_color < 120:
                 #or (#pixel_color[0] < 150 #and pixel_color[1] < 150 and pixel_color[2] > 200#):
                 gap += 1
            #print(gap)
            if gap > 2 :
                row +=1
                gap=0

    
        #print(pixel_color)
    print(row)

    if row > 2 :
        results += "There is a diastema"
    else:
        results += "There is no diastema"
    cv2.imwrite(imagePath2, img6)


def matchTeethColor(self, teeth_mean):
    global results
    """ parameters: BGR color array"""
    # Vita Classical color palette BGR Values
    BGR_palette_values = [
        (169, 207, 222),
        (149, 197, 231),
        (128, 186, 219),
        (130, 186, 217),
        (121, 166, 210),
        (169, 212, 218),
        (149, 203, 220),
        (113, 190, 221),
        (113, 179, 213),
        (143, 198, 216),
        (133, 193, 211),
        (120, 174, 203),
        (107, 156, 198),
        (146, 196, 221),
        (130, 184, 214),
        (110, 186, 212),
    ]

    shades_map = {
        0: "A1",
        1: "A2",
        2: "A3",
        3: "A3.5",
        4: "A4",
        5: "B1",
        6: "B2",
        7: "B3",
        8: "B4",
        9: "C1",
        10: "C2",
        11: "C3",
        12: "C4",
        13: "D2",
        14: "D3",
        15: "D4",
    }
    index = 0
    result = 1000
    similarity = 0

    for idx, color in enumerate(BGR_palette_values):
        mean_avg = np.mean(teeth_mean)
        color_avg = np.mean(color)
        subtraction = abs(mean_avg - color_avg)

        if subtraction < result:
            result = subtraction
            index = idx
            similarity = 100 - (100 * (result / mean_avg))
            similarity = round(similarity, 2)
            # print(
            #     f"difference: {result} ,index: {idx}, percentage: {similarity}")

    color_shade = shades_map.get(index)
    # print(f"Closest shade: ({color_shade}) with similarity = {similarity}%")
    results += f"Closest shade: ({color_shade}) with similarity = {similarity}%\n"


def checkAll(self):
    global results

    results = ""
    checkGummySmile()
    checkDiscoloration(self)
    checkMidline()
    checkDiastema()
    Helper.plotImageAfter(self, imagePath)
    showResults(self)


def showResults(self):
    Message.info(self, results)