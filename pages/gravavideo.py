import cv2
import PySimpleGUI as sg
from threading import Thread, Event
import queue
import os
import mediapipe as mp

class GravadorVideo:
    def __init__(self, janela, label_resultado, event_queue, stop_event):
        self.janela = janela
        self.label_resultado = label_resultado
        self.cap = None
        self.window = None
        self.event_queue = event_queue
        self.stop_event = stop_event
        self.descricao_video = None

        # Inicializa os módulos do mediapipe para reconhecimento facial e detecção de mãos
        self.mp_face = mp.solutions.face_detection
        self.mp_hands = mp.solutions.hands
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.2)
        self.hands = self.mp_hands.Hands()

    def iniciar_gravacao(self):
        self.cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        nome_arquivo = f"{self.descricao_video}.avi"
        caminho_arquivo = os.path.join("videos", nome_arquivo)
        out = cv2.VideoWriter(caminho_arquivo, fourcc, 20.0, (640, 480))

        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                # Detecta faces no frame
                results = self.face_detection.process(frame)
                if results.detections:
                    for detection in results.detections:
                        bboxC = detection.location_data.relative_bounding_box
                        ih, iw, _ = frame.shape
                        bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                               int(bboxC.width * iw), int(bboxC.height * ih)
                        cv2.rectangle(frame, bbox, (0, 255, 0), 2)

                # Converte o frame para o formato RGB para o mediapipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Detecta mãos no frame
                results_hands = self.hands.process(rgb_frame)
                if results_hands.multi_hand_landmarks:
                    for hand_landmarks in results_hands.multi_hand_landmarks:
                        for landmark in hand_landmarks.landmark:
                            h, w, c = frame.shape
                            x, y = int(landmark.x * w), int(landmark.y * h)
                            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)  # Marca pontos da mão

                out.write(frame)
                self.event_queue.put(frame)
                self.stop_event.wait(0.01)

        self.obter_descricao_video()
        self.salvar_descricao_em_arquivo(nome_arquivo)
        self.encerrar_gravacao(out)

    def obter_descricao_video(self):
        self.janela.write_event_value('-DESCRICAO-', None)

    def salvar_descricao_em_arquivo(self, nome_arquivo):
        if self.descricao_video:
            try:
                with open(os.path.join("videos", f"{nome_arquivo}.txt"), 'w') as file:
                    file.write(self.descricao_video)
            except Exception as e:
                print(f"Erro ao salvar o arquivo de descrição: {e}")

    def encerrar_gravacao(self, out):
        if self.cap:
            self.cap.release()
        if out:
            out.release()

        if self.window:
            self.window.write_event_value('-STOP-', None)

        if self.label_resultado:
            self.label_resultado.update(value="Opção selecionada: Gravar Libras (encerrado)")

    def exibir_descricao(self, nome_arquivo):
        layout = [
            [sg.Text("Descrição do Vídeo:")],
            [sg.Text(self.descricao_video, size=(30, 2), key='-DESCRICAO_TEXT-')],
            [sg.Button('OK')]
        ]

        window = sg.Window('Descrição do Vídeo', layout)

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'OK'):
                window.close()
                break

def gravar_libras(janela, label_resultado, event_queue, stop_event):
    if label_resultado:
        label_resultado.update(value="Opção selecionada: Gravar Libras (gravando)")

    descricao_video = sg.popup_get_text("Digite a descrição do vídeo:", title="Descrição do Vídeo")

    layout = [
        [sg.Image(filename='', key='-VIDEO-')],
        [sg.Button('Parar Gravação', key='-STOP-')]
    ]

    window = sg.Window('Gravação de Vídeo', layout, finalize=True)
    gravador = GravadorVideo(janela, label_resultado, event_queue, stop_event)
    gravador.window = window
    gravador.descricao_video = descricao_video

    thread_gravacao = Thread(target=gravador.iniciar_gravacao)
    thread_gravacao.start()

    while True:
        event, values = window.read(timeout=20)
        if event in (sg.WINDOW_CLOSED, '-STOP-'):
            stop_event.set()
            thread_gravacao.join()
            gravador.exibir_descricao(nome_arquivo)
            break
        elif event == '-DESCRICAO-':
            gravador.descricao_video = sg.popup_get_text("Digite a descrição do vídeo:", title="Descrição do Vídeo")

        elif event == '__TIMEOUT__':
            try:
                frame = event_queue.get_nowait()
                window['-VIDEO-'].update(data=cv2.imencode('.png', frame)[1].tobytes())
            except queue.Empty:
                pass

if __name__ == "__main__":
    root = sg.Window('Gravar Vídeo', [[sg.Button('Gravar Libras', key='-GRAVAR-')]], finalize=True)
    stop_event = Event()
    event_queue = queue.Queue()

    while True:
        event, values = root.read()
        if event == sg.WINDOW_CLOSED:
            stop_event.set()
            break
        elif event == '-GRAVAR-':
            gravar_libras(root, None, event_queue, stop_event)

    root.close()
