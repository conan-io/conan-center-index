from conan import ConanFile, conan_version
from conan.tools.build import cross_building, can_run
from conan.tools.files import chdir, mkdir, rm
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
import glob
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str) # Needed as a requirement for CMake to see libraries

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("autoconf/2.71") # Needed for autoreconf
        self.tool_requires("automake/1.16.5") # Needed for aclocal called by autoreconf--does Coanan 2.0 need a transitive_run trait?
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
        # Coulld reuse single autotools instance because they are identical, but good example of
        # how to use "namespace" should they differ.
        tc = AutotoolsToolchain(self, namespace="autotools")
        env = tc.environment()
        if is_msvc(self):
            env.append("CC", "cl -nologo") # Don't use compile-wrapper as it doesn't work with CMake
            env.append("CXX", "cl -nologo")
            env.append("AR", f'{unix_path(self, self.conf.get("user.automake:lib-wrapper"))} lib')
            env.append("LD", "link")
        tc.generate(env)
        tc = AutotoolsToolchain(self, namespace="sis")
        env = tc.environment()
        if is_msvc(self):
            env.append("CC", "cl -nologo")
            env.append("CXX", "cl -nologo")
            env.append("AR", f'{unix_path(self, self.conf.get("user.automake:lib-wrapper"))} lib')
            env.append("LD", "link")
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

    def _build_autotools(self):
        """ Test autotools integration """
        # Copy autotools directory to build folder
        autotools_build_folder = os.path.join(self.build_folder, "autotools")
        shutil.copytree(os.path.join(self.source_folder, "autotools"), autotools_build_folder)
        with chdir(self, "autotools"):
            self.run("autoreconf --install --verbose --force -Wall")

        mkdir(self, self.autotools_package_folder)
        mkdir(self, "bin_autotools")
        with chdir(self, "bin_autotools"):
            autotools = Autotools(self, namespace="autotools")
            autotools.configure(build_script_folder=autotools_build_folder)
            autotools.make(args=["V=1"])
            autotools.install(args=[f'DESTDIR={unix_path(self, self.autotools_package_folder)}'])

    def _test_autotools(self):
        assert os.path.isdir(os.path.join(self.autotools_package_folder, "bin"))
        assert os.path.isfile(os.path.join(self.autotools_package_folder, "include", "lib.h"))
        assert os.path.isdir(os.path.join(self.autotools_package_folder, "lib"))

        if can_run(self):
            if self.settings.os == "Windows":
                libpath = ""
            elif is_apple_os(self):
                libpath = f'DYLD_LIBRARY_PATH={os.path.join(self.autotools_package_folder, "lib")}'
            else:
                libpath = f'LD_LIBRARY_PATH={os.path.join(self.autotools_package_folder, "lib")}'
            self.run(f'{libpath} {unix_path(self, os.path.join(self.autotools_package_folder, "bin", "test_package"))}')

    def _build_ltdl(self):
        """ Build library using ltdl library """
        cmake = CMake(self)
        cmake.configure(build_script_folder="ltdl")
        cmake.build()
        # Conan 1.x does not define self.package_folder when running the "test" command,
        # which prevents the use of cmake.install in the build method of a test package
        if Version(conan_version).major >= 2:
             cmake.install() # Installs into self.package_folder, which is test_package/test_ouput

    def _test_ltdl(self):
        """ Test library using ltdl library"""
        lib_suffix = {
            "Linux": "so",
            "FreeBSD": "so",
            "Macos": "dylib",
            "Windows": "dll",
        }[str(self.settings.os)]

        if can_run(self):
            if Version(conan_version).major >= 2:
                # In Conan 2.0, we can call cmake.install, which places artifacts in subdirectories of <self.package_folder>
                bin_path = unix_path(self, os.path.join(self.package_folder, "bin", "test_package"))
                libdir = "bin" if self.settings.os == "Windows" else "lib"
                lib_path = unix_path(self, os.path.join(self.package_folder, libdir, f'{"lib" if self.settings.os != "Windows" else ""}liba.{lib_suffix}'))
            else:
                # We can't call cmake.install with Conan 1.x, so we find artifacts in <self.build_folder>
                bin_path = unix_path(self, os.path.join(self.build_folder, "test_package"))
                lib_path = unix_path(self, os.path.join(self.build_folder, f'{"lib" if self.settings.os != "Windows" else ""}liba.{lib_suffix}'))
            self.run(f'{bin_path} {lib_path}', scope="run")

    def _build_static_lib_in_shared(self):
        """ Build shared library using libtool (while linking to a static library) """

        # Copy static-in-shared directory to build folder
        autotools_sis_folder = os.path.join(self.build_folder, "sis")
        shutil.copytree(os.path.join(self.source_folder, "sis"), autotools_sis_folder)

        # Build static library using CMake
        rm(self, "CMakeCache.txt", self.build_folder) # or pass --fresh to cmake.configure()
        cmake = CMake(self)
        cmake.configure(build_script_folder=autotools_sis_folder) # cli_args=["--fresh"]) # Requires CMake 3.24
        cmake.build()
        # Conan 1.x does not define self.package_folder when running the "test" command,
        # which prevents the use of cmake.install in the build method of a test package
        if Version(conan_version).major >= 2:
            cmake.install() # Installs into self.package_folder, which is test_package/test_ouput

        # Copy autotools directory to build folder
        with chdir(self, autotools_sis_folder):
            self.run("autoreconf --install --verbose --force -Wall")

        with chdir(self, autotools_sis_folder):
            autotools = Autotools(self, namespace="sis")
            autotools.configure(build_script_folder=autotools_sis_folder)
            if Version(conan_version).major >= 2:
                autotools.make(args=["V=1", f'LDFLAGS+=-L{unix_path(self, os.path.join(self.package_folder, "lib"))}']) # CMake installs in <self.package_folder>/lib
            else:
                autotools.make(args=["V=1", f'LDFLAGS+=-L{unix_path(self, self.build_folder)}']) # CMake creates artifacts in <self.build_folder> sans install
            autotools.install(args=[f'DESTDIR={unix_path(self, self.sis_package_folder)}'])

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
        self._test_ltdl()
        if can_run(self):
            self._test_autotools()
            self._test_static_lib_in_shared()
