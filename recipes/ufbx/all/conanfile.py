import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

required_conan_version = ">=2.4"


class UfbxConan(ConanFile):
    name = "ufbx"
    description = "Single source file FBX file loader."
    topics = ("fbx", "importer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ufbx/ufbx"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    implements = ["auto_shared_fpic"]
    languages = "C"

    exports_sources = "CMakeLists.txt"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=self.package_folder, src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # These are the libs to link against
        self.cpp_info.libs = ["ufbx"]
        self.cpp_info.set_property("cmake_file_name", "ufbx")
        self.cpp_info.set_property("cmake_target_name", "ufbx::ufbx")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
