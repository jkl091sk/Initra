from __future__ import annotations

from pathlib import Path
import shlex
import subprocess

from PySide6.QtWidgets import QLabel, QMessageBox


class V31CompatService:
    """v3.1 fixes for workflows that still contained legacy APT-only assumptions."""

    @staticmethod
    def install(MainWindow):
        original_init = MainWindow.__init__
        original_log_history = MainWindow.log_history
        original_build_cleanup_page = MainWindow.build_cleanup_page
        original_build_software_page = MainWindow.build_software_page
        original_build_repositories_page = MainWindow.build_repositories_page
        original_build_updates_page = MainWindow.build_updates_page

        def init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.maintenance.distro = self.distro
            self.software.distro = self.distro
            self.history_service.prune(self.history_path, int(self.settings.get("history_days", 30) or 0))

        def log_history(self, text):
            original_log_history(self, text)
            self.history_service.prune(self.history_path, int(self.settings.get("history_days", 30) or 0))

        def build_software_page(self):
            page = original_build_software_page(self)
            manager = self.distro.info.get("package_manager", "native").upper()
            if hasattr(self, "software_source"):
                index = self.software_source.findText("APT")
                if index >= 0:
                    self.software_source.setItemText(index, "Native")
            for item in page.findChildren(QLabel):
                if "APT + FLATPAK" in item.text():
                    item.setText(f"{manager} + FLATPAK")
            return page

        def refresh_software(self):
            if not hasattr(self, "software_list"):
                return
            self.clear_layout(self.software_list)
            query = self.software_search.text().strip().lower()
            source_filter = self.software_source.currentText()
            category_filter = self.software_category.currentText()
            entries = []
            if source_filter in ("All sources", "Native", "APT"):
                for category, apps in self.software.APT_APPS.items():
                    for package, desc in apps.items():
                        entries.append(("Native", category, package, package, desc))
            if source_filter in ("All sources", "Flatpak"):
                for category, apps in self.software.FLATPAK_APPS.items():
                    for app_id, (name, desc) in apps.items():
                        entries.append(("Flatpak", category, app_id, name, desc))
            shown = 0
            for source, category, app_id, name, desc in entries:
                if category_filter != "All categories" and category != category_filter:
                    continue
                if query and query not in f"{name} {app_id} {desc}".lower():
                    continue
                installed = self.software.native_installed(app_id) if source == "Native" else self.software.flatpak_installed(app_id)
                from app.views.main_window import Card, label
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
                card = Card("softwareRow")
                row = QHBoxLayout(card)
                row.setContentsMargins(14, 11, 14, 11)
                icon = label(name[:1].upper(), "appIcon")
                icon.setAlignment(Qt.AlignCenter)
                icon.setFixedSize(38, 38)
                row.addWidget(icon)
                text = QVBoxLayout()
                text.setSpacing(2)
                text.addWidget(label(name, "cardTitle")); text.addWidget(label(desc, "muted")); text.addWidget(label(app_id, "command"))
                row.addLayout(text, 1); row.addWidget(label(category.upper(), "tag")); row.addWidget(label((self.distro.info['package_manager'] if source == 'Native' else source).upper(), "sourceTag"))
                action = QPushButton("Remove" if installed else "Install")
                action.setObjectName("secondaryButton" if installed else "primaryButton")
                action.clicked.connect(lambda checked=False, src=source, aid=app_id, nm=name, ins=installed: self.software_action(src, aid, nm, ins))
                row.addWidget(action); self.software_list.addWidget(card); shown += 1
            if not shown:
                from app.views.main_window import Card, label
                from PySide6.QtWidgets import QVBoxLayout
                empty = Card("noticeCard"); el = QVBoxLayout(empty)
                el.addWidget(label("No matching applications", "cardTitle")); el.addWidget(label("Try another search term, category or package source.", "muted")); self.software_list.addWidget(empty)
            self.software_list.addStretch()

        def software_action(self, source, app_id, name, installed):
            action = "Remove" if installed else "Install"
            if source == "Flatpak" and not self.software.has_flatpak():
                if QMessageBox.question(self, "Flatpak is not installed", "Install Flatpak first? Administrator privileges will be requested.") != QMessageBox.Yes:
                    return
                command = self.software.install_flatpak_command()
                if not command:
                    QMessageBox.warning(self, "Flatpak", "Flatpak installation is unavailable on this distribution."); return
                self.run_maintenance_command(command, "Install Flatpak", self.refresh_software); return
            if QMessageBox.question(self, f"{action} {name}", f"{action} {name} using {self.distro.info['package_manager'] if source == 'Native' else source}?") != QMessageBox.Yes:
                return
            if source == "Native":
                command = self.software.native_remove_command(app_id) if installed else self.software.native_install_command(app_id)
            else:
                command = self.software.flatpak_remove_command(app_id) if installed else self.software.flatpak_install_command(app_id)
            if not command:
                QMessageBox.warning(self, name, "This package action is unavailable on the detected distribution."); return
            self.run_maintenance_command(command, f"{action} {name}", self.refresh_software)

        def build_repositories_page(self):
            page = original_build_repositories_page(self)
            for item in page.findChildren(QLabel):
                text = item.text()
                if text == "Inspect APT sources and manage Flathub for Flatpak.": item.setText("Inspect native package sources and manage Flathub for Flatpak.")
                elif text == "APT sources are shown read-only to avoid unsafe source-file edits.": item.setText("Native package sources are shown read-only to avoid unsafe repository edits.")
            return page

        def refresh_repositories(self):
            if not hasattr(self, "repo_view"): return
            has_flatpak = self.software.has_flatpak(); remotes = self.software.flatpak_remotes() if has_flatpak else []
            has_flathub = any(name == "flathub" for name, _ in remotes)
            self.flathub_button.setEnabled(True)
            if not has_flatpak: self.flatpak_status.setText("Flatpak is not installed."); self.flathub_button.setText("Install Flatpak")
            elif has_flathub: self.flatpak_status.setText("Flatpak is installed and Flathub is configured."); self.flathub_button.setText("Flathub ready"); self.flathub_button.setEnabled(False)
            else: self.flatpak_status.setText("Flatpak is installed. Flathub is not configured yet."); self.flathub_button.setText("Add Flathub")
            manager = self.distro.info.get("package_manager", "native").upper()
            lines = [f"{manager} SOURCES", "────────────"]
            sources = self.software.native_sources()
            if not sources: lines.append("No readable native repository files found.")
            for file, entries in sources:
                lines.append(f"\n{file}"); lines.extend((f"  • {entry}" for entry in entries),) if entries else lines.append("  (no enabled entries)")
            lines += ["", "FLATPAK REMOTES", "───────────────"]
            if not has_flatpak: lines.append("Flatpak not installed.")
            elif not remotes: lines.append("No Flatpak remotes configured.")
            else: lines.extend(f"  • {name}  {url}" for name, url in remotes)
            self.repo_view.setPlainText("\n".join(lines))

        def configure_flathub(self):
            if not self.software.has_flatpak():
                manager = self.distro.info.get("package_manager", "package manager")
                if QMessageBox.question(self, "Install Flatpak", f"Install Flatpak using {manager}? Administrator privileges will be requested.") != QMessageBox.Yes: return
                command = self.software.install_flatpak_command()
                if not command: QMessageBox.warning(self, "Flatpak", "Flatpak installation is unavailable on this distribution."); return
                self.run_maintenance_command(command, "Install Flatpak", self.refresh_repositories); return
            if QMessageBox.question(self, "Add Flathub", "Add the official Flathub remote for this user?") != QMessageBox.Yes: return
            self.run_maintenance_command(self.software.add_flathub_command(), "Add Flathub", self.refresh_repositories)

        def build_updates_page(self):
            page = original_build_updates_page(self)
            manager = self.distro.info.get("package_manager", "native").upper()
            for item in page.findChildren(QLabel):
                if item.text() == "Review available APT updates before applying them.": item.setText(f"Review available {manager} updates before applying them.")
                elif item.text() == "APT": item.setText(manager)
            return page

        def refresh_updates(self):
            if not hasattr(self, "update_list"): return
            packages = self.maintenance.upgradable_packages(); self.available_updates = packages
            self.update_big.setText(f"{len(packages)} update(s) available" if packages else "System is up to date")
            manager = self.distro.info.get("package_manager", "package manager").upper()
            self.update_sub.setText("Review the package list below." if packages else f"No package upgrades are currently reported by {manager}.")
            self.update_list.setPlainText("\n".join(f"  ↻  {name}" for name in packages) if packages else "✓ No updates available.")

        def refresh_update_index(self):
            manager = self.distro.info.get("package_manager", "package manager").upper()
            if QMessageBox.question(self, "Refresh package index", f"Refresh {manager} package metadata? Administrator privileges may be requested.") != QMessageBox.Yes: return
            command = self.maintenance.update_command()
            if not command: QMessageBox.warning(self, "Updates", "Package metadata refresh is unavailable on this distribution."); return
            self.run_maintenance_command(command, "Refresh package index", self.refresh_updates)

        def build_cleanup_page(self):
            page = original_build_cleanup_page(self)
            if "APT package cache" in self.cleanup_rows: self.cleanup_rows["Package cache"] = self.cleanup_rows.pop("APT package cache")
            for item in page.findChildren(QLabel):
                if item.text() == "APT package cache": item.setText("Package cache")
                elif item.text() == "Downloaded .deb package files": item.setText(f"Cached packages managed by {self.distro.info.get('package_manager', 'the system')}")
                elif item.text() == "APT cache, thumbnails and user trash": item.setText("Package cache, thumbnails and user trash")
            return page

        def clean_selected(self):
            chosen = [name for name, (cb, _) in self.cleanup_rows.items() if cb.isChecked()]
            if not chosen: QMessageBox.information(self, "Cleanup", "Nothing is selected."); return
            if self.settings.get("confirm_cleanup", True) and QMessageBox.question(self, "Clean selected", "The following items will be cleaned:\n\n• " + "\n• ".join(chosen) + "\n\nOnly checked items will be touched. Deleted trash contents cannot be restored.") != QMessageBox.Yes: return
            messages = []
            if "Thumbnail cache" in chosen: messages.append(f"Thumbnail cache: removed {self.maintenance.cleanup_thumbnails()} item(s).")
            if "User trash" in chosen: messages.append(f"User trash: removed {self.maintenance.cleanup_trash()} item(s).")
            if "Package cache" in chosen:
                command = self.distro.cleanup_command()
                if command: self.run_maintenance_command(command, "Package cache cleanup", self.refresh_cleanup); messages.append(f"{self.distro.info['package_manager']} package-cache cleanup started.")
                else: messages.append("Package cache cleanup is unavailable on this distribution.")
            else: self.refresh_cleanup()
            self.log_history("Cleanup: " + ", ".join(chosen)); QMessageBox.information(self, "Cleanup", "\n".join(messages) or "Cleanup complete.")

        def dry_run(self):
            packages = self.profile_packages(); translated, unsupported = self.distro.translate_packages(packages); manager = self.distro.info.get("package_manager", "unknown")
            cmd = {"apt": ["apt-get", "-s", "install", *translated], "dnf": ["dnf", "--assumeno", "install", *translated], "pacman": ["pacman", "-Sp", "--needed", *translated], "zypper": ["zypper", "--non-interactive", "--dry-run", "install", *translated]}.get(manager)
            if not cmd: QMessageBox.warning(self, "Dry run", "Package simulation is unavailable for this distribution."); return
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False); self.log_history(f"Dry run ({manager}): {len(translated)} packages")
                box = QMessageBox(self); box.setWindowTitle("Dry run"); box.setText(f"{manager.upper()} simulation finished with exit code {result.returncode}.")
                details = result.stdout + "\n" + result.stderr
                if unsupported: details += "\n\nUnsupported aliases: " + ", ".join(unsupported)
                box.setDetailedText(details[-16000:]); box.exec()
            except Exception as exc: QMessageBox.warning(self, "Dry run", str(exc))

        def export_script(self):
            path = Path.home() / "initra-setup.sh"; packages = self.profile_packages(); translated, unsupported = self.distro.translate_packages(packages); manager = self.distro.info.get("package_manager", "unknown"); quoted = " ".join(shlex.quote(x) for x in translated); rows = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
            if manager == "apt": rows += ["sudo apt-get update"] + ([f"sudo apt-get install -y {quoted}"] if translated else [])
            elif manager == "dnf": rows += ["sudo dnf makecache"] + ([f"sudo dnf install -y {quoted}"] if translated else [])
            elif manager == "pacman": rows += [f"sudo pacman -S --needed --noconfirm {quoted}" if translated else "sudo pacman -Sy"]
            elif manager == "zypper": rows += ["sudo zypper --non-interactive refresh"] + ([f"sudo zypper --non-interactive install {quoted}"] if translated else [])
            else: QMessageBox.warning(self, "Export", "Package script export is unavailable for this distribution."); return
            if unsupported: rows += ["", "# Unsupported package aliases skipped: " + ", ".join(unsupported)]
            path.write_text("\n".join(rows) + "\n", encoding="utf-8"); path.chmod(0o755); self.log_history(f"Exported setup script ({manager})"); QMessageBox.information(self, "Export complete", f"Saved to:\n{path}")

        def apply_setup(self):
            packages = self.profile_packages()
            if not packages: QMessageBox.information(self, "Initra", "No packages are selected."); return
            command, unsupported = self.distro.install_command(packages)
            if not command: QMessageBox.warning(self, "Initra", "Package installation is unavailable for this distribution."); return
            if self.settings.get("confirm_apply", True):
                message = f"Install {len(packages)} selected package(s) using {self.distro.info['package_manager']}?\n\nAdministrator privileges will be requested."
                if unsupported: message += "\n\nUnsupported aliases will be skipped: " + ", ".join(unsupported)
                if QMessageBox.question(self, "Apply setup", message) != QMessageBox.Yes: return
            self.log_history(f"Setup started ({self.distro.info['package_manager']}): {len(packages)} selected package(s)"); self.run_maintenance_command(command, f"Install {len(packages)} package(s)", self.refresh_setup)

        MainWindow.__init__ = init; MainWindow.log_history = log_history
        MainWindow.build_software_page = build_software_page; MainWindow.refresh_software = refresh_software; MainWindow.software_action = software_action
        MainWindow.build_repositories_page = build_repositories_page; MainWindow.refresh_repositories = refresh_repositories; MainWindow.configure_flathub = configure_flathub
        MainWindow.build_updates_page = build_updates_page; MainWindow.refresh_updates = refresh_updates; MainWindow.refresh_update_index = refresh_update_index
        MainWindow.build_cleanup_page = build_cleanup_page; MainWindow.clean_selected = clean_selected
        MainWindow.dry_run = dry_run; MainWindow.export_script = export_script; MainWindow.apply_setup = apply_setup
