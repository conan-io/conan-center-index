from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os


required_conan_version = ">=2.1"


class TrinityConan(ConanFile):
    name = "trinity"
    description = "C11 execution library for the Aurora model"
    license = "Apache-2.0 AND CC-BY-4.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Aurora-Program/Aurora-Trinity"
    topics = ("c", "cmake", "aurora", "trinity", "ternary")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_SHARED_LIBS"] = self.options.shared
        toolchain.variables["BUILD_TESTING"] = False
        if self.options.get_safe("fPIC") is not None:
            toolchain.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Trinity")

        self.cpp_info.components["trinity"].set_property(
            "cmake_target_name", "Trinity::trinity")
        self.cpp_info.components["trinity"].libs = ["trinity"]

        self.cpp_info.components["genesis"].set_property(
            "cmake_target_name", "Trinity::genesis")
        self.cpp_info.components["genesis"].libs = ["genesis"]
        self.cpp_info.components["genesis"].requires = ["trinity"]