import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class LinuxHeadersGenericConan(ConanFile):
    name = "linux-headers-generic"
    description = "Generic Linux kernel headers"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kernel.org/"
    topics = ("linux", "headers", "generic", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.build_type
        del self.info.settings.compiler

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def validate(self):
        if self.settings.os != "Linux" or (not self._is_legacy_one_profile and self.settings_build.os != "Linux"):
            raise ConanInvalidConfiguration("linux-headers-generic supports only Linux")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="headers")

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "include/*.h",
             dst=self.package_folder,
             src=os.path.join(self.source_folder, "usr"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
