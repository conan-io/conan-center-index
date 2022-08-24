import os
import shutil

from conan import ConanFile
from conan.tools.build import cross_building

from conans import tools, Meson, RunEnvironment, CMake
from conan.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "qt", "cmake", "cmake_find_package_multi", "cmake_find_package", "pkg_config", "qmake"

    def build_requirements(self):
        self.build_requires("cmake/3.23.2")
        if self._meson_supported():
            self.build_requires("meson/0.60.2")

    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def _meson_supported(self):
        return False and self.options["qt"].shared and\
            not cross_building(self) and\
            not tools.os_info.is_macos and\
            not self._is_mingw()

    def _qmake_supported(self):
        return self.settings.compiler != "Visual Studio" or self.options["qt"].shared

    def _cmake_multi_supported(self):
        return True

    def _build_with_qmake(self):
        if not self._qmake_supported():
            return
        tools.files.mkdir(self, "qmake_folder")
        with tools.files.chdir(self, "qmake_folder"):
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
                    args.append('QMAKE_CC="%s"' % value)

                value = _getenvpath('CXX')
                if value:
                    args.append('QMAKE_CXX="%s"' % value)

                value = _getenvpath('LD')
                if value:
                    args.append('QMAKE_LINK_C="%s"' % value)
                    args.append('QMAKE_LINK_C_SHLIB="%s"' % value)
                    args.append('QMAKE_LINK="%s"' % value)
                    args.append('QMAKE_LINK_SHLIB="%s"' % value)

                self.run("qmake %s" % " ".join(args), run_environment=True)
                if tools.os_info.is_windows:
                    if self.settings.compiler == "Visual Studio":
                        self.run("nmake", run_environment=True)
                    else:
                        self.run("mingw32-make", run_environment=True)
                else:
                    self.run("make", run_environment=True)

    def _build_with_meson(self):
        if self._meson_supported():
            self.output.info("Building with Meson")
            tools.files.mkdir(self, "meson_folder")
            with tools.environment_append(RunEnvironment(self).vars):
                meson = Meson(self)
                try:
                    meson.configure(build_folder="meson_folder", defs={"cpp_std": "c++11"})
                except ConanException:
                    self.output.info(open("meson_folder/meson-logs/meson-log.txt", 'r').read())
                    raise
                meson.build()

    def _build_with_cmake_find_package_multi(self):
        if not self._cmake_multi_supported():
            return
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
        if not self._qmake_supported():
            return
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
        if not self._cmake_multi_supported():
            return
        self.output.info("Testing CMake_find_package_multi")
        shutil.copy("qt.conf", "bin")
        self.run(os.path.join("bin", "test_package"), run_environment=True)

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            self._test_with_qmake()
            self._test_with_meson()
            self._test_with_cmake_find_package_multi()
