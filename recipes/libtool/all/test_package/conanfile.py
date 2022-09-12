from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import chdir, mkdir
from conan.tools.microsoft import unix_path, is_msvc
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
from conan.tools.env import Environment

from contextlib import contextmanager
import glob
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv"
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")
        self.tool_requires(self.tested_reference_str)

    @property
    def _package_folder(self):
        return self.build_path.joinpath("package")

    def layout(self):
        basic_layout(self, src_folder=".")

    def generate(self):
        if can_run(self):
            tc = AutotoolsToolchain(self)
            tc.configure_args.extend([
                "--enable-shared",
                "--enable-static",
            ])
            env = tc.environment()
            if is_msvc(self):
                env.define("CC", f"{unix_path(self, self.deps_user_info['automake'].compile)} cl -nologo")
                env.define("CXX", f"{unix_path(self, self.deps_user_info['automake'].compile)} cl -nologo")
                env.define("AR", f"{unix_path(self, self.deps_user_info['automake'].ar_lib)} lib")
                env.define("LD", "link -nologo")
            tc.generate(env)

    def build(self):
        self._build_ltdl()
        if can_run(self):
            self._build_autotools()
            # self._build_static_lib_in_shared()

    def _build_ltdl(self):
        """ Build library using ltdl library """
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.joinpath("ltdl"))
        cmake.build()
    def _build_autotools(self):
        """ Test autotools integration """
        # Copy autotools directory to build folder
        shutil.copytree(self.source_path.joinpath("autotools"), self.build_path.joinpath("autotools"), dirs_exist_ok=True)
        mkdir(self, self._package_folder)
        mkdir(self, self.build_path.joinpath("bin_autotools"))

        with chdir(self, self.build_path.joinpath("bin_autotools")):
            autotools = Autotools(self)
            self.run("autoreconf -ifv -Wall", cwd=str(self.build_path.joinpath("autotools")))  # Workaround for `Autools.autoreconf()` always running from source
            autotools.configure(build_script_folder=unix_path(self, str(self.build_path.joinpath("autotools"))))
            autotools.make()
            autotools.install(args=[f"DESTDIR={unix_path(self, str(self._package_folder.joinpath('autotool_inst')))}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem

            # Defining the run environment for testing the autotools created test_package
            env = Environment()
            env.prepend_path("PATH", str(self._package_folder.joinpath("autotool_inst", "lib")))
            env.prepend_path("LD_LIBRARY_PATH", str(self._package_folder.joinpath("autotool_inst", "lib")))
            env.prepend_path("DYLD_LIBRARY_PATH", str(self._package_folder.joinpath("autotool_inst", "lib")))
            vars = env.vars(self, scope="run")
            vars.save_script("autotoolrun")

    # def _build_static_lib_in_shared(self):
    #     """ Build shared library using libtool (while linking to a static library) """
    #
    #     # Copy static-in-shared directory to build folder
    #     autotools_folder = self.build_path.joinpath("sis")
    #     shutil.copytree(self.source_path.joinpath("sis"), autotools_folder, dirs_exist_ok=True)
    #
    #     install_prefix = autotools_folder.joinpath("prefix")
    #
    #     # Build static library using CMake
    #     cmake = CMake(self)
    #     cmake.configure(build_script_folder=autotools_folder)
    #     cmake.build()
    #     cmake.install()
    #
    #     with chdir(self, autotools_folder):
    #         autotools = Autotools(self)
    #         self.run("autoreconf -ifv -Wall", cwd=str(autotools_folder))  # Workaround for `Autools.autoreconf()` always running from source
    #         autotools.configure(build_script_folder=unix_path(self, str(autotools_folder)))
    #         autotools.make()
    #         autotools.install(args=[f"DESTDIR={unix_path(self, str(self._package_folder.joinpath('sis_inst')))}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem
    #
    #         # Defining the run environment for testing the autotools created test_package
    #         env = Environment()
    #         env.prepend_path("PATH", str(self._package_folder.joinpath("sis_inst", "lib")))
    #         env.prepend_path("LD_LIBRARY_PATH", str(self._package_folder.joinpath("sis_inst", "lib")))
    #         env.prepend_path("DYLD_LIBRARY_PATH", str(self._package_folder.joinpath("sis_inst", "lib")))
    #         vars = env.vars(self, scope="run")
    #         vars.save_script("sisrun")

    def test(self):
        self._test_ltdl()
        if can_run(self):
            self._test_autotools()
            # self._test_static_lib_in_shared()

    def _test_ltdl(self):
        """ Test library using ltdl library"""
        lib_suffix = {
            "Linux": "so",
            "FreeBSD": "so",
            "Macos": "dylib",
            "Windows": "dll",
        }[str(self.settings.os)]
        ext = ".exe" if self.settings.os == "Windows" else ""

        if can_run(self):
            bin_path = self.build_path.joinpath(f"test_package{ext}")
            lib_path = self.build_path.joinpath(f"liba.{lib_suffix}")
            self.run(f"{bin_path} {lib_path}", run_environment=True)

    def _test_autotools(self):
        assert self._package_folder.joinpath("autotool_inst", "bin").exists()
        assert self._package_folder.joinpath("autotool_inst", "include", "lib.h").exists()
        assert self._package_folder.joinpath("autotool_inst", "lib").exists()

        if can_run(self):
            ext = ".exe" if self.settings.os == "Windows" else ""
            self.run(str(self._package_folder.joinpath("autotool_inst", "bin", f"test_package{ext}")), run_environment=True, env="autotoolrun")

    # def _test_static_lib_in_shared(self):
    #     """ Test existence of shared library """
    #     install_prefix = os.path.join(self.build_folder, "sis", "prefix")
    #
    #     with tools.chdir(install_prefix):
    #         if self.settings.os == "Windows":
    #             assert len(list(glob.glob(os.path.join("bin", "*.dll")))) > 0
    #         elif tools.is_apple_os(self.settings.os):
    #             assert len(list(glob.glob(os.path.join("lib", "*.dylib")))) > 0
    #         else:
    #             assert len(list(glob.glob(os.path.join("lib", "*.so")))) > 0
