from conan import ConanFile
from conans import tools, AutoToolsBuildEnvironment
from conan.tools.files import get
from conan.tools.files import rmdir
from conan.tools.files import rm
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.45.0"

class UvmSystemC(ConanFile):
    name = "uvm-systemc"
    description = """Universal Verification Methodology for SystemC"""
    homepage = "https://systemc.org/about/systemc-verification/uvm-systemc-faq"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("systemc", "verification", "tlm", "uvm")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.tool_requires("cmake/3.24.0")
        self.tool_requires("systemc/2.3.3")

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos build not supported")
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(configure_dir=os.path.join(self.build_folder, self._source_subfolder)
        ,args=['--with-systemc=%s' % self.deps_cpp_info["systemc"].rootpath])
        autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("NOTICE", src=self._source_subfolder, dst="licenses")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
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
        os.rename(os.path.join(self.package_folder, "lib-linux64"), os.path.join(self.package_folder, "lib"))
        rm(self, "libuvm-systemc.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["uvm-systemc"]
