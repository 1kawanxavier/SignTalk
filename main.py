import cv2
import mediapipe as mp
import json
import numpy as np
from sklearn.svm import SVC

def carregar_dados_treinamento(caminho_json):
    with open(caminho_json, 'r') as json_file:
        dados_treinamento = json.load(json_file)
    amostras = [np.array(d['amostra']).flatten() for d in dados_treinamento]  # Achatando as amostras
    rotulos = [d['rotulo'] for d in dados_treinamento]
    return amostras, rotulos


def treinar_modelo(amostras, rotulos):
    modelo = SVC(kernel='linear')
    modelo.fit(amostras, rotulos)
    return modelo

def detectar_letra_mao(modelo, mp_hands, image):
    resultado = mp_hands.process(image)
    if resultado.multi_hand_landmarks:
        for hand_landmarks in resultado.multi_hand_landmarks:
            pontos_mao = []
            for ponto in hand_landmarks.landmark:
                ponto_x = ponto.x
                ponto_y = ponto.y
                ponto_z = ponto.z if ponto.HasField('z') else None
                pontos_mao.extend([ponto_x, ponto_y, ponto_z])  # Extendendo a lista de pontos
            pontos_mao = np.array(pontos_mao).reshape(1, -1)  # Convertendo para matriz bidimensional
            letra_predita = modelo.predict(pontos_mao)[0]
            return letra_predita


def main():
    mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1)
    
    # Tentar abrir diferentes câmeras
    for camera_index in range(3):  # Tentar até 3 câmeras
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            break  # Sai do loop se uma câmera for encontrada

    if not cap.isOpened():
        print("Nenhuma câmera encontrada.")
        return

    amostras, rotulos = carregar_dados_treinamento('dados_treinamento.json')
    modelo = treinar_modelo(amostras, rotulos)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        letra_predita = detectar_letra_mao(modelo, mp_hands, frame_rgb)
        if letra_predita:
            cv2.putText(frame, letra_predita, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Hand Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
