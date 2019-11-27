import os
from PySide2 import (QtWidgets, QtCore, QtGui)


DIR = os.path.dirname(__file__)


class LineEdit(QtWidgets.QLineEdit):
    '''
    Inherits QLineEdit and creates it.
    '''
    def __init__(self, name, value, parent=None):
        '''
        Our line init.
        '''
        super(LineEdit, self).__init__(parent)
        self.setObjectName(name)
        self.setText(value)


class Button(QtWidgets.QPushButton):
    '''
    Inherits QPushButton and creates it.
    '''
    def __init__(self, string, parent=None):
        '''
        Our line init.
        '''
        super(Button, self).__init__(string, parent)
        self.setObjectName(string)


class CheckBox(QtWidgets.QCheckBox):
    '''
    Inherits QCheckBox and creates it.
    '''
    def __init__(self, name, parent=None):
        '''
        Our line init.
        '''
        super(CheckBox, self).__init__(parent)
        self.setObjectName(name)
        self.setAutoExclusive(False)


class Label(QtWidgets.QLabel):
    '''
    Inherits QLabel and creates it.
    '''
    def __init__(self, name, parent=None):
        '''
        Our label init.
        '''
        super(Label, self).__init__(parent)

        self.setText(name)
        self.setObjectName("{0}_lbl".format(name))

        # Font.
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)


class UI(QtWidgets.QDialog):
    '''
    QMainWindow.
    '''
    def __init__(self, parent=None):
        '''
        @param parent - QMainWindow to parent to.
        '''
        super(UI, self).__init__(parent)

        self.setWindowTitle("StabilizeUI")
        self.resize(400, 100)
        self.setObjectName("Stabilize")

        with open(os.path.join(DIR, "style.css")) as f:
            self.setStyleSheet(f.read())

        # Center the window.
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Our main layout
        self.central_boxLayout = QtWidgets.QVBoxLayout()
        self.central_boxLayout.setSpacing(10)
        self.central_boxLayout.setContentsMargins(10, 10, 10, 10)

        self.create_layout()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setLayout(self.central_boxLayout)

        self.cam_LEdit.setFocus()

    def create_layout(self):
        '''
        Creates our layout.
        '''
        self.create_widgets()

        self.main_boxLayout = QtWidgets.QVBoxLayout()
        self.main_boxLayout.setContentsMargins(10, 10, 10, 10)

        self.cam_boxLayout = QtWidgets.QHBoxLayout()
        self.cam_boxLayout.addWidget(self.cam_Btn)
        self.cam_boxLayout.addWidget(self.cam_LEdit)

        self.chk_boxLayout = QtWidgets.QHBoxLayout()
        self.chk_boxLayout.addWidget(self.rotate_lbl)
        self.chk_boxLayout.addWidget(self.rotate_chkBox)
        self.chk_boxLayout.addWidget(self.scale_lbl)
        self.chk_boxLayout.addWidget(self.scale_chkBox)
        self.chk_boxLayout.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.chk_boxLayout.setContentsMargins(20, 10, 0, 0)

        self.main_boxLayout.addLayout(self.cam_boxLayout)
        self.main_boxLayout.addLayout(self.chk_boxLayout)

        self.central_boxLayout.addLayout(self.main_boxLayout)
        self.central_boxLayout.addWidget(self.doIt_Btn)

    def create_widgets(self):
        '''
        Creates our widgets.
        '''
        self.cam_Btn = Button(" Load Camera ")
        self.cam_LEdit = LineEdit("cam_LEdit", "Select an camera.")

        self.rotate_lbl = Label("Rotate: ")
        self.rotate_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.rotate_lbl.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Minimum)

        self.rotate_chkBox = CheckBox("rotate")
        self.rotate_chkBox.setChecked(True)

        self.scale_lbl = Label("Scale: ")
        self.scale_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.scale_lbl.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Minimum)

        self.scale_chkBox = CheckBox("scale")

        self.doIt_Btn = Button("Stabilize Object to Camera")
