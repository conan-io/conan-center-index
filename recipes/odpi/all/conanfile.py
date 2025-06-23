from conan import ConanFile
from conan.tools.files import copy, chdir, get, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.apple import fix_apple_shared_install_name
import os


required_conan_version = ">=2.0.9"

class ODPIConan(ConanFile):
    name = "odpi"
    description = "Oracle Database Programming Interface for Drivers and Applications"
    license = ("UPL-1.0", "Apache-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oracle/odpi"
    topics = ("oracle", "database", "oci")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    languages = ["C"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if self.settings.os == "Linux":
            tc.extra_cflags = ["-fPIC"]
            tc.extra_ldflags = ["-shared"]
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            if self.settings.os == "Windows":
                self.run(f"nmake -f Makefile.win32")
            else:
                autotools = Autotools(self)
                autotools.make(target="all")

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            copy(self, "*.lib", os.path.join(self.source_folder, "lib"), os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", os.path.join(self.source_folder, "lib"), os.path.join(self.package_folder, "bin"))
            copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install(args=[f"PREFIX={self.package_folder}"])
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["odpic"]
        if self.settings.os in ["Linux"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
