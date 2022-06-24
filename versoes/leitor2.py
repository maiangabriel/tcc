from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2

#abre a imagem. as variaveis gray, blurred e edged são alterações da imagem original.
image = cv2.imread("teste2.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 75, 200)
cv2.imshow("prova", edged)
cv2.waitKey(0)

res = []
#Varíavel para gabarito
gb = {0:2, 1:2, 2:2, 3:2, 4:2,5:2,6:2,7:2,8:2,9:2}

#Enontra os contornos na imagem
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
docContour = None

#Se tiver contorno, segue esse if
if len(cnts) > 0:
	#faz o sort dos contornos em ordem descendente
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
	# passa pelos contornos e verifica se o contorno possui 4 pontos
	for c in cnts:
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		#tem 4 pontos? Achou o contorno certo
		if len(approx) == 4:
			docContour = approx
			break

#Faz um recorte da imagem , pegando só a parte dos contornos, facilitando o tratamento
paper = four_point_transform(image, docContour.reshape(4, 2))
warped = four_point_transform(gray, docContour.reshape(4, 2))
thresh = cv2.threshold(
	warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
cnts = cv2.findContours(
	thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

#Seta os contornos das bolhas
questionCnts = []

for c in cnts:
	# A partir daqui, ele trata as bolhas
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)
	#AQUI É UMA PARTE IMPORTANTE. ELE SETA O RATIO DA BOLHA. Caso quisermos mudar de bolha para retâNGULO, basta mudar o valor abaixo
	if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
		questionCnts.append(c)


#A partir daqui, ele trata as questões
questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]
correct = 0
#No caso do papel testedois.png, temos 5 questões. Ele faz o loop a partir daqui
res = []
cont = 0
x = 0
y = 0
bubbled = []
for (q, i) in enumerate(np.arange(0, len(questionCnts), 9)):
	cont = 0
	cnts = contours.sort_contours(questionCnts[i:i + 9])[0]
	bubbled = None
	#Aqui ele verifica se a bolha está correta
	#bubbled = []
	for (j, c) in enumerate(cnts):
		#x = thresh.shape[0]
		#y = thresh.shape[1]
		#Verifica quem tá marcado
		mask = np.zeros(thresh.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)
		mask = cv2.bitwise_and(thresh, thresh, mask=mask)
		total = cv2.countNonZero(mask)
		if bubbled is None or total > bubbled[0]:
			bubbled = (total, j)

		#PRESTAR ATENÇAO AQUI.

		#if total > x//20*y//10:
		#	bubbled.append(j)
		#	cont += 1
#	if cont == 1:
#		res.append(bubbled[0])
#	else:
#		res.append(-1)
	#faz a verificação se a questão marcada está correta. A variavel 'K' ali tá puxando a gb, que é o gabarito(bem no início do código)
	color = (0, 0, 255)
	k = gb[q]
	#Se a questão estiver correta, ele faz o count aqui
	if k == bubbled[0]:
		color = (0, 255, 0)
		correct += 1
	#Se baseando na variavel k, ele marca a questão correta
	cv2.drawContours(paper, [cnts[k]], -1, color, 3)


#loop de teste
##or i in range(len(res)):
#	res2.append(res[len(res)-1-i])
#respostas = res2[::-1]
#print('respostas: ', respostas)


#Faz a porcentagem de acerto e mostra na tela e mostra a imagem.
score = (correct / 5.0) * 100
print("[INFO] score: {:.2f}%".format(score))

cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
cv2.imshow("Original", image)
cv2.imshow("prova", paper)
cv2.waitKey(0)
