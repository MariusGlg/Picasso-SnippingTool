import sys


from PyQt5.QtWidgets import (

    QApplication,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout,
    QPushButton,QLineEdit,
    QWidget, QLabel, QPushButton

)


class Window(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("QHBoxLayout Example")

        self.resize(600, 600)

        # btns
        self.btn1 = QPushButton("keep Data in ROI")
        self.btn2 = QPushButton("keep Data in ROI")

        # Create a QHBoxLayout instance

        self.gridLayout = QGridLayout()

        # Add widgets to the layout
        self.label = QLabel('It is Label 1', self)
        self.label.setStyleSheet("border: 1px solid black")
        self.label2 = QLabel('It is Label 2', self)
        self.label2.setStyleSheet("border: 1px solid black")
        self.gridLayout.addWidget(self.label, 0, 0, 5, 5)
        self.gridLayout.addWidget(self.label2, 0, 5, 5, 2)
        self.gridLayout.addWidget(self.btn1, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.btn2, 5, 1, 1, 1)




        self.setLayout(self.gridLayout)


        # outerLayout = QVBoxLayout()
        # topLayout = QHBoxLayout()
        # topLayout.addWidget(QLabel("left"))
        # topLayout.addWidget(QLabel("right"))
        #
        #
        # bottomLayout = QHBoxLayout()
        # bottomLayout.addWidget(QPushButton("Left-Most"))
        # bottomLayout.addWidget(QPushButton("Center"))
        # bottomLayout.addWidget(QPushButton("Right-Most"))
        #
        # outerLayout.addLayout(topLayout)
        # outerLayout.addLayout(bottomLayout)

        #self.setLayout(outerLayout)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())