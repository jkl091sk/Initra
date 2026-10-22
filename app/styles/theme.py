"""Initra visual theme (v3.2).

One stylesheet, one palette. Qt style sheets have no CSS variables, so the
colour tokens below are substituted into the template at import time.
Change a colour here and it changes everywhere.
"""

PALETTE = {
    "BG": "#14111B",        # window / page background
    "SIDE": "#1A1623",      # sidebar and secondary surfaces
    "CARD": "#201B2B",      # cards, elevated surfaces
    "HOVER": "#292335",     # hover surface
    "INPUT": "#17131F",     # text inputs
    "PINK": "#F178B6",      # primary brand accent
    "PINK2": "#F690C6",     # highlight / hover of the accent
    "PINKBG": "#3A2236",    # selected-item tint
    "TEXT": "#FAF7FF",
    "MUTED": "#A29BB5",
    "FAINT": "#6F687E",
    "BD": "#322B40",
    "BD2": "#463D58",
    "BLUE": "#8DB8F2",      # tiny accents only
    "OK": "#7BDCB0",
    "OKBG": "#18282A",
    "OKBD": "#2C5445",
    "WARN": "#F1C46C",
    "WARNBG": "#2E2619",
    "WARNBD": "#5E4B27",
    "DANGER": "#F19A94",
    "DANGERBD": "#7A4450",
}

