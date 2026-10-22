"""Line icons for the sidebar, drawn as SVG so they stay crisp and match the theme."""
from __future__ import annotations

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_PATHS = {
    "Dashboard": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="4" rx="1.5"/><rect x="14" y="11" width="7" height="10" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/>',
    "Setup": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "Software": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12L4 7.5M12 12v9"/>',
    "System": '<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="2.3"/><circle cx="15" cy="17" r="2.3"/>',
    "Maintenance": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',
    "Tools": '<path d="M14.5 6.5a4 4 0 00-5 5L3.5 17.5l3 3 6-6a4 4 0 005-5l-2.5 2.5-2-2z"/>',
    "Settings": '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M18.4 5.6l-1.8 1.8M7.4 16.6l-1.8 1.8"/>',
}


def _pixmap(name: str, color: str, size: int) -> QPixmap:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f'{_PATHS[name]}</svg>'
    )
    ratio = 2  # crisp on HiDPI screens
    pix = QPixmap(size * ratio, size * ratio)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    QSvgRenderer(QByteArray(svg.encode())).render(painter)
    painter.end()
    pix.setDevicePixelRatio(ratio)
    return pix


def nav_icon(name: str, size: int = 18) -> QIcon:
    """Grey icon normally, pink when the (checkable) button is checked."""
    icon = QIcon()
    icon.addPixmap(_pixmap(name, "#A29BB5", size), QIcon.Normal, QIcon.Off)
    icon.addPixmap(_pixmap(name, "#F178B6", size), QIcon.Normal, QIcon.On)
    return icon
