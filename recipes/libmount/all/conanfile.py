from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class LibmountConan(ConanFile):
    name = "libmount"
    description = (
        "The libmount library is used to parse /etc/fstab, /etc/mtab and "
        "/proc/self/mountinfo files, manage the mtab file, evaluate mount options, etc"
    )
    topics = ("mount", "linux", "util-linux")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git"
    license = "LGPL-2.1-or-later"

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--disable-all-programs",
            "--enable-libmount",
            "--enable-libblkid",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=os.path.join(self.source_folder, "libmount"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.LGPL-2.1-or-later", src=os.path.join(self.source_folder, "Documentation", "licenses"), dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "sbin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "usr"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.components["libblkid"].libs = ["blkid"]
        self.cpp_info.components["libblkid"].set_property("pkg_config_name", "blkid")

        self.cpp_info.components["libmount"].libs = ["mount"]
        self.cpp_info.components["libmount"].system_libs = ["rt"]
        self.cpp_info.components["libmount"].includedirs.append(os.path.join("include", "libmount"))
        self.cpp_info.components["libmount"].set_property("pkg_config_name", "mount")
        self.cpp_info.components["libmount"].requires = ["libblkid"]
