from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QTabWidget, QWidget


class UiAnimationService:
    """Small, non-blocking UI transitions for Initra v3.1.

    Animations are deliberately short so the application stays responsive.
    They respect the existing `animations` setting and keep animation objects
    alive until completion to avoid Qt/Python lifetime issues.
    """

    def __init__(self, window):
        self.window = window
        self._animations = []
        self._last_tab_index = {}

    def enabled(self) -> bool:
        return bool(getattr(self.window, "settings", {}).get("animations", True))

    def install(self):
        for tabs in self.window.findChildren(QTabWidget):
            self._last_tab_index[tabs] = tabs.currentIndex()
            tabs.currentChanged.connect(lambda index, widget=tabs: self._tab_changed(widget, index))

        # Give the first rendered page a subtle entrance after the event loop
        # has painted it. Top-level navigation already has the built-in fade in
        # MainWindow; this initial entrance makes startup feel consistent.
        QTimer.singleShot(0, self.animate_widget_entrance)

    def animate_widget_entrance(self):
        if not self.enabled():
            return
        pages = getattr(self.window, "pages", None)
        if pages is not None:
            self.fade_in(pages.currentWidget(), 220, 0.72)

    def _tab_changed(self, tabs: QTabWidget, index: int):
        previous = self._last_tab_index.get(tabs, index)
        self._last_tab_index[tabs] = index
        if not self.enabled() or previous == index:
            return
        widget = tabs.currentWidget()
        if widget is not None:
            self.fade_in(widget, 170, 0.58)

    def fade_in(self, widget: QWidget | None, duration: int = 180, start: float = 0.6):
        if widget is None or not self.enabled():
            return

        # Do not stack effects if the user clicks through tabs very quickly.
        old_effect = widget.graphicsEffect()
        if old_effect is not None:
            widget.setGraphicsEffect(None)

        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(start)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self.window)
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animations.append(animation)

        def finish():
            if widget.graphicsEffect() is effect:
                widget.setGraphicsEffect(None)
            if animation in self._animations:
                self._animations.remove(animation)

        animation.finished.connect(finish)
        animation.start()
