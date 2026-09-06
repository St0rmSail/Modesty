"""Keep the local process alive while the visual Study is deliberately hidden."""

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAY_ICON = PROJECT_ROOT / "Assets" / "Modesty" / "Standing" / "modesty_standing_v1.png"


class BackgroundPresenceHost(QObject):
    """Own the Windows tray restore surface without starting new duties."""

    state_changed = Signal(str)

    def __init__(self, window, presence=None):
        super().__init__(window)
        self.window = window
        self.presence = presence
        self.explicit_quit = False
        self.tray = QSystemTrayIcon(self)
        icon = QIcon(str(TRAY_ICON))
        if icon.isNull():
            icon = window.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.setToolTip("Modesty — running in the background")

        menu = QMenu(window)
        show_action = QAction("Show the Study", menu)
        show_action.triggered.connect(self.restore)
        menu.addAction(show_action)
        quit_action = QAction("Quit Modesty", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)

    @property
    def available(self) -> bool:
        return QSystemTrayIcon.isSystemTrayAvailable()

    def start(self):
        if self.available:
            QApplication.instance().setQuitOnLastWindowClosed(False)
            self.tray.show()

    def hide(self) -> bool:
        if not self.available:
            return False
        self.window.hide()
        if self.presence is not None:
            self.presence.set_presence("background")
        self.state_changed.emit("background")
        self.tray.showMessage(
            "Modesty is still here",
            "The Study is hidden. Use the tray icon to bring it back.",
            QSystemTrayIcon.MessageIcon.Information,
            3500,
        )
        return True

    def restore(self):
        self.window.showMaximized()
        self.window.raise_()
        self.window.activateWindow()
        if self.presence is not None:
            self.presence.set_presence("present")
        self.state_changed.emit("present")

    def quit(self):
        self.explicit_quit = True
        self.tray.hide()
        QApplication.instance().quit()

    def handle_close(self, event) -> bool:
        if self.explicit_quit or not self.available:
            return False
        event.ignore()
        self.hide()
        return True

    def _tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.restore()
