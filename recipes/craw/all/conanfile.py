from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import get, copy
import os


class CrawConan(ConanFile):
    name = "craw"
    description = "C Reddit API wrapper"
    license = "MIT"
    url = "https://github.com/YOUR_USERNAME/craw"
    homepage = "https://github.com/YOUR_USERNAME/craw"
    topics = ("reddit", "api", "c")

    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True, False]}
    default_options = {"shared": False}

    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    generators = "CMakeToolchain", "CMakeDeps"

    requires = (
        "libcurl/8.18.0"
        "cjson/1.7.17",
    )

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["craw"]
