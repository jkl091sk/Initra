from pathlib import Path
import shutil

class DotfilesService:
    def __init__(self):
        self.source = Path.home() / ".dotfiles"

    def exists(self):
        return self.source.exists() and self.source.is_dir()

    def candidates(self):
        if not self.exists():
            return []
        result = []
        for item in sorted(self.source.iterdir()):
            if item.name.startswith(".git"):
                continue
            result.append(item)
        return result

    def preview(self):
        rows = []
        home = Path.home()
        for source in self.candidates():
            target = home / source.name
            if target.is_symlink():
                state = "Linked"
            elif target.exists():
                state = "Will backup"
            else:
                state = "New link"
            rows.append((source, target, state))
        return rows

    def apply(self):
        backup = Path.home() / ".local/share/initra/dotfiles-backup"
        backup.mkdir(parents=True, exist_ok=True)
        results = []
        for source, target, _ in self.preview():
            try:
                if target.is_symlink():
                    target.unlink()
                elif target.exists():
                    dest = backup / target.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(target), str(dest))
                target.symlink_to(source, target_is_directory=source.is_dir())
                results.append(f"Linked {target} -> {source}")
            except OSError as exc:
                results.append(f"Failed {target}: {exc}")
        return results
