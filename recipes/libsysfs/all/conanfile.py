from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
import os


required_conan_version = ">=2.1"


class LibsysfsConan(ConanFile):
    name = "libsysfs"
    description = (
        "Library used in handling linux kernel sysfs mounts and their various files."
    )
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linux-ras/sysfsutils"
    topics = ("sysfs",)
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
    implements = ["auto_shared_fpic"]
    languages = ["C"]

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.name} only supports Linux")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        with chdir(self, os.path.join(self.source_folder, "lib")):
            autotools.make()

    def package(self):
        copy(
            self,
            "LGPL",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        autotools = Autotools(self)
        with chdir(self, os.path.join(self.source_folder, "lib")):
            autotools.install()
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include", "sysfs"),
        )

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["sysfs"]
        self.cpp_info.set_property("pkg_config_name", "libsysfs")
