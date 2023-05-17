from conan import ConanFile
from conans import AutoToolsBuildEnvironment
from conan.tools.files import get, rmdir, rm, copy, rename
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"

class UvmSystemC(ConanFile):
    name = "accellera-uvm-systemc"
    description = """Universal Verification Methodology for SystemC"""
    homepage = "https://systemc.org/about/systemc-verification/uvm-systemc-faq"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("systemc", "verification", "tlm", "uvm")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("systemc/2.3.3")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            
    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos build not supported")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows build not yet supported")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        args = [f"--with-systemc={self.deps_cpp_info['systemc'].rootpath}"]
        if self.options.shared:
            args.extend(["--enable-shared", "--disable-static"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        autotools.configure(configure_dir=self._source_subfolder, args=args)
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=os.path.join(self.build_folder, self._source_subfolder), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=os.path.join(self.build_folder, self._source_subfolder), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING", src=os.path.join(self.build_folder, self._source_subfolder), dst=os.path.join(self.package_folder, "licenses"))
        autotools = AutoToolsBuildEnvironment(self)
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
        rename(self, os.path.join(self.package_folder, "lib-linux64"), os.path.join(self.package_folder, "lib"))
        rm(self, "libuvm-systemc.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["uvm-systemc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
