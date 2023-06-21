from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc
import os

required_conan_version = ">=1.57.0"


class LibConfuseConan(ConanFile):
    name = "libconfuse"
    description = "Small configuration file parser library for C"
    topics = ("configuration", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinh/libconfuse"
    license = "ISC"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if is_msvc(self) and check_min_vs(self, "180", raise_invalid=False):
            tc.extra_cflags.append("-FS")
        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link -nologo")
        tc.generate(env)

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"),
                              "SUBDIRS = m4 po src $(EXAMPLES) tests doc",
                              "SUBDIRS = m4 src")
        if not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "src", "confuse.h"),
                                  "__declspec (dllimport)", "")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "confuse.dll.lib"),
                         os.path.join(self.package_folder, "lib", "confuse.lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libconfuse")
        self.cpp_info.libs = ["confuse"]
