from __future__ import annotations

from pathlib import Path
from datetime import datetime
import subprocess

from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QIcon, QPixmap, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QScrollArea, QCheckBox, QLineEdit, QComboBox, QDialog, QTabWidget, QFileDialog, QPlainTextEdit,
    QMessageBox, QProgressBar, QGraphicsOpacityEffect, QSizePolicy
)

from app.services.system_info import SystemInfoService
from app.services.dotfiles_service import DotfilesService
from app.services.service_manager import ServiceManager
from app.services.settings_service import SettingsService
from app.services.maintenance_service import MaintenanceService
from app.services.software_service import SoftwareService
from app.services.system_tools_service import SystemToolsService
from app.services.health_service import HealthService
from app.services.backup_service import BackupService
from app.services.profile_service import ProfileService
from app.services.transfer_service import TransferService
from app.services.command_preview_service import CommandPreviewService
from app.services.distro_service import DistroService
from app.services.notification_service import NotificationService
from app.services.history_service import HistoryService
from app.models.package_catalog import PACKAGE_CATALOG


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"


def label(text: str, role: str = "") -> QLabel:
    w = QLabel(text)
    if role:
        w.setObjectName(role)
    w.setWordWrap(True)
    return w


class Card(QFrame):
    def __init__(self, role: str = "card"):
        super().__init__()
        self.setObjectName(role)


