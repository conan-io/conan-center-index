from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import copy, get, replace_in_file, rmdir, patch, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class LzipConan(ConanFile):
    name = "lzip"
    description = "Lzip is a lossless data compressor with a user interface similar to the one of gzip or bzip2"
    license = "GPL-v2-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nongnu.org/lzip/"
    topics = ("compressor", "lzma")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("Only gcc supported for windows builds")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(target="install-bin")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.runenv_info.prepend_path("PATH", bindir)
