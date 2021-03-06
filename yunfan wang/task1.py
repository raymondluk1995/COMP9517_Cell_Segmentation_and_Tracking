import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

path = "./data/Fluo-N2DL-HeLa/Sequence 5"

file_lst = []
os.chdir(path)
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if name.endswith("tif"):
            file_lst.append(os.path.join(root, name))
if not os.path.exists("mask"):
    os.mkdir("mask")
if not os.path.exists("tracking"):
    os.mkdir("tracking")


def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def process_2(img_path):
    ### pre-processing
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    print(img_path)
    # plt.figure('test1')
    # plt.imshow(img, cmap='gray')
    # plt.axis('off')
    # plt.title('test1')
    # plt.show()

    kernel = 11
    img = cv2.GaussianBlur(img, (kernel, kernel), 0)
    hist, bins = np.histogram(img.flatten(), 256, [0, 256])
    th = np.where(hist == np.max(hist))
    ret, thresh = cv2.threshold(img, th[0] + 1, 255, cv2.THRESH_BINARY)
    thresh = cv2.erode(thresh, np.ones((9, 9)))
    thresh = cv2.dilate(thresh, np.ones((9, 9)))
    # plt.imshow(thresh, cmap='gray')
    # plt.axis('off')
    # plt.show()

    thresh, contours, hirearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    original = cv2.imread(img_path, 1)

    # plt.imshow(original)
    # plt.axis('off')
    # plt.show()
    draw = cv2.drawContours(original, contours, -1, (0, 255, 0), 2)
    cent = []
    for i, j in zip(contours, range(len(contours))):
        M = cv2.moments(i)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cent.append((cX, cY))
        draw1 = cv2.circle(draw, (cX, cY), 1, (0, 255, 0), 2)

    cents.append(cent)
    # plt.imshow(original)
    # plt.axis('off')
    # plt.show()
    cv2.imwrite("./mask/" + img_path, draw1)

    if len(cents) > 1:
        index = len(cents)
        # tracking_img = cv2.imread(img_path, 1)
        while index > 1:
            second = cents[index - 1]
            first = cents[index - 2]
            index = index -1
            for p1 in second:
                nearest = None
                dis = 100
                for p2 in first:
                    if distance(p1, p2) < dis:
                        nearest = p2
                        dis = distance(p1, p2)
                if dis < 5:
                    draw1 = cv2.line(draw1, p1, nearest, (0, 255, 0), 1, 4)
        plt.imshow(draw1)
        plt.axis('off')
        plt.show()
        cv2.imwrite("./tracking/" + img_path, draw1)



number = len(files)
cents = []

for img_path in files:
    img_path = ".\\" + img_path
    process_2(img_path)