_TEMPLATE = """
* {
    font-family: "Inter", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 14px;
    color: @TEXT@;
}
QMainWindow, QWidget#root, QWidget#page, QStackedWidget#pages { background: @BG@; }
QToolTip { background: @HOVER@; color: @TEXT@; border: 1px solid @BD2@; padding: 5px; }

/* ---------- Sidebar ---------- */
QFrame#sidebar { background: @SIDE@; border-right: 1px solid @BD@; }
QLabel#brand { font-size: 21px; font-weight: 700; color: @TEXT@; }
QScrollArea#sidebarScroll,
QScrollArea#sidebarScroll > QWidget > QWidget,
QWidget#sidebarNavBody { background: transparent; }
QScrollArea#sidebarScroll QScrollBar:vertical { width: 5px; background: transparent; }
QScrollArea#sidebarScroll QScrollBar::handle:vertical { background: @BD2@; border-radius: 2px; min-height: 36px; }
QPushButton#navButton {
    background: transparent; border: 1px solid transparent; border-left: 3px solid transparent;
    border-radius: 10px; padding: 10px 12px; text-align: left; color: @MUTED@; font-weight: 500;
}
QPushButton#navButton:hover { background: @HOVER@; color: @TEXT@; }
QPushButton#navButton:checked {
    background: @HOVER@; color: @TEXT@; border: 1px solid @BD2@; border-left: 3px solid @PINK@;
}
QFrame#systemCard { background: @CARD@; border: 1px solid @BD@; border-radius: 12px; }

/* ---------- Surfaces ---------- */
QFrame#card, QFrame#stepCard, QFrame#packageRow, QFrame#serviceCard, QFrame#settingsCard,
QFrame#toolbarCard, QFrame#noticeCard, QFrame#progressCard, QFrame#applySteps,
QFrame#terminalCard, QFrame#resultsCard, QFrame#summaryCard,
QFrame#heroCard, QFrame#dashboardCard, QFrame#metricCard, QFrame#updateHero,
QFrame#cleanupHero, QFrame#cleanupRow, QFrame#softwareRow, QFrame#repoHero,
QFrame#tweakCard, QFrame#startupAdd, QFrame#startupRow, QFrame#driverHero, QFrame#infoCard,
QFrame#healthHero, QFrame#healthRow, QFrame#backupHero, QFrame#backupRow,
QFrame#profileCard, QFrame#distroCard {
    background: @CARD@; border: 1px solid @BD@; border-radius: 12px;
}
QFrame#softwareRow:hover, QFrame#startupRow:hover, QFrame#tweakCard:hover,
QFrame#healthRow:hover, QFrame#backupRow:hover, QFrame#profileCard:hover,
QFrame#metricCard:hover {
    background: @HOVER@; border: 1px solid @BD2@;
}
QFrame#warningCard { background: @WARNBG@; border: 1px solid @WARNBD@; border-radius: 12px; }
QFrame#cleanupHero { min-height: 92px; }
QFrame#cleanupRow { min-height: 58px; }

/* ---------- Text ---------- */
QLabel#pageTitle { color: @TEXT@; font-size: 28px; font-weight: 700; }
QLabel#systemTitle, QLabel#cardTitle { color: @TEXT@; font-weight: 600; }
QLabel#sectionTitle { color: @TEXT@; font-size: 15px; font-weight: 600; }
QLabel#heroTitle { color: @TEXT@; font-size: 18px; font-weight: 700; }
QLabel#systemValue, QLabel#muted, QLabel#subtitle, QLabel#footerText { color: @MUTED@; }
QLabel#eyebrow { color: @MUTED@; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }
QLabel#command { color: @MUTED@; font-family: monospace; }
QLabel#stepNumber { color: @MUTED@; font-family: monospace; }
QLabel#summaryValue, QLabel#dashboardValue, QLabel#infoValue { color: @TEXT@; font-weight: 500; }
QLabel#metricIcon { color: @PINK@; font-size: 16px; }
QLabel#metricValue { color: @TEXT@; font-size: 18px; font-weight: 700; }
QLabel#updateBig, QLabel#driverBig { color: @TEXT@; font-size: 18px; font-weight: 700; }
QLabel#cleanupNumber { color: @TEXT@; font-size: 34px; font-weight: 700; }
QLabel#cleanupSize { color: @PINK@; font-weight: 700; }
QLabel#progressNumber { font-size: 22px; font-weight: 700; }
QLabel#stepState { color: @PINK@; font-size: 17px; }
QLabel#serviceIcon { color: @PINK@; font-size: 18px; }
QLabel#warningTitle { color: @WARN@; font-weight: 600; }
QLabel#profileMeta { color: @PINK2@; font-size: 11px; font-weight: 600; padding-top: 3px; }
QLabel#healthDetail { color: @MUTED@; font-family: monospace; padding-top: 5px; }
QLabel#terminalTabActive { color: @TEXT@; border-bottom: 2px solid @PINK@; padding: 7px; }
QLabel#terminalTab { color: @MUTED@; padding: 7px; }

/* ---------- Tags and status ---------- */
QLabel#tag {
    background: @SIDE@; border: 1px solid @BD2@; border-radius: 10px;
    padding: 5px 10px; color: @MUTED@; font-size: 11px;
}
QLabel#accentTag, QLabel#versionTag {
    background: @PINKBG@; border: 1px solid @PINK@; border-radius: 10px;
    padding: 5px 10px; color: @PINK2@; font-size: 11px; font-weight: 600;
}
QLabel#statusTag {
    background: @OKBG@; border: 1px solid @OKBD@; border-radius: 10px;
    padding: 5px 12px; color: @OK@; font-size: 12px; font-weight: 600;
}
QLabel#statusTagWarn {
    background: @WARNBG@; border: 1px solid @WARNBD@; border-radius: 10px;
    padding: 5px 12px; color: @WARN@; font-size: 12px; font-weight: 600;
}
QLabel#sourceTag {
    background: @SIDE@; color: @BLUE@; border: 1px solid @BD2@; border-radius: 10px;
    padding: 5px 10px; font-size: 11px; font-weight: 600;
}
QLabel#appIcon {
    background: @BG@; color: @PINK@; border: 1px solid @BD2@; border-radius: 9px;
    font-size: 16px; font-weight: 700;
}
QLabel#scoreNumber {
    color: @OK@; font-size: 18px; font-weight: 700;
    background: @OKBG@; border: 1px solid @OKBD@; border-radius: 10px; padding: 8px 16px;
}
QLabel#healthScore { color: @OK@; font-size: 34px; font-weight: 700; }
QLabel#healthOk {
    color: @OK@; background: @OKBG@; border: 1px solid @OKBD@; border-radius: 17px; font-weight: 700;
}
QLabel#healthWarn {
    color: @WARN@; background: @WARNBG@; border: 1px solid @WARNBD@; border-radius: 17px; font-weight: 700;
}

/* ---------- Buttons ---------- */
QPushButton#primaryButton {
    background: @PINK@; color: @BG@; border: 1px solid @PINK@; border-radius: 10px;
    padding: 10px 18px; font-weight: 700;
}
QPushButton#primaryButton:hover { background: @PINK2@; border-color: @PINK2@; }
QPushButton#primaryButton:disabled { background: @BD@; border-color: @BD@; color: @FAINT@; }
QPushButton#secondaryButton {
    background: transparent; color: @TEXT@; border: 1px solid @BD2@; border-radius: 10px;
    padding: 10px 16px; font-weight: 600;
}
QPushButton#secondaryButton:hover { background: @HOVER@; border-color: @PINK@; }
QPushButton#ghostButton { background: transparent; color: @MUTED@; border: none; padding: 9px; }
QPushButton#ghostButton:hover { color: @TEXT@; }
QPushButton#dangerButton {
    background: transparent; color: @DANGER@; border: 1px solid @DANGERBD@; border-radius: 10px;
    padding: 10px 16px; font-weight: 600;
}
QPushButton#dangerButton:hover { background: @HOVER@; }
QPushButton#quickButton {
    background: @BG@; color: @TEXT@; border: 1px solid @BD@; border-radius: 10px;
    min-height: 38px; padding: 7px 14px; text-align: left; font-weight: 500;
}
QPushButton#quickButton:hover { background: @HOVER@; border: 1px solid @PINK@; }
QPushButton#paletteItem, QPushButton#wizardProfile {
    text-align: left; background: @CARD@; border: 1px solid @BD@; border-radius: 12px; padding: 8px;
}
QPushButton#paletteItem:hover, QPushButton#wizardProfile:hover { background: @HOVER@; border: 1px solid @BD2@; }
QPushButton#wizardProfile:checked { background: @PINKBG@; border: 1px solid @PINK@; }
QPushButton#profileChoice {
    background: @CARD@; color: @MUTED@; border: 1px solid @BD@; border-radius: 12px;
    padding: 12px; font-weight: 600;
}
QPushButton#profileChoice:hover { background: @HOVER@; border: 1px solid @BD2@; color: @TEXT@; }
QPushButton#profileChoice:checked { background: @PINKBG@; border: 1px solid @PINK@; color: @TEXT@; }
QPushButton:disabled { color: @FAINT@; }

/* ---------- Inputs ---------- */
QLineEdit, QComboBox {
    background: @INPUT@; border: 1px solid @BD2@; border-radius: 10px; padding: 9px 12px; color: @TEXT@;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid @PINK@; }
QLineEdit:disabled, QComboBox:disabled { color: @FAINT@; }
QComboBox QAbstractItemView {
    background: @CARD@; color: @TEXT@; border: 1px solid @BD2@; selection-background-color: @PINKBG@;
}
QCheckBox { spacing: 9px; color: @TEXT@; }
QCheckBox:disabled { color: @FAINT@; }
QCheckBox::indicator {
    width: 17px; height: 17px; border: 1px solid @BD2@; border-radius: 5px; background: @INPUT@;
}
QCheckBox::indicator:hover { border: 1px solid @PINK@; }
QCheckBox::indicator:checked { background: @PINK@; border: 1px solid @PINK@; }
QPlainTextEdit {
    background: @INPUT@; border: 1px solid @BD@; border-radius: 10px; padding: 12px;
    color: @MUTED@; font-family: monospace;
}
QPlainTextEdit#terminal { border: none; background: @INPUT@; }
QProgressBar { background: @BD@; border: none; border-radius: 3px; height: 7px; }
QProgressBar::chunk { background: @PINK@; border-radius: 3px; }

/* ---------- Scrolling ---------- */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollArea#sectionContentScroll,
QScrollArea#sectionContentScroll > QWidget,
QScrollArea#sectionContentScroll > QWidget > QWidget { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: @BD2@; border-radius: 4px; min-height: 32px; }
QScrollBar::handle:vertical:hover { background: @MUTED@; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ---------- Tabs: independent pills ---------- */
QTabWidget::pane { border: 0px; background: transparent; }
QTabWidget#sectionTabs { background: transparent; border: none; }
QTabWidget#sectionTabs::pane { border: 0px; background: transparent; margin-top: 10px; }
QTabBar { background: transparent; border: none; }
QTabBar::tab {
    min-height: 22px; min-width: 76px; background: @SIDE@; color: @MUTED@;
    border: 1px solid @BD@; border-radius: 10px; padding: 9px 18px; margin-right: 7px; font-weight: 600;
}
QTabBar::tab:hover { color: @TEXT@; background: @HOVER@; border-color: @BD2@; }
QTabBar::tab:selected { color: @TEXT@; background: @PINKBG@; border: 1px solid @PINK@; }

/* ---------- Welcome / dialogs ---------- */
QWidget#welcomeOverlay { background: @BG@; }
QFrame#welcomePanel { background: @CARD@; border: 1px solid @BD2@; border-radius: 16px; }
QFrame#detectedCard { background: @SIDE@; border: 1px solid @BD@; border-radius: 10px; }
QLabel#welcomeBrand { font-size: 19px; font-weight: 700; color: @TEXT@; }
QLabel#welcomeTitle { font-size: 31px; font-weight: 700; color: @TEXT@; }
QLabel#welcomeSubtitle { color: @MUTED@; font-size: 14px; }
QDialog#profileDialog { background: @SIDE@; }
QFileDialog { background: @SIDE@; color: @TEXT@; }
QMessageBox { background: @SIDE@; }
"""


def build_style() -> str:
    out = _TEMPLATE
    for key, value in PALETTE.items():
        out = out.replace(f"@{key}@", value)
    return out


APP_STYLE = build_style()
