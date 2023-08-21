from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.2"


class CsmConan(ConanFile):
    name = "csm"
    description = "Community Sensor Model base interface library"
    license = "Unlicense"
    topics = ("sensor", "camera", "camera-model", "geospatial", "planetary", "planetary-data")
    homepage = "https://github.com/ngageoint/csm"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "CMakeLists.txt"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CSM_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["CSM_VERSION"] = self.version
        tc.variables["CSM_MAJOR_VERSION"] = str(Version(self.version).major)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["csmapi"]
