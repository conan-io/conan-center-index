from pathlib import Path

from conan import ConanFile
from conan.tools.microsoft import is_msvc, unix_path, check_min_vs
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, chdir, rename, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
import glob
import os
from conan.tools.layout import basic_layout

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        # For shared builds we always need to depend on ncurses, since otherwise we get undefined
        # symbols, like:
        # /usr/bin/ld: package/9333ccd2ec7e28099e1c04b315e2384b012b7a19/lib/libcunit.so: undefined reference to `echo'
        # /usr/bin/ld: package/9333ccd2ec7e28099e1c04b315e2384b012b7a19/lib/libcunit.so: undefined reference to `wattr_on'
        # /usr/bin/ld: package/9333ccd2ec7e28099e1c04b315e2384b012b7a19/lib/libcunit.so: undefined reference to `acs_map'
        # /usr/bin/ld: package/9333ccd2ec7e28099e1c04b315e2384b012b7a19/lib/libcunit.so: undefined reference to `cbreak'
        if self.options.shared:
            self.options.with_curses = "ncurses"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_curses == "ncurses":
            self.requires("ncurses/6.4")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        with chdir(self, self.source_folder):
            for f in glob.glob("*.c"):
                os.chmod(f, 0o644)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if check_min_vs(self, "180", raise_invalid=False):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        tc.configure_args.append("--datarootdir=${prefix}/bin/share")
        tc.configure_args.append("--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug")
        tc.configure_args.append("--enable-automated" if self.options.enable_automated else "--disable-automated")
        tc.configure_args.append("--enable-basic" if self.options.enable_basic else "--disable-basic")
        tc.configure_args.append("--enable-console" if self.options.enable_console else "--disable-console")
        tc.configure_args.append("--enable-curses" if self.options.with_curses is not False else "--disable-curses")

        env = tc.environment()

        if is_msvc(self):
            automake_info = self.dependencies.build["automake"].conf_info
            env.append("CC", f'{unix_path(self, automake_info.get("user.automake:compile-wrapper", check_type=str))} cl -nologo')
            env.append("CXX", f'{unix_path(self, automake_info.get("user.automake:compile-wrapper", check_type=str))} cl -nologo')
            env.append("AR", f'{unix_path(self, automake_info.get("user.automake:lib-wrapper", check_type=str))} lib')
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
            rename(self, os.path.join(self.package_folder, "lib", "cunit.dll.lib"),
                   os.path.join(self.package_folder, "lib", "cunit.lib"))

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "bin", "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "doc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CUnit"
        self.cpp_info.names["cmake_find_package_multi"] = "CUnit"
        self.cpp_info.libs = ["cunit"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("CU_DLL")
