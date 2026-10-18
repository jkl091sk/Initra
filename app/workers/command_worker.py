from PySide6.QtCore import QThread, Signal
import subprocess

class CommandWorker(QThread):
    line = Signal(str)
    finished_code = Signal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self._process = None

    def run(self):
        try:
            self._process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if self._process.stdout:
                for line in self._process.stdout:
                    self.line.emit(line.rstrip())
            code = self._process.wait()
        except Exception as exc:
            self.line.emit(f"Error: {exc}")
            code = -1
        self.finished_code.emit(code)

    def cancel(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()
