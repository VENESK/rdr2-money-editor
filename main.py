import sys
import webbrowser
import ctypes
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSpinBox, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QRectF, QTimer
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QPixmap, QPainterPath, QFontDatabase
from patcher import attach_to_game, set_money

# App configuration
APP_TITLE = "RDR2 Money Changer"
CONTENT_SIZE = (340, 420)  # Size of the visible UI
WINDOW_SIZE = (380, 460)   # Larger window to fit glow effect
SPACING = 18
MARGINS = (18, 18, 18, 18)

# Colors & styling
BG_GRADIENT = {
    'start': '#1A0000',  # Dark red
    'end': '#000000'     # Black
}
GLOW_COLOR = QColor('#FF4136')  # Red glow
GLOW_COLOR.setAlpha(220)

BUTTON_GRADIENT = {
    'start': '#D32F2F',  # Dark red
    'end': '#B71C1C'     # Darker red
}
BUTTON_HOVER = {
    'start': '#E53935',  # Bright red
    'end': '#C62828'
}

# Money input settings
MONEY_DEFAULT = 1000
MONEY_MAX = 999999999
INPUT_SIZE = {
    'width': 180,
    'height': 12
}

# Button sizes
MAIN_BUTTON_SIZE = {
    'width': 160,
    'height': 50
}
LINK_BUTTON_SIZE = {
    'width': 96,
    'height': 36
}

# Social links
DISCORD_LINK = 'https://discord.gg/dYu4Gnm7Ke'
WEBSITE_LINK = 'https://0ixe.site'

# Glow animation config
GLOW_DURATION = 1500
GLOW_MIN = 15
GLOW_MAX = 25

# UI Styles
STYLES = f"""
    #rootWidget {{
        border-radius: 24px;
        background-color: {BG_GRADIENT['end']};
    }}
    QWidget {{
        background: transparent;
        color: white;
        font-family: 'Chinese Rocks', 'Arial Black', 'Segoe UI', Arial;
        font-size: 48px;
    }}
    QWidget#mainWidget, QWidget#linkContainer {{
        background: transparent;
        margin: 0px;
    }}
    QPushButton#closeButton {{
        background-color: rgba(255, 255, 255, 0.1);
        border: none;
        border-radius: 10px;
        font-weight: bold;
        font-size: 24px;
    }}
    QPushButton#closeButton:hover {{
        background-color: rgba(231, 76, 60, 0.8);
    }}
    QLabel#title {{
        color: #ffffff;
        font-size: 32px;
        font-weight: bold;
        background: transparent;
        padding: 6px;
    }}
    QLabel#dollar {{
        color: {GLOW_COLOR.name()};
        font-size: 36px;
        font-weight: bold;
        background: transparent;
        padding-right: 6px;
    }}
    QSpinBox {{
        background: #190001;
        border: 2px solid {GLOW_COLOR.name()};
        border-radius: 24px;
        padding: 6px 12px;
        min-width: {INPUT_SIZE['width']}px;
        min-height: {INPUT_SIZE['height']}px;
        font-size: 26px;
        font-weight: bold;
        color: white;
    }}
    QSpinBox:hover {{
        background: #1f0102;
        border: 2px solid {BUTTON_HOVER['start']};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{ 
        width: 0;
    }}
    QPushButton#mainButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 {BUTTON_GRADIENT['start']}, 
                                  stop:1 {BUTTON_GRADIENT['end']});
        border: none;
        border-radius: 24px;
        padding: 12px;
        font-size: 22px;
        font-weight: bold;
        min-height: {MAIN_BUTTON_SIZE['height']}px;
        min-width: {MAIN_BUTTON_SIZE['width']}px;
    }}
    QPushButton#mainButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 {BUTTON_HOVER['start']}, 
                                  stop:1 {BUTTON_HOVER['end']});
    }}
    QPushButton#linkButton {{
        background: rgba(183, 28, 28, 0.15);
        border: 2px solid {BUTTON_GRADIENT['start']};
        border-radius: 20px;
        padding: 6px;
        font-size: 17px;
        font-weight: bold;
        min-height: {LINK_BUTTON_SIZE['height']}px;
        min-width: {LINK_BUTTON_SIZE['width']}px;
    }}
    QPushButton#linkButton:hover {{
        background: rgba(183, 28, 28, 0.25);
        border-color: {BUTTON_HOVER['start']};
    }}
    #creditLabel {{
        font-size: 12px;
        color: rgba(255, 255, 255, 180);
        font-weight: bold;
    }}
"""

# Helper functions and widgets
def create_text_shadow(widget):
    """Adds a drop shadow effect to text"""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(8)
    shadow.setColor(QColor(0, 0, 0, 200))
    shadow.setOffset(4, 4)
    widget.setGraphicsEffect(shadow)

class BackgroundImageWidget(QWidget):
    """Widget for displaying the background image"""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 20, 20)
        painter.setClipPath(path)
        
        if self.pixmap.isNull():
            super().paintEvent(event)
            return

        scaled_pixmap = self.pixmap.scaled(self.size(), 
                                           Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                           Qt.TransformationMode.SmoothTransformation)
        
        x = (self.width() - scaled_pixmap.width()) / 2
        y = (self.height() - scaled_pixmap.height()) / 2
        
        painter.drawPixmap(int(x), int(y), scaled_pixmap)

