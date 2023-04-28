from conan import ConanFile
from conan.tools import build, files
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class LinuxHeadersGenericConan(ConanFile):
    name = "linux-headers-generic"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kernel.org/"
    license = "GPL-2.0-only"
    description = "Generic Linux kernel headers"
    topics = ("linux", "headers", "generic")
    settings = "os", "arch", "build_type", "compiler"

    def package_id(self):
        self.info.settings.clear()


    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("linux-headers-generic supports only Linux")
        if hasattr(self, "settings_build") and build.cross_building(self):
            raise ConanInvalidConfiguration("linux-headers-generic can not be cross-compiled")

    def layout(self):
       basic_layout(self, src_folder="source")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        tc.generate(env)

    def build(self):
        with files.chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="headers")

    def package(self):
        files.copy(self, "COPYING", dst="licenses", src=self.source_folder)
        files.copy(self, "include/*.h", src=os.path.join(self.source_folder, "usr"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "linux-headers-generic")
        self.cpp_info.libs = ["linux-headers-generic"]
