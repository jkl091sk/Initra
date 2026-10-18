APP_STYLE = """
* {
    font-family: "Ubuntu", "Noto Sans", sans-serif;
    font-size: 14px;
    color: #E8EDF5;
}
QMainWindow, QWidget#root, QWidget#page, QStackedWidget#pages {
    background: #101419;
}
QFrame#sidebar {
    background: #191E24;
    border-right: 1px solid #252C35;
}
QLabel#brand { font-size: 20px; font-weight: 800; color: #F6F8FB; }
QPushButton#navButton {
    background: transparent; border: none; border-radius: 8px;
    padding: 11px 12px; text-align: left; color: #8994A3; font-weight: 500;
}
QPushButton#navButton:hover { background: #202731; color: #E8EDF5; }
QPushButton#navButton:checked {
    background: #222A34; color: #F8FAFC; border-left: 3px solid #50D8B7;
}
QFrame#systemCard, QFrame#card, QFrame#stepCard, QFrame#packageRow,
QFrame#serviceCard, QFrame#settingsCard, QFrame#toolbarCard, QFrame#noticeCard,
QFrame#progressCard, QFrame#applySteps, QFrame#terminalCard, QFrame#resultsCard {
    background: #191F26; border: 1px solid #29313B; border-radius: 9px;
}
QFrame#summaryCard {
    background: #191F26; border: 1px solid #2B333E; border-radius: 10px;
}
QFrame#warningCard {
    background: #1C1E1F; border: 1px solid #66512D; border-radius: 9px;
}
QLabel#systemTitle, QLabel#cardTitle { color: #F0F3F7; font-weight: 700; }
QLabel#systemValue, QLabel#muted, QLabel#subtitle, QLabel#footerText { color: #8290A2; }
QLabel#eyebrow { color: #748092; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#pageTitle { color: #F5F7FA; font-size: 30px; font-weight: 800; }
QLabel#command { color: #7E8FA5; font-family: monospace; }
QLabel#stepNumber { color: #61758E; font-family: monospace; }
QLabel#tag {
    background: #222B35; border: 1px solid #2C3743; border-radius: 10px;
    padding: 5px 8px; color: #8EA0B6; font-size: 10px;
}
QLabel#accentTag {
    background: #14372F; border: 1px solid #245A4C; border-radius: 10px;
    padding: 5px 8px; color: #59E0BD; font-size: 10px; font-weight: 700;
}
QLabel#summaryValue { color: #E9EDF3; font-weight: 700; }
QPushButton#primaryButton {
    background: #52D6B5; color: #0A1714; border: none; border-radius: 8px;
    padding: 11px 18px; font-weight: 800;
}
QPushButton#primaryButton:hover { background: #68E1C1; }
QPushButton#secondaryButton {
    background: transparent; color: #DDE4EC; border: 1px solid #34404D;
    border-radius: 8px; padding: 10px 15px; font-weight: 600;
}
QPushButton#secondaryButton:hover { background: #202731; }
QPushButton#ghostButton {
    background: transparent; color: #98A5B5; border: none; padding: 9px;
}
QPushButton#dangerButton {
    background: transparent; color: #F19A94; border: 1px solid #8B4B47;
    border-radius: 8px; padding: 10px 15px; font-weight: 600;
}
QLineEdit, QComboBox {
    background: #0F141A; border: 1px solid #2C3743; border-radius: 8px;
    padding: 9px 11px; color: #E8EDF5;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #50D8B7; }
QComboBox QAbstractItemView { background: #171D24; color: #E8EDF5; selection-background-color: #24302E; }
QCheckBox { spacing: 9px; color: #DDE4EC; }
QCheckBox::indicator {
    width: 17px; height: 17px; border: 1px solid #526174;
    border-radius: 3px; background: #11171D;
}
QCheckBox::indicator:checked { background: #50D8B7; border: 1px solid #50D8B7; }
QPlainTextEdit {
    background: #0B0F14; border: 1px solid #29313B; border-radius: 8px;
    padding: 12px; color: #AAB7C8; font-family: monospace;
}
QPlainTextEdit#terminal { border: none; background: #0B0F14; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: #101419; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: #34404D; border-radius: 4px; min-height: 32px; }
QProgressBar {
    background: #222A33; border: none; border-radius: 3px; height: 7px;
}
QProgressBar::chunk { background: #50D8B7; border-radius: 3px; }
QLabel#progressNumber { font-size: 22px; font-weight: 800; }
QLabel#stepState { color: #50D8B7; font-size: 17px; }
QLabel#terminalTabActive { color: #F3F6F9; border-bottom: 2px solid #50D8B7; padding: 7px; }
QLabel#terminalTab { color: #7D8998; padding: 7px; }
QLabel#warningTitle { color: #E6C27D; font-weight: 700; }
QLabel#serviceIcon { color: #50D8B7; font-size: 18px; }

/* Welcome */
QWidget#welcomeOverlay { background: #0B1016; }
QFrame#welcomePanel {
    background: #151B22; border: 1px solid #29333F; border-radius: 14px;
}
QFrame#detectedCard {
    background: #11171D; border: 1px solid #29333F; border-radius: 8px;
}
QLabel#welcomeBrand { font-size: 19px; font-weight: 800; color: #F5F7FA; }
QLabel#welcomeTitle { font-size: 31px; font-weight: 800; color: #F5F7FA; }
QLabel#welcomeSubtitle { color: #8795A8; font-size: 14px; }
QPushButton#profileChoice {
    background: #191F27; color: #A4B0C0; border: 1px solid #2B3541;
    border-radius: 10px; padding: 12px; font-weight: 600;
}
QPushButton#profileChoice:hover { background: #202833; border: 1px solid #3B4B5C; color: #FFFFFF; }
QPushButton#profileChoice:checked {
    background: #1A2928; border: 1px solid #50D8B7; color: #FFFFFF;
}
QToolTip {
    background: #202731; color: #F2F5F8; border: 1px solid #34404D; padding: 5px;
}

/* v1.2 Dashboard / Updates / Cleanup */
QFrame#heroCard, QFrame#dashboardCard, QFrame#metricCard,
QFrame#updateHero, QFrame#cleanupHero, QFrame#cleanupRow {
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
}
QLabel#heroTitle { color:#F5F7FA; font-size:18px; font-weight:800; }
QLabel#scoreNumber {
    color:#59E0BD; font-size:20px; font-weight:900;
    background:#14372F; border:1px solid #245A4C; border-radius:10px; padding:10px 14px;
}
QLabel#metricIcon { color:#50D8B7; font-size:16px; }
QLabel#metricValue { color:#F5F7FA; font-size:18px; font-weight:800; }
QLabel#sectionTitle { color:#F5F7FA; font-size:15px; font-weight:800; }
QLabel#dashboardValue { color:#C8D1DD; }
QPushButton#quickButton {
    background:#151B22; color:#C8D2DE; border:1px solid #29333F;
    border-radius:8px; padding:11px 12px; text-align:left; font-weight:600;
}
QPushButton#quickButton:hover {
    background:#1D2630; color:#FFFFFF; border:1px solid #3A4B5D;
}
QLabel#updateBig { color:#F5F7FA; font-size:19px; font-weight:800; }
QLabel#cleanupNumber { color:#F5F7FA; font-size:34px; font-weight:900; }
QLabel#cleanupSize { color:#59E0BD; font-weight:800; }


/* v1.3 Software Center / Repositories */
QFrame#softwareRow, QFrame#repoHero {
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
}
QFrame#softwareRow:hover {
    background: #1C232B;
    border: 1px solid #354352;
}
QLabel#appIcon {
    background: #172B31;
    color: #62E3C2;
    border: 1px solid #28515A;
    border-radius: 9px;
    font-size: 16px;
    font-weight: 900;
}
QLabel#sourceTag {
    background: #172333;
    color: #91BDF4;
    border: 1px solid #2C4766;
    border-radius: 10px;
    padding: 5px 8px;
    font-size: 10px;
    font-weight: 800;
}


/* v1.4 Tweaks / Startup / Drivers / System */
QFrame#tweakCard, QFrame#startupAdd, QFrame#startupRow,
QFrame#driverHero, QFrame#infoCard {
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
}
QFrame#startupRow:hover, QFrame#tweakCard:hover {
    background: #1D242C;
    border: 1px solid #354352;
}
QLabel#driverBig {
    color: #F5F7FA;
    font-size: 18px;
    font-weight: 800;
}
QLabel#infoValue {
    color: #D7DEE8;
    font-weight: 600;
}


/* v1.5 Health Check */
QFrame#healthHero, QFrame#healthRow {
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
}
QFrame#healthRow:hover {
    background: #1D242C;
    border: 1px solid #354352;
}
QLabel#healthScore {
    color: #5DE2BE;
    font-size: 34px;
    font-weight: 900;
}
QLabel#healthOk {
    color: #5DE2BE;
    background: #15372F;
    border: 1px solid #285A4D;
    border-radius: 17px;
    font-weight: 900;
}
QLabel#healthWarn {
    color: #F1C46C;
    background: #3A3020;
    border: 1px solid #67532D;
    border-radius: 17px;
    font-weight: 900;
}
QLabel#healthDetail {
    color: #9BA8B7;
    font-family: monospace;
    padding-top: 5px;
}


/* v1.6 Backup & Restore */
QFrame#backupHero, QFrame#backupRow {
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
}
QFrame#backupRow:hover {
    background: #1D242C;
    border: 1px solid #354352;
}


/* v1.7 Profiles 2.0 */
QFrame#profileCard {
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
}
QFrame#profileCard:hover {
    background: #1D242C;
    border: 1px solid #354352;
}
QLabel#profileMeta {
    color: #62DDBD;
    font-size: 11px;
    font-weight: 700;
    padding-top: 3px;
}
QDialog#profileDialog {
    background: #11161C;
}
QTabWidget::pane {
    border: 1px solid #29313B;
    background: #151B22;
    border-radius: 8px;
}
QTabBar::tab {
    background: #171D24;
    color: #8F9CAA;
    padding: 9px 14px;
    border: 1px solid #29313B;
}
QTabBar::tab:selected {
    color: #5DE2BE;
    background: #1D272C;
}


/* v1.8 Import / Export */
QFileDialog {
    background: #11161C;
    color: #E8EDF3;
}


/* v1.9 UX / Wizard / Command Palette */
QPushButton#paletteItem, QPushButton#wizardProfile {
    text-align: left;
    background: #191F26;
    border: 1px solid #29313B;
    border-radius: 10px;
    padding: 8px;
}
QPushButton#paletteItem:hover, QPushButton#wizardProfile:hover {
    background: #1D252D;
    border: 1px solid #3B4A59;
}
QPushButton#wizardProfile:checked {
    background: #17312E;
    border: 1px solid #45B99C;
}


/* v2.0 distro compatibility */
QFrame#distroCard {
    background: #161F25;
    border: 1px solid #2D4851;
    border-radius: 11px;
}


QScrollArea#sidebarScroll,
QScrollArea#sidebarScroll > QWidget > QWidget,
QWidget#sidebarNavBody {
    background: transparent;
}
QScrollArea#sidebarScroll QScrollBar:vertical {
    width: 5px;
    background: transparent;
}
QScrollArea#sidebarScroll QScrollBar::handle:vertical {
    background: #313B47;
    border-radius: 2px;
    min-height: 36px;
}
QFrame#systemCard {
    background: #151B22;
    border: 1px solid #2B3541;
    border-radius: 10px;
}
QFrame#cleanupHero { min-height: 92px; }
QFrame#cleanupRow { min-height: 58px; }



/* v2.1.1 grouped navigation fixes */
QTabWidget#sectionTabs {
    background: transparent;
}
QTabWidget#sectionTabs::pane {
    border: 1px solid #26313C;
    border-radius: 10px;
    background: #10161D;
    margin-top: 0px;
}
QTabWidget#sectionTabs QTabBar {
    background: transparent;
}
QTabWidget#sectionTabs QTabBar::tab {
    min-height: 20px;
    background: #111820;
    color: #8FA0B4;
    border: 1px solid #26313C;
    border-bottom: none;
    padding: 9px 18px;
    margin-right: 4px;
    font-weight: 600;
}
QTabWidget#sectionTabs QTabBar::tab:first {
    border-top-left-radius: 8px;
}
QTabWidget#sectionTabs QTabBar::tab:last {
    border-top-right-radius: 8px;
}
QTabWidget#sectionTabs QTabBar::tab:hover {
    color: #E6EDF3;
    background: #18222C;
}
QTabWidget#sectionTabs QTabBar::tab:selected {
    color: #64E2CF;
    background: #172129;
    border-bottom: 2px solid #64E2CF;
}
QScrollArea#sectionContentScroll,
QScrollArea#sectionContentScroll > QWidget > QWidget {
    background: #10161D;
    border: none;
}
QPushButton#quickButton {
    min-height: 38px;
    padding: 7px 12px;
    text-align: left;
}

"""
