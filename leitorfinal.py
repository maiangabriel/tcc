#importação de bibliotecas
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2

#variável de abertura da imagem
image = cv2.imread("testeandrew.png")
#tratamento 1- retira a cor, deixando somente entre 2 pontos: preto e branco 
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#borra para diminuir os ruídos desnecessários na imagem
#blurred = cv2.GaussianBlur(gray, (5, 5), 0)
blurred = cv2.bilateralFilter(gray, 11,41,21)
#auxilia a encontrar as bordas da imagem. no nosso caso, o papel de correção
edged = cv2.Canny(gray, 75, 200)
cv2.imshow("Exam", blurred)
cv2.waitKey(0)
cv2.imshow("Exam", edged)
cv2.waitKey(0)
#Lista de gabarito. Valores setados no código no momento, para teste
gb = [0, 1, 2, 2, 4, 1, 1, 1, 1, 2]

# a variavel cnts armazena a busca dos contornos. a partir da variável edged +
#o parametro cv2.RETR_EXTERNAL busca os contornos externos, enquanto o cv2.CHAIN_APPROX_SIMPLE +
#marca os "endpoints" do contorno
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
#aqui utilizo o imutils para armazenar os contornos encontrados anteriormente
cnts = imutils.grab_contours(cnts)

docContour = None

if len(cnts) > 0:
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
	# passa pelos contornos e verifica se o contorno possui 4 pontos
	for c in cnts:
		perimetro = cv2.arcLength(c, True)
		aprox = cv2.approxPolyDP(c, 0.02 * perimetro, True)
		if len(aprox) == 4:
			docContour = aprox
			break

paper = four_point_transform(image, docContour.reshape(4, 2))
warped = four_point_transform(gray, docContour.reshape(4, 2))
thresh = cv2.threshold(
	warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
cnts = cv2.findContours(
	thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)


questionCnts = []
for c in cnts:
	# A partir daqui, ele trata as bolhas
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)
	#AQUI É UMA PARTE IMPORTANTE. ELE SETA O RATIO DA BOLHA. Caso quisermos mudar de bolha para retâNGULO, basta mudar o valor abaixo
	if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
		questionCnts.append(c)

questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]
correct = 0

res = []
cont = 0
#x = 0
#y = 0
bubbled = []
umalista = []

# start,stop,step - o ultimo valor corresponde a varredura do arquivo -
for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
	#DE A a D - 4 / de A a E - 5
	cont = 0
	cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
	bubbled = None
	#Aqui ele verifica se a bolha está correta

	for (j, c) in enumerate(cnts):
		#x = thresh.shape[0]
		#y = thresh.shape[1]
		#Verifica quem tá marcado
		mask = np.zeros(thresh.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)
		mask = cv2.bitwise_and(thresh, thresh, mask=mask)
		total = cv2.countNonZero(mask)
		#cv2.imshow("Exam", mask)
		#cv2.waitKey(0)

		if bubbled is None or total > bubbled[0]:
			bubbled = (total, j)

		
        

		bubbled = list(bubbled)
		# if total > x//20*y//10:

		# 	bubbled.append(j)
		# 	cont += 1
	if cont == 1:
		res.append(bubbled[0])
	else:
		res.append(-1)
	
	color = (0, 0, 255)
	k = gb[q]

	#Se a questão estiver correta, ele faz o count aqui
	if k == bubbled[1]:
		color = (0, 255, 0)
		correct += 1
		bubbled3 = list(bubbled)
		bubbled3.append(correct)

	else:
		bubbled2 = list(bubbled)
		bubbled2.append(correct)

	#Se baseando na variavel k, ele marca a questão correta
	cv2.drawContours(paper, [cnts[k]], -1, color, 3)

	resposta = list(bubbled)
	resposta.append(correct)
	umalista.insert(0, resposta[1])

respostas = umalista[::-1]
print('respostas: ', respostas)

score = (correct / float(len(umalista))) * 100
print("[INFO] score: {:.2f}%".format(score))

cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
cv2.imshow("Original", image)
cv2.imshow("Exam", paper)
cv2.waitKey(0)
