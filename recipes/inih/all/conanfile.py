from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class InihConan(ConanFile):
    name = "inih"
    description = "Simple .INI file parser in C, good for embedded systems "
    license = "BSD-3-Clause"
    topics = ("ini", "configuration", "parser")
    homepage = "https://github.com/benhoyt/inih"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_inireader": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_inireader": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # INIReader is written in C++
        if not self.options.with_inireader:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        # since 57, INIReader requires C++11
        if Version(self.version) >= "57" and self.options.with_inireader and \
            self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.options.shared and is_msvc(self):
            raise ConanInvalidConfiguration("Shared inih is not supported with msvc")

    def build_requirements(self):
        self.tool_requires("meson/1.2.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["distro_install"] = True
        tc.project_options["with_INIReader"] = self.options.with_inireader
        # since 57, INIReader requires C++11
        if Version(self.version) >= "57" and not is_msvc(self):
            tc.cpp_args.append("-std=c++11")
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "INIReader")

        self.cpp_info.components["libinih"].set_property("pkg_config_name", "inih")
        self.cpp_info.components["libinih"].libs = ["inih"]

        if self.options.with_inireader:
            self.cpp_info.components["inireader"].set_property("pkg_config_name", "INIReader")
            self.cpp_info.components["inireader"].libs = ["INIReader"]
            self.cpp_info.components["inireader"].requires = ["libinih"]

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib in case of cl like compiler"""
    from conan.tools.files import rename
    import glob
    if not conanfile.settings.get_safe("compiler.runtime"):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
