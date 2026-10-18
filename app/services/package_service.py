import shutil
import subprocess

class PackageService:
    @staticmethod
    def apt_available():
        return shutil.which("apt") is not None

    @staticmethod
    def is_installed(package):
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Status}", package],
            capture_output=True, text=True, check=False
        )
        return result.returncode == 0 and "install ok installed" in result.stdout

    @staticmethod
    def dry_run(packages):
        if not packages:
            return ["No packages selected."]
        cmd = ["apt-get", "-s", "install", *packages]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = (result.stdout + "\n" + result.stderr).strip()
        return output.splitlines() if output else ["Dry run produced no output."]

    @staticmethod
    def install_command(packages):
        # pkexec handles privilege elevation without storing a sudo password.
        return ["pkexec", "apt-get", "install", "-y", *packages]
