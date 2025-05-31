from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class UnityConan(ConanFile):
    exports_sources = "src/*"
    name = "cmock"
    description = "CMock is a mock and stub generator and runtime for unit testing C. It's been designed to work smoothly with Unity Test,"
    topics = ("mock", "unit-test", "testing")
    license = "MIT"
    homepage = "http://www.throwtheswitch.org"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("unity/2.5.2")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["cmock"]
        self.cpp_info.includedirs = ["include", "include/cmock"]
