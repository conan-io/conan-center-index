from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0"

class upa_urlRecipe(ConanFile):
    name = "upa-url"
    package_type = "library"

    # Optional metadata
    license = "BSD-2-Clause"
    author = "Rimas Misevičius <rmisev3@gmail.com>"
    url = "https://github.com/conan-io/conan-center-index"
    description = "An implementation of the WHATWG URL Standard in C++"
    topics = ("url", "parser", "psl", "whatwg")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Equivalent to:
        # data = self.conan_data["sources"][self.version]
        # get(self, data["url"], sha256=data["sha256"], strip_root=data["strip_root"])

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def validate(self):
        check_min_cppstd(self, 17)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["UPA_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Remove unused files
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "upa")
        self.cpp_info.set_property("cmake_target_name", "upa::url")
        self.cpp_info.libs = ["upa_url"]