class DraggableWindow(QWidget):
    """Main window with drag functionality"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.pos())
            if not child or not isinstance(child, (QPushButton, QSpinBox)):
                 self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

def create_glow_animation(widget, color):
    """Creates pulsing glow effect"""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(color)
    effect.setOffset(0, 0)
    effect.setBlurRadius(GLOW_MIN)
    widget.setGraphicsEffect(effect)
    
    anim = QPropertyAnimation(effect, b"blurRadius")
    anim.setDuration(GLOW_DURATION)
    anim.setStartValue(GLOW_MIN)
    anim.setEndValue(GLOW_MAX)
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    
    def reverse_animation():
        anim.setDirection(QAbstractAnimation.Direction.Backward 
                         if anim.direction() == QAbstractAnimation.Direction.Forward 
                         else QAbstractAnimation.Direction.Forward)
        anim.start()
    
    anim.finished.connect(reverse_animation)
    anim.start()
    
    return anim

def resource_path(relative_path):
    """Gets absolute path to resource files"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    """Main application entry point"""

    # Request admin privileges
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

    app = QApplication(sys.argv)

    # Load custom font
    font_path = resource_path('res/chinese rocks.ttf')
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        print(f"Successfully loaded font: '{font_family}'")
    else:
        print(f"Warning: Could not load '{os.path.basename(font_path)}'. Using system default fonts.")

    # Create main window
    window = DraggableWindow()
    window.setWindowTitle(APP_TITLE)

    app_icon = QIcon(resource_path('res/icon.ico'))
    window.setWindowIcon(app_icon)

    window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.setFixedSize(*WINDOW_SIZE)
    
    # Create root widget with background
    root_widget = BackgroundImageWidget(resource_path('res/bg.png'), window)
    root_widget.setObjectName("rootWidget")
    root_widget.setGeometry(
        (WINDOW_SIZE[0] - CONTENT_SIZE[0]) // 2,
        (WINDOW_SIZE[1] - CONTENT_SIZE[1]) // 2,
        *CONTENT_SIZE
    )
    window.setStyleSheet(STYLES)
    
    glow_animation = create_glow_animation(root_widget, GLOW_COLOR)

    # Set up layout
    layout = QVBoxLayout(root_widget)
    layout.setSpacing(SPACING)
    layout.setContentsMargins(*MARGINS)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Add close button
    close_btn = QPushButton("✕", objectName="closeButton", parent=root_widget)
    close_btn.setFixedSize(30, 30)
    close_btn.move(CONTENT_SIZE[0] - close_btn.width() - 8, 8)
    close_btn.clicked.connect(app.quit)

    # Add title
    title = QLabel(f"{APP_TITLE}", objectName="title")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    create_text_shadow(title)
    layout.addWidget(title)
    
    layout.addSpacing(12)
    
    # Add money input
    money_container = QWidget(objectName="mainWidget")
    money_layout = QHBoxLayout(money_container)
    money_layout.setContentsMargins(0, 0, 0, 0)
    money_layout.setSpacing(5)
    money_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    dollar_label = QLabel("$", objectName="dollar")
    create_text_shadow(dollar_label)
    
    money_input = QSpinBox()
    money_input.setRange(0, MONEY_MAX)
    money_input.setValue(MONEY_DEFAULT)
    money_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
    money_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
    
    money_layout.addWidget(dollar_label)
    money_layout.addWidget(money_input)
    layout.addWidget(money_container)
    
    layout.addSpacing(18)

    # Add apply button
    button_container = QWidget(objectName="mainWidget")
    button_layout = QHBoxLayout(button_container)
    button_layout.setContentsMargins(0, 0, 0, 0)
    
    apply_btn = QPushButton("🔒 Apply Changes", objectName="mainButton")
    button_layout.addWidget(apply_btn)
    layout.addWidget(button_container)

    layout.addSpacing(18)

    # Add social links
    links_outer = QWidget(objectName="linkContainer")
    links_layout = QHBoxLayout(links_outer)
    links_layout.setContentsMargins(0, 0, 0, 0)
    links_layout.setSpacing(10)
    links_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    links = {"💬 Discord": DISCORD_LINK, "🌐 Website": WEBSITE_LINK}
    for text, url in links.items():
        btn = QPushButton(text, objectName="linkButton")
        btn.setFixedWidth(100)
        btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
        create_text_shadow(btn)
        links_layout.addWidget(btn)
    
    layout.addWidget(links_outer)

    # Add credit label
    credit_label = QLabel("discord@0ixe", objectName="creditLabel", parent=root_widget)
    credit_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
    create_text_shadow(credit_label)
    
    credit_label.adjustSize()
    credit_x = CONTENT_SIZE[0] - credit_label.width() - 15
    credit_y = CONTENT_SIZE[1] - credit_label.height() - 10
    credit_label.move(credit_x, credit_y)

    # Set up game connection
    attach_to_game()

    def handle_apply_changes():
        """Handles money value changes"""
        original_text = apply_btn.text()
        amount_to_set = money_input.value()

        apply_btn.setEnabled(False)
        apply_btn.setText("Working...")

        success = set_money(amount_to_set)

        if success:
            apply_btn.setText("Done!")
        else:
            apply_btn.setText("Failed!")
        
        QTimer.singleShot(2000, lambda: (
            apply_btn.setEnabled(True),
            apply_btn.setText(original_text)
        ))

    apply_btn.clicked.connect(handle_apply_changes)

    # Start app
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
