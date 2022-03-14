from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from contextlib import contextmanager
import glob
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    test_type = "explicit"
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

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
                autotools.make(args=["V=1"])
                autotools.install()

    def _test_autotools(self):
        assert os.path.isdir(os.path.join(self._package_folder, "bin"))
        assert os.path.isfile(os.path.join(self._package_folder, "include", "lib.h"))
        assert os.path.isdir(os.path.join(self._package_folder, "lib"))

        if not tools.cross_building(self):
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
            "FreeBSD": "so",
            "Macos": "dylib",
            "Windows": "dll",
        }[str(self.settings.os)]

        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            libdir = "bin" if self.settings.os == "Windows" else "lib"
            lib_path = os.path.join(libdir, "liba.{}".format(lib_suffix))
            self.run("{} {}".format(bin_path, lib_path), run_environment=True)

    def _build_static_lib_in_shared(self):
        """ Build shared library using libtool (while linking to a static library) """

        # Copy static-in-shared directory to build folder
        autotools_folder = os.path.join(self.build_folder, "sis")
        shutil.copytree(os.path.join(self.source_folder, "sis"), autotools_folder)

        install_prefix = os.path.join(autotools_folder, "prefix")

        # Build static library using CMake
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = install_prefix
        cmake.configure(source_folder=autotools_folder, build_folder=os.path.join(autotools_folder, "cmake_build"))
        cmake.build()
        cmake.install()

        # Copy autotools directory to build folder
        with tools.chdir(autotools_folder):
            self.run("{} -ifv -Wall".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)

        with tools.chdir(autotools_folder):
            conf_args = [
                "--enable-shared",
                "--disable-static",
                "--prefix={}".format(tools.unix_path(os.path.join(install_prefix))),
            ]
            with self._build_context():
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                autotools.libs = []
                autotools.link_flags.append("-L{}".format(tools.unix_path(os.path.join(install_prefix, "lib"))))
                autotools.configure(args=conf_args, configure_dir=autotools_folder)
                autotools.make(args=["V=1"])
                autotools.install()

    def _test_static_lib_in_shared(self):
        """ Test existence of shared library """
        install_prefix = os.path.join(self.build_folder, "sis", "prefix")

        with tools.chdir(install_prefix):
            if self.settings.os == "Windows":
                assert len(list(glob.glob(os.path.join("bin", "*.dll")))) > 0
            elif tools.is_apple_os(self.settings.os):
                assert len(list(glob.glob(os.path.join("lib", "*.dylib")))) > 0
            else:
                assert len(list(glob.glob(os.path.join("lib", "*.so")))) > 0

    def build(self):
        self._build_ltdl()
        if not tools.cross_building(self):
            self._build_autotools()
            self._build_static_lib_in_shared()

    def test(self):
        self._test_ltdl()
        if not tools.cross_building(self):
            self._test_autotools()
            self._test_static_lib_in_shared()