class CommandWorker(QThread):
    line = Signal(str)
    finished_code = Signal(int)

    def __init__(self, command: list[str]):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            if self.process.stdout:
                for line_text in self.process.stdout:
                    self.line.emit(line_text.rstrip())
            self.finished_code.emit(self.process.wait())
        except Exception as exc:
            self.line.emit(str(exc))
            self.finished_code.emit(1)

    def cancel(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.info = SystemInfoService()
        self.dotfiles = DotfilesService()
        self.settings_service = SettingsService()
        self.settings = self.settings_service.load()
        self.current_profile = self.settings.get("profile", "Developer")
        self.selected_extra: set[str] = set()
        self.worker = None
        self.maintenance = MaintenanceService()
        self.software = SoftwareService()
        self.system_tools = SystemToolsService()
        self.health = HealthService()
        self.backups = BackupService()
        self.profiles = ProfileService()
        self.transfer = TransferService()
        self.command_preview = CommandPreviewService()
        self.distro = DistroService()
        self.notifications = NotificationService()
        self.history_service = HistoryService()

        self.setWindowTitle("Initra Linux Setup Manager")
        self.setWindowIcon(QIcon(str(ASSETS / "initra_logo.png")))
        self.resize(1440, 900)
        self.setMinimumSize(1120, 720)

        self.root = QWidget()
        self.root.setObjectName("root")
        self.setCentralWidget(self.root)
        self.shell = QHBoxLayout(self.root)
        self.shell.setContentsMargins(0, 0, 0, 0)
        self.shell.setSpacing(0)

        self.build_sidebar()

        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        self.shell.addWidget(self.pages, 1)

        # v3.0: seven clean top-level sections. Existing features live in tabs.
        self.section_tabs = {}
        self.pages.addWidget(self.build_dashboard_section())
        self.pages.addWidget(self.build_setup_section())
        self.pages.addWidget(self.build_software_section())
        self.pages.addWidget(self.build_system_section())
        self.pages.addWidget(self.build_maintenance_section())
        self.pages.addWidget(self.build_tools_section())
        self.pages.addWidget(self.build_settings_section())

        self.select_page(0)
        self.command_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.command_shortcut.activated.connect(self.open_command_palette)
        QTimer.singleShot(250, self.maybe_show_first_run_wizard)
        self.build_welcome()

    # ---------- shell ----------
    def build_sidebar(self):
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(248)

        outer = QVBoxLayout(side)
        outer.setContentsMargins(16, 18, 16, 16)
        outer.setSpacing(12)

        brand = QHBoxLayout()
        brand.setSpacing(10)
        icon = QLabel()
        pix = QPixmap(str(ASSETS / "initra_logo.png"))
        icon.setPixmap(pix.scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setFixedSize(42, 42)
        brand.addWidget(icon)
        brand.addWidget(label("Initra", "brand"))
        brand.addStretch()
        outer.addLayout(brand)

        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("sidebarScroll")
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setFrameShape(QFrame.NoFrame)

        nav_body = QWidget()
        nav_body.setObjectName("sidebarNavBody")
        nav_lay = QVBoxLayout(nav_body)
        nav_lay.setContentsMargins(0, 4, 4, 4)
        nav_lay.setSpacing(5)

        self.nav = []
        entries = [
            ("▦", "Dashboard"),
            ("▣", "Setup"),
            ("▤", "Software"),
            ("◈", "System"),
            ("✦", "Maintenance"),
            ("⌘", "Tools"),
            ("⚙", "Settings"),
        ]
        for i, (icon_text, name) in enumerate(entries):
            button = QPushButton(f"  {icon_text}   {name}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(38)
            button.clicked.connect(lambda checked=False, index=i: self.select_page(index))
            nav_lay.addWidget(button)
            self.nav.append(button)

        nav_lay.addStretch()
        nav_scroll.setWidget(nav_body)
        outer.addWidget(nav_scroll, 1)

        system_card = Card("systemCard")
        system_card.setMinimumHeight(92)
        system_layout = QVBoxLayout(system_card)
        system_layout.setContentsMargins(13, 11, 13, 11)
        system_layout.setSpacing(4)
        system_layout.addWidget(label("THIS SYSTEM", "eyebrow"))
        system_layout.addWidget(label(self.distro.info["pretty_name"], "systemTitle"))
        system_layout.addWidget(label(
            f'{self.distro.info["package_manager"]}  •  '
            f'{self.distro.info["architecture"]}  •  {self.info.disk_free()}',
            "systemValue"
        ))
        outer.addWidget(system_card)

        self.shell.addWidget(side)

    def page(self):
        w = QWidget()
        w.setObjectName("page")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(38, 28, 38, 28)
        lay.setSpacing(14)
        return w, lay

    def header(self, eyebrow, title, subtitle, badge=None):
        row = QHBoxLayout()
        text = QVBoxLayout()
        text.setSpacing(3)
        text.addWidget(label(eyebrow, "eyebrow"))
        text.addWidget(label(title, "pageTitle"))
        text.addWidget(label(subtitle, "subtitle"))
        row.addLayout(text, 1)
        if badge:
            row.addWidget(label(badge, "accentTag"), 0, Qt.AlignTop)
        return row

    def select_page(self, index):
        index = max(0, min(index, self.pages.count() - 1))
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav):
            button.setChecked(i == index)
        self.refresh_current_section(index)
        self.fade(self.pages.currentWidget())

    def refresh_current_section(self, index):
        # Refresh only lightweight/current data. Individual tab changes refresh their page.
        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.refresh_setup()
        elif index == 2:
            self.refresh_software()
        elif index == 3:
            self.refresh_tweaks()
        elif index == 4:
            self.refresh_cleanup()
        elif index == 6:
            self.refresh_settings_controls()

    def open_section(self, section, tab=0):
        self.select_page(section)
        tabs = self.section_tabs.get(section)
        if tabs is not None:
            tabs.setCurrentIndex(tab)

    def refresh_settings_controls(self):
        # Settings controls already reflect persisted values when built.
        return


    def fade(self, widget):
        if not self.settings.get("animations", True):
            return
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(180)
        anim.setStartValue(0.55)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: widget.setGraphicsEffect(None))
        self._fade_anim = anim
        anim.start()

    # ---------- v3.0 grouped navigation ----------
    def _section(self, title, subtitle, tab_specs):
        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(26, 18, 26, 20)
        layout.setSpacing(10)

        heading = QVBoxLayout()
        heading.setSpacing(2)
        heading.addWidget(label(title.upper(), "eyebrow"))
        heading.addWidget(label(title, "pageTitle"))
        heading.addWidget(label(subtitle, "subtitle"))
        layout.addLayout(heading)

        tabs = QTabWidget()
        tabs.setObjectName("sectionTabs")
        tabs.setDocumentMode(True)
        tabs.setUsesScrollButtons(True)

        for tab_name, builder in tab_specs:
            content = builder()

            # Every legacy page already has its own generous outer margins.
            # Inside a section tab those margins made the content too tall and
            # caused buttons/text to be clipped. Reduce them only when nested.
            inner_layout = content.layout()
            if inner_layout is not None:
                inner_layout.setContentsMargins(16, 14, 16, 16)
                inner_layout.setSpacing(10)

            scroll = QScrollArea()
            scroll.setObjectName("sectionContentScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setWidget(content)
            tabs.addTab(scroll, tab_name)

        layout.addWidget(tabs, 1)
        return page, tabs

    def build_dashboard_section(self):
        page, tabs = self._section(
            "Dashboard",
            "Overview, system health and hardware information.",
            [
                ("Overview", self.build_dashboard_page),
                ("Health", self.build_health_page),
                ("System Info", self.build_system_info_page),
            ],
        )
        self.section_tabs[0] = tabs
        tabs.currentChanged.connect(self._dashboard_tab_changed)
        return page

    def _dashboard_tab_changed(self, index):
        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.refresh_health()
        elif index == 2:
            self.refresh_system_info()

    def build_setup_section(self):
        page, tabs = self._section(
            "Setup",
            "Plan a setup, manage profiles, recovery points and dotfiles.",
            [
                ("Setup Plan", self.build_setup_page),
                ("Profiles", self.build_profiles_page),
                ("Backup & Restore", self.build_backups_page),
                ("Dotfiles", self.build_dotfiles_page),
            ],
        )
        self.section_tabs[1] = tabs
        tabs.currentChanged.connect(self._setup_tab_changed)
        return page

    def _setup_tab_changed(self, index):
        if index == 0:
            self.refresh_setup()
        elif index == 1:
            self.refresh_profiles()
        elif index == 2:
            self.refresh_backups()

    def build_software_section(self):
        page, tabs = self._section(
            "Software",
            "Applications, updates, repositories and hardware drivers.",
            [
                ("Applications", self.build_software_page),
                ("Updates", self.build_updates_page),
                ("Repositories", self.build_repositories_page),
                ("Drivers", self.build_drivers_page),
            ],
        )
        self.section_tabs[2] = tabs
        tabs.currentChanged.connect(self._software_tab_changed)
        return page

    def _software_tab_changed(self, index):
        if index == 0:
            self.refresh_software()
        elif index == 1:
            self.refresh_updates()
        elif index == 2:
            self.refresh_repositories()
        elif index == 3:
            self.refresh_drivers()

    def build_system_section(self):
        page, tabs = self._section(
            "System",
            "Desktop tweaks, startup applications and system services.",
            [
                ("Tweaks", self.build_tweaks_page),
                ("Startup Apps", self.build_startup_page),
                ("Services", self.build_services_page),
            ],
        )
        self.section_tabs[3] = tabs
        tabs.currentChanged.connect(self._system_tab_changed)
        return page

    def _system_tab_changed(self, index):
        if index == 0:
            self.refresh_tweaks()
        elif index == 1:
            self.refresh_startup()

    def build_maintenance_section(self):
        page, tabs = self._section(
            "Maintenance",
            "Storage cleanup, diagnostics and activity history.",
            [
                ("Cleanup", self.build_cleanup_page),
                ("Diagnostics", self.build_diagnostics_page),
                ("History", self.build_history_page),
            ],
        )
        self.section_tabs[4] = tabs
        tabs.currentChanged.connect(self._maintenance_tab_changed)
        return page

    def _maintenance_tab_changed(self, index):
        if index == 0:
            self.refresh_cleanup()
        elif index == 1:
            self.refresh_diagnostics_summary()
        elif index == 2:
            self.refresh_history()

    def build_diagnostics_page(self):
        page, layout = self.page()
        layout.addLayout(self.header(
            "DIAGNOSTICS", "Maintenance diagnostics",
            "Quick access to system health and recovery tools.", "v3.0"
        ))
        card = Card("dashboardCard")
        row = QHBoxLayout(card)
        text = QVBoxLayout()
        text.addWidget(label("System Health Check", "sectionTitle"))
        self.maintenance_diag_status = label(
            "Run the full Health Check from Dashboard to inspect packages, services, storage and network.",
            "muted"
        )
        text.addWidget(self.maintenance_diag_status)
        row.addLayout(text, 1)
        health = QPushButton("Open Health Check")
        health.setObjectName("primaryButton")
        health.clicked.connect(lambda: self.open_section(0, 1))
        row.addWidget(health)
        layout.addWidget(card)

        backup = Card("dashboardCard")
        brow = QHBoxLayout(backup)
        btext = QVBoxLayout()
        btext.addWidget(label("Recovery", "sectionTitle"))
        btext.addWidget(label("Create or restore a configuration restore point before major changes.", "muted"))
        brow.addLayout(btext, 1)
        b = QPushButton("Open Backup & Restore")
        b.setObjectName("secondaryButton")
        b.clicked.connect(lambda: self.open_section(1, 2))
        brow.addWidget(b)
        layout.addWidget(backup)
        layout.addStretch()
        return page

    def refresh_diagnostics_summary(self):
        if hasattr(self, "maintenance_diag_status"):
            self.maintenance_diag_status.setText(
                "Health Check is available under Dashboard → Health. Cleanup remains selective and preview-first."
            )

    def build_tools_section(self):
        page, tabs = self._section(
            "Tools",
            "Transfer setups, preview commands and inspect Linux compatibility.",
            [
                ("Import / Export", self.build_transfer_tools_page),
                ("Command Preview", self.build_preview_tools_page),
                ("Linux Compatibility", self.build_compatibility_tools_page),
            ],
        )
        self.section_tabs[5] = tabs
        return page

    def build_transfer_tools_page(self):
        page, layout = self.page()
        layout.addLayout(self.header(
            "TRANSFER", "Import & export",
            "Move reusable Initra profiles between Linux installations.", "JSON + SHELL"
        ))
        card = Card("dashboardCard")
        cl = QVBoxLayout(card)
        cl.addWidget(label("Portable profiles", "sectionTitle"))
        cl.addWidget(label(
            "Import a .json profile or export one of your profiles as JSON / shell script.",
            "muted"
        ))
        row = QHBoxLayout()
        imp = QPushButton("Import profile .json")
        imp.setObjectName("primaryButton")
        imp.clicked.connect(self.import_profile)
        profiles = QPushButton("Open Profiles")
        profiles.setObjectName("secondaryButton")
        profiles.clicked.connect(lambda: self.open_section(1, 1))
        row.addWidget(imp)
        row.addWidget(profiles)
        row.addStretch()
        cl.addLayout(row)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def build_preview_tools_page(self):
        page, layout = self.page()
        layout.addLayout(self.header(
            "COMMANDS", "Command Preview",
            "Review generated commands before applying a setup.", "SAFE PREVIEW"
        ))
        card = Card("dashboardCard")
        cl = QVBoxLayout(card)
        cl.addWidget(label("Preview a profile", "sectionTitle"))
        cl.addWidget(label(
            "Choose a profile from Setup → Profiles and press Preview. Nothing is executed in preview mode.",
            "muted"
        ))
        button = QPushButton("Open Profiles")
        button.setObjectName("primaryButton")
        button.clicked.connect(lambda: self.open_section(1, 1))
        cl.addWidget(button, 0, Qt.AlignLeft)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def build_compatibility_tools_page(self):
        page, layout = self.page()
        info = self.distro.info
        layout.addLayout(self.header(
            "LINUX", "Compatibility",
            "Detected distribution and package-management capabilities.", "AUTO-DETECTED"
        ))
        card = Card("distroCard")
        cl = QVBoxLayout(card)
        cl.addWidget(label(info["pretty_name"], "sectionTitle"))
        for key, value in [
            ("Family", info["family"]),
            ("Package manager", info["package_manager"]),
            ("Architecture", info["architecture"]),
            ("Kernel", info["kernel"]),
            ("Desktop", info["desktop"]),
            ("Session", info["session"]),
        ]:
            row = QHBoxLayout()
            row.addWidget(label(key, "muted"))
            row.addStretch()
            row.addWidget(label(str(value), "dashboardValue"))
            cl.addLayout(row)
        details = QPushButton("Compatibility details")
        details.setObjectName("secondaryButton")
        details.clicked.connect(self.show_linux_compatibility)
        cl.addWidget(details, 0, Qt.AlignLeft)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def build_settings_section(self):
        page, tabs = self._section(
            "Settings",
            "General preferences, behavior and information about Initra.",
            [
                ("General", self.build_settings_page),
                ("About", self.build_about_page),
            ],
        )
        self.section_tabs[6] = tabs
        return page

    def build_about_page(self):
        page, layout = self.page()
        layout.addLayout(self.header(
            "ABOUT", "Initra Linux Setup Manager",
            "Your Linux. Ready your way.", "v3.0"
        ))
        card = Card("dashboardCard")
        cl = QVBoxLayout(card)
        logo = QLabel()
        pix = QPixmap(str(ASSETS / "initra_logo.png"))
        logo.setPixmap(pix.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        cl.addWidget(logo, 0, Qt.AlignLeft)
        cl.addWidget(label("Initra 3.0 Stable", "pageTitle"))
        cl.addWidget(label(
            "A unified Linux setup, software, maintenance and configuration manager.",
            "muted"
        ))
        cl.addWidget(label(
            f'Detected: {self.distro.info["pretty_name"]} • {self.distro.info["package_manager"]} • '
            f'{self.distro.info["architecture"]}',
            "profileMeta"
        ))
        layout.addWidget(card)
        layout.addStretch()
        return page

    def notify_user(self, title, message):
        if self.settings.get("notifications", True):
            self.notifications.send(title, message)

    # ---------- welcome ----------
    def build_welcome(self):
        self.welcome = QWidget(self)
        self.welcome.setObjectName("welcomeOverlay")
        self.welcome.setGeometry(self.rect())
        self.welcome.raise_()

        root = QVBoxLayout(self.welcome)
        root.setContentsMargins(64, 40, 64, 44)

        top = QHBoxLayout()
        pix = QPixmap(str(ASSETS / "initra_logo.png"))
        logo = QLabel()
        logo.setPixmap(pix.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top.addWidget(logo)
        top.addWidget(label("Initra", "welcomeBrand"))
        top.addStretch()
        top.addWidget(label("v3.0", "accentTag"))
        root.addLayout(top)
        root.addStretch()

        row = QHBoxLayout()
        row.addStretch()
        panel = Card("welcomePanel")
        panel.setMaximumWidth(940)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(40, 30, 40, 34)
        pl.setSpacing(12)

        big = QLabel()
        big.setAlignment(Qt.AlignCenter)
        big.setPixmap(pix.scaled(88, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        pl.addWidget(big)
        t = label("Set up a fresh Linux install", "welcomeTitle")
        t.setAlignment(Qt.AlignCenter)
        pl.addWidget(t)
        st = label("Choose a starting point. You can review every change before anything runs.", "welcomeSubtitle")
        st.setAlignment(Qt.AlignCenter)
        pl.addWidget(st)

        detected = Card("detectedCard")
        dl = QHBoxLayout(detected)
        dl.addWidget(label("DETECTED", "eyebrow"))
        dl.addStretch()
        dl.addWidget(label(
            f"{self.info.pretty_name()}   ·   {self.info.package_manager()}   ·   {self.info.architecture()}",
            "cardTitle"
        ))
        pl.addWidget(detected)
        pl.addWidget(label("STARTING PROFILE", "eyebrow"))

        profiles = QHBoxLayout()
        profiles.setSpacing(10)
        self.welcome_profiles = {}
        for name, icon, desc in [
            ("Developer", "⌘", "Code, Python and build tools"),
            ("Essential", "◆", "A clean everyday Linux setup"),
            ("Gaming", "◈", "Steam and performance tools"),
            ("Creator", "✦", "Graphics, video and streaming"),
        ]:
            b = QPushButton(f"{icon}\n{name}\n{desc}")
            b.setObjectName("profileChoice")
            b.setCheckable(True)
            b.setMinimumHeight(118)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False, n=name: self.choose_welcome_profile(n))
            profiles.addWidget(b)
            self.welcome_profiles[name] = b
        pl.addLayout(profiles)
        self.choose_welcome_profile(self.current_profile if self.current_profile in self.welcome_profiles else "Developer")

        actions = QHBoxLayout()
        actions.addWidget(label("Nothing changes until you press Apply setup.", "footerText"))
        actions.addStretch()
        go = QPushButton("Continue  →")
        go.setObjectName("primaryButton")
        go.setCursor(Qt.PointingHandCursor)
        go.clicked.connect(self.close_welcome)
        actions.addWidget(go)
        pl.addLayout(actions)

        row.addWidget(panel, 1)
        row.addStretch()
        root.addLayout(row)
        root.addStretch()

        eff = QGraphicsOpacityEffect(self.welcome)
        self.welcome.setGraphicsEffect(eff)
        self.welcome_anim = QPropertyAnimation(eff, b"opacity", self)
        self.welcome_anim.setDuration(380)
        self.welcome_anim.setStartValue(0)
        self.welcome_anim.setEndValue(1)
        self.welcome_anim.start()

    def choose_welcome_profile(self, name):
        self.current_profile = name
        for n, b in self.welcome_profiles.items():
            b.setChecked(n == name)

    def close_welcome(self):
        self.settings["profile"] = self.current_profile
        self.settings_service.save(self.settings)
        self.refresh_setup()
        self.open_section(1, 0)
        eff = self.welcome.graphicsEffect()
        self.welcome_anim = QPropertyAnimation(eff, b"opacity", self)
        self.welcome_anim.setDuration(220)
        self.welcome_anim.setStartValue(1)
        self.welcome_anim.setEndValue(0)
        self.welcome_anim.finished.connect(self.welcome.hide)
        self.welcome_anim.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "welcome") and self.welcome.isVisible():
            self.welcome.setGeometry(self.rect())


    # ---------- dashboard ----------
    def build_dashboard_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "OVERVIEW", "System dashboard",
            "A quick snapshot of this Linux installation and what needs attention.",
            "INITRA v3.0"
        ))

        lay.addWidget(self.distro_compatibility_card())

        hero = Card("heroCard")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(20, 17, 20, 17)
        hero_text = QVBoxLayout()
        hero_text.addWidget(label("Your Linux, ready your way.", "heroTitle"))
        hero_text.addWidget(label(
            "Initra keeps setup, updates and maintenance in one safe workflow.",
            "muted"
        ))
        hl.addLayout(hero_text, 1)
        self.dashboard_score = label("—", "scoreNumber")
        hl.addWidget(self.dashboard_score)
        lay.addWidget(hero)

        stats = QHBoxLayout()
        stats.setSpacing(10)
        self.dash_update_value = label("…", "metricValue")
        self.dash_disk_value = label(self.info.disk_free(), "metricValue")
        self.dash_memory_value = label(self.info.memory(), "metricValue")
        self.dash_health_value = label("Checking", "metricValue")
        for icon, title, value in [
            ("↻", "Updates", self.dash_update_value),
            ("◫", "Disk", self.dash_disk_value),
            ("▤", "Memory", self.dash_memory_value),
            ("✓", "Package health", self.dash_health_value),
        ]:
            c = Card("metricCard")
            cl = QVBoxLayout(c)
            cl.setContentsMargins(15, 13, 15, 13)
            cl.addWidget(label(icon, "metricIcon"))
            cl.addWidget(value)
            cl.addWidget(label(title, "muted"))
            stats.addWidget(c, 1)
        lay.addLayout(stats)

        content = QHBoxLayout()
        content.setSpacing(14)

        system = Card("dashboardCard")
        sl = QVBoxLayout(system)
        sl.addWidget(label("System", "sectionTitle"))
        for k, v in [
            ("Distribution", self.info.pretty_name()),
            ("Kernel", self.info.kernel()),
            ("Desktop", self.info.desktop()),
            ("CPU", self.info.cpu()),
            ("Architecture", self.info.architecture()),
        ]:
            r = QHBoxLayout()
            r.addWidget(label(k, "muted"))
            r.addStretch()
            value = label(v, "dashboardValue")
            value.setMaximumWidth(360)
            r.addWidget(value)
            sl.addLayout(r)
        sl.addStretch()
        content.addWidget(system, 3)

        quick = Card("dashboardCard")
        ql = QVBoxLayout(quick)
        ql.addWidget(label("Quick actions", "sectionTitle"))
        quick_actions = [
            ("Health check  →", lambda: self.open_section(0, 1)),
            ("Backup & restore  →", lambda: self.open_section(1, 2)),
            ("Command palette  Ctrl+K", self.open_command_palette),
            ("Profiles  →", lambda: self.open_section(1, 1)),
            ("Review setup  →", lambda: self.open_section(1, 0)),
            ("Check updates  →", lambda: self.open_section(2, 1)),
            ("Free disk space  →", lambda: self.open_section(4, 0)),
            ("Software center  →", lambda: self.open_section(2, 0)),
        ]
        for text, callback in quick_actions:
            b = QPushButton(text)
            b.setObjectName("quickButton")
            b.setMinimumHeight(38)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(callback)
            ql.addWidget(b)
        ql.addStretch()
        content.addWidget(quick, 2)
        lay.addLayout(content, 1)
        return w

    def distro_compatibility_card(self):
        info = self.distro.info
        card = Card("distroCard")
        row = QHBoxLayout(card)
        text = QVBoxLayout()
        text.addWidget(label("DETECTED LINUX", "eyebrow"))
        text.addWidget(label(info["pretty_name"], "sectionTitle"))
        text.addWidget(label(
            f'{info["architecture"]}  •  {info["desktop"]}  •  {info["package_manager"]}',
            "muted"
        ))
        row.addLayout(text, 1)
        status = "SUPPORTED" if self.distro.supported() else "LIMITED"
        row.addWidget(label(status, "tag"))
        return card

    def refresh_dashboard(self):
        if not hasattr(self, "dash_update_value"):
            return
        report = self.health.full_scan()
        updates = report["updates"]
        broken = report["broken_packages"]
        failed = report["failed_services"]
        self.dash_update_value.setText(str(len(updates)))
        issues = len(broken) + len(failed)
        self.dash_health_value.setText("Healthy" if issues == 0 else f"{issues} issue(s)")
        self.dashboard_score.setText(f'{report["score"]}%\\nREADY')


    # ---------- health check ----------
    def build_health_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "HEALTH CHECK", "System health",
            "Diagnostics for packages, services, storage, network and repositories.",
            "INITRA v3.0"
        ))

        hero = Card("healthHero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(20, 16, 20, 16)
        text = QVBoxLayout()
        text.addWidget(label("Setup Score", "muted"))
        self.health_score = label("—", "healthScore")
        text.addWidget(self.health_score)
        self.health_status = label("Run a scan to evaluate this system.", "muted")
        text.addWidget(self.health_status)
        hl.addLayout(text, 1)
        scan = QPushButton("Run health check")
        scan.setObjectName("primaryButton")
        scan.clicked.connect(self.refresh_health)
        hl.addWidget(scan)
        lay.addWidget(hero)

        self.health_scroll = QScrollArea()
        self.health_scroll.setWidgetResizable(True)
        self.health_body = QWidget()
        self.health_body.setObjectName("page")
        self.health_list = QVBoxLayout(self.health_body)
        self.health_list.setContentsMargins(0, 0, 5, 0)
        self.health_list.setSpacing(8)
        self.health_scroll.setWidget(self.health_body)
        lay.addWidget(self.health_scroll, 1)

        actions = QHBoxLayout()
        actions.addWidget(label(
            "Health Check is diagnostic. It does not change the system automatically.",
            "footerText"
        ))
        actions.addStretch()
        services = QPushButton("Open Services")
        services.setObjectName("secondaryButton")
        services.clicked.connect(lambda: self.open_section(3, 2))
        updates = QPushButton("Open Updates")
        updates.setObjectName("secondaryButton")
        updates.clicked.connect(lambda: self.open_section(2, 1))
        actions.addWidget(services)
        actions.addWidget(updates)
        lay.addLayout(actions)
        return w

    def refresh_health(self):
        if not hasattr(self, "health_list"):
            return
        self.health_score.setText("Scanning…")
        QApplication.processEvents()
        report = self.health.full_scan()
        self.health_report = report
        self.health_score.setText(f'{report["score"]}%')
        self.health_status.setText(report["status"])
        self.clear_layout(self.health_list)

        for check in report["checks"]:
            c = Card("healthRow")
            r = QHBoxLayout(c)
            icon_text = "✓" if check["ok"] else ("!" if check["severity"] != "info" else "i")
            icon = label(icon_text, "healthOk" if check["ok"] else "healthWarn")
            icon.setAlignment(Qt.AlignCenter)
            icon.setFixedSize(34, 34)
            r.addWidget(icon)
            text = QVBoxLayout()
            text.addWidget(label(check["name"], "cardTitle"))
            text.addWidget(label(check["detail"], "muted"))
            if check["data"]:
                preview = "  •  " + "\n  •  ".join(check["data"][:5])
                text.addWidget(label(preview, "healthDetail"))
            r.addLayout(text, 1)
            status = "PASS" if check["ok"] else check["severity"].upper()
            r.addWidget(label(status, "tag"))
            self.health_list.addWidget(c)
        self.health_list.addStretch()
        self.log_history(f'Health check: {report["score"]}% ({report["status"]})')


    # ---------- backup & restore ----------
    def build_backups_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "BACKUP & RESTORE", "Recovery center",
            "Create restore points for configuration managed by Initra.", "INITRA v3.0"
        ))

        hero = Card("backupHero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(20, 16, 20, 16)
        text = QVBoxLayout()
        text.addWidget(label("Configuration restore points", "sectionTitle"))
        self.backup_summary = label(
            "Back up Initra settings, autostart entries and supported desktop preferences.",
            "muted"
        )
        text.addWidget(self.backup_summary)
        hl.addLayout(text, 1)
        create = QPushButton("Create restore point")
        create.setObjectName("primaryButton")
        create.clicked.connect(self.create_restore_point)
        hl.addWidget(create)
        lay.addWidget(hero)

        safety = Card("noticeCard")
        sl = QVBoxLayout(safety)
        sl.addWidget(label("Safe scope", "cardTitle"))
        sl.addWidget(label(
            "Initra backs up configuration managed by Initra. It is not a full disk image "
            "and does not copy personal documents or installed packages.",
            "muted"
        ))
        lay.addWidget(safety)

        self.backup_scroll = QScrollArea()
        self.backup_scroll.setWidgetResizable(True)
        self.backup_body = QWidget()
        self.backup_body.setObjectName("page")
        self.backup_list = QVBoxLayout(self.backup_body)
        self.backup_list.setContentsMargins(0, 0, 5, 0)
        self.backup_list.setSpacing(8)
        self.backup_scroll.setWidget(self.backup_body)
        lay.addWidget(self.backup_scroll, 1)

        actions = QHBoxLayout()
        actions.addWidget(label(
            "Restore replaces only files/settings included in that restore point.",
            "footerText"
        ))
        actions.addStretch()
        undo = QPushButton("Undo last configuration change")
        undo.setObjectName("secondaryButton")
        undo.clicked.connect(self.undo_last_change)
        actions.addWidget(undo)
        lay.addLayout(actions)
        return w

    def refresh_backups(self):
        if not hasattr(self, "backup_list"):
            return
        self.clear_layout(self.backup_list)
        backups = self.backups.list_backups()
        self.backup_summary.setText(
            f"{len(backups)} restore point(s) stored locally."
            if backups else
            "No restore points yet. Create one before making configuration changes."
        )
        if not backups:
            c = Card("backupRow")
            cl = QVBoxLayout(c)
            cl.addWidget(label("No backups yet", "cardTitle"))
            cl.addWidget(label(
                "Initra can also create restore points automatically before supported tweaks.",
                "muted"
            ))
            self.backup_list.addWidget(c)

        for item in backups:
            c = Card("backupRow")
            r = QHBoxLayout(c)
            text = QVBoxLayout()
            text.addWidget(label(item.get("reason", "Restore point"), "cardTitle"))
            created = item.get("created", item["id"]).replace("T", " ")
            count = len(item.get("files", []))
            text.addWidget(label(f"{created}  •  {count} backed-up item(s)", "muted"))
            r.addLayout(text, 1)
            r.addWidget(label(item["id"], "tag"))

            restore = QPushButton("Restore")
            restore.setObjectName("secondaryButton")
            restore.clicked.connect(
                lambda checked=False, bid=item["id"]: self.restore_backup(bid)
            )
            delete = QPushButton("Delete")
            delete.setObjectName("dangerButton")
            delete.clicked.connect(
                lambda checked=False, bid=item["id"]: self.delete_backup(bid)
            )
            r.addWidget(restore)
            r.addWidget(delete)
            self.backup_list.addWidget(c)
        self.backup_list.addStretch()

    def create_restore_point(self):
        try:
            folder = self.backups.create_backup("Manual restore point")
            self.log_history(f"Restore point created: {folder.name}")
            self.notify_user("Backup created", f"Restore point {folder.name} is ready.")
            self.refresh_backups()
            QMessageBox.information(
                self, "Backup created",
                f"Restore point {folder.name} was created successfully."
            )
        except Exception as exc:
            QMessageBox.warning(self, "Backup", str(exc))

    def restore_backup(self, backup_id):
        if QMessageBox.question(
            self, "Restore configuration",
            "Restore this configuration snapshot?\n\n"
            "Current versions of included files/settings will be replaced."
        ) != QMessageBox.Yes:
            return
        try:
            # Safety net before restore itself.
            try:
                self.backups.create_backup(f"Before restoring {backup_id}")
            except Exception:
                pass
            restored = self.backups.restore(backup_id)
            self.log_history(f"Backup restored: {backup_id}")
            QMessageBox.information(
                self, "Restore complete",
                "Restored: " + (", ".join(restored) if restored else "desktop preferences")
                + "\n\nSome desktop changes may appear after logging in again."
            )
            self.refresh_backups()
            self.refresh_tweaks()
            self.refresh_startup()
        except Exception as exc:
            QMessageBox.warning(self, "Restore", str(exc))

    def delete_backup(self, backup_id):
        if QMessageBox.question(
            self, "Delete restore point",
            "Delete this restore point permanently?"
        ) != QMessageBox.Yes:
            return
        try:
            self.backups.delete(backup_id)
            self.log_history(f"Restore point deleted: {backup_id}")
            self.refresh_backups()
        except Exception as exc:
            QMessageBox.warning(self, "Backup", str(exc))

    def undo_last_change(self):
        latest = self.backups.latest()
        if not latest:
            QMessageBox.information(self, "Undo", "There is no restore point to use.")
            return
        if QMessageBox.question(
            self, "Undo last configuration change",
            f"Restore the newest snapshot?\n\n{latest.get('reason', latest['id'])}\n"
            f"{latest.get('created', '')}"
        ) != QMessageBox.Yes:
            return
        self.restore_backup(latest["id"])


    # ---------- profiles 2.0 ----------
    def build_profiles_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "PROFILES 2.0", "Setup profiles",
            "Build reusable Linux setups from packages, services, tweaks and dotfiles.",
            "INITRA v3.0"
        ))

        top = QHBoxLayout()
        self.profile_filter = QLineEdit()
        self.profile_filter.setPlaceholderText("Search profiles…")
        self.profile_filter.textChanged.connect(self.refresh_profiles)
        top.addWidget(self.profile_filter, 1)
        import_btn = QPushButton("Import .json")
        import_btn.setObjectName("secondaryButton")
        import_btn.clicked.connect(self.import_profile)
        top.addWidget(import_btn)
        create = QPushButton("Create profile")
        create.setObjectName("primaryButton")
        create.clicked.connect(lambda: self.open_profile_editor(None))
        top.addWidget(create)
        lay.addLayout(top)

        self.profile_scroll = QScrollArea()
        self.profile_scroll.setWidgetResizable(True)
        self.profile_body = QWidget()
        self.profile_body.setObjectName("page")
        self.profile_list = QVBoxLayout(self.profile_body)
        self.profile_list.setContentsMargins(0, 0, 5, 0)
        self.profile_list.setSpacing(9)
        self.profile_scroll.setWidget(self.profile_body)
        lay.addWidget(self.profile_scroll, 1)
        return w

    def refresh_profiles(self):
        if not hasattr(self, "profile_list"):
            return
        self.clear_layout(self.profile_list)
        query = self.profile_filter.text().strip().lower()
        profiles = self.profiles.all_profiles()
        shown = 0
        for profile in profiles:
            hay = f"{profile['name']} {profile.get('description','')}".lower()
            if query and query not in hay:
                continue
            c = Card("profileCard")
            r = QHBoxLayout(c)
            text = QVBoxLayout()
            title = QHBoxLayout()
            title.addWidget(label(profile["name"], "cardTitle"))
            title.addWidget(label("BUILT-IN" if profile.get("builtin") else "CUSTOM", "tag"))
            title.addStretch()
            text.addLayout(title)
            text.addWidget(label(profile.get("description") or "No description.", "muted"))
            packages = profile.get("packages", [])
            services = profile.get("services", [])
            summary = f"{len(packages)} packages  •  {len(services)} services"
            if profile.get("dotfiles"):
                summary += "  •  dotfiles"
            text.addWidget(label(summary, "profileMeta"))
            r.addLayout(text, 1)

            use = QPushButton("Use profile")
            use.setObjectName("primaryButton")
            use.clicked.connect(
                lambda checked=False, p=profile: self.use_profile_2(p)
            )
            duplicate = QPushButton("Duplicate")
            duplicate.setObjectName("secondaryButton")
            duplicate.clicked.connect(
                lambda checked=False, p=profile: self.duplicate_profile(p)
            )
            preview = QPushButton("Preview")
            preview.setObjectName("secondaryButton")
            preview.clicked.connect(
                lambda checked=False, p=profile: self.show_command_preview(p)
            )
            export = QPushButton("Export")
            export.setObjectName("secondaryButton")
            export.clicked.connect(
                lambda checked=False, p=profile: self.export_profile_menu(p)
            )
            r.addWidget(use)
            r.addWidget(duplicate)
            r.addWidget(preview)
            r.addWidget(export)

            if not profile.get("builtin"):
                edit = QPushButton("Edit")
                edit.setObjectName("secondaryButton")
                edit.clicked.connect(
                    lambda checked=False, p=profile: self.open_profile_editor(p)
                )
                delete = QPushButton("Delete")
                delete.setObjectName("dangerButton")
                delete.clicked.connect(
                    lambda checked=False, pid=profile["id"]: self.delete_profile(pid)
                )
                r.addWidget(edit)
                r.addWidget(delete)
            self.profile_list.addWidget(c)
            shown += 1

        if not shown:
            c = Card("noticeCard")
            cl = QVBoxLayout(c)
            cl.addWidget(label("No profiles found", "cardTitle"))
            cl.addWidget(label("Create a custom profile or change the search query.", "muted"))
            self.profile_list.addWidget(c)
        self.profile_list.addStretch()

    def open_profile_editor(self, profile):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit profile" if profile else "Create profile")
        dialog.resize(650, 720)
        dialog.setObjectName("profileDialog")
        outer = QVBoxLayout(dialog)

        outer.addWidget(label("PROFILE EDITOR", "eyebrow"))
        outer.addWidget(label("Custom Linux setup", "pageTitle"))

        name = QLineEdit()
        name.setPlaceholderText("Profile name")
        description = QLineEdit()
        description.setPlaceholderText("Short description")
        if profile:
            name.setText(profile.get("name", ""))
            description.setText(profile.get("description", ""))
        outer.addWidget(name)
        outer.addWidget(description)

        tabs = QTabWidget()
        outer.addWidget(tabs, 1)

        # Packages
        package_page = QWidget()
        pl = QVBoxLayout(package_page)
        package_checks = {}
        catalog = {}
        for category, apps in self.software.APT_APPS.items():
            for package, desc in apps.items():
                catalog[package] = (category, desc)
        selected_packages = set(profile.get("packages", []) if profile else [])
        for package, (category, desc) in sorted(catalog.items()):
            cb = QCheckBox(f"{package}   —   {desc}")
            cb.setChecked(package in selected_packages)
            pl.addWidget(cb)
            package_checks[package] = cb
        pl.addStretch()
        pscroll = QScrollArea()
        pscroll.setWidgetResizable(True)
        pscroll.setWidget(package_page)
        tabs.addTab(pscroll, "Packages")

        # Services
        service_page = QWidget()
        sv = QVBoxLayout(service_page)
        service_checks = {}
        for service_name, desc in [
            ("ssh", "OpenSSH server"),
            ("ufw", "Uncomplicated Firewall"),
        ]:
            cb = QCheckBox(f"{service_name.upper()}   —   {desc}")
            cb.setChecked(service_name in set(profile.get("services", []) if profile else []))
            sv.addWidget(cb)
            service_checks[service_name] = cb
        sv.addStretch()
        tabs.addTab(service_page, "Services")

        # Preferences
        pref_page = QWidget()
        pf = QVBoxLayout(pref_page)
        dotfiles = QCheckBox("Include Initra dotfiles step")
        dotfiles.setChecked(bool(profile.get("dotfiles", False)) if profile else False)
        animations = QCheckBox("Enable GNOME animations")
        animations.setChecked(profile.get("tweaks", {}).get("animations", True) if profile else True)
        hot_corners = QCheckBox("Enable GNOME hot corner")
        hot_corners.setChecked(profile.get("tweaks", {}).get("hot_corners", False) if profile else False)
        pf.addWidget(dotfiles)
        pf.addWidget(animations)
        pf.addWidget(hot_corners)
        pf.addStretch()
        tabs.addTab(pref_page, "Preferences")

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondaryButton")
        cancel.clicked.connect(dialog.reject)
        save = QPushButton("Save profile")
        save.setObjectName("primaryButton")
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        outer.addLayout(buttons)

        def commit():
            if not name.text().strip():
                QMessageBox.information(dialog, "Profile", "Enter a profile name.")
                return
            payload = {
                "id": profile.get("id", "") if profile else "",
                "name": name.text().strip(),
                "description": description.text().strip(),
                "packages": [k for k, cb in package_checks.items() if cb.isChecked()],
                "services": [k for k, cb in service_checks.items() if cb.isChecked()],
                "dotfiles": dotfiles.isChecked(),
                "tweaks": {
                    "animations": animations.isChecked(),
                    "hot_corners": hot_corners.isChecked(),
                },
                "created": profile.get("created") if profile else None,
            }
            saved = self.profiles.save(payload)
            self.log_history(f"Profile saved: {saved['name']}")
            dialog.accept()
            self.refresh_profiles()

        save.clicked.connect(commit)
        dialog.exec()

    def show_command_preview(self, profile):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Command Preview — {profile['name']}")
        dialog.resize(760, 560)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label("COMMAND PREVIEW", "eyebrow"))
        layout.addWidget(label(profile["name"], "pageTitle"))
        layout.addWidget(label(
            "Review the commands represented by this profile. Preview mode does not execute them.",
            "muted"
        ))
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setPlainText(self.command_preview.profile_preview(profile, self.distro.info['package_manager']))
        layout.addWidget(view, 1)
        row = QHBoxLayout()
        row.addStretch()
        close = QPushButton("Close")
        close.setObjectName("primaryButton")
        close.clicked.connect(dialog.accept)
        row.addWidget(close)
        layout.addLayout(row)
        dialog.exec()

    def open_command_palette(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Initra Command Palette")
        dialog.resize(540, 620)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label("COMMAND PALETTE", "eyebrow"))
        layout.addWidget(label(
            f'{self.distro.info["pretty_name"]} • {self.distro.info["package_manager"]}',
            "muted"
        ))
        search = QLineEdit()
        search.setPlaceholderText("Type a page or action…")
        layout.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body.setObjectName("page")
        items_layout = QVBoxLayout(body)
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        actions = [
            ("Dashboard", "Open system overview", lambda: self.open_section(0, 0)),
            ("Health Check", "Run and review diagnostics", lambda: self.open_section(0, 1)),
            ("Backups", "Open Recovery Center", lambda: self.open_section(1, 2)),
            ("Profiles", "Manage setup profiles", lambda: self.open_section(1, 1)),
            ("Setup", "Open current setup plan", lambda: self.open_section(1, 0)),
            ("Software", "Browse APT and Flatpak applications", lambda: self.open_section(2, 0)),
            ("Repositories", "Inspect software sources", lambda: self.open_section(2, 2)),
            ("Updates", "Check package updates", lambda: self.open_section(2, 1)),
            ("Cleanup", "Review reclaimable space", lambda: self.open_section(4, 0)),
            ("Tweaks", "Open GNOME preferences", lambda: self.open_section(3, 0)),
            ("Startup", "Manage startup applications", lambda: self.open_section(3, 1)),
            ("Drivers", "Inspect hardware drivers", lambda: self.open_section(2, 3)),
            ("System", "Show detailed system information", lambda: self.open_section(0, 2)),
            ("Dotfiles", "Open dotfiles manager", lambda: self.open_section(1, 3)),
            ("Services", "Manage supported services", lambda: self.open_section(3, 2)),
            ("History", "Review Initra activity", lambda: self.open_section(4, 2)),
            ("Settings", "Open Initra preferences", lambda: self.open_section(6, 0)),
            ("Linux Compatibility", "Show detected distro and package manager", self.show_linux_compatibility),
            ("Create backup", "Create a configuration restore point", self.create_restore_point),
            ("Run Health Check", "Scan system health now", self.refresh_health),
        ]

        def render(text=""):
            self.clear_layout(items_layout)
            q = text.strip().lower()
            for title, desc, callback in actions:
                if q and q not in f"{title} {desc}".lower():
                    continue
                b = QPushButton()
                b.setObjectName("paletteItem")
                bl = QHBoxLayout(b)
                info = QVBoxLayout()
                info.addWidget(label(title, "cardTitle"))
                info.addWidget(label(desc, "muted"))
                bl.addLayout(info, 1)
                bl.addWidget(label("↵", "tag"))
                def trigger(checked=False, cb=callback):
                    dialog.accept()
                    cb()
                b.clicked.connect(trigger)
                items_layout.addWidget(b)
            items_layout.addStretch()

        search.textChanged.connect(render)
        render()
        search.setFocus()
        dialog.exec()

    def show_linux_compatibility(self):
        info = self.distro.info
        notes = self.distro.compatibility_notes()
        paths = self.distro.repo_paths()
        message = (
            f'{info["pretty_name"]}\n\n'
            f'Distro ID: {info["id"]}\n'
            f'Family: {info["family"]}\n'
            f'Package manager: {info["package_manager"]}\n'
            f'Architecture: {info["architecture"]}\n'
            f'Kernel: {info["kernel"]}\n'
            f'Desktop: {info["desktop"]}\n'
            f'Session: {info["session"]}\n\n'
            f'Repository locations:\n' + ("\n".join(paths) if paths else "Unknown")
        )
        if notes:
            message += "\n\nCompatibility notes:\n• " + "\n• ".join(notes)
        QMessageBox.information(self, "Linux Compatibility", message)

    def maybe_show_first_run_wizard(self):
        if self.settings.get("first_run_complete", False):
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Welcome to Initra")
        dialog.resize(720, 560)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label("WELCOME TO INITRA", "eyebrow"))
        layout.addWidget(label("Set up your Linux your way.", "pageTitle"))
        layout.addWidget(label(
            f'Detected: {self.distro.info["pretty_name"]} • '
            f'{self.distro.info["architecture"]} • {self.distro.info["package_manager"]}',
            "profileMeta"
        ))
        layout.addWidget(label(
            "Choose a starting profile. Initra adapts supported package actions to the detected Linux distribution.",
            "muted"
        ))

        cards = QVBoxLayout()
        group = []
        selected = {"name": self.settings.get("wizard_profile", "Developer")}
        for profile in self.profiles.built_ins():
            b = QPushButton()
            b.setCheckable(True)
            b.setChecked(profile["name"] == selected["name"])
            b.setObjectName("wizardProfile")
            row = QHBoxLayout(b)
            text = QVBoxLayout()
            text.addWidget(label(profile["name"], "cardTitle"))
            text.addWidget(label(profile["description"], "muted"))
            row.addLayout(text, 1)
            row.addWidget(label(f'{len(profile["packages"])} PACKAGES', "tag"))
            def choose(checked=False, btn=b, name=profile["name"]):
                selected["name"] = name
                for other in group:
                    other.setChecked(other is btn)
            b.clicked.connect(choose)
            group.append(b)
            cards.addWidget(b)
        layout.addLayout(cards)
        layout.addStretch()

        footer = QHBoxLayout()
        skip = QPushButton("Skip for now")
        skip.setObjectName("secondaryButton")
        start = QPushButton("Start with this profile")
        start.setObjectName("primaryButton")
        footer.addStretch()
        footer.addWidget(skip)
        footer.addWidget(start)
        layout.addLayout(footer)

        def finish(use_profile):
            if use_profile:
                profile = self.profiles.get(selected["name"])
                if profile:
                    self.current_profile = profile["name"]
                    self.settings["profile"] = profile["name"]
                    self.settings["profile_id"] = profile["id"]
            self.settings["wizard_profile"] = selected["name"]
            self.settings["first_run_complete"] = True
            self.settings_service.save(self.settings)
            dialog.accept()
            self.refresh_setup()

        skip.clicked.connect(lambda: finish(False))
        start.clicked.connect(lambda: finish(True))
        dialog.exec()

    def import_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Initra profile", str(Path.home()),
            "Initra Profile (*.json);;JSON files (*.json)"
        )
        if not path:
            return
        try:
            payload = self.transfer.import_profile_json(path)
            # Imported profiles are always new local custom profiles.
            existing = {p["name"] for p in self.profiles.all_profiles()}
            base_name = payload["name"]
            if base_name in existing:
                n = 2
                while f"{base_name} ({n})" in existing:
                    n += 1
                payload["name"] = f"{base_name} ({n})"
            saved = self.profiles.save(payload)
            self.log_history(f"Profile imported: {saved['name']}")
            self.refresh_profiles()
            QMessageBox.information(
                self, "Import complete",
                f"Profile “{saved['name']}” was imported successfully."
            )
        except Exception as exc:
            QMessageBox.warning(self, "Import profile", str(exc))

    def export_profile_menu(self, profile):
        box = QMessageBox(self)
        box.setWindowTitle("Export profile")
        box.setText(f"Export “{profile['name']}”")
        box.setInformativeText("Choose a portable Initra profile or a standalone shell script.")
        json_btn = box.addButton("Portable .json", QMessageBox.AcceptRole)
        sh_btn = box.addButton("Setup .sh", QMessageBox.ActionRole)
        box.addButton(QMessageBox.Cancel)
        box.exec()
        clicked = box.clickedButton()
        if clicked == json_btn:
            self.export_profile_json(profile)
        elif clicked == sh_btn:
            self.export_profile_shell(profile)

    def export_profile_json(self, profile):
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in profile["name"]).strip("_")
        path, _ = QFileDialog.getSaveFileName(
            self, "Export portable profile",
            str(Path.home() / f"{safe or 'initra_profile'}.json"),
            "Initra Profile (*.json)"
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            result = self.transfer.export_profile_json(profile, path)
            self.log_history(f"Profile exported: {profile['name']} -> JSON")
            QMessageBox.information(self, "Export complete", f"Saved to:\n{result}")
        except Exception as exc:
            QMessageBox.warning(self, "Export profile", str(exc))

    def export_profile_shell(self, profile):
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in profile["name"]).strip("_")
        path, _ = QFileDialog.getSaveFileName(
            self, "Export setup script",
            str(Path.home() / f"{safe or 'initra_setup'}.sh"),
            "Shell script (*.sh)"
        )
        if not path:
            return
        if not path.lower().endswith(".sh"):
            path += ".sh"
        try:
            script = self.transfer.shell_script_for_manager(
                profile, self.distro.info["package_manager"]
            )
            Path(path).write_text(script, encoding="utf-8")
            Path(path).chmod(Path(path).stat().st_mode | 0o111)
            result = path
            self.log_history(f"Profile exported: {profile['name']} -> shell")
            QMessageBox.information(
                self, "Script generated",
                f"Saved to:\n{result}\n\nReview the script before running it."
            )
        except Exception as exc:
            QMessageBox.warning(self, "Export script", str(exc))

    def duplicate_profile(self, profile):
        try:
            clone = self.profiles.duplicate(profile)
            self.log_history(f"Profile duplicated: {clone['name']}")
            self.refresh_profiles()
        except Exception as exc:
            QMessageBox.warning(self, "Profiles", str(exc))

    def delete_profile(self, profile_id):
        if QMessageBox.question(
            self, "Delete profile", "Delete this custom profile permanently?"
        ) != QMessageBox.Yes:
            return
        self.profiles.delete(profile_id)
        self.log_history(f"Profile deleted: {profile_id}")
        self.refresh_profiles()

    def use_profile_2(self, profile):
        self.current_profile = profile["name"]
        self.settings["profile"] = self.current_profile
        self.settings["profile_id"] = profile["id"]
        self.settings_service.save(self.settings)

        # Feed selected packages into the existing setup pipeline.
        try:
            self.extra_packages = set(profile.get("packages", []))
        except Exception:
            pass

        self.log_history(f"Profile selected: {profile['name']}")
        self.refresh_setup()
        self.open_section(1, 0)

    # ---------- profiles / plan ----------
    def profile_packages(self):
        profiles = {
            "Essential": ["git", "curl", "wget", "vlc"],
            "Developer": ["git", "curl", "build-essential", "ripgrep", "python3-pip", "python3-venv"],
            "Gaming": ["steam", "gamemode", "mangohud", "wine"],
            "Creator": ["gimp", "blender", "obs-studio", "audacity", "inkscape", "kdenlive"],
        }
        return profiles.get(self.current_profile, []) + sorted(self.selected_extra)

    def build_setup_page(self):
        w, lay = self.page()
        self.setup_layout = lay
        self.setup_header = self.header(
            "PROFILE", f"{self.current_profile} workstation",
            "Review each step. Nothing changes until you apply.", "READY TO REVIEW"
        )
        lay.addLayout(self.setup_header)

        content = QHBoxLayout()
        content.setSpacing(20)

        left = QVBoxLayout()
        top = QHBoxLayout()
        self.setup_title = label(f"{self.current_profile} workstation", "pageTitle")
        top.addStretch()
        switch = QPushButton("Switch profile")
        switch.setObjectName("secondaryButton")
        switch.clicked.connect(self.show_profile_dialog)
        top.addWidget(switch)
        left.addLayout(top)

        self.step_cards_box = QVBoxLayout()
        self.step_cards_box.setSpacing(9)
        left.addLayout(self.step_cards_box)
        left.addStretch()

        summary = Card("summaryCard")
        summary.setFixedWidth(285)
        sy = QVBoxLayout(summary)
        sy.setContentsMargins(18, 18, 18, 18)
        sy.setSpacing(12)
        sy.addWidget(label("Summary", "cardTitle"))
        self.summary_steps = label("", "summaryValue")
        self.summary_packages = label("", "summaryValue")
        self.summary_download = label(f"via {self.distro.info['package_manager']}", "summaryValue")
        self.summary_disk = label("checked before install", "summaryValue")
        for name, value in [
            ("Steps", self.summary_steps), ("Packages", self.summary_packages),
            ("Download", self.summary_download), ("Disk space", self.summary_disk)
        ]:
            r = QHBoxLayout()
            r.addWidget(label(name, "muted"))
            r.addStretch()
            r.addWidget(value)
            sy.addLayout(r)
        sy.addSpacing(5)
        sy.addWidget(label("Privileges are requested only when required.", "footerText"))
        apply = QPushButton("Apply setup")
        apply.setObjectName("primaryButton")
        apply.clicked.connect(self.apply_setup)
        dry = QPushButton("Dry run")
        dry.setObjectName("secondaryButton")
        dry.clicked.connect(self.dry_run)
        sy.addWidget(apply)
        sy.addWidget(dry)
        export = QPushButton("Export as shell script")
        export.setObjectName("ghostButton")
        export.clicked.connect(self.export_script)
        sy.addWidget(export)
        sy.addStretch()

        content.addLayout(left, 1)
        content.addWidget(summary)
        lay.addLayout(content, 1)
        self.refresh_setup()
        return w

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def refresh_setup(self):
        if not hasattr(self, "step_cards_box"):
            return
        self.setup_title.setText(f"{self.current_profile} workstation")
        self.clear_layout(self.step_cards_box)
        packages = self.profile_packages()
        translated_packages, unsupported_packages = self.distro.translate_packages(packages)
        steps = [
            ("Refresh package index", f"{self.distro.info['package_manager']} repository metadata", "Required"),
            (f"Install {self.current_profile.lower()} packages",
              "  ".join(translated_packages) or "No compatible packages selected",
              f"{len(translated_packages)} packages"),
            ("Install Docker Engine", "Optional third-party development environment", "Optional"),
            ("Link dotfiles", "~/.dotfiles → ~/", "Optional"),
            ("Enable services", "ssh · ufw", "Optional"),
        ]
        for i, (title, desc, tag) in enumerate(steps, 1):
            c = Card("stepCard")
            r = QHBoxLayout(c)
            r.setContentsMargins(14, 12, 14, 12)
            r.addWidget(label(f"{i:02}", "stepNumber"))
            check = QCheckBox()
            check.setChecked(i <= 2)
            r.addWidget(check)
            text = QVBoxLayout()
            text.setSpacing(2)
            text.addWidget(label(title, "cardTitle"))
            text.addWidget(label(desc, "command"))
            r.addLayout(text, 1)
            r.addWidget(label(tag, "tag"))
            self.step_cards_box.addWidget(c)
        self.summary_steps.setText("5 of 5")
        self.summary_packages.setText(str(len(translated_packages)))

    def show_profile_dialog(self):
        box = QMessageBox(self)
        box.setWindowTitle("Switch profile")
        box.setText("Choose the profile from the Welcome screen.")
        box.setInformativeText("Reopen Initra to use the Welcome selector, or choose from Packages for custom additions.")
        box.exec()

    # ---------- software center ----------
    def build_software_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "SOFTWARE", "Software Center",
            "Browse and manage applications from native packages and Flatpak.", f"{self.distro.info['package_manager'].upper()} + FLATPAK"
        ))

        toolbar = Card("toolbarCard")
        tl = QHBoxLayout(toolbar)
        self.software_search = QLineEdit()
        self.software_search.setPlaceholderText("Search applications…")
        self.software_source = QComboBox()
        self.software_source.addItems(["All sources", "APT", "Flatpak"])
        self.software_category = QComboBox()
        categories = sorted(set(self.software.APT_APPS) | set(self.software.FLATPAK_APPS))
        self.software_category.addItems(["All categories", *categories])
        tl.addWidget(self.software_search, 1)
        tl.addWidget(self.software_source)
        tl.addWidget(self.software_category)
        lay.addWidget(toolbar)

        self.software_scroll = QScrollArea()
        self.software_scroll.setWidgetResizable(True)
        self.software_body = QWidget()
        self.software_body.setObjectName("page")
        self.software_list = QVBoxLayout(self.software_body)
        self.software_list.setContentsMargins(0, 0, 5, 0)
        self.software_list.setSpacing(8)
        self.software_scroll.setWidget(self.software_body)
        lay.addWidget(self.software_scroll, 1)

        self.software_search.textChanged.connect(self.refresh_software)
        self.software_source.currentTextChanged.connect(self.refresh_software)
        self.software_category.currentTextChanged.connect(self.refresh_software)
        return w

    def refresh_software(self):
        if not hasattr(self, "software_list"):
            return
        self.clear_layout(self.software_list)
        query = self.software_search.text().strip().lower()
        source_filter = self.software_source.currentText()
        category_filter = self.software_category.currentText()

        entries = []
        if source_filter in ("All sources", "APT"):
            for category, apps in self.software.APT_APPS.items():
                for package, desc in apps.items():
                    entries.append(("APT", category, package, package, desc))
        if source_filter in ("All sources", "Flatpak"):
            for category, apps in self.software.FLATPAK_APPS.items():
                for app_id, (name, desc) in apps.items():
                    entries.append(("Flatpak", category, app_id, name, desc))

        shown = 0
        for source, category, app_id, name, desc in entries:
            if category_filter != "All categories" and category != category_filter:
                continue
            haystack = f"{name} {app_id} {desc}".lower()
            if query and query not in haystack:
                continue
            installed = (
                self.software.apt_installed(app_id)
                if source == "APT"
                else self.software.flatpak_installed(app_id)
            )
            card = Card("softwareRow")
            row = QHBoxLayout(card)
            row.setContentsMargins(14, 11, 14, 11)
            icon = label(name[:1].upper(), "appIcon")
            icon.setAlignment(Qt.AlignCenter)
            icon.setFixedSize(38, 38)
            row.addWidget(icon)
            text = QVBoxLayout()
            text.setSpacing(2)
            text.addWidget(label(name, "cardTitle"))
            text.addWidget(label(desc, "muted"))
            text.addWidget(label(app_id, "command"))
            row.addLayout(text, 1)
            row.addWidget(label(category.upper(), "tag"))
            row.addWidget(label(source.upper(), "sourceTag"))
            action = QPushButton("Remove" if installed else "Install")
            action.setObjectName("secondaryButton" if installed else "primaryButton")
            action.clicked.connect(
                lambda checked=False, src=source, aid=app_id, nm=name, ins=installed:
                self.software_action(src, aid, nm, ins)
            )
            row.addWidget(action)
            self.software_list.addWidget(card)
            shown += 1

        if not shown:
            empty = Card("noticeCard")
            el = QVBoxLayout(empty)
            el.addWidget(label("No matching applications", "cardTitle"))
            el.addWidget(label("Try another search term, category or package source.", "muted"))
            self.software_list.addWidget(empty)
        self.software_list.addStretch()

    def software_action(self, source, app_id, name, installed):
        action = "Remove" if installed else "Install"
        if source == "Flatpak" and not self.software.has_flatpak():
            answer = QMessageBox.question(
                self, "Flatpak is not installed",
                "Install Flatpak first? Administrator privileges will be requested."
            )
            if answer != QMessageBox.Yes:
                return
            self.run_maintenance_command(
                self.software.install_flatpak_command(), "Install Flatpak",
                self.refresh_software
            )
            return

        if QMessageBox.question(
            self, f"{action} {name}",
            f"{action} {name} using {source}?"
        ) != QMessageBox.Yes:
            return

        if source == "APT":
            command = (
                self.software.apt_remove_command(app_id)
                if installed else self.software.apt_install_command(app_id)
            )
        else:
            command = (
                self.software.flatpak_remove_command(app_id)
                if installed else self.software.flatpak_install_command(app_id)
            )
        self.run_maintenance_command(command, f"{action} {name}", self.refresh_software)

    # ---------- repositories ----------
    def build_repositories_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "REPOSITORIES", "Software sources",
            "Inspect APT sources and manage Flathub for Flatpak.", "SOURCE CONTROL"
        ))

        flatpak = Card("repoHero")
        fl = QHBoxLayout(flatpak)
        text = QVBoxLayout()
        text.addWidget(label("Flatpak & Flathub", "sectionTitle"))
        self.flatpak_status = label("", "muted")
        text.addWidget(self.flatpak_status)
        fl.addLayout(text, 1)
        self.flathub_button = QPushButton("Configure Flathub")
        self.flathub_button.setObjectName("primaryButton")
        self.flathub_button.clicked.connect(self.configure_flathub)
        fl.addWidget(self.flathub_button)
        lay.addWidget(flatpak)

        self.repo_view = QPlainTextEdit()
        self.repo_view.setReadOnly(True)
        lay.addWidget(self.repo_view, 1)

        row = QHBoxLayout()
        row.addWidget(label(
            "APT sources are shown read-only to avoid unsafe source-file edits.",
            "footerText"
        ))
        row.addStretch()
        refresh = QPushButton("Refresh sources")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_repositories)
        row.addWidget(refresh)
        lay.addLayout(row)
        return w

    def refresh_repositories(self):
        if not hasattr(self, "repo_view"):
            return
        has_flatpak = self.software.has_flatpak()
        remotes = self.software.flatpak_remotes() if has_flatpak else []
        has_flathub = any(name == "flathub" for name, _ in remotes)
        if not has_flatpak:
            self.flatpak_status.setText("Flatpak is not installed.")
            self.flathub_button.setText("Install Flatpak")
        elif has_flathub:
            self.flatpak_status.setText("Flatpak is installed and Flathub is configured.")
            self.flathub_button.setText("Flathub ready")
            self.flathub_button.setEnabled(False)
        else:
            self.flatpak_status.setText("Flatpak is installed. Flathub is not configured yet.")
            self.flathub_button.setText("Add Flathub")
            self.flathub_button.setEnabled(True)

        lines = ["APT SOURCES", "───────────"]
        sources = self.software.apt_sources()
        if not sources:
            lines.append("No readable APT source files found.")
        for file, entries in sources:
            lines.append(f"\n{file}")
            if entries:
                lines.extend(f"  • {entry}" for entry in entries)
            else:
                lines.append("  (no enabled entries)")

        lines.extend(["", "FLATPAK REMOTES", "───────────────"])
        if not has_flatpak:
            lines.append("Flatpak not installed.")
        elif not remotes:
            lines.append("No Flatpak remotes configured.")
        else:
            lines.extend(f"  • {name}  {url}" for name, url in remotes)
        self.repo_view.setPlainText("\n".join(lines))

    def configure_flathub(self):
        if not self.software.has_flatpak():
            if QMessageBox.question(
                self, "Install Flatpak",
                "Install Flatpak using APT? Administrator privileges will be requested."
            ) != QMessageBox.Yes:
                return
            self.run_maintenance_command(
                self.software.install_flatpak_command(), "Install Flatpak",
                self.refresh_repositories
            )
            return
        if QMessageBox.question(
            self, "Add Flathub",
            "Add the official Flathub remote for this user?"
        ) != QMessageBox.Yes:
            return
        self.run_maintenance_command(
            self.software.add_flathub_command(), "Add Flathub",
            self.refresh_repositories
        )

    # ---------- updates ----------
    def build_updates_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "UPDATES", "System updates",
            "Review available APT updates before applying them.", "APT"
        ))

        status = Card("updateHero")
        st = QHBoxLayout(status)
        st.setContentsMargins(18, 15, 18, 15)
        self.update_big = label("Checking…", "updateBig")
        text = QVBoxLayout()
        text.addWidget(self.update_big)
        self.update_sub = label("Reading package metadata", "muted")
        text.addWidget(self.update_sub)
        st.addLayout(text, 1)
        refresh = QPushButton("Refresh index")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_update_index)
        st.addWidget(refresh)
        lay.addWidget(status)

        self.update_list = QPlainTextEdit()
        self.update_list.setReadOnly(True)
        lay.addWidget(self.update_list, 1)

        actions = QHBoxLayout()
        actions.addWidget(label("Package upgrades always require explicit confirmation.", "footerText"))
        actions.addStretch()
        check = QPushButton("Check again")
        check.setObjectName("secondaryButton")
        check.clicked.connect(self.refresh_updates)
        upgrade = QPushButton("Update all")
        upgrade.setObjectName("primaryButton")
        upgrade.clicked.connect(self.apply_updates)
        actions.addWidget(check)
        actions.addWidget(upgrade)
        lay.addLayout(actions)
        return w

    def refresh_updates(self):
        if not hasattr(self, "update_list"):
            return
        packages = self.maintenance.upgradable_packages()
        self.available_updates = packages
        self.update_big.setText(f"{len(packages)} update(s) available" if packages else "System is up to date")
        self.update_sub.setText("Review the package list below." if packages else "No package upgrades are currently reported by APT.")
        self.update_list.setPlainText(
            "\n".join(f"  ↻  {name}" for name in packages) if packages else "✓ No updates available."
        )

    def refresh_update_index(self):
        if QMessageBox.question(
            self, "Refresh package index",
            "Refresh APT package metadata? Administrator privileges may be requested."
        ) != QMessageBox.Yes:
            return
        self.run_maintenance_command(
            self.maintenance.update_command(), "Refresh package index", self.refresh_updates
        )

    def apply_updates(self):
        packages = getattr(self, "available_updates", self.maintenance.upgradable_packages())
        if not packages:
            QMessageBox.information(self, "Updates", "The system is already up to date.")
            return
        if QMessageBox.question(
            self, "Update all",
            f"Apply {len(packages)} available update(s)?\n\nAdministrator privileges will be requested."
        ) != QMessageBox.Yes:
            return
        self.run_maintenance_command(
            self.maintenance.upgrade_command(), f"Upgrade {len(packages)} package(s)", self.refresh_updates
        )

    # ---------- cleanup ----------
    def build_cleanup_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "CLEANUP", "Storage cleanup",
            "Preview reclaimable space before deleting anything.", "SAFE CLEANUP"
        ))

        self.cleanup_total = label("Scanning…", "cleanupNumber")
        hero = Card("cleanupHero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(20, 16, 20, 16)
        left = QVBoxLayout()
        left.addWidget(label("Reclaimable space", "muted"))
        left.addWidget(self.cleanup_total)
        left.addWidget(label("APT cache, thumbnails and user trash", "muted"))
        hl.addLayout(left)
        hl.addStretch()
        scan = QPushButton("Scan again")
        scan.setObjectName("secondaryButton")
        scan.clicked.connect(self.refresh_cleanup)
        hl.addWidget(scan)
        lay.addWidget(hero)

        self.cleanup_rows = {}
        for name, desc in [
            ("APT package cache", "Downloaded .deb package files"),
            ("Thumbnail cache", "Generated image and video thumbnails"),
            ("User trash", "Files currently stored in your desktop trash"),
        ]:
            c = Card("cleanupRow")
            r = QHBoxLayout(c)
            check = QCheckBox()
            check.setChecked(True)
            r.addWidget(check)
            text = QVBoxLayout()
            text.addWidget(label(name, "cardTitle"))
            text.addWidget(label(desc, "muted"))
            r.addLayout(text, 1)
            size = label("—", "cleanupSize")
            r.addWidget(size)
            self.cleanup_rows[name] = (check, size)
            lay.addWidget(c)

        note = Card("noticeCard")
        nl = QVBoxLayout(note)
        nl.addWidget(label("What Initra will not touch", "cardTitle"))
        nl.addWidget(label(
            "Personal documents, application data and configuration files are not included in cleanup.",
            "muted"
        ))
        lay.addWidget(note)
        lay.addStretch()

        actions = QHBoxLayout()
        actions.addStretch()
        clean = QPushButton("Clean selected")
        clean.setObjectName("primaryButton")
        clean.clicked.connect(self.clean_selected)
        actions.addWidget(clean)
        lay.addLayout(actions)
        return w

    def refresh_cleanup(self):
        if not hasattr(self, "cleanup_rows"):
            return
        scan = self.maintenance.cleanup_scan()
        self.cleanup_scan_data = scan
        total = sum(scan.values())
        self.cleanup_total.setText(self.maintenance.human_size(total))
        for name, value in scan.items():
            if name in self.cleanup_rows:
                self.cleanup_rows[name][1].setText(self.maintenance.human_size(value))

    def clean_selected(self):
        chosen = [name for name, (cb, _) in self.cleanup_rows.items() if cb.isChecked()]
        if not chosen:
            QMessageBox.information(self, "Cleanup", "Nothing is selected.")
            return
        if self.settings.get("confirm_cleanup", True):
            if QMessageBox.question(
                self, "Clean selected",
                "The following items will be cleaned:\n\n• " + "\n• ".join(chosen) + "\n\nOnly checked items will be touched. Deleted trash contents cannot be restored."
            ) != QMessageBox.Yes:
                return

        messages = []
        if "Thumbnail cache" in chosen:
            count = self.maintenance.cleanup_thumbnails()
            messages.append(f"Thumbnail cache: removed {count} item(s).")

        if "User trash" in chosen:
            count = self.maintenance.cleanup_trash()
            messages.append(f"User trash: removed {count} item(s).")

        if "APT package cache" in chosen:
            command = self.distro.cleanup_command()
            if command:
                self.run_maintenance_command(
                    command,
                    f"{self.distro.info['package_manager']} cache cleanup",
                    self.refresh_cleanup
                )
                messages.append(f"{self.distro.info['package_manager']} cache cleanup started.")
            else:
                messages.append("Package cache cleanup is unavailable on this distribution.")
        else:
            self.refresh_cleanup()

        self.log_history("Cleanup: " + ", ".join(chosen))
        QMessageBox.information(self, "Cleanup", "\n".join(messages) or "Cleanup complete.")

    def run_maintenance_command(self, command, title, callback=None):
        self.worker = CommandWorker(command)
        output = []
        self.worker.line.connect(output.append)
        def done(code):
            self.log_history(f"{title}: exit={code}")
            if callback:
                callback()
            if code != 0:
                QMessageBox.warning(self, title, "\n".join(output[-12:]) or f"Command exited with code {code}.")
        self.worker.finished_code.connect(done)
        self.worker.start()


    # ---------- tweaks ----------
    def build_tweaks_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "TWEAKS", "Desktop tweaks",
            "Safe GNOME preferences with live state detection.", "GNOME"
        ))

        self.tweak_controls = {}
        tweaks = [
            ("Animations", "Enable GNOME interface animations",
             "org.gnome.desktop.interface", "enable-animations", "bool"),
            ("Hot corner", "Open Activities when moving to the top-left corner",
             "org.gnome.desktop.interface", "enable-hot-corners", "bool"),
            ("Battery percentage", "Show battery percentage in the top bar",
             "org.gnome.desktop.interface", "show-battery-percentage", "bool"),
            ("Weekday in clock", "Show the weekday in the top-bar clock",
             "org.gnome.desktop.interface", "clock-show-weekday", "bool"),
        ]
        for title, desc, schema, key, kind in tweaks:
            c = Card("tweakCard")
            r = QHBoxLayout(c)
            text = QVBoxLayout()
            text.addWidget(label(title, "cardTitle"))
            text.addWidget(label(desc, "muted"))
            r.addLayout(text, 1)
            cb = QCheckBox()
            cb.stateChanged.connect(
                lambda state, sc=schema, k=key: self.apply_tweak(sc, k, state)
            )
            r.addWidget(cb)
            lay.addWidget(c)
            self.tweak_controls[(schema, key)] = cb

        note = Card("noticeCard")
        nl = QVBoxLayout(note)
        nl.addWidget(label("Desktop-aware", "cardTitle"))
        nl.addWidget(label(
            "Unavailable GNOME keys are disabled instead of being written blindly. "
            "Initra never edits GNOME schema files.",
            "muted"
        ))
        lay.addWidget(note)
        lay.addStretch()
        return w

    def refresh_tweaks(self):
        if not hasattr(self, "tweak_controls"):
            return
        for (schema, key), cb in self.tweak_controls.items():
            value = self.system_tools.get_setting(schema, key)
            cb.blockSignals(True)
            cb.setEnabled(value is not None)
            cb.setChecked(value == "true")
            cb.blockSignals(False)

    def apply_tweak(self, schema, key, state):
        value = "true" if state else "false"
        try:
            self.backups.create_backup(f"Before tweak: {key}")
        except Exception:
            pass
        ok, message = self.system_tools.set_setting(schema, key, value)
        if not ok:
            QMessageBox.warning(self, "Desktop tweak", message)
        else:
            self.log_history(f"Tweak {schema}:{key}={value}")

    # ---------- startup ----------
    def build_startup_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "STARTUP", "Startup applications",
            "Manage per-user autostart without modifying system files.", "AUTOSTART"
        ))

        add = Card("startupAdd")
        al = QHBoxLayout(add)
        self.startup_name = QLineEdit()
        self.startup_name.setPlaceholderText("Application name")
        self.startup_command = QLineEdit()
        self.startup_command.setPlaceholderText("Command, e.g. /usr/bin/example --minimized")
        button = QPushButton("Add startup app")
        button.setObjectName("primaryButton")
        button.clicked.connect(self.add_startup_app)
        al.addWidget(self.startup_name)
        al.addWidget(self.startup_command, 1)
        al.addWidget(button)
        lay.addWidget(add)

        self.startup_scroll = QScrollArea()
        self.startup_scroll.setWidgetResizable(True)
        self.startup_body = QWidget()
        self.startup_body.setObjectName("page")
        self.startup_list = QVBoxLayout(self.startup_body)
        self.startup_list.setContentsMargins(0, 0, 5, 0)
        self.startup_list.setSpacing(8)
        self.startup_scroll.setWidget(self.startup_body)
        lay.addWidget(self.startup_scroll, 1)
        return w

    def refresh_startup(self):
        if not hasattr(self, "startup_list"):
            return
        self.clear_layout(self.startup_list)
        entries = self.system_tools.startup_entries()
        if not entries:
            c = Card("noticeCard")
            cl = QVBoxLayout(c)
            cl.addWidget(label("No startup applications found", "cardTitle"))
            cl.addWidget(label("Add one above or install an application that provides an autostart entry.", "muted"))
            self.startup_list.addWidget(c)
        for entry in entries:
            c = Card("startupRow")
            r = QHBoxLayout(c)
            text = QVBoxLayout()
            text.addWidget(label(entry["name"], "cardTitle"))
            text.addWidget(label(entry["exec"] or "No Exec command", "command"))
            r.addLayout(text, 1)
            r.addWidget(label("USER" if entry["user_owned"] else "SYSTEM", "tag"))
            toggle = QCheckBox("Enabled")
            toggle.setChecked(not entry["hidden"])
            toggle.stateChanged.connect(
                lambda state, e=entry: self.toggle_startup(e, bool(state))
            )
            r.addWidget(toggle)
            self.startup_list.addWidget(c)
        self.startup_list.addStretch()

    def add_startup_app(self):
        name = self.startup_name.text().strip()
        command = self.startup_command.text().strip()
        if not name or not command:
            QMessageBox.information(self, "Startup", "Enter both an application name and command.")
            return
        try:
            self.backups.create_backup("Before adding startup application")
            path = self.system_tools.add_startup(name, command)
            self.log_history(f"Startup entry added: {path.name}")
            self.startup_name.clear()
            self.startup_command.clear()
            self.refresh_startup()
        except Exception as exc:
            QMessageBox.warning(self, "Startup", str(exc))

    def toggle_startup(self, entry, enabled):
        try:
            self.backups.create_backup(f"Before startup change: {entry['name']}")
        except Exception:
            pass
        ok, message = self.system_tools.set_startup_enabled(entry, enabled)
        if not ok:
            QMessageBox.warning(self, "Startup", message)
        else:
            self.log_history(f"Startup {entry['name']}: {'enabled' if enabled else 'disabled'}")

    # ---------- drivers ----------
    def build_drivers_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "DRIVERS", "Hardware drivers",
            "Inspect graphics hardware and Ubuntu driver recommendations.", "HARDWARE"
        ))

        gpu = Card("driverHero")
        gl = QVBoxLayout(gpu)
        gl.addWidget(label("Graphics hardware", "sectionTitle"))
        self.gpu_summary = label("Detecting…", "driverBig")
        gl.addWidget(self.gpu_summary)
        lay.addWidget(gpu)

        self.driver_view = QPlainTextEdit()
        self.driver_view.setReadOnly(True)
        lay.addWidget(self.driver_view, 1)

        row = QHBoxLayout()
        row.addWidget(label(
            "Initra uses Ubuntu's own ubuntu-drivers utility for recommendations.",
            "footerText"
        ))
        row.addStretch()
        refresh = QPushButton("Detect again")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_drivers)
        install = QPushButton("Install recommended")
        install.setObjectName("primaryButton")
        install.clicked.connect(self.install_recommended_driver)
        row.addWidget(refresh)
        row.addWidget(install)
        lay.addLayout(row)
        return w

    def refresh_drivers(self):
        if not hasattr(self, "driver_view"):
            return
        blocks = self.system_tools.pci_graphics()
        self.gpu_summary.setText(self.system_tools.graphics_summary())
        recommendation = self.system_tools.ubuntu_driver_devices()
        self.driver_view.setPlainText(
            "GRAPHICS DEVICES\n───────────────\n" +
            "\n\n".join(blocks) +
            "\n\nUBUNTU DRIVER RECOMMENDATIONS\n─────────────────────────────\n" +
            recommendation
        )

    def install_recommended_driver(self):
        if QMessageBox.question(
            self, "Install recommended driver",
            "Run Ubuntu's recommended driver installer?\n\n"
            "Administrator privileges will be requested. A reboot may be required."
        ) != QMessageBox.Yes:
            return
        self.run_maintenance_command(
            self.system_tools.install_recommended_driver_command(),
            "Install recommended drivers",
            self.refresh_drivers
        )

    # ---------- extended system information ----------
    def build_system_info_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "SYSTEM", "System information",
            "Detailed hardware, operating system and desktop information.", "LIVE"
        ))

        self.system_info_box = QVBoxLayout()
        lay.addLayout(self.system_info_box)
        lay.addStretch()

        row = QHBoxLayout()
        row.addStretch()
        refresh = QPushButton("Refresh information")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_system_info)
        row.addWidget(refresh)
        lay.addLayout(row)
        return w

    def refresh_system_info(self):
        if not hasattr(self, "system_info_box"):
            return
        self.clear_layout(self.system_info_box)
        sections = [
            ("Operating system", [
                ("Distribution", self.info.pretty_name()),
                ("Kernel", self.info.kernel()),
                ("Architecture", self.info.architecture()),
                ("Hostname", self.system_tools.hostname()),
            ]),
            ("Desktop session", [
                ("Desktop", self.info.desktop()),
                ("Session", self.system_tools.session_type()),
                ("Shell", self.system_tools.shell()),
            ]),
            ("Hardware", [
                ("CPU", self.info.cpu()),
                ("Memory", self.info.memory()),
                ("Graphics", self.system_tools.graphics_summary()),
                ("Root filesystem", self.system_tools.root_filesystem()),
            ]),
        ]
        for title, rows in sections:
            c = Card("infoCard")
            cl = QVBoxLayout(c)
            cl.addWidget(label(title, "sectionTitle"))
            for key, value in rows:
                r = QHBoxLayout()
                r.addWidget(label(key, "muted"))
                r.addStretch()
                v = label(str(value), "infoValue")
                v.setMaximumWidth(620)
                r.addWidget(v)
                cl.addLayout(r)
            self.system_info_box.addWidget(c)

    # ---------- dotfiles ----------
    def build_dotfiles_page(self):
        w, lay = self.page()
        lay.addLayout(self.header("DOTFILES", "Dotfile linking",
                                  "Preview every link. Existing targets are backed up first.", "SAFE BY DEFAULT"))
        note = Card("noticeCard")
        nl = QVBoxLayout(note)
        nl.addWidget(label("Backup before linking", "cardTitle"))
        nl.addWidget(label("Existing files are moved to ~/.local/share/initra/dotfiles-backup before a symlink is created.", "muted"))
        lay.addWidget(note)
        self.dot_preview = QPlainTextEdit()
        self.dot_preview.setReadOnly(True)
        lay.addWidget(self.dot_preview, 1)
        row = QHBoxLayout()
        row.addStretch()
        refresh = QPushButton("Refresh preview")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_dotfiles)
        apply = QPushButton("Apply links")
        apply.setObjectName("primaryButton")
        apply.clicked.connect(self.apply_dotfiles)
        row.addWidget(refresh)
        row.addWidget(apply)
        lay.addLayout(row)
        self.refresh_dotfiles()
        return w

    def refresh_dotfiles(self):
        if not hasattr(self, "dot_preview"):
            return
        rows = self.dotfiles.preview()
        if not rows:
            self.dot_preview.setPlainText("No ~/.dotfiles directory found.\n\nCreate ~/.dotfiles and place files or folders inside it.")
        else:
            self.dot_preview.setPlainText("\n".join(f"[{state}]  {src.name}  →  {target}" for src, target, state in rows))

    def apply_dotfiles(self):
        if not self.dotfiles.preview():
            QMessageBox.information(self, "Initra", "No dotfiles are available.")
            return
        if QMessageBox.question(self, "Apply dotfiles", "Back up existing targets and create links?") != QMessageBox.Yes:
            return
        results = self.dotfiles.apply()
        self.log_history("Dotfiles: " + "; ".join(results))
        self.refresh_dotfiles()
        QMessageBox.information(self, "Initra", "\n".join(results))

    # ---------- services ----------
    def build_services_page(self):
        w, lay = self.page()
        lay.addLayout(self.header("SERVICES", "System services",
                                  "Inspect live status and make explicit changes.", "LIVE STATUS"))
        self.service_labels = {}
        for icon, title, unit, desc in [
            ("⇄", "SSH", "ssh", "Remote shell service"),
            ("◉", "UFW", "ufw", "Ubuntu uncomplicated firewall")
        ]:
            c = Card("serviceCard")
            r = QHBoxLayout(c)
            r.addWidget(label(icon, "serviceIcon"))
            text = QVBoxLayout()
            text.addWidget(label(title, "cardTitle"))
            text.addWidget(label(desc, "muted"))
            r.addLayout(text, 1)
            state = ServiceManager.state(unit)
            status = label(state.upper(), "accentTag" if state == "Active" else "tag")
            self.service_labels[unit] = status
            r.addWidget(status)
            enable = QPushButton("Enable")
            enable.setObjectName("secondaryButton")
            enable.clicked.connect(lambda checked=False, u=unit: self.change_service(u, True))
            disable = QPushButton("Disable")
            disable.setObjectName("secondaryButton")
            disable.clicked.connect(lambda checked=False, u=unit: self.change_service(u, False))
            r.addWidget(enable)
            r.addWidget(disable)
            lay.addWidget(c)
        lay.addStretch()
        return w

    def change_service(self, unit, enable):
        verb = "Enable" if enable else "Disable"
        if QMessageBox.question(self, "Service change", f"{verb} {unit}? Administrator privileges may be requested.") != QMessageBox.Yes:
            return
        self.worker = CommandWorker(ServiceManager.command(unit, enable))
        self.worker.line.connect(lambda x: self.log_history(f"{unit}: {x}"))
        self.worker.finished_code.connect(lambda code, u=unit: self.service_done(u, code))
        self.worker.start()

    def service_done(self, unit, code):
        state = ServiceManager.state(unit)
        self.service_labels[unit].setText(state.upper())
        self.log_history(f"Service {unit}: {state}; exit={code}")

    # ---------- history/settings ----------
    @property
    def history_path(self):
        return Path.home() / ".local/share/initra/history.log"

    def log_history(self, text):
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {text}\n")
        self.refresh_history()

    def build_history_page(self):
        w, lay = self.page()
        lay.addLayout(self.header("HISTORY", "Activity history",
                                  "Actions performed by Initra on this account.", "LOCAL LOG"))
        self.history_view = QPlainTextEdit()
        self.history_view.setReadOnly(True)
        lay.addWidget(self.history_view, 1)
        clear = QPushButton("Clear local history")
        clear.setObjectName("secondaryButton")
        clear.clicked.connect(self.clear_history)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(clear)
        lay.addLayout(row)
        return w

    def refresh_history(self):
        if not hasattr(self, "history_view"):
            return
        try:
            self.history_view.setPlainText(self.history_path.read_text(encoding="utf-8"))
        except OSError:
            self.history_view.setPlainText("No activity yet.")

    def clear_history(self):
        if QMessageBox.question(self, "Clear history", "Delete Initra's local activity history?") == QMessageBox.Yes:
            try:
                self.history_path.unlink(missing_ok=True)
            except OSError:
                pass
            self.refresh_history()

    def build_settings_page(self):
        w, lay = self.page()
        lay.addLayout(self.header(
            "SETTINGS", "Preferences",
            "Control confirmations, motion, maintenance and local history.", "v3.0"
        ))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setSpacing(10)

        bl.addWidget(label("BEHAVIOR", "eyebrow"))
        self.confirm_apply = QCheckBox("Confirm before privileged package changes")
        self.confirm_apply.setChecked(self.settings.get("confirm_apply", True))
        self.remember_profile = QCheckBox("Remember selected setup profile")
        self.remember_profile.setChecked(self.settings.get("remember_profile", True))
        self.animations = QCheckBox("Use interface animations")
        self.animations.setChecked(self.settings.get("animations", True))
        self.notifications = QCheckBox("Show completion notifications when supported")
        self.notifications.setChecked(self.settings.get("notifications", True))

        for title, desc, control in [
            ("Apply confirmation", "Require a final confirmation before package installation or upgrades.", self.confirm_apply),
            ("Remember profile", "Restore the most recently selected setup profile.", self.remember_profile),
            ("Animations", "Use subtle page and overlay transitions.", self.animations),
            ("Notifications", "Allow Initra to show desktop completion notifications in future/background workflows.", self.notifications),
        ]:
            bl.addWidget(self.setting_card(title, desc, control))

        bl.addWidget(label("MAINTENANCE", "eyebrow"))
        self.confirm_cleanup = QCheckBox("Confirm before cleanup")
        self.confirm_cleanup.setChecked(self.settings.get("confirm_cleanup", True))
        self.auto_updates = QCheckBox("Check update status when Initra opens")
        self.auto_updates.setChecked(self.settings.get("auto_check_updates", True))
        bl.addWidget(self.setting_card(
            "Cleanup confirmation", "Ask before deleting selected cache or trash contents.", self.confirm_cleanup
        ))
        bl.addWidget(self.setting_card(
            "Update checks", "Read APT upgrade status automatically when opening the app.", self.auto_updates
        ))

        history = Card("settingsCard")
        hr = QHBoxLayout(history)
        text = QVBoxLayout()
        text.addWidget(label("History retention", "cardTitle"))
        text.addWidget(label("Preferred retention period for Initra's local activity log.", "muted"))
        hr.addLayout(text, 1)
        self.history_days = QComboBox()
        self.history_days.addItems(["7 days", "14 days", "30 days", "90 days", "Forever"])
        days = self.settings.get("history_days", 30)
        self.history_days.setCurrentText("Forever" if days == 0 else f"{days} days")
        hr.addWidget(self.history_days)
        bl.addWidget(history)

        bl.addWidget(label("DATA & RESET", "eyebrow"))
        data = Card("settingsCard")
        dr = QHBoxLayout(data)
        text = QVBoxLayout()
        text.addWidget(label("Local Initra data", "cardTitle"))
        text.addWidget(label("Settings and history are stored only in your home directory.", "muted"))
        dr.addLayout(text, 1)
        reset = QPushButton("Reset defaults")
        reset.setObjectName("dangerButton")
        reset.clicked.connect(self.reset_settings)
        dr.addWidget(reset)
        bl.addWidget(data)

        bl.addStretch()
        scroll.setWidget(body)
        lay.addWidget(scroll, 1)

        actions = QHBoxLayout()
        actions.addStretch()
        save = QPushButton("Save preferences")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save_settings)
        actions.addWidget(save)
        lay.addLayout(actions)
        return w

    def setting_card(self, title, desc, control):
        c = Card("settingsCard")
        r = QHBoxLayout(c)
        text = QVBoxLayout()
        text.addWidget(label(title, "cardTitle"))
        text.addWidget(label(desc, "muted"))
        r.addLayout(text, 1)
        r.addWidget(control)
        return c

    def save_settings(self):
        self.settings["confirm_apply"] = self.confirm_apply.isChecked()
        self.settings["remember_profile"] = self.remember_profile.isChecked()
        self.settings["animations"] = self.animations.isChecked()
        self.settings["notifications"] = self.notifications.isChecked()
        self.settings["confirm_cleanup"] = self.confirm_cleanup.isChecked()
        self.settings["auto_check_updates"] = self.auto_updates.isChecked()
        text = self.history_days.currentText()
        self.settings["history_days"] = 0 if text == "Forever" else int(text.split()[0])
        self.settings["profile"] = self.current_profile
        self.settings_service.save(self.settings)
        self.log_history("Preferences saved")
        QMessageBox.information(self, "Initra", "Preferences saved.")

    def reset_settings(self):
        if QMessageBox.question(
            self, "Reset settings", "Restore all Initra preferences to their defaults?"
        ) != QMessageBox.Yes:
            return
        self.settings = dict(self.settings_service.defaults)
        self.settings_service.save(self.settings)
        QMessageBox.information(self, "Initra", "Defaults restored. Restart Initra to refresh all controls.")

    # ---------- dry run/apply ----------
    def dry_run(self):
        packages = self.profile_packages()
        cmd = ["apt-get", "-s", "install", *packages] if packages else ["apt-get", "-s", "update"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.log_history(f"Dry run: {len(packages)} packages")
            box = QMessageBox(self)
            box.setWindowTitle("Dry run")
            box.setText("APT simulation finished.")
            box.setDetailedText((r.stdout + "\n" + r.stderr)[-12000:])
            box.exec()
        except Exception as exc:
            QMessageBox.warning(self, "Dry run", str(exc))

    def export_script(self):
        path = Path.home() / "initra-setup.sh"
        packages = self.profile_packages()
        text = "#!/usr/bin/env bash\nset -e\nsudo apt update\n"
        if packages:
            text += "sudo apt install -y " + " ".join(packages) + "\n"
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)
        QMessageBox.information(self, "Export complete", f"Saved to:\n{path}")

    def apply_setup(self):
        packages = self.profile_packages()
        if not packages:
            QMessageBox.information(self, "Initra", "No packages are selected.")
            return
        if self.settings.get("confirm_apply", True):
            if QMessageBox.question(
                self, "Apply setup",
                f"Install {len(packages)} package(s)?\n\nAdministrator privileges will be requested."
            ) != QMessageBox.Yes:
                return
        self.show_applying(packages)

    def show_applying(self, packages):
        page = QWidget()
        page.setObjectName("page")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(38, 28, 38, 28)
        lay.setSpacing(15)
        lay.addLayout(self.header("APPLYING", f"{self.current_profile} workstation",
                                  "Step 2 of 5 · Install selected packages", "RUNNING"))

        progress_card = Card("progressCard")
        pc = QVBoxLayout(progress_card)
        top = QHBoxLayout()
        self.progress_text = label("18%", "progressNumber")
        top.addWidget(self.progress_text)
        top.addWidget(label("Preparing package transaction…", "muted"))
        top.addStretch()
        top.addWidget(label("APT", "tag"))
        pc.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        pc.addWidget(self.progress)
        lay.addWidget(progress_card)

        body = QHBoxLayout()
        steps = Card("applySteps")
        steps.setFixedWidth(310)
        sl = QVBoxLayout(steps)
        for state, text in [
            ("✓", "Refresh package index"),
            ("◌", "Install selected packages"),
            ("○", "Install Docker Engine"),
            ("○", "Link dotfiles"),
            ("○", "Enable services")
        ]:
            r = QHBoxLayout()
            r.addWidget(label(state, "stepState"))
            r.addWidget(label(text, "cardTitle"))
            r.addStretch()
            sl.addLayout(r)
        sl.addStretch()
        body.addWidget(steps)

        terminal = Card("terminalCard")
        tr = QVBoxLayout(terminal)
        tabs = QHBoxLayout()
        tabs.addWidget(label("Output", "terminalTabActive"))
        tabs.addWidget(label("Changes", "terminalTab"))
        tabs.addWidget(label("Warnings", "terminalTab"))
        tabs.addStretch()
        tr.addLayout(tabs)
        self.live_log = QPlainTextEdit()
        self.live_log.setReadOnly(True)
        self.live_log.setObjectName("terminal")
        tr.addWidget(self.live_log)
        body.addWidget(terminal, 1)
        lay.addLayout(body, 1)

        footer = QHBoxLayout()
        footer.addWidget(label("You can minimize this window. Initra will continue while it is open.", "footerText"))
        footer.addStretch()
        copy = QPushButton("Copy log")
        copy.setObjectName("secondaryButton")
        copy.clicked.connect(lambda: self.live_log.selectAll())
        cancel = QPushButton("Cancel setup")
        cancel.setObjectName("dangerButton")
        cancel.clicked.connect(self.cancel_apply)
        footer.addWidget(copy)
        footer.addWidget(cancel)
        lay.addLayout(footer)

        self.pages.addWidget(page)
        self.pages.setCurrentWidget(page)
        for b in self.nav:
            b.setChecked(False)
        self.nav[4].setChecked(True)

        cmd = ["pkexec", "apt-get", "install", "-y", *packages]
        self.live_log.appendPlainText("$ " + " ".join(cmd))
        self.worker = CommandWorker(cmd)
        self.worker.line.connect(self.live_log.appendPlainText)
        self.worker.finished_code.connect(lambda code: self.finish_apply(code, packages))
        self.worker.start()

    def cancel_apply(self):
        if self.worker:
            self.worker.cancel()
            self.log_history("Setup cancelled")
        self.open_section(0, 0)

    def finish_apply(self, code, packages):
        self.log_history(f"Apply finished: exit={code}; packages={len(packages)}")
        self.show_finished(code, packages)

    def show_finished(self, code, packages):
        page = QWidget()
        page.setObjectName("page")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(38, 28, 38, 28)
        lay.setSpacing(15)
        success = code == 0
        lay.addLayout(self.header("FINISHED", "Setup complete" if success else "Setup stopped",
                                  f"{len(packages)} package(s) processed.", "DONE" if success else "CHECK LOG"))

        if success:
            note = Card("warningCard")
            nl = QVBoxLayout(note)
            nl.addWidget(label("One more step", "warningTitle"))
            nl.addWidget(label("Some system or group changes may require logging out and back in.", "muted"))
            lay.addWidget(note)

        results = Card("resultsCard")
        rl = QVBoxLayout(results)
        for name in ["Refresh package index", "Install selected packages", "Install Docker Engine", "Link dotfiles", "Enable services"]:
            r = QHBoxLayout()
            r.addWidget(label(name, "cardTitle"))
            r.addStretch()
            r.addWidget(label("Done" if success else "Review", "accentTag" if success else "tag"))
            rl.addLayout(r)
        lay.addWidget(results)
        lay.addStretch()

        actions = QHBoxLayout()
        back = QPushButton("Back to setup")
        back.setObjectName("secondaryButton")
        back.clicked.connect(lambda: self.open_section(1, 0))
        history = QPushButton("View log")
        history.setObjectName("primaryButton")
        history.clicked.connect(lambda: self.open_section(4, 2))
        actions.addStretch()
        actions.addWidget(back)
        actions.addWidget(history)
        lay.addLayout(actions)

        self.pages.addWidget(page)
        self.pages.setCurrentWidget(page)
