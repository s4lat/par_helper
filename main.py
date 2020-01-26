from tensorflow.keras.models import load_model
from widgets.sayWidget import SayWidget
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Ui(QMainWindow):
	def __init__(self):
		super(Ui, self).__init__() # Call the inherited classes __init__ method

		self.setGeometry(150, 150, 640, 480)

		self.central_widget = QStackedWidget()
		self.setObjectName("centralWidget")
		self.setCentralWidget(self.central_widget)

		self.say_widget = SayWidget(self)
		self.central_widget.addWidget(self.say_widget)

		self.show()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = Ui()
	app.exec_()