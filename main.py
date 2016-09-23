#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys
import json
import os
from room import Room, Model
from PyQt4 import QtGui, QtCore


class Test(QtGui.QWidget):

    def __init__(self):
        super(Test, self).__init__()
        self.initUI()
        self.initSignal()
        self.configPath = 'config/'

    def initUI(self):
        self.setWindowTitle(u"一键设计二期模拟程序")

        label0 = QtGui.QLabel(u"原始形状:")
        label1 = QtGui.QLabel(u"目标形状:")
        label2 = QtGui.QLabel(u"原始房间点:")
        label3 = QtGui.QLabel(u"原始模型点:")
        label4 = QtGui.QLabel(u"目标房间点:")
        label5 = QtGui.QLabel(u"目标模型点:")

        emptyImage = Room.emptyRoomImage()

        self.imageLabelOrigin = QtGui.QLabel()
        self.imageLabelOrigin.setPixmap(emptyImage.toqpixmap())
        self.imageLabelDest = QtGui.QLabel()
        self.imageLabelDest.setPixmap(emptyImage.toqpixmap())
        self.pointsEditOrigin = QtGui.QPlainTextEdit("")
        self.pointsEditOriginModel = QtGui.QPlainTextEdit("")
        self.pointsEditDest = QtGui.QPlainTextEdit("")
        self.pointsEditDestModel = QtGui.QPlainTextEdit("")

        self.button1 = QtGui.QPushButton(u"绘制样板房形状")
        self.button2 = QtGui.QPushButton(u"添加样板房模型")
        self.button3 = QtGui.QPushButton(u"计算样板房模型射线")
        self.button4 = QtGui.QPushButton(u"绘制目标房形状")
        self.button5 = QtGui.QPushButton(u"推荐")

        self.button6 = QtGui.QPushButton(u"绘制目标房模型")
        self.button7 = QtGui.QPushButton(u"一键测试")

        slabel1 = QtGui.QLabel(u"配置文件：")
        self.slineedit1 = QtGui.QLineEdit("config4.json")
        self.sbutton1 = QtGui.QPushButton(u"从配置文件加载数据")
        self.sbutton2 = QtGui.QPushButton(u"将当前数据保存到配置文件")

        grid0 = QtGui.QGridLayout()
        grid0.addWidget(label0,0,0)
        grid0.addWidget(label1,20,0)
        grid0.addWidget(self.imageLabelOrigin,0,3,20,20)
        grid0.addWidget(self.imageLabelDest,20,3,20,20)

        grid1 = QtGui.QGridLayout()
        grid1.addWidget(label2,0,0)
        grid1.addWidget(label3,12,0)
        grid1.addWidget(self.pointsEditOrigin,0,3,12,20)
        grid1.addWidget(self.pointsEditOriginModel,12,3,8,20)
        grid1.addWidget(label4,20,0)
        grid1.addWidget(label5,32,0)
        grid1.addWidget(self.pointsEditDest,20,3,12,20)
        grid1.addWidget(self.pointsEditDestModel,32,3,8,20)

        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(self.button1)
        vlayout.addWidget(self.button2)
        vlayout.addWidget(self.button3)
        vlayout.addWidget(self.button4)
        vlayout.addWidget(self.button5)
        vlayout.addWidget(self.button6)
        vlayout.addWidget(self.button7)


        vlayout2 = QtGui.QVBoxLayout()
        # vlayout2.addWidget(slabel1,0)
        vlayout2.addWidget(self.slineedit1,1)
        vlayout2.addWidget(self.sbutton1,2)
        vlayout2.addWidget(self.sbutton2,3)
        # vlayout2.addSeper

        grid = QtGui.QGridLayout()
        grid.addLayout(grid0,0,0)
        grid.addLayout(grid1,0,1)
        grid.addLayout(vlayout,0,2)
        grid.addLayout(vlayout2,0,3)

        self.setLayout(grid)
        self.show()

    def initSignal(self):
        self.connect(self.button1,QtCore.SIGNAL("clicked()"), self.button1_clicked)
        self.connect(self.button2,QtCore.SIGNAL("clicked()"), self.button2_clicked)
        self.connect(self.button3,QtCore.SIGNAL("clicked()"), self.button3_clicked)

        self.connect(self.button4,QtCore.SIGNAL("clicked()"), self.button4_clicked)
        self.connect(self.button5,QtCore.SIGNAL("clicked()"), self.button5_clicked)
        self.connect(self.button6,QtCore.SIGNAL("clicked()"), self.button6_clicked)

        self.connect(self.button7,QtCore.SIGNAL("clicked()"), self.button7_clicked)

        self.connect(self.sbutton1 ,QtCore.SIGNAL("clicked()"), self.sbutton1_clicked)
        self.connect(self.sbutton2 ,QtCore.SIGNAL("clicked()"), self.sbutton2_clicked)

    def Qstring2Unicode(self, s):
        """QSting类型转Unicode"""
        return unicode(s.toUtf8(), 'utf-8', 'ignore')

    def button1_clicked(self):
        """绘制样板房形状"""
        origin_points_text = self.Qstring2Unicode(self.pointsEditOrigin.toPlainText())
        self.originRoom = Room.loadData(origin_points_text)
        if self.originRoom:
            self.imageLabelOrigin.setPixmap(self.originRoom.getImage().toqpixmap())

    def button2_clicked(self):
        """绘制样板房模型"""
        origin_model_points_text = self.Qstring2Unicode(self.pointsEditOriginModel.toPlainText())
        models = Model.loadString(origin_model_points_text)
        self.originRoom.addModel(models)

        im = self.originRoom.getImageWithModel()
        # im = self.originRoom.getImageWithModelRay()
        if im:
            self.imageLabelOrigin.setPixmap(im.toqpixmap())

    def button3_clicked(self):
        """绘制样板房模型射线"""
        im = self.originRoom.getImageWithModelRay()
        if im:
            self.imageLabelOrigin.setPixmap(im.toqpixmap())

    def button4_clicked(self):
        """绘制目标房形状"""
        dest_points_text = self.Qstring2Unicode(self.pointsEditDest.toPlainText())
        self.destRoom = Room.loadData(dest_points_text)
        if self.destRoom:
            self.imageLabelDest.setPixmap(self.destRoom.getImage().toqpixmap())

    def button5_clicked(self):
        """推荐模型"""
        model_points = []
        for model in self.originRoom.models:
            point = self.destRoom.getPointByPercentDirection(model.percent, model.direction)
            model_points.append(point)
        result = [(int(p.x),int(p.y)) for p in model_points]
        self.pointsEditDestModel.setPlainText(result.__str__())

    def button6_clicked(self):
        """绘制目标房模型"""
        dest_model_points_text = self.Qstring2Unicode(self.pointsEditDestModel.toPlainText())
        models = Model.loadString(dest_model_points_text)
        self.destRoom.addModel(models)

        im = self.destRoom.getImageWithModel()
        im = self.destRoom.getImageWithModelRay()
        if im:
            self.imageLabelDest.setPixmap(im.toqpixmap())

    def button7_clicked(self):
        """一键测试"""
        for i in range(1,7):
            exec("self.button%d_clicked()" % i)
            # self.updateGui()

    def sbutton1_clicked(self):
        """从配置文件加载数据"""
        filename = self.slineedit1.displayText()
        filename = self.configPath + filename

        if os.path.exists(filename):
            f = open(filename)
            data = json.load(f)
            f.close()
            # print data
            if 'O' in data:
                self.pointsEditOrigin.setPlainText(data['O'].__str__())
            if 'OM' in data:
                self.pointsEditOriginModel.setPlainText(data['OM'].__str__())
            if 'D' in data:
                self.pointsEditDest.setPlainText(data['D'].__str__())
            if 'DM' in data:
                self.pointsEditDestModel.setPlainText(data['DM'].__str__())

    def sbutton2_clicked(self):
        """将当前数据保存到配置文件"""
        # sbutton2_clicked
        filename = self.slineedit1.displayText()
        filename = self.configPath + filename
        if not filename:
            return

        data = {}
        origin_points_text = self.Qstring2Unicode(self.pointsEditOrigin.toPlainText())
        origin_model_points_text = self.Qstring2Unicode(self.pointsEditOriginModel.toPlainText())
        dest_points_text = self.Qstring2Unicode(self.pointsEditDest.toPlainText())
        dest_model_points_text = self.Qstring2Unicode(self.pointsEditDestModel.toPlainText())
        if origin_points_text:
            data['O'] = eval(origin_points_text)
        if origin_model_points_text:
            data['OM'] = eval(origin_model_points_text)
        if dest_points_text:
            data['D'] = eval(dest_points_text)
        if dest_model_points_text:
            data['DM'] = eval(dest_model_points_text)

        f = open(filename,'w')
        json.dump(data, f, indent=4)
        f.close()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    test = Test()
    sys.exit(app.exec_())
