import numpy as np
import cv2
import json
f1=open('safecheck2.json')
f=json.load(f1)
f1.close()
f2=[]
for i in f:
    f2.append(i)
img = cv2.imread('T13.png',1)
for i in f2:
    pts = np.array([f[i]['top_left'],f[i]['top_right'],f[i]['down_right'],f[i]['down_left']],np.int32)
    pts = pts.reshape((-1,1,2))
    cv2.polylines(img,[pts],False,(0,0,255),2)
for i in f2:
    text = f[i]['ID']
    cv2.putText(img, text,(f[i]['top_left'][0], f[i]['top_left'][1]), cv2.FONT_HERSHEY_SIMPLEX,0.4, (255,0,255), 1) 
cv2.namedWindow('image', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
cv2.imshow('image', img)
k = cv2.waitKey(0)
if k == 27:  # wait for ESC key to exit
    cv2.destroyAllWindows()
elif k == ord('s'):  # wait for 's' key to save and exit
    cv2.imwrite('a.jpg', img)
    cv2.destroyAllWindows()