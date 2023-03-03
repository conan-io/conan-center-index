from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.54.0"


class LibDNetConan(ConanFile):
    name = "libdnet"
    description = "Provides a simplified, portable interface to several low-level networking routines."
    homepage = "https://github.com/ofalk/libdnet"
    topics = ("libdnet", "libdumbnet")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)


    def layout(self):
        basic_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("libdnet has not supported Visual Studio yet")
            # windows build requires winpcap (looks like we can use npcap)


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("libcheck/0.15.2")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        # if is_msvc(self):
        #     env.define("CC", "cl -nologo")
        #     env.define("CXX", "cl -nologo")
        #     env.define("LD", "link -nologo")
        #     env.define("AR", "lib -nologo")
        # if self._settings_build.os == "Windows":
        #     # TODO: Something to fix in conan client or pkgconf recipe?
        #     # This is a weird workaround when build machine is Windows. Here we have to inject regular
        #     # Windows path to pc files folder instead of unix path flavor injected by AutotoolsToolchain...
        #     env.define("PKG_CONFIG_PATH", self.generators_folder)
        tc.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self,"COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        copy(self, "config.h", src=os.path.join(self.build_folder, "include"), dst=os.path.join(self.package_folder, "include"))

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_id(self):
        del self.info.options.default

    def package_info(self):
        self.cpp_info.components["dnet"].libs = ["dnet"]
        self.cpp_info.components["dnet"].names["pkg_config"] = "libdnet"
