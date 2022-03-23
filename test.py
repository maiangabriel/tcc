import numpy as np
import imutils
import cv2
from imutils.perspective import four_point_transform
from imutils import contours

ct = 0
cap = cv2.imread('teste.png', cv2.IMREAD_GRAYSCALE)
correct = 0
gb = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
while(1):
    ct= 0
    ret, image = cap.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edged = cv2.Canny(blurred, 20, 150)
    cv2.imshow("Camera", edged)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.moveWindow("Camera", 0, 0)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    docCnt = 0

    if cnts != []: 
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        for c in cnts:
            peri = 0.02 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, peri, True)
            if len(approx) == 4:
                ct = 1
                docCnt = approx
                break   
    if ct == 1:
        paper = four_point_transform(image, docCnt.reshape(4, 2))
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
        altura = paper.shape[0]//11
        largura = paper.shape[0]//2.95
        paper = paper[altura:paper.shape[0], largura:paper.shape[1]]
        thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        thresh = thresh[altura:thresh.shape[0], largura:thresh.shape[1]]

        if thresh.shape[0] > 0 and thresh.shape[1] > 0:
            cnts = cv2.findContours(
                thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]
            questionCnts = []
            for c in cnts:
                tamanho = thresh.shape[1]/5
                (x, y, w, h) = cv2.boundingRect(c)
                ar = w / float(h)
                approx = cv2.approxPolyDP(c, peri, True)
                if (w <= tamanho and h < tamanho) and (ar >= 1.6 and ar <= 2.6) and (w > tamanho/10 and h > tamanho/10):
                    questionCnts.append(c)
            print(len(questionCnts))
            if len(questionCnts) == 50:
                break
            cont = 0
x = 0
y = 0
res = []
bubbled = []
questao = []
for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
    cont = 0
    cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
    bubbled = []
    for (j, c) in enumerate(cnts):
        x = thresh.shape[0]
        y = thresh.shape[1]
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        mask = cv2.bitwise_and(thresh, thresh, mask=mask)
        total = cv2.countNonZero(mask)
        if total > x//20*y//10:
            bubbled.append(j)
            cont += 1
    if cont == 1:
        res.append(bubbled[0])
    else:
        res.append(-1)
    color = (0, 0, 255)
    k = gb[q]
    if cont == 1:
        if k == bubbled[0]:
            color = (0, 255, 0)
            correct += 1
    for s in range(cont):
        cv2.drawContours(paper, [cnts[bubbled[s]]], -1, color, 3)
res2 = []
for i in range(len(res)):
    res2.append(res[len(res)-i-1])
print("Gabarito:", gb)
print("Respostas:", res2)
print("Nota:", float(correct))
cv2.imshow("Cartao Resposta", paper)
cv2.waitKey(0)
cv2.imshow("real", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()





