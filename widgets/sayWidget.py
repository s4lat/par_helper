from PyQt5 import QtCore, QtGui, QtWidgets, uic
from functools import partial
import json, pyttsx3
from subprocess import call, Popen

class SayWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		super(SayWidget, self).__init__(parent)

		self.parent = parent

		self.load_ui()

		self.backToCatBtn.clicked.connect(self.reset_choose)
		self.backToCatBtn.enterEvent = partial(self.parent.n_enterEvent, self.backToCatBtn)
		self.backToCatBtn.leaveEvent = partial(self.parent.n_leaveEvent)

		self.settingsBtn.clicked.connect(self.parent.open_settings)


		with open('phrases.json', 'r') as f:
			self.phrases = json.loads(f.read())[0]

		self.btns = [self.btn1, self.btn2, self.btn3, 
					self.btn4, self.btn5, self.btn6]

		for (cat, btn) in zip(self.phrases['categories'].keys(), self.btns):
			if len(self.phrases['categories'][cat]) != 6:
				btn.setText(cat + "\n(Не готово)")
			else:
				btn.setText(cat)

			btn.clicked.connect(partial(self.btn_click, btn))
			btn.enterEvent = partial(self.parent.n_enterEvent, btn)
			btn.leaveEvent = self.parent.n_leaveEvent


		self.choosed = False
		self.messages = []

	def btn_click(self, btn):
		if not self.choosed:
			if len(btn.text().split('\n')) > 1:
				return

			self.messages = self.phrases['categories'][btn.text()]
			self.choosed = True

			for (msg, btn) in zip(self.messages, self.btns):
				btn.setText(msg)

		else:
			proc = Popen('python3 speak.py "%s"' % btn.text(), shell=True)
			# call(["python3", "speak.py", btn.text()]) # blocking call


	def reset_choose(self):
		for (cat, btn) in zip(self.phrases['categories'].keys(), self.btns):
			if len(self.phrases['categories'][cat]) != 6:
				btn.setText(cat + "\n(Не готово)")
			else:
				btn.setText(cat)

		self.choosed = False

	def load_ui(self):
		uic.loadUi('./templates/sayWidget.ui', self) # Load the .ui file




		

