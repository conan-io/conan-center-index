from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, chdir, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0.9"

class ODPIConan(ConanFile):
    name = "odpi"
    description = "Oracle Database Programming Interface for Drivers and Applications"
    license = ("UPL-1.0", "Apache-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oracle/odpi"
    topics = ("oracle", "database", "oci")
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

    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} recipe only supports Linux for now. Pull requests to add new configurtations are welcomed.")
        # TODO: Check support for other platforms

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="all")

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install(args=[f"PREFIX={self.package_folder}"])
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["odpic"]
        self.cpp_info.set_property("pkg_config_name", "odpi")
        if self.settings.os in ["Linux"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
