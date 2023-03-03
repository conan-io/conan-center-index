from conan import ConanFile
from conan.tools.build import cross_building, can_run
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, mkdir, rmdir
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.apple import is_apple_os

import glob
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"
    short_paths = True
    win_bash = True # This assignment must be *here* to avoid "Cannot wrap command with different envs." in Conan 1.x

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str) # Since we are testing libltdl as well

    def build_requirements(self):
        if hasattr(self, "settings_build") and not cross_building(self):
            self.tool_requires(self.tested_reference_str) # We are testing libtool/libtoolize
    
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    @property
    def autotools_package_folder(self):
        return os.path.join(self.build_folder, "pkg_autotools")

    @property
    def sis_package_folder(self):
        return os.path.join(self.build_folder, "pkg_sis")

    def generate(self):
        if is_msvc(self):
            # __VSCMD_ARG_NO_LOGO: this test_package has too many invocations,
            #                      this avoids printing the logo everywhere
            # VSCMD_SKIP_SENDTELEMETRY: avoid the telemetry process holding onto the directory
            #                           unnecessarily
            env = Environment()
            env.define("__VSCMD_ARG_NO_LOGO", "1")
            env.define("VSCMD_SKIP_SENDTELEMETRY", "1")
            env.vars(self, scope="build").save_script("conanbuild_vcvars_options.bat")

        # Use two instances of AutotoolsToolchain with namespaceas,
        # as we have two different projects with different settings.
        ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
        msvc_vars = {
            "CC": "cl -nologo", 
            "CXX": "cl -nologo", 
            "AR": f"{ar_wrapper} lib",
            "LD": "link"
        }

        # "Autotools" subfolder: project to test integration of Autotools with libtool 
        # at build time
        tc = AutotoolsToolchain(self, namespace="autotools")
        env = tc.environment()
        if is_msvc(self):
            for key, value in msvc_vars.items():
                env.append(key, value)
        tc.generate(env)

        # "sis" subfder: project to test building shared library using libtool
        # while linking to a static library
        tc = AutotoolsToolchain(self, namespace="sis")
        tc.configure_args.extend(["--enable-shared", "--disable-static"])
        lib_folder = unix_path(self, os.path.join(self.sis_package_folder, "lib"))
        tc.extra_ldflags.append(f"-L{lib_folder}")
        env = tc.environment()
        if is_msvc(self):
            for key, value in msvc_vars.items():
                env.append(key, value)
        tc.generate(env)

        # Note: Using AutotoolsDeps causes errors on Windows when configure tries to determine compiler
        #       because injected values for environment variables CPPFLAGS and LDFLAGS that are not
        #       interpreted correctly
        if is_msvc(self):
            # Use NMake to workaround bug in MSBuild versions prior to 2022 that shows up as:
            #    error MSB6001: Invalid command line switch for "cmd.exe". System.ArgumentException: Item
            #                   has already been added. Key in dictionary: 'tmp'  Key being added: 'TMP'
            self.conf.define("tools.cmake.cmaketoolchain:generator", "NMake Makefiles")
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        env = Environment()
        for var in ["DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"]:
            env.append_path(var, os.path.join(self.autotools_package_folder, "lib"))
        env.vars(self, scope="run").save_script("conanrun_libtool_testpackage")

        runenv = VirtualRunEnv(self)
        runenv.generate()


    def _build_autotools(self):
        """ Test autotools integration """
        # Copy autotools directory to build folder
        autotools_build_folder = os.path.join(self.build_folder, "autotools")
        rmdir(self, autotools_build_folder)
        shutil.copytree(os.path.join(self.source_folder, "autotools"), autotools_build_folder)
        with chdir(self, "autotools"):
            self.run("autoreconf --install --verbose --force -Wall")

        mkdir(self, self.autotools_package_folder)
        with chdir(self, autotools_build_folder):
            autotools = Autotools(self, namespace="autotools")
            autotools.configure(build_script_folder=autotools_build_folder)
            autotools.make(args=["V=1"])
            autotools.install(args=[f'DESTDIR={unix_path(self, self.autotools_package_folder)}'])

    def _test_autotools(self):
        assert os.path.isdir(os.path.join(self.autotools_package_folder, "bin"))
        assert os.path.isfile(os.path.join(self.autotools_package_folder, "include", "lib.h"))
        assert os.path.isdir(os.path.join(self.autotools_package_folder, "lib"))

        if can_run(self):
            self.run(f'{unix_path(self, os.path.join(self.autotools_package_folder, "bin", "test_package"))}', env="conanrun")

    def _build_ltdl(self):
        """ Build library using ltdl library """
        cmake = CMake(self)
        cmake.configure(build_script_folder="ltdl")
        cmake.build()

    def _test_ltdl(self):
        """ Test library using ltdl library"""
        lib_prefix = "lib" if self.settings.os != "Windows" else ""
        lib_extension = "dll" if self.settings.os == "Windows" else "so"

        if can_run(self):
            bin_executable = unix_path(self, os.path.join(self.cpp.build.bindirs[0], "test_package"))
            lib_path = unix_path(self, os.path.join(self.cpp.build.libdirs[0], f'{lib_prefix}liba.{lib_extension}'))
            self.run(f'{bin_executable} {lib_path}', env="conanrun")

    def _build_static_lib_in_shared(self):
        """ Build shared library using libtool (while linking to a static library) """

        # Copy static-in-shared directory to build folder
        autotools_sis_folder = os.path.join(self.build_folder, "sis")
        rmdir(self, autotools_sis_folder)
        shutil.copytree(os.path.join(self.source_folder, "sis"), autotools_sis_folder)

        # Build static library using CMake and install into a folder inside the build folder
        cmake = CMake(self)
        cmake.configure(build_script_folder="ltdl")
        cmake.build(target="static_lib")
        install_prefix = unix_path(self, self.sis_package_folder)
        self.run(f"cmake --install . --config {self.settings.build_type} --prefix {install_prefix} --component static_lib")

        with chdir(self, autotools_sis_folder):
            self.run("autoreconf --install --verbose --force -Wall")
            autotools = Autotools(self, namespace="sis")
            autotools.configure(build_script_folder=autotools_sis_folder)
            autotools.install(args=[f"DESTDIR={unix_path(self, self.sis_package_folder)}"])

    def _test_static_lib_in_shared(self):
        """ Test existence of shared library """
        with chdir(self, self.sis_package_folder):
            if self.settings.os == "Windows":
                assert len(list(glob.glob(os.path.join("bin", "*.dll")))) > 0
            elif is_apple_os(self):
                assert len(list(glob.glob(os.path.join("lib", "*.dylib")))) > 0
            else:
                assert len(list(glob.glob(os.path.join("lib", "*.so")))) > 0

    def build(self):
        self._build_ltdl()
        if not cross_building(self):
            self._build_autotools()
            self._build_static_lib_in_shared()

    def test(self):
        if can_run(self):
            self._test_ltdl()
            self._test_autotools()
            self._test_static_lib_in_shared()
