# -*- coding: utf-8 -*-
import cv2

image = cv2.imread("back.png")
image = cv2.flip(image, 1)

cv2.imwrite("output.png", image)