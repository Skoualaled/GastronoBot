import cv2, os
import numpy as np

# Compare les images de ImagesTMP à celle de Image pour trouver des doublons
# A lancer à la main

ImagesTMP = os.listdir('..\\ImagesTMP')
ImagesDB = os.listdir('..\\Images')

for img in ImagesTMP:
    
    imgTest = cv2.imread('..\\ImagesTMP\\' + img)
    print('Image test : ' + img)
    old = False
    for imgDB in ImagesDB:
        if imgDB.split('.')[1] != 'gif':
            imgComp = cv2.imread('..\\Images\\' + imgDB)
            if imgComp.shape == imgTest.shape:
                diff = cv2.subtract(imgComp, imgTest)
                b, g, r = cv2.split(diff)
                if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                    print("OLD")
                    old = True
                    break
    if not old:
        os.rename('..\\ImagesTMP\\' + img, '..\\Images\\' + img)
    else:
        os.remove('..\\ImagesTMP\\' + img)
