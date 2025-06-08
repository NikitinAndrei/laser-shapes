import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QFileDialog, QGraphicsView,
    QGraphicsScene, QGroupBox, QGridLayout
)
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QRectF, Qt, QPointF


class LaserMakerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laser Maker")
        self.init_ui()

    def init_ui(self):
        # === Группа: Фигура ===
        shape_box = QGroupBox("Фигура")
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Квадрат", "Эллипс"])
        shape_layout = QVBoxLayout()
        shape_layout.addWidget(self.shape_combo)
        shape_box.setLayout(shape_layout)

        # === Группа: Соединение ===
        joint_box = QGroupBox("Соединение")
        self.joint_combo = QComboBox()
        self.joint_combo.addItems(["Нет", "Зубы", "Пазы"])
        joint_layout = QVBoxLayout()
        joint_layout.addWidget(self.joint_combo)
        joint_box.setLayout(joint_layout)

        # === Группа: Параметры ===
        param_box = QGroupBox("Параметры")
        self.thickness_input = QLineEdit()
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.length_input = QLineEdit()
        self.joint_length_input = QLineEdit()
        param_layout = QFormLayout()
        param_layout.addRow("Толщина материала", self.thickness_input)
        param_layout.addRow("Ширина", self.width_input)
        param_layout.addRow("Высота", self.height_input)
        param_layout.addRow("Длина", self.length_input)
        param_layout.addRow("Длина зуба", self.joint_length_input)
        param_box.setLayout(param_layout)

        # === Предпросмотр ===
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        # === Кнопка сохранить ===
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_svg)

        # === Верхняя панель с группами ===
        top_layout = QHBoxLayout()
        top_layout.addWidget(shape_box)
        top_layout.addWidget(joint_box)
        top_layout.addWidget(param_box)

        # === Главный лэйаут ===
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(QLabel("Окно предпросмотра"))
        main_layout.addWidget(self.view)
        main_layout.addWidget(self.save_button, alignment=Qt.AlignRight)

        self.setLayout(main_layout)

        # Отрисовка по изменению параметров
        self.shape_combo.currentIndexChanged.connect(self.draw_shape)
        self.joint_combo.currentIndexChanged.connect(self.draw_shape)
        for line_edit in [self.thickness_input, self.width_input, self.height_input, self.length_input, self.joint_length_input]:
            line_edit.textChanged.connect(self.draw_shape)

        self.draw_shape()

    def draw_shape(self):
        self.scene.clear()

        try:
            width = float(self.width_input.text()) if self.width_input.text() else 100
            height = float(self.height_input.text()) if self.height_input.text() else 100
            thickness = float(self.thickness_input.text()) if self.thickness_input.text() else 5
            joint_length = float(self.joint_length_input.text()) if self.joint_length_input.text() else 10
        except ValueError:
            return

        shape = self.shape_combo.currentText()
        joint = self.joint_combo.currentText()

        if shape == "Квадрат":
            self.draw_rect_with_joints(50, 50, width, height, joint, thickness, joint_length)
        elif shape == "Эллипс":
            self.scene.addEllipse(50, 50, width, height, QPen(Qt.black))

    def draw_rect_with_joints(self, x, y, w, h, joint, thickness, joint_length):
        pen = QPen(Qt.black)

        if joint == "Нет":
            self.scene.addRect(x, y, w, h, pen)
        elif joint == "Зубы":
            self.draw_rectangle_with_teeth(self.scene, x, y, w, h, joint_length=joint_length, thickness=thickness)
        elif joint == "Пазы":
            self.scene.addRect(x, y, w, h, pen)
            for i in range(int(w // joint_length)):
                if i % 2 == 0:
                    self.scene.addRect(x + i * joint_length, y - thickness, joint_length, thickness, pen)

    def draw_meander(self, x, y, length, horizontal=True, step=10, thickness=5):
        pen = QPen(Qt.black)
        for i in range(int(length // step)):
            if horizontal:
                if i % 2 == 0:
                    self.scene.addRect(x + i * step, y, step, thickness, pen)
            else:
                if i % 2 == 0:
                    self.scene.addRect(x, y + i * step, thickness, step, pen)


    def draw_rectangle_with_teeth(self, scene, x, y, width, height, joint_length, thickness):
        pen = QPen(Qt.black)

        def draw_edge(start: QPointF, length: float, is_horizontal: bool, flip: bool):
            count = int(length // joint_length)
            if count == 0:
                count = 1
            padding = (length - count * joint_length) / 2
            for i in range(count):
                offset = padding + i * joint_length
                if is_horizontal:
                    rect_x = start.x() + offset
                    rect_y = start.y() - thickness if flip else start.y()
                    scene.addRect(rect_x, rect_y, joint_length, thickness, pen)
                else:
                    rect_x = start.x() - thickness if flip else start.x()
                    rect_y = start.y() + offset
                    scene.addRect(rect_x, rect_y, thickness, joint_length, pen)

        # Внутренний прямоугольник
        scene.addRect(x, y, width, height, pen)
        # Верхняя и нижняя стороны
        draw_edge(QPointF(x, y), width, is_horizontal=True, flip=False)
        draw_edge(QPointF(x, y + height), width, is_horizontal=True, flip=True)
        # Левая и правая стороны
        draw_edge(QPointF(x, y), height, is_horizontal=False, flip=False)
        draw_edge(QPointF(x + width, y), height, is_horizontal=False, flip=True)

    def save_svg(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить SVG", "", "SVG Files (*.svg)")
        if not filename:
            return

        generator = QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(self.view.size())
        generator.setViewBox(QRectF(0, 0, self.view.width(), self.view.height()))
        generator.setTitle("Laser Shape")
        generator.setDescription("SVG for laser cutting")

        painter = QPainter()
        painter.begin(generator)
        self.scene.render(painter)
        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LaserMakerApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
