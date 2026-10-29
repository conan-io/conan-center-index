from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"


class GlmConan(ConanFile):
    name = "glm"
    description = "OpenGL Mathematics (GLM)"
    topics = ("glm", "opengl", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/glm"
    license = "LicenseRef-HappyBunny OR MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "header_only": False,
    }
    implements = ["auto_shared_fpic", "auto_header_only"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["GLM_BUILD_INSTALL"] = True
        tc.cache_variables["GLM_BUILD_LIBRARY"] = not self.options.header_only
        tc.generate()

    def validate(self):
        if self.settings.os == "Windows" and self.options.get_safe("shared"):
            raise ConanInvalidConfiguration("GLM does not export symbols when built as shared library on Windows.")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "copying.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glm")
        self.cpp_info.set_property("cmake_target_name", "none")
        self.cpp_info.components["headers"].set_property("cmake_target_name", "glm::glm-header-only")
        self.cpp_info.components["headers"].libdirs = []
        self.cpp_info.components["headers"].bindirs = []
        if not self.options.header_only:
            self.cpp_info.components["library"].set_property("cmake_target_name", "glm::glm")
            self.cpp_info.components["library"].set_property("cmake_target_aliases", ["glm",])
            self.cpp_info.components["library"].libs = ["glm"]
            self.cpp_info.components["library"].requires = ["headers"]
