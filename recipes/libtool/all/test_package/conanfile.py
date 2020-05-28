from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from contextlib import contextmanager
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "LD": "link",
                }):
                    yield
        else:
            yield

    @property
    def _package_folder(self):
        return os.path.join(self.build_folder, "package")

    def _build_autotools(self):
        """ Test autotools integration """
        # Copy autotools directory to build folder
        shutil.copytree(os.path.join(self.source_folder, "autotools"), os.path.join(self.build_folder, "autotools"))
        with tools.chdir("autotools"):
            self.run("{} --install --verbose -Wall".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)

        tools.mkdir(self._package_folder)
        conf_args = [
            "--prefix={}".format(tools.unix_path(self._package_folder)),
            "--enable-shared", "--enable-static",
        ]

        os.mkdir("bin_autotools")
        with tools.chdir("bin_autotools"):
            with self._build_context():
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                autotools.libs = []
                autotools.configure(args=conf_args, configure_dir=os.path.join(self.build_folder, "autotools"))
                autotools.make(args=["V=1", "-j1"])
                autotools.install()

    def _test_autotools(self):
        assert os.path.isdir(os.path.join(self._package_folder, "bin"))
        assert os.path.isfile(os.path.join(self._package_folder, "include", "lib.h"))
        assert os.path.isdir(os.path.join(self._package_folder, "lib"))

        if not tools.cross_building(self.settings):
            self.run(os.path.join(self._package_folder, "bin", "test_package"), run_environment=True)

    def _build_ltdl(self):
        """ Build library using ltdl library """
        cmake = CMake(self)
        cmake.configure(source_folder="ltdl")
        cmake.build()

    def _test_ltdl(self):
        """ Test library using ltdl library"""
        lib_suffix = {
            "Linux": "so",
            "Macos": "dylib",
            "Windows": "dll",
        }[str(self.settings.os)]

        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            libdir = "bin" if self.settings.os == "Windows" else "lib"
            lib_path = os.path.join(libdir, "liba.{}".format(lib_suffix))
            self.run("{} {}".format(bin_path, lib_path), run_environment=True)

    def build(self):
        self._build_autotools()
        self._build_ltdl()

    def test(self):
        self._test_autotools()
        self._test_ltdl()
