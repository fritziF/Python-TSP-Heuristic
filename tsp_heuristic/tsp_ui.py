# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Fritzi\Dropbox\VU Computational Techniques\Teil2\tsp.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui
import matplotlib.pyplot as plt
import networkx as nx

from tsp_worker import Problem

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Tsp(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

    def setupUi(self, TSP):
        TSP.setObjectName(_fromUtf8("TSP"))
        TSP.resize(771, 356)
        self.verticalLayout_3 = QtGui.QVBoxLayout(TSP)
        self.verticalLayout_3.setMargin(5)
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.widget = QtGui.QWidget(TSP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_4.setMargin(5)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.commentLabel = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commentLabel.sizePolicy().hasHeightForWidth())
        self.commentLabel.setSizePolicy(sizePolicy)
        self.commentLabel.setObjectName(_fromUtf8("commentLabel"))
        self.gridLayout_4.addWidget(self.commentLabel, 0, 1, 1, 1)
        self.fileComboBox = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileComboBox.sizePolicy().hasHeightForWidth())
        self.fileComboBox.setSizePolicy(sizePolicy)
        self.fileComboBox.setObjectName(_fromUtf8("fileComboBox"))
        self.gridLayout_4.addWidget(self.fileComboBox, 0, 0, 1, 1)
        self.dimensionLabel = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dimensionLabel.sizePolicy().hasHeightForWidth())
        self.dimensionLabel.setSizePolicy(sizePolicy)
        self.dimensionLabel.setObjectName(_fromUtf8("dimensionLabel"))
        self.gridLayout_4.addWidget(self.dimensionLabel, 0, 2, 1, 1)
        self.runTsp_btn = QtGui.QPushButton(self.widget)
        self.runTsp_btn.setObjectName(_fromUtf8("runTsp_btn"))
        self.gridLayout_4.addWidget(self.runTsp_btn, 1, 2, 1, 1)
        self.resultLabel = QtGui.QLabel(self.widget)
        self.resultLabel.setObjectName(_fromUtf8("resultLabel"))
        self.gridLayout_4.addWidget(self.resultLabel, 1, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_4)
        self.verticalLayout_2.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(TSP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout_2.addWidget(self.widget_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(TSP)
        QtCore.QMetaObject.connectSlotsByName(TSP)

    def retranslateUi(self, TSP):
        TSP.setWindowTitle(_translate("TSP", "Form", None))
        self.commentLabel.setText(_translate("TSP", "TextLabel", None))
        self.dimensionLabel.setText(_translate("TSP", "TextLabel", None))
        self.runTsp_btn.setText(_translate("TSP", "Run!", None))
        self.runTsp_btn.clicked.connect(self.run_tsp)
        self.resultLabel.setText(_translate("TSP", "TextLabel", None))

    def run_tsp(self):
        file_path = "../problems/berlin52.tsp"

        problem = Problem(file_path)

        calc_matrix = problem.calc_dist_matrix()

        for row in calc_matrix:
            print row
            print '\t'.join([str(cell) for cell in row])

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ui = Ui_Tsp()
    ui.show()
    sys.exit(app.exec_())