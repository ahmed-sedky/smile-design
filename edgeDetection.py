import cv2

# Read the original image
# img = cv2.imread('test/img7.jpg')
# img = cv2.imread('test/IMG_2266.png')
# img = cv2.imread('test/Mostafa_V2.jpg')
# img = cv2.imread('test/photo_2021-12-22_21-52-131.jpg')
img = cv2.imread('test/Anas2.jpg')
# Display original image
# Convert to graycsale
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Blur the image for better edge detection
img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)


# Canny Edge Detection
edges = cv2.Canny(image=img_blur, threshold1=100,
                  threshold2=200)  # Canny Edge Detection
# Display Canny Edge Detection Image
cv2.imwrite('Canny Edge Detection.png', edges)
