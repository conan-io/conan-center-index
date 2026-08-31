from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.1"


class KahipConan(ConanFile):
    name = "kahip"
    description = "Karlsruhe High Quality Partitioning"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KaHIP/KaHIP"
    topics = ("graph", "partitioning", "algorithms")
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

    def validate(self):
        check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            # shared=True is not supported on Windows because the upstream build does not generate the ".lib" for the shared DLL.
            raise ConanInvalidConfiguration("shared=True is not supported on Windows")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NOMPI"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rm(self, "*.pc", self.package_folder, recursive=True)
        if self.options.shared:
            rm(self, "*.a", self.package_folder, recursive=True)
            rm(self, "*_static*", self.package_folder, recursive=True)
        else:
            rm(self, "*.dll", self.package_folder, recursive=True)
            rm(self, "*.so", self.package_folder, recursive=True)
            rm(self, "*.dylib", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "KaHIP")
        self.cpp_info.set_property("cmake_target_name", "KaHIP::kahip")
        self.cpp_info.libs = ["kahip"] if self.options.shared else ["kahip_static"]
