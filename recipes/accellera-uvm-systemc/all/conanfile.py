import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, rm, copy, rename, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class UvmSystemC(ConanFile):
    name = "accellera-uvm-systemc"
    description = "Universal Verification Methodology for SystemC"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://systemc.org/overview/uvm-systemc-faq"
    topics = ("systemc", "verification", "tlm", "uvm")

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
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("systemc/2.3.4", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.os == "Windows" or is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.settings.os} build not supported")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        systemc_root = self.dependencies["systemc"].package_folder
        tc.configure_args.append(f"--with-systemc={systemc_root}")
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        # Replace lib-linux64/ with lib/ for the systemc dependency
        replace_in_file(self, os.path.join(self.build_folder, "src", "uvmsc", "Makefile"),
                        "-linux64", "")
        autotools.make()

    def package(self):
        for license in ["LICENSE", "NOTICE", "COPYING"]:
            copy(self, license,
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "docs"))
        rmdir(self, os.path.join(self.package_folder, "examples"))
        rm(self, "AUTHORS", self.package_folder)
        rm(self, "COPYING", self.package_folder)
        rm(self, "ChangeLog", self.package_folder)
        rm(self, "LICENSE", self.package_folder)
        rm(self, "NOTICE", self.package_folder)
        rm(self, "NEWS", self.package_folder)
        rm(self, "RELEASENOTES", self.package_folder)
        rm(self, "README", self.package_folder)
        rm(self, "INSTALL", self.package_folder)
        rename(self,
               os.path.join(self.package_folder, "lib-linux64"),
               os.path.join(self.package_folder, "lib"))
        rm(self, "libuvm-systemc.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["uvm-systemc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
