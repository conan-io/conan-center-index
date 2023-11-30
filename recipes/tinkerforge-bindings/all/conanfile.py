import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc_static_runtime

required_conan_version = ">=1.53.0"


class TinkerforgeBindingsConan(ConanFile):
    name = "tinkerforge-bindings"
    description = "API bindings to control Tinkerforge's Bricks and Bricklets"
    license = "CC0 1.0 Universal"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.tinkerforge.com/"
    topics = ("iot", "maker", "bindings")

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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime + shared is failing to link")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINKERFORGE_BINDINGS_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "license.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tinkerforge-bindings")
        self.cpp_info.set_property("cmake_target_name", "tinkerforge::bindings")

        self.cpp_info.components["_bindings"].set_property("cmake_target_name", "bindings")
        self.cpp_info.components["_bindings"].names["cmake_find_package"] = "bindings"
        self.cpp_info.components["_bindings"].names["cmake_find_package_multi"] = "bindings"
        self.cpp_info.components["_bindings"].libs = ["tinkerforge_bindings"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_bindings"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["_bindings"].system_libs = ["advapi32", "ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "tinkerforge"
        self.cpp_info.names["cmake_find_package_multi"] = "tinkerforge"
        self.cpp_info.filenames["cmake_find_package"] = "tinkerforge-bindings"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tinkerforge-bindings"
