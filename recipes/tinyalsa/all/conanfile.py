from conan import ConanFile
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, chdir, copy, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"

class TinyAlsaConan(ConanFile):
    name = "tinyalsa"
    description = "A small library to interface with ALSA in the Linux kernel"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tinyalsa/tinyalsa"
    topics = ("tiny", "alsa", "sound", "audio", "tinyalsa")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "with_utils": [True, False]}
    default_options = {"shared": False, "with_utils": False}

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("{} only works for Linux.".format(self.name))

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            at = Autotools(self)
            at.make()

    def package(self):
        copy(self, "NOTICE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        with chdir(self, self.source_folder):
            at = Autotools(self)
            at.install(args=[f"DESTDIR={self.package_folder}", "PREFIX="])

        rmdir(self, os.path.join(self.package_folder, "share"))

        pattern_to_remove = "*.a" if self.options.shared else "*.so"
        rm(self, pattern_to_remove, os.path.join(self.package_folder, "lib"))

        if not self.options.with_utils:
            rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["tinyalsa"]
        if Version(self.version) >= "2.0.0":
            self.cpp_info.system_libs.append("dl")
        
        if self.options.with_utils:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.path.append(bin_path)
        
        # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f'Appending PATH environment variable: {bin_path}')
        self.env_info.PATH.append(bin_path)
