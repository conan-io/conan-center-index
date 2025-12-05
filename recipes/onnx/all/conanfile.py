import os
import sys

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=2.0.5"


class OnnxConan(ConanFile):
    name = "onnx"
    description = "Open standard for machine learning interoperability."
    license = "Apache-2.0"
    topics = ("machine-learning", "deep-learning", "neural-network")
    homepage = "https://github.com/onnx/onnx"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_static_registration": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_static_registration": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if is_msvc(self):
            del self.options.shared
            self.package_type = "static-library"
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("protobuf/[>=4.25.3 <7]", transitive_headers=True, transitive_libs=True)
        self.requires("abseil/[>=20230802.1 <=20250814.0]")

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ONNX_USE_PROTOBUF_SHARED_LIBS"] = self.dependencies.host["protobuf"].options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.get_safe("shared", False)
        tc.cache_variables["ONNX_BUILD_PYTHON"] = False
        tc.cache_variables["ONNX_GEN_PB_TYPE_STUBS"] = False
        tc.cache_variables["ONNX_WERROR"] = False
        tc.cache_variables["ONNX_COVERAGE"] = False
        tc.cache_variables["ONNX_BUILD_TESTS"] = False
        tc.cache_variables["ONNX_USE_LITE_PROTO"] = self.dependencies.host["protobuf"].options.lite
        tc.cache_variables["ONNX_ML"] = True
        tc.cache_variables["ONNX_VERIFY_PROTO3"] = False
        if is_msvc(self):
            tc.cache_variables["ONNX_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.cache_variables["ONNX_DISABLE_STATIC_REGISTRATION"] = self.options.disable_static_registration
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ONNX")
        requires = [
            "protobuf::libprotobuf",
            "abseil::absl_absl_check",
            "abseil::absl_absl_log",
            "abseil::absl_algorithm",
            "abseil::absl_base",
            "abseil::absl_bind_front",
            "abseil::absl_bits",
            "abseil::absl_btree",
            "abseil::absl_cleanup",
            "abseil::absl_cord",
            "abseil::absl_core_headers",
            "abseil::absl_debugging",
            "abseil::absl_die_if_null",
            "abseil::absl_dynamic_annotations",
            "abseil::absl_flags",
            "abseil::absl_flat_hash_map",
            "abseil::absl_flat_hash_set",
            "abseil::absl_function_ref",
            "abseil::absl_hash",
            "abseil::absl_layout",
            "abseil::absl_log_initialize",
            "abseil::absl_log_severity",
            "abseil::absl_memory",
            "abseil::absl_node_hash_map",
            "abseil::absl_node_hash_set",
            "abseil::absl_optional",
            "abseil::absl_span",
            "abseil::absl_status",
            "abseil::absl_statusor",
            "abseil::absl_strings",
            "abseil::absl_synchronization",
            "abseil::absl_time",
            "abseil::absl_type_traits",
            "abseil::absl_utility",
            "abseil::absl_variant"
        ]
        host_protobuf = self.dependencies.host["protobuf"]
        if "utf8_range" in host_protobuf.cpp_info.components:
            requires += ["protobuf::utf8_range", "protobuf::utf8_validity"]
        defines = ["ONNX_NAMESPACE=onnx", "ONNX_ML=1"]
        if self.options.disable_static_registration:
            defines.append("__ONNX_DISABLE_STATIC_REGISTRATION")
        if host_protobuf.options.lite:
            defines.append("ONNX_USE_LITE_PROTO=1")
        # onnx
        self.cpp_info.components["libonnx"].set_property("cmake_target_name", "ONNX::onnx")
        self.cpp_info.components["libonnx"].set_property("cmake_target_aliases", ["onnx"])
        self.cpp_info.components["libonnx"].libs = ["onnx"]
        self.cpp_info.components["libonnx"].defines = defines
        self.cpp_info.components["libonnx"].requires = requires
        # onnx_proto
        self.cpp_info.components["onnx_proto"].set_property("cmake_target_name", "ONNX::onnx_proto")
        self.cpp_info.components["onnx_proto"].set_property("cmake_target_aliases", ["onnx_proto"])
        self.cpp_info.components["onnx_proto"].libs = ["onnx_proto"]
        self.cpp_info.components["onnx_proto"].defines = defines
        self.cpp_info.components["onnx_proto"].requires = requires
