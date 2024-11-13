from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class GlmConan(ConanFile):
    name = "glm"
    description = "OpenGL Mathematics (GLM)"
    topics = ("glm", "opengl", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/glm"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=self.version < Version("1.0.0"))

    def build(self):
        pass

    def package(self):
        if self.version < Version("1.0.0"):
            copy(self, "copying.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, "copying.txt", src=os.path.join(self.source_folder, "glm"), dst=os.path.join(self.package_folder, "licenses"))
        for headers in ("*.hpp", "*.inl", "*.h", "*.cppm"):
            copy(self, headers, src=os.path.join(self.source_folder, "glm"),
                                dst=os.path.join(self.package_folder, "include", "glm"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glm")
        self.cpp_info.set_property("cmake_target_name", "glm::glm")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
