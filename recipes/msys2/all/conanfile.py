from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.files import chdir, get, replace_in_file
import fnmatch
import os
import shutil
import subprocess
import errno

try:
    import ctypes
except ImportError:
    pass
except ValueError:
    pass

required_conan_version = ">=1.47.0"


class lock:
    def __init__(self):
        self.handle = ctypes.windll.kernel32.CreateMutexA(None, 0, "Global\\ConanMSYS2".encode())
        if not self.handle:
            raise ctypes.WinError()

    def __enter__(self):
        status = ctypes.windll.kernel32.WaitForSingleObject(self.handle, 0xFFFFFFFF)
        if status not in [0, 0x80]:
            raise ctypes.WinError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = ctypes.windll.kernel32.ReleaseMutex(self.handle)
        if not status:
            raise ctypes.WinError()

    def close(self):
        ctypes.windll.kernel32.CloseHandle(self.handle)

    __del__ = close


class MSYS2Conan(ConanFile):
    name = "msys2"
    description = "MSYS2 is a software distro and building platform for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.msys2.org"
    license = "MSYS license"
    topics = ("msys", "unix", "subsystem")

    settings = "os", "arch", "compiler", "build_type"
    # "exclude_files" "packages" "additional_packages" values are a comma separated list
    options = {
        "exclude_files": "ANY",
        "packages": "ANY",
        "additional_packages": "ANY"
    }
    default_options = {
        "exclude_files": "*/link.exe",
        "packages": "base-devel,binutils,gcc",
        "additional_packages": None
    }

    short_paths = True

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.info.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")
        if self.info.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only Windows x64 supported")

    def source(self):
        # sources are different per configuration - do download in build
        pass

    def _update_pacman(self):
        with chdir(self, os.path.join(self._msys_dir, "usr", "bin")):
            try:
                self._kill_pacman()

                # https://www.msys2.org/docs/ci/
                self.run('bash -l -c "pacman --debug --noconfirm --ask 20 -Syuu"')  # Core update (in case any core packages are outdated)
                self._kill_pacman()
                self.run('bash -l -c "pacman --debug --noconfirm --ask 20 -Syuu"')  # Normal update
                self._kill_pacman()
                self.run('bash -l -c "pacman --debug -Rc dash --noconfirm"')
            except ConanException:
                self.run('bash -l -c "cat /var/log/pacman.log || echo nolog"')
                self._kill_pacman()
                raise

    # https://github.com/msys2/MSYS2-packages/issues/1966
    def _kill_pacman(self):
        if (self.settings.os == "Windows"):
            taskkill_exe = os.path.join(os.environ.get('SystemRoot'), 'system32', 'taskkill.exe')

            log_out = True
            if log_out:
                out = subprocess.PIPE
                err = subprocess.STDOUT
            else:
                out = open(os.devnull, 'w')
                err = subprocess.PIPE

            if os.path.exists(taskkill_exe):
                taskkill_cmds = [
                    f"{taskkill_exe} /f /t /im pacman.exe",
                    f"{taskkill_exe} /f /im gpg-agent.exe",
                    f"{taskkill_exe} /f /im dirmngr.exe",
                    f'{taskkill_exe} /fi "MODULES eq msys-2.0.dll"',
                ]
                for taskkill_cmd in taskkill_cmds:
                    try:
                        proc = subprocess.Popen(taskkill_cmd, stdout=out, stderr=err, bufsize=1)
                        proc.wait()
                    except OSError as e:
                        if e.errno == errno.ENOENT:
                            raise ConanException("Cannot kill pacman")

    @property
    def _msys_dir(self):
        subdir = "msys64"
        return os.path.join(self.package_folder, "bin", subdir)

    def build(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=os.path.join(self.package_folder, "bin"))
        with lock():
            self._do_build()

    def _do_build(self):
        packages = []
        if self.options.packages:
            packages.extend(str(self.options.packages).split(","))
        if self.options.additional_packages:
            packages.extend(str(self.options.additional_packages).split(","))

        self._update_pacman()

        with chdir(os.path.join(self._msys_dir, "usr", "bin")):
            for package in packages:
                self.run(f'bash -l -c "pacman -S {package}--noconfirm"')
            for package in ['pkgconf']:
                self.run(f'bash -l -c "pacman -Rs -d -d $(pacman -Qsq {package}) --noconfirm"')

        self._kill_pacman()

        # create /tmp dir in order to avoid
        # bash.exe: warning: could not find /tmp, please create!
        tmp_dir = os.path.join(self._msys_dir, 'tmp')
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        tmp_name = os.path.join(tmp_dir, 'dummy')
        with open(tmp_name, 'a'):
            os.utime(tmp_name, None)

        # Prepend the PKG_CONFIG_PATH environment variable with an eventual PKG_CONFIG_PATH environment variable
        replace_in_file(self, os.path.join(self._msys_dir, "etc", "profile"),
                              'PKG_CONFIG_PATH="', 'PKG_CONFIG_PATH="$PKG_CONFIG_PATH:')

    def package(self):
        excludes = None
        if self.options.exclude_files:
            excludes = tuple(str(self.options.exclude_files).split(","))
        #self.copy("*", dst="bin", src=self._msys_dir, excludes=excludes)
        for exclude in excludes:
            for root, _, filenames in os.walk(self._msys_dir):
                for filename in filenames:
                    fullname = os.path.join(root, filename)
                    if fnmatch.fnmatch(fullname, exclude):
                        os.unlink(fullname)
        shutil.copytree(os.path.join(self._msys_dir, "usr", "share", "licenses"),
                        os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.resdirs = []

        msys_root = self._msys_dir
        msys_bin = os.path.join(msys_root, "usr", "bin")
        self.cpp_info.bindirs.append(msys_bin)

        self.output.info(f"Creating MSYS_ROOT env var : {msys_root}")
        self.buildenv_info.define_path("MSYS_ROOT", msys_root)

        self.output.info(f"Creating MSYS_BIN env var : {msys_bin}")
        self.buildenv_info.define_path("MSYS_BIN", msys_bin)

        self.conf_info.define("tools.microsoft.bash:subsystem", "msys2")
        self.conf_info.define("tools.microsoft.bash:path", os.path.join(msys_bin, "bash.exe"))

        # conan v1 specific stuff
        self.env_info.MSYS_ROOT = msys_root
        self.env_info.MSYS_BIN = msys_bin
        self.output.info(f"Appending PATH env var with : {msys_bin}")
        self.env_info.path.append(msys_bin)
