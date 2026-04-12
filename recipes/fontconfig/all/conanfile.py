from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=2.1"


class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Fontconfig is a library for configuring and customizing font access"
    homepage = "https://gitlab.freedesktop.org/fontconfig/fontconfig"
    topics = ("fonts", "freedesktop")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_system_dirs_if_supported": [True, False],
        "datadir": ["package", "system-if-known", "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_system_dirs_if_supported": False,
        "datadir": "package"
    }
    options_description = {
        "use_system_dirs_if_supported": "Use Fontconfig system directories if supported",
        "datadir": "directory name, or relative path, for the GNU DATADIR. "
                   "Note that the prefix will be / . Special values: "
                   "package: use package DATADIR, require to set the FONTCONFIG_PATH env var at runtime. "
                   "system-if-known: will set DATADIR to system dir, like usr/share on Linux, "
                   "fallbacks to package if the platform is not known.",
    }
    package_type = "library"


    class _DirsHelper:
        def __init__(self, conanfile):
            self.conanfile = conanfile
            self.datadir = None
            self.sysconfdir = None
            self.use_package_dirs = True
            self._set_standard_dirs()

        def use_package_datadir(self):
            return self.datadir == "package"

        def use_package_sysconfdir(self):
            return self.sysconfdir == "package"

        def _set_package_standard_dirs(self):
            self.datadir = os.path.join("res", "share")
            self.sysconfdir = os.path.join("res", "etc")
            self.use_package_dirs = True

        def _set_standard_dirs(self):
            if not self.conanfile.options.use_system_dirs_if_supported:
                self._set_package_standard_dirs()
                return
            self.use_package_dirs = False
            if self.conanfile.settings.os == "Linux":
                self.datadir = "usr/share"
                self.sysconfdir = "etc"
            else:
                # TODO: make message better
                self.conanfile.output.warning(f"it was requested to use system dirs, but it is not supported for {self.conanfile.settings.os}."
                                              " Fallback to using package dirs. Set the FONTCONFIG_PATH environment variable at runtime")
                self._set_package_standard_dirs()


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # TODO: not reliable + should we do that ?
    def validate(self):
        datadir = str(self.options.datadir)
        if os.path.isabs(datadir):
            raise ConanInvalidConfiguration(f"datadir option must not be an absolute path (given: {datadir})")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/[>=2.13.2 <3]")
        self.requires("expat/[>=2.6.2 <3]")

    def build_requirements(self):
        self.tool_requires("gperf/3.1")
        self.tool_requires("meson/[>=1.4.0 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.1 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        dirs_helper = self._DirsHelper(self)
        tc.project_options.update({
            "doc": "disabled",
            "nls": "disabled",
            "tests": "disabled",
            "tools": "disabled",
            "sysconfdir": dirs_helper.sysconfdir,
            "datadir": dirs_helper.datadir,
        })
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        dirs_helper = self._DirsHelper(self)
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        # TODO: A) always delete, or only when using system dirs ? B) What to delete ?
        rm(self, "*.pdb", self.package_folder, recursive=True)
        rm(self, "*.conf", os.path.join(self.package_folder, dirs_helper.sysconfdir, "fonts", "conf.d"))
        rm(self, "*.def", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)
        if Version(self.version) <= "2.15.0":
            # TODO: Keep this for versions <= 2.15.0, remove in future versions
            fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Fontconfig")
        self.cpp_info.set_property("cmake_target_name", "Fontconfig::Fontconfig")
        self.cpp_info.set_property("pkg_config_name", "fontconfig")
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        dirs_helper = self._DirsHelper(self)
        if dirs_helper.use_package_dirs:
            fontconfig_path = os.path.join(self.package_folder, dirs_helper.sysconfdir, "fonts")
            self.runenv_info.append_path("FONTCONFIG_PATH", fontconfig_path)

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib in case of cl like compiler"""
    if not conanfile.settings.get_safe("compiler.runtime"):
        return
    from conan.tools.files import rename
    import glob
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
