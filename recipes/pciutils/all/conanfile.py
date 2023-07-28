import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get, rename, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class PciUtilsConan(ConanFile):
    name = "pciutils"
    description = "The PCI Utilities package contains a library for portable access to PCI bus"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pciutils/pciutils"
    topics = ("pci", "pci-bus", "hardware", "local-bus")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_udev": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_udev": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(
                f"Platform {self.settings.os} is currently not supported by this recipe"
            )

        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_udev:
            self.requires("libudev/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.make_args = [
            "SHARED={}".format(yes_no(self.options.shared)),
            "ZLIB={}".format(yes_no(self.options.with_zlib)),
            "HWDB={}".format(yes_no(self.options.with_udev)),
            "DESTDIR={}".format(self.package_folder),
            "PREFIX=/",
            "DNS=no",
        ]
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="all")

    def package(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="install")
            autotools.make(target="install-pcilib")

        copy(self, "COPYING",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "include"),
             keep_path=True)

        if self.options.shared:
            rename(self, src=os.path.join(self.source_folder, "lib", "libpci.so.3.7.0"),
                   dst=os.path.join(self.package_folder, "lib", "libpci.so"))

        rmdir(self, os.path.join(self.package_folder, "sbin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libpci")
        self.cpp_info.libs = ["pci"]
