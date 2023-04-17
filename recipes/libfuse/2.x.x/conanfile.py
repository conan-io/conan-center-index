from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class LibfuseConan(ConanFile):
    name = "libfuse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libfuse/libfuse"
    license = "LGPL-2.1"
    description = "The reference implementation of the Linux FUSE interface"
    topics = ("fuse", "libfuse", "filesystem", "linux")
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
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("libfuse supports only Linux and FreeBSD")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-lib",
            "--disable-util",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        # remove ulockmgr stuff lib and header file
        rm(self, "*ulockmgr*", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "fuse")
        self.cpp_info.libs = ["fuse"]
        self.cpp_info.includedirs = [os.path.join("include", "fuse")]
        self.cpp_info.system_libs = ["pthread"]
        # libfuse requires this define to compile successfully
        self.cpp_info.defines = ["_FILE_OFFSET_BITS=64"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")

