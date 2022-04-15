# -*- coding: utf-8 -*-
import cv2

cap = cv2.VideoCapture("rtsp://test:test@10.0.0.2/live_drogon")
# rtsp://test:test@10.0.0.2/live_drogon
# rtsp://test:test@10.0.0.2/live_lady
# rtsp://test:test@10.0.0.2/live_greywind
# rtsp://test:test@10.0.0.2/live_rhaegal_l
# rtsp://test:test@10.0.0.2/live_rhaegal_r

while (cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)
    # ESC
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
