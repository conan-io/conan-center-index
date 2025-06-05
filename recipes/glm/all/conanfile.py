from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
        "force_aligned_gentypes": [True, False],
        "force_ctor_init": [True, False],
        "force_default_aligned_gentypes": [True, False],
        "force_depth_zero_to_one": [True, False],
        "force_explicit_ctor": [True, False],
        "force_inline": [True, False],
        "force_intrinsics": [True, False],
        "force_left_handed": [True, False],
        "force_messages": [True, False],
        "force_pure": [True, False],
        "force_silent_warnings": [True, False],
        "force_single_only": [True, False],
        "force_size_t_length": [True, False],
        "force_swizzle": [True, False],
        "force_unrestricted_gentype": [True, False],
        "force_xyzw_only": [True, False],
        "quaternion_order": ["wxyz", "xyzw"],
    }

    default_options = {
        "enable_experimental": False,
        "force_aligned_gentypes": False,
        "force_ctor_init": False,
        "force_default_aligned_gentypes": False,
        "force_depth_zero_to_one": False,
        "force_explicit_ctor": False,
        "force_inline": False,
        "force_intrinsics": False,
        "force_left_handed": False,
        "force_messages": False,
        "force_pure": False,
        "force_silent_warnings": False,
        "force_single_only": False,
        "force_size_t_length": False,
        "force_swizzle": False,
        "force_unrestricted_gentype": False,
        "force_xyzw_only": False,
        "quaternion_order": "wxyz",
    }

    options_descriptions = {
        "enable_experimental": "Enable experimental features",
        "force_aligned_gentypes": "Enable aligned types",
        "force_ctor_init": "Default-initialize matrices and vectors in constructors",
        "force_default_aligned_gentypes": "Use aligned types by default",
        "force_depth_zero_to_one": "Use clip space between 0 and 1",
        "force_explicit_ctor": "Require explicit conversions",
        "force_inline": "Inline GLM code for performance",
        "force_intrinsics": "Enable SIMD optimizations",
        "force_left_handed": "Use left-handed coordinate system",
        "force_messages": "Print GLM configuration messages at build time",
        "force_pure": "Disable intrinsics, use pure C++",
        "force_silent_warnings": "Silence warnings from language extensions",
        "force_single_only": "Remove explicit 64-bit float types",
        "force_size_t_length": "Use size_t for .length() return type",
        "force_swizzle": "Enable swizzle operators",
        "force_unrestricted_gentype": "Allow unrestricted genType usage",
        "force_xyzw_only": "Only expose x, y, z, w vector components",
        "quaternion_order": "Order that GLM stores quaternion components.",
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.options.force_pure and self.options.force_intrinsics:
            raise ConanInvalidConfiguration("Cannot use both 'force_pure' and 'force_intrinsics' options together.")

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
        if self.options.force_aligned_gentypes:
            self.cpp_info.defines.append("GLM_FORCE_ALIGNED_GENTYPES")
        if self.options.force_ctor_init:
            self.cpp_info.defines.append("GLM_FORCE_CTOR_INIT")
        if self.options.force_default_aligned_gentypes:
            self.cpp_info.defines.append("GLM_FORCE_DEFAULT_ALIGNED_GENTYPES")
        if self.options.force_depth_zero_to_one:
            self.cpp_info.defines.append("GLM_FORCE_DEPTH_ZERO_TO_ONE")
        if self.options.force_explicit_ctor:
            self.cpp_info.defines.append("GLM_FORCE_EXPLICIT_CTOR")
        if self.options.force_inline:
            self.cpp_info.defines.append("GLM_FORCE_INLINE")
        if self.options.force_intrinsics:
            self.cpp_info.defines.append("GLM_FORCE_INTRINSICS")
        if self.options.force_left_handed:
            self.cpp_info.defines.append("GLM_FORCE_LEFT_HANDED")
        if self.options.force_messages:
            self.cpp_info.defines.append("GLM_FORCE_MESSAGES")
        if self.options.force_pure:
            self.cpp_info.defines.append("GLM_FORCE_PURE")
        if self.options.force_silent_warnings:
            self.cpp_info.defines.append("GLM_FORCE_SILENT_WARNINGS")
        if self.options.force_single_only:
            self.cpp_info.defines.append("GLM_FORCE_SINGLE_ONLY")
        if self.options.force_size_t_length:
            self.cpp_info.defines.append("GLM_FORCE_SIZE_T_LENGTH")
        if self.options.force_swizzle:
            self.cpp_info.defines.append("GLM_FORCE_SWIZZLE")
        if self.options.force_unrestricted_gentype:
            self.cpp_info.defines.append("GLM_FORCE_UNRESTRICTED_GENTYPE")
        if self.options.force_xyzw_only:
            self.cpp_info.defines.append("GLM_FORCE_XYZW_ONLY")
        if self.options.quaternion_order == "xyzw":
            self.cpp_info.defines.append("GLM_FORCE_QUAT_DATA_XYZW")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
