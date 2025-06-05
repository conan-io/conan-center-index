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

    options = {
        "enable_experimental": [True, False],
        "force_ctor_init": [True, False],
        "force_explicit_ctor": [True, False],
        "force_inline": [True, False]
    }

    default_options = {
        "enable_experimental": False,
        "force_ctor_init": False,
        "force_explicit_ctor": False,
        "force_inline": False
    }

    options_descriptions = {
        "enable_experimental": "Enable experimental features",
        "force_ctor_init": "Default-initialize matrices and vectors in constructors",
        "force_explicit_ctor": "Require explicit conversions",
        "force_inline": "Inline GLM code for performance",
    }

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

        if self.options.enable_experimental:
            self.cpp_info.defines.append("GLM_ENABLE_EXPERIMENTAL")
        if self.options.force_ctor_init:
            self.cpp_info.defines.append("GLM_FORCE_CTOR_INIT")
        if self.options.force_explicit_ctor:
            self.cpp_info.defines.append("GLM_FORCE_EXPLICIT_CTOR")
        if self.options.force_inline:
            self.cpp_info.defines.append("GLM_FORCE_INLINE")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
