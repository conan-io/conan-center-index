from conan import ConanFile
from conan.tools.files import copy, get
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "KaHIP")
        self.cpp_info.set_property("cmake_target_name", "KaHIP::KaHIP")
        self.cpp_info.libs = ["kahip"] if self.options.shared else ["kahip_static"]
