from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
import os

required_conan_version = ">=2"


class DracoConan(ConanFile):
    name = "draco"
    description = "Draco is a library for compressing and decompressing 3D " \
                  "geometric meshes and point clouds. It is intended to " \
                  "improve the storage and transmission of 3D graphics."
    license = "Apache-2.0"
    topics = ("draco", "3d", "graphics", "mesh", "compression", "decompression")
    homepage = "https://google.github.io/draco/"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "target": ["draco", "encode_and_decode", "encode_only", "decode_only"],
        "enable_point_cloud_compression": [True, False],
        "enable_mesh_compression": [True, False],
        "enable_standard_edgebreaker": [True, False],
        "enable_predictive_edgebreaker": [True, False],
        "enable_backwards_compatibility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "target": "draco",
        "enable_point_cloud_compression": True,
        "enable_mesh_compression": True,
        "enable_standard_edgebreaker": True,
        "enable_predictive_edgebreaker": True,
        "enable_backwards_compatibility": True,
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_mesh_compression:
            del self.options.enable_standard_edgebreaker
            del self.options.enable_predictive_edgebreaker

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["DRACO_POINT_CLOUD_COMPRESSION"] = self.options.enable_point_cloud_compression
        tc.cache_variables["DRACO_MESH_COMPRESSION"] = self.options.enable_mesh_compression
        if self.options.enable_mesh_compression:
            tc.cache_variables["DRACO_STANDARD_EDGEBREAKER"] = self.options.enable_standard_edgebreaker
            tc.cache_variables["DRACO_PREDICTIVE_EDGEBREAKER"] = self.options.enable_predictive_edgebreaker
        tc.cache_variables["DRACO_ANIMATION_ENCODING"] = False
        tc.cache_variables["DRACO_BACKWARDS_COMPATIBILITY"] = self.options.enable_backwards_compatibility
        tc.cache_variables["DRACO_DECODER_ATTRIBUTE_DEDUPLICATION"] = False
        tc.cache_variables["DRACO_FAST"] = False
        # DRACO_GLTF True overrides options by enabling
        #   DRACO_MESH_COMPRESSION_SUPPORTED,
        #   DRACO_NORMAL_ENCODING_SUPPORTED,
        #   DRACO_STANDARD_EDGEBREAKER_SUPPORTED
        tc.cache_variables["DRACO_GLTF"] = False
        tc.cache_variables["DRACO_JS_GLUE"] = False
        tc.cache_variables["DRACO_MAYA_PLUGIN"] = False
        tc.cache_variables["DRACO_TESTS"] = False
        tc.cache_variables["DRACO_UNITY_PLUGIN"] = False
        tc.cache_variables["DRACO_WASM"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.shared:
            rm(self, "*draco.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "draco")
        self.cpp_info.set_property("cmake_target_name", "draco::draco")
        self.cpp_info.set_property("pkg_config_name", "draco")
        self.cpp_info.libs = ["draco"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
