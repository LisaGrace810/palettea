"""
Palettea Final Desktop App with Brush Preview
---------------------------------------------
Requirements:
pip install PyQt6 opencv-python mss numpy
"""

import sys, random, math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QListWidget, QListWidgetItem, QSlider, QFileDialog, QAction
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QPolygonF, QImage

import numpy as np
try:
    import mss
    import cv2
except ImportError:
    mss = None
    cv2 = None

CANVAS_W, CANVAS_H = 800, 600

# ---------------- Layer ----------------
class Layer:
    def __init__(self, name):
        self.name = name
        self.pixmap = QPixmap(CANVAS_W, CANVAS_H)
        self.pixmap.fill(Qt.GlobalColor.transparent)
        self.visible = True
        self.locked = False

# ---------------- Canvas ----------------
class Canvas(QWidget):
    def __init__(self, layers, undo_stack, redo_stack):
        super().__init__()
        self.setFixedSize(CANVAS_W, CANVAS_H)
        self.layers = layers
        self.undo_stack = undo_stack
        self.redo_stack = redo_stack
        self.current_layer = self.layers[-1] if self.layers else None
        self.drawing = False
        self.last_point = QPoint()
        self.brush_color = QColor(0,0,0)
        self.brush_size = 12
        self.brush_opacity = 255
        self.brush_type = "round"
        self.symmetry_mode = "none"
        self.recording = False
        self.record_frames = []
        self.record_fps = 15
        self.record_canvas_only = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0,0,self.width(),self.height(),QColor("white"))
        for layer in self.layers:
            if layer.visible:
                painter.drawPixmap(0,0,layer.pixmap)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.current_layer and not self.current_layer.locked:
            self.drawing = True
            self.last_point = e.position().toPoint()
            self._push_undo()
            self.redo_stack.clear()

    def mouseMoveEvent(self, e):
        if self.drawing:
            self._draw_line(self.last_point, e.position().toPoint())
            self.last_point = e.position().toPoint()
            self.update()
            self._record_frame_if_active()

    def mouseReleaseEvent(self, e):
        self.drawing = False

    def _draw_line(self, start, end):
        points = self._sample_points(start, end)
        for pt in points:
            self._draw_at_point(pt)
            cx,cy = CANVAS_W//2,CANVAS_H//2
            if self.symmetry_mode in ("horizontal","both"):
                self._draw_at_point(QPoint(2*cx - pt.x(), pt.y()))
            if self.symmetry_mode in ("vertical","both"):
                self._draw_at_point(QPoint(pt.x(), 2*cy - pt.y()))
            if self.symmetry_mode=="both":
                self._draw_at_point(QPoint(2*cx - pt.x(), 2*cy - pt.y()))

    def _draw_at_point(self, pt):
        painter = QPainter(self.current_layer.pixmap)
        size = self.brush_size
        if self.brush_type=="scatter":
            sx = pt.x()+random.randint(-size,size)
            sy = pt.y()+random.randint(-size,size)
            painter.setPen(QPen(self.brush_color, size))
            painter.drawPoint(sx,sy)
        elif self.brush_type=="soft":
            for dx in range(-size,size):
                for dy in range(-size,size):
                    if (dx*dx+dy*dy)**0.5 <= size:
                        c = QColor(self.brush_color)
                        alpha=int(self.brush_opacity*(1-((dx*dx+dy*dy)**0.5)/size))
                        c.setAlpha(alpha)
                        painter.setPen(QPen(c,1))
                        painter.drawPoint(pt.x()+dx, pt.y()+dy)
        else:
            c = QColor(self.brush_color)
            c.setAlpha(self.brush_opacity)
            painter.setPen(QPen(c,size,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
            painter.drawPoint(pt.x(), pt.y())
        painter.end()

    def _sample_points(self,start,end):
        distance=max(abs(end.x()-start.x()),abs(end.y()-start.y()),1)
        return [QPoint(int(start.x()*(1-t)+end.x()*t),int(start.y()*(1-t)+end.y()*t)) for t in [i/distance for i in range(distance+1)]]

    def _push_undo(self):
        self.undo_stack.append([l.pixmap.copy() for l in self.layers])
        if len(self.undo_stack)>60: self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack: return
        state=self.undo_stack.pop()
        self.redo_stack.append([l.pixmap.copy() for l in self.layers])
        for i,l in enumerate(state):
            self.layers[i].pixmap = l.copy()
        self.update()

    def redo(self):
        if not self.redo_stack: return
        state=self.redo_stack.pop()
        self.undo_stack.append([l.pixmap.copy() for l in self.layers])
        for i,l in enumerate(state):
            self.layers[i].pixmap = l.copy()
        self.update()

    # ---------------- Recording ----------------
    def start_recording(self, canvas_only=True):
        if mss is None or cv2 is None:
            return
        self.recording=True
        self.record_frames=[]
        self.record_canvas_only=canvas_only

    def stop_recording(self, filename="palettea_recording.mp4"):
        if not self.recording: return
        self.recording=False
        fourcc=cv2.VideoWriter_fourcc(*"mp4v")
        if self.record_frames:
            h,w=self.record_frames[0].shape[:2]
            out=cv2.VideoWriter(filename,fourcc,self.record_fps,(w,h))
            for frame in self.record_frames: out.write(frame)
            out.release()

    def _record_frame_if_active(self):
        if not self.recording: return
        if self.record_canvas_only: pix=self.grab()
        else: pix=QApplication.primaryScreen().grabWindow(self.winId())
        img=pix.toImage()
        ptr=img.bits()
        ptr.setsize(img.byteCount())
        arr=np.array(ptr).reshape(img.height(),img.width(),4)
        arr=cv2.cvtColor(arr,cv2.COLOR_BGRA2BGR)
        self.record_frames.append(arr)
        if len(self.record_frames)>self.record_fps*60: self.record_frames.pop(0)

# ---------------- Color Picker ----------------
class ColorPicker(QWidget):
    def __init__(self, parent_canvas):
        super().__init__()
        self.setFixedSize(200, 200)
        self.canvas = parent_canvas
        self.hue = 0
        self.saturation = 1.0
        self.value = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        center = QPointF(self.width()/2, self.height()/2)
        radius = min(self.width(), self.height())/2 - 5
        # Hue ring
        for angle in range(360):
            color = QColor()
            color.setHsv(angle, 255, 255)
            painter.setPen(color)
            x1 = center.x() + math.cos(math.radians(angle)) * (radius*0.8)
            y1 = center.y() + math.sin(math.radians(angle)) * (radius*0.8)
            x2 = center.x() + math.cos(math.radians(angle)) * radius
            y2 = center.y() + math.sin(math.radians(angle)) * radius
            painter.drawLine(QPointF(x1,y1), QPointF(x2,y2))
        # Hexagon
        hex_radius = radius*0.6
        polygon = QPolygonF()
        for i in range(6):
            angle = math.radians(60*i - 30)
            x = center.x() + math.cos(angle)*hex_radius
            y = center.y() + math.sin(angle)*hex_radius
            polygon.append(QPointF(x,y))
        painter.setPen(Qt.GlobalColor.black)
        painter.drawPolygon(polygon)
        painter.setBrush(self.current_qcolor())
        painter.drawEllipse(center,10,10)

    def current_qcolor(self):
        c = QColor()
        c.setHsv(self.hue,int(self.saturation*255),int(self.value*255))
        return c

    def mousePressEvent(self,e):
        self._update_color_from_pos(e.position())
    def mouseMoveEvent(self,e):
        if e.buttons() & Qt.MouseButton.LeftButton:
            self._update_color_from_pos(e.position())
    def _update_color_from_pos(self,pos):
        center = QPointF(self.width()/2,self.height()/2)
        dx = pos.x()-center.x()
        dy = pos.y()-center.y()
        distance = math.hypot(dx,dy)
        radius = min(self.width(), self.height())/2-5
        if distance>radius*0.8 and distance<=radius:
            self.hue=int(math.degrees(math.atan2(dy,dx)))%360
        elif distance<=radius*0.6:
            self.saturation = min(max((dx+radius*0.6)/(radius*1.2),0),1)
            self.value = min(max((dy+radius*0.6)/(radius*1.2),0),1)
        self.canvas.brush_color=self.current_qcolor()
        self.update()

# ---------------- Brush Preview ----------------
class BrushPreview(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedSize(60, 60)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), Qt.GlobalColor.white)
        c = QColor(self.canvas.brush_color)
        c.setAlpha(self.canvas.brush_opacity)
        painter.setBrush(c)
        painter.setPen(Qt.PenStyle.NoPen)
        center = QPointF(self.width()/2, self.height()/2)
        size = self.canvas.brush_size
        painter.drawEllipse(center, size/2, size/2)

# ---------------- Main App ----------------
class PaletteaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palettea")
        self.layers=[Layer("Layer 1")]
        self.undo_stack,self.redo_stack=[],[]
        self.canvas=Canvas(self.layers,self.undo_stack,self.redo_stack)
        self.init_ui()
        self.show()

    def init_ui(self):
        central=QWidget()
        layout=QHBoxLayout()
        central.setLayout(layout)
        layout.addWidget(self.canvas)
        side_panel=QVBoxLayout()

        # Color Picker
        self.color_picker=ColorPicker(self.canvas)
        side_panel.addWidget(QLabel("Color Picker"))
        side_panel.addWidget(self.color_picker)

        # Brush Preview
        self.brush_preview=BrushPreview(self.canvas)
        side_panel.addWidget(QLabel("Brush Preview"))
        side_panel.addWidget(self.brush_preview)

        # Layers
        self.layer_list=QListWidget()
        self.layer_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.layer_list.model().rowsMoved.connect(self.update_layer_order)
        side_panel.addWidget(QLabel("Layers"))
        side_panel.addWidget(self.layer_list)
        self.refresh_layers()
        add_btn=QPushButton("Add Layer")
        add_btn.clicked.connect(self.add_layer)
        del_btn=QPushButton("Delete Layer")
        del_btn.clicked.connect(self.delete_layer)
        side_panel.addWidget(add_btn)
        side_panel.addWidget(del_btn)

        # Brush controls
        side_panel.addWidget(QLabel("Brush Size"))
        self.brush_slider=QSlider(Qt.Orientation.Horizontal)
        self.brush_slider.setMinimum(1)
        self.brush_slider.setMaximum(50)
        self.brush_slider.setValue(self.canvas.brush_size)
        self.brush_slider.valueChanged.connect(lambda v: [setattr(self.canvas,'brush_size',v), self.brush_preview.update()])
        side_panel.addWidget(self.brush_slider)

        side_panel.addWidget(QLabel("Brush Type"))
        self.brush_type_btn=QPushButton("Round")
        self.brush_type_btn.clicked.connect(lambda: [self.toggle_brush(), self.brush_preview.update()])
        side_panel.addWidget(self.brush_type_btn)

        layout.addLayout(side_panel)
        self.setCentralWidget(central)
        self.create_menus()

    # ---------------- Layer Functions ----------------
    def refresh_layers(self):
        self.layer_list.clear()
        for layer in reversed(self.layers):
            item=QListWidgetItem()
            item.setText(layer.name)
            self.layer_list.addItem(item)
        self.canvas.current_layer=self.layers[-1]

    def add_layer(self):
        name=f"Layer {len(self.layers)+1}"
        l=Layer(name)
        self.layers.append(l)
        self.refresh_layers()

    def delete_layer(self):
        idx=self.layer_list.currentRow()
        if idx>=0 and len(self.layers)>1:
            self.layers.pop(len(self.layers)-1-idx)
            self.refresh_layers()

    def update_layer_order(self):
        new_order=[]
        for i in range(self.layer_list.count()):
            name=self.layer_list.item(i).text()
            for l in self.layers:
                if l.name==name:
                    new_order.insert(0,l)
        self.layers=new_order
        self.canvas.update()

    # ---------------- Brush ----------------
    def toggle_brush(self):
        types=["round","soft","scatter"]
        current=types.index(self.canvas.brush_type) if self.canvas.brush_type in types else 0
        new=current+1 if current+1<len(types) else 0
        self.canvas.brush_type=types[new]
        self.brush_type_btn.setText(types[new].capitalize())

    # ---------------- Menus ----------------
    def create_menus(self):
        menu=self.menuBar()
        file_menu=menu.addMenu("File")
        new_action=QAction("New Canvas",self)
        new_action.triggered.connect(lambda:self.new_canvas())
        export_action=QAction("Export PNG",self)
        export_action.triggered.connect(lambda:self.export_png())
        rec_canvas=QAction("Record Canvas Only",self)
        rec_canvas.triggered.connect(lambda:self.canvas.start_recording(True))
        rec_full=QAction("Record Entire App",self)
        rec_full.triggered.connect(lambda:self.canvas.start_recording(False))
        stop_rec=QAction("Stop Recording",self)
        stop_rec.triggered.connect(lambda:self.canvas.stop_recording())
        exit_action=QAction("Exit",self)
        exit_action.triggered.connect(lambda:self.close())
        for act in [new_action, export_action, rec_canvas, rec_full, stop_rec, exit_action]: file_menu.addAction(act)

        sym_menu=menu.addMenu("Symmetry")
        for mode in ["none","horizontal","vertical","both"]:
            a=QAction(mode.capitalize(),self)
            a.triggered.connect(lambda checked,m=mode:setattr(self.canvas,"symmetry_mode",m))
            sym_menu.addAction(a)

        edit_menu=menu.addMenu("Edit")
        undo_act=QAction("Undo",self)
        undo_act.triggered.connect(self.canvas.undo)
        redo_act=QAction("Redo",self)
        redo_act.triggered.connect(self.canvas.redo)
        edit_menu.addAction(undo_act)
        edit_menu.addAction(redo_act)

    # ---------------- File ----------------
    def new_canvas(self):
        self.layers=[Layer("Layer 1")]
        self.canvas.layers=self.layers
        self.refresh_layers()
        self.canvas.update()

    def export_png(self):
        path,_=QFileDialog.getSaveFileName(self,"Export PNG","","PNG Image (*.png)")
        if not path: return
        img=QImage(CANVAS_W,CANVAS_H,QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.white)
        painter=QPainter(img)
        for l in self.layers:
            if l.visible:
                painter.drawPixmap(0,0,l.pixmap)
        painter.end()
        img.save(path)

# ---------------- Run App ----------------
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=PaletteaApp()
    sys.exit(app.exec())
