from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.53.0"


class HwDataConan(ConanFile):
    name = "hwdata"
    description = "hwdata contains various hardware identification and configuration data, such as the pci.ids and usb.ids databases"
    license = ("GPL-2.0-or-later", "XFree86-1.1")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vcrhonek/hwdata"
    topics = ("hardware", "id", "pci", "usb")
    package_type = "unknown"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "disable_blacklist": [True, False],
    }
    default_options = {
        "disable_blacklist": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")
        self.folders.build = "src"

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.build_type
        del self.info.settings.compiler
        del self.info.settings.os

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
        tc.configure_args.append("--datarootdir=/res")
        if self.options.disable_blacklist:
            tc.configure_args.append("--disable-blacklist")
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "res", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]
        pkg_config_variables = {
            "pkgdatadir": os.path.join(self.package_folder, "res", self.name)
        }
        self.cpp_info.set_property("pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkg_config_variables.items()))
