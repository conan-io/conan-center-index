from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.54.0"


class ReboundConan(ConanFile):
    name = "rebound"
    description = "REBOUND is an N-body integrator, i.e. a software package that can integrate the motion of particles under the influence of gravity."
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hannorein/rebound"
    topics = ("physics", "simulation", "n-body", "gravity", "integrator")
    package_type = "shared-library"
    # Scripts always compile with optimizations enabled
    settings = "os", "arch", "compiler"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)
    
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os in ["Windows", "Macos"]:
            raise ConanInvalidConfiguration(f"{self.ref} recipe does not support {self.settings.os}, contributions welcomed!")

    def validate_build(self):
        if cross_building(self):
            raise ConanInvalidConfiguration(f"{self.ref} cross-building is not supported yet, contributions welcomed!")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="librebound")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "librebound.so", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "lib"))

        copy(self, "*.h", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "include"))

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["rebound"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
