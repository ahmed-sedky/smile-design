import numpy as np
import cv2
# python
image = cv2.imread(
    'D:/4th year first term/BioMetrics/tasks/task1/images/WhatsApp Image 2021-11-01 at 6.17.46 PM.jpeg')


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
print(ratio)
print(count)
print((rows * cols) - countb)
if (ratio > 0.5):
    print("There Is Discoloration")
else:
    print("There Is No Discoloration")
# cv2.imshow('BGR image', masked_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# cv2.waitKey(1)
