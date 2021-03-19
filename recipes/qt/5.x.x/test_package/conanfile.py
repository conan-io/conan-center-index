import os
import shutil

from conans import ConanFile, tools, Meson, RunEnvironment, CMake
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "qt", "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom/1.1.3")
        if self._meson_supported():
            self.build_requires("meson/0.56.2")

    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def _meson_supported(self):
        return self.options["qt"].shared and\
            not tools.cross_building(self.settings) and\
            not tools.os_info.is_macos and\
            not self._is_mingw()

    def _build_with_qmake(self):
        tools.mkdir("qmake_folder")
        with tools.chdir("qmake_folder"):
            self.output.info("Building with qmake")

            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                args = [self.source_folder, "DESTDIR=bin"]

                def _getenvpath(var):
                    val = os.getenv(var)
                    if val and tools.os_info.is_windows:
                        val = val.replace("\\", "/")
                        os.environ[var] = val
                    return val

                value = _getenvpath('CC')
                if value:
                    args += ['QMAKE_CC=' + value,
                             'QMAKE_LINK_C=' + value,
                             'QMAKE_LINK_C_SHLIB=' + value]

                value = _getenvpath('CXX')
                if value:
                    args += ['QMAKE_CXX=' + value,
                             'QMAKE_LINK=' + value,
                             'QMAKE_LINK_SHLIB=' + value]

                self.run("qmake %s" % " ".join(args), run_environment=True)
                if tools.os_info.is_windows:
                    if self.settings.compiler == "Visual Studio":
                        self.run("jom", run_environment=True)
                    else:
                        self.run("mingw32-make", run_environment=True)
                else:
                    self.run("make", run_environment=True)

    def _build_with_meson(self):
        if self._meson_supported():
            self.output.info("Building with Meson")
            tools.mkdir("meson_folder")
            with tools.environment_append(RunEnvironment(self).vars):
                meson = Meson(self)
                try:
                    meson.configure(build_folder="meson_folder", defs={"cpp_std": "c++11"})
                except ConanException:
                    self.output.info(open("meson_folder/meson-logs/meson-log.txt", 'r').read())
                    raise
                meson.build()

    def _build_with_cmake_find_package_multi(self):
        self.output.info("Building with cmake_find_package_multi")
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self, set_cmake_flags=True)
            if self.settings.os == "Macos":
                cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.14'

            cmake.configure()
            cmake.build()

    def build(self):
        self._build_with_qmake()
        self._build_with_meson()
        self._build_with_cmake_find_package_multi()

    def _test_with_qmake(self):
        self.output.info("Testing qmake")
        bin_path = os.path.join("qmake_folder", "bin")
        if tools.os_info.is_macos:
            bin_path = os.path.join(bin_path, "test_package.app", "Contents", "MacOS")
        shutil.copy("qt.conf", bin_path)
        self.run(os.path.join(bin_path, "test_package"), run_environment=True)

    def _test_with_meson(self):
        if self._meson_supported():
            self.output.info("Testing Meson")
            shutil.copy("qt.conf", "meson_folder")
            self.run(os.path.join("meson_folder", "test_package"), run_environment=True)
    
    def _test_with_cmake_find_package_multi(self):
        self.output.info("Testing CMake_find_package_multi")
        shutil.copy("qt.conf", "bin")
        self.run(os.path.join("bin", "test_package"), run_environment=True)

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self._test_with_qmake()
            self._test_with_meson()
            self._test_with_cmake_find_package_multi()
