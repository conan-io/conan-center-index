from pathlib import Path

from conans import ConanFile
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
import glob
import os
from conan.tools.layout import basic_layout
from conans.tools import chdir, remove_files_by_mask, rename

required_conan_version = ">=1.57.0"


class CunitConan(ConanFile):
    name = "cunit"
    description = "A Unit Testing Framework for C"
    topics = ("conan", "cunit", "testing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://cunit.sourceforge.net/"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_automated": [True, False],
        "enable_basic": [True, False],
        "enable_console": [True, False],
        "with_curses": [False, "ncurses"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_automated": True,
        "enable_basic": True,
        "enable_console": True,
        "with_curses": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_curses == "ncurses":
            self.requires("ncurses/6.2")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            self.build_requires("autoconf/2.71")
            self.tool_requires("automake/1.16.5")  # Needed for complie and lib wrappers
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        with chdir(self.source_folder):
            for f in glob.glob("*.c"):
                os.chmod(f, 0o644)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if (self.settings.get_safe("compiler") == "Visual Studio" and self.settings.get_safe("compiler.version") >= "12") or \
                (self.settings.get_safe("compiler") == "msvc" and self.settings.get_safe("compiler.version") >= "180"):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        env = tc.environment()
        tc.configure_args.append("--datarootdir={}".format(os.path.join(self.package_folder, "bin", "share").replace("\\", "/")))
        tc.configure_args.append("--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug")
        tc.configure_args.append("--enable-automated" if self.options.enable_automated else "--disable-automated")
        tc.configure_args.append("--enable-basic" if self.options.enable_basic else "--disable-basic")
        tc.configure_args.append("--enable-console" if self.options.enable_console else "--disable-console")
        tc.configure_args.append("--enable-curses" if self.options.with_curses != False else "--disable-curses")

        if is_msvc(self):
            env.append("CC", f'{unix_path(self, self.conf.get("user.automake:compile-wrapper"))} cl -nologo')
            env.append("CXX", f'{unix_path(self, self.conf.get("user.automake:compile-wrapper"))} cl -nologo')
            env.append("AR", f'{unix_path(self, self.conf.get("user.automake:lib-wrapper"))} lib')
            env.define("LD", "link -nologo")
            env.append("NM", "dumpbin -symbols")
            env.append("OBJDUMP", ":")
            env.append("RANLIB", ":")
            env.append("STRIP", ":")
        tc.generate(env)

    def build(self):
        apply_conandata_patches(self)

        # Clean up makefiles from source folder
        os.unlink(Path(self.source_folder) / "config.status")
        os.unlink(Path(self.source_folder) / "config.log")
        os.unlink(Path(self.source_folder) / "Makefile")

        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            rename(os.path.join(self.package_folder, "lib", "cunit.dll.lib"),
                   os.path.join(self.package_folder, "lib", "cunit.lib"))

        remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        rmdir(self, os.path.join(self.package_folder, "bin", "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "doc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CUnit"
        self.cpp_info.names["cmake_find_package_multi"] = "CUnit"
        self.cpp_info.libs = ["cunit"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("CU_DLL")
