from PyQt5 import QtCore, QtGui, QtWidgets, uic
from tensorflow.keras.models import load_model
import os, cfg

class SettingsWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		super(SettingsWidget, self).__init__(parent)

		self.load_ui()
		self.update_lists()

		self.parent = parent

		self.backBtn.clicked.connect(self.parent.open_say_widget)
		self.loadBtn.clicked.connect(self.load_model)

		self.show()

	def load_model(self, event):
		s = self.modelsList.currentItem() #Selection
		if not s:
			return

		try:
			model_name = s.text()
			self.parent.model = load_model(cfg.MODELS_PATH+model_name)
			print("%s succesfully loaded!" % model_name)
			self.parent.init_cam_thread()
			self.backBtn.click()

		except OSError:
			print("%s not exists" % model_name)

	def update_lists(self):
		models = [f for f in os.listdir(cfg.MODELS_PATH) if f[0] != '.']

		self.modelsList.clear()
		self.modelsList.addItems(models)

	def load_ui(self):
		uic.loadUi('./templates/settingsWidget.ui', self) # Load the .ui file
