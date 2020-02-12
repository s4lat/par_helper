from tensorflow.keras.models import load_model
from widgets.sayWidget import SayWidget
from widgets.settingsWidget import SettingsWidget
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from imutils import face_utils
import dlib, cv2, pyautogui, threading
import sys, time, queue
import numpy as np
import cfg


class Ui(QMainWindow):
	def __init__(self):
		super(Ui, self).__init__()

		self.setGeometry(150, 150, 640, 480)

		self.q = queue.Queue()

		self.central_widget = QStackedWidget()
		self.setObjectName("centralWidget")
		self.setCentralWidget(self.central_widget)

		self.say_widget = SayWidget(self)
		self.central_widget.addWidget(self.say_widget)

		self.settings_widget = SettingsWidget(self)
		self.central_widget.addWidget(self.settings_widget)

		self.central_widget.setCurrentWidget(self.say_widget)

		self.timer = None
		self.hov_btn = None

		self.t = QTimer(self) 
		self.t.timeout.connect(self.check_timer) #Проверяем сколько времени курсор
		self.t.start(500) #находится на кнопке, каждые пол секунды

		self.isEyeDriven = False
		self.model = None

		self.cam_t = None

		self.screen = pyautogui.size()

		self.t1 = QTimer(self)
		self.t1.timeout.connect(self.move_cursor) # Получаем координаты курсора
		self.t1.start(0)

		self.show()

	def init_cam_thread(self):
		if not self.cam_t:
			self.cam_t = threading.Thread(target=self.cam_thread)
			self.cam_t.daemon = True
			self.cam_t.start()

	def cam_thread(self):
		cap = cv2.VideoCapture(cfg.CAM)

		face_detector = dlib.get_frontal_face_detector()
		shapes_predictor = dlib.shape_predictor("static/shape_predictor_68_face_landmarks.dat")

		eyes_roi = np.zeros((128, 256), dtype='int8')
		# g = self.eyesLabel.geometry()
		# w, h = g.width(), g.height()
		# out_eyes_roi = cv2.resize(eyes_roi, (w, h))

		print("Cam thread started!")

		x, y = 0, 0
		while True:
			if not self.isEyeDriven:
				continue

			if not self.model:
				continue

			ret, frame = cap.read()
	
			if not ret:
				print('[ERROR] Camera disconnected!')
				break
				continue

			frame = cv2.resize(frame, (cfg.FRAME_W, cfg.FRAME_H))
			frame = cv2.flip(frame, 1)
			# frame_src = np.copy(frame)
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			faces = face_detector(gray, 1)

			if not len(faces):
				continue

			face = faces[0]
			shapes = shapes_predictor(gray, face)
			shapes = face_utils.shape_to_np(shapes)

			# for shape in shapes:
				# cv2.circle(frame, tuple(shape), 1, (0, 255, 0), -1)

			#Getting eyes
			x0, y0 = shapes[17][0], shapes[17][1]
			x1, y1 = shapes[26][0], shapes[29][1]

			eyes_roi = gray[y0:y1, x0:x1]
			try:
				eyes_roi = cv2.resize(eyes_roi, self.model.input_shape[2:0:-1])
				eyes_roi = np.reshape(eyes_roi, (*(eyes_roi.shape), 1))
				# cv2.rectangle(frame, (x0, y0), 
					# (x1, y1), (0, 0, 255), 2)

				if self.isEyeDriven:
					pred = self.model.predict(np.expand_dims(eyes_roi/255, 0))[0]
					btn_ind = np.argmax(pred)
						
			except cv2.error as e:
				print('[ERROR] Eyes roi is empty!')
				
			# g = self.camLabel.geometry()
			# w, h = g.width(), g.height()
			# out_frame = cv2.resize(frame, (w, h))

			self.q.put({'coords' : cfg.ball_positions[btn_ind]})

	def move_cursor(self):
		if self.q.empty() or not self.isEyeDriven:
			return

		data = self.q.get()
		x = self.screen[0] * data['coords'][0]
		y = self.screen[1] * data['coords'][1]

		pyautogui.moveTo(x, y)

	def open_settings(self):
		self.central_widget.setCurrentWidget(self.settings_widget)

	def open_say_widget(self):
		self.central_widget.setCurrentWidget(self.say_widget)

	def check_timer(self):
		if self.timer is not None:
			if time.time() - self.timer > 5:
				self.hov_btn.click()
				self.timer = None
				self.hov_btn = None

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			if not self.isEyeDriven and self.model:
				self.isEyeDriven = True
				print("Eys driven!")
			else:
				self.isEyeDriven = False

	def n_enterEvent(self, btn, event):
		self.timer = time.time()
		self.hov_btn = btn
		print("Ждем 5 сек и нажмем %s" % btn.text())

	def n_leaveEvent(self, event):
		self.timer = None
		self.hov_btn = None
		print("Сброс таймера")



if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = Ui()
	app.exec_()