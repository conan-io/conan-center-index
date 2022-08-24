from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class DracoConan(ConanFile):
    name = "draco"
    description = "Draco is a library for compressing and decompressing 3D " \
                  "geometric meshes and point clouds. It is intended to " \
                  "improve the storage and transmission of 3D graphics."
    license = "Apache-2.0"
    topics = ("draco", "3d", "graphics", "mesh", "compression", "decompression")
    homepage = "https://google.github.io/draco/"
    url = "https://github.com/conan-io/conan-center-index"

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
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.enable_mesh_compression:
            del self.options.enable_standard_edgebreaker
            del self.options.enable_predictive_edgebreaker
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        # use different cmake definitions based on package version
        if tools.scm.Version(self, self.version) < "1.4.0":
            cmake.definitions["ENABLE_POINT_CLOUD_COMPRESSION"] = self.options.enable_point_cloud_compression
            cmake.definitions["ENABLE_MESH_COMPRESSION"] = self.options.enable_mesh_compression
            if self.options.enable_mesh_compression:
                cmake.definitions["ENABLE_STANDARD_EDGEBREAKER"] = self.options.enable_standard_edgebreaker
                cmake.definitions["ENABLE_PREDICTIVE_EDGEBREAKER"] = self.options.enable_predictive_edgebreaker
            cmake.definitions["ENABLE_BACKWARDS_COMPATIBILITY"] = self.options.enable_backwards_compatibility

            # BUILD_FOR_GLTF is not needed, it is equivalent to:
            # - enable_point_cloud_compression=False
            # - enable_mesh_compression=True
            # - enable_standard_edgebreaker=True
            # - enable_predictive_edgebreaker=False
            # - enable_backwards_compatibility=False
            cmake.definitions["BUILD_FOR_GLTF"] = False

            cmake.definitions["BUILD_UNITY_PLUGIN"] = False
            cmake.definitions["BUILD_MAYA_PLUGIN"] = False
            cmake.definitions["BUILD_USD_PLUGIN"] = False

            cmake.definitions["ENABLE_CCACHE"] = False
            cmake.definitions["ENABLE_DISTCC"] = False
            cmake.definitions["ENABLE_EXTRA_SPEED"] = False
            cmake.definitions["ENABLE_EXTRA_WARNINGS"] = False
            cmake.definitions["ENABLE_GOMA"] = False
            cmake.definitions["ENABLE_JS_GLUE"] = False
            cmake.definitions["ENABLE_DECODER_ATTRIBUTE_DEDUPLICATION"] = False
            cmake.definitions["ENABLE_TESTS"] = False
            cmake.definitions["ENABLE_WASM"] = False
            cmake.definitions["ENABLE_WERROR"] = False
            cmake.definitions["ENABLE_WEXTRA"] = False
            cmake.definitions["IGNORE_EMPTY_BUILD_TYPE"] = False
            cmake.definitions["BUILD_ANIMATION_ENCODING"] = False
        else:
            cmake.definitions["DRACO_POINT_CLOUD_COMPRESSION"] = self.options.enable_point_cloud_compression
            cmake.definitions["DRACO_MESH_COMPRESSION"] = self.options.enable_mesh_compression
            if self.options.enable_mesh_compression:
                cmake.definitions["DRACO_STANDARD_EDGEBREAKER"] = self.options.enable_standard_edgebreaker
                cmake.definitions["DRACO_PREDICTIVE_EDGEBREAKER"] = self.options.enable_predictive_edgebreaker
            cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            cmake.definitions["DRACO_ANIMATION_ENCODING"] = False
            cmake.definitions["DRACO_BACKWARDS_COMPATIBILITY"] = self.options.enable_backwards_compatibility
            cmake.definitions["DRACO_DECODER_ATTRIBUTE_DEDUPLICATION"] = False
            cmake.definitions["DRACO_FAST"] = False
            # DRACO_GLTF True overrides options by enabling
            #   DRACO_MESH_COMPRESSION_SUPPORTED,
            #   DRACO_NORMAL_ENCODING_SUPPORTED,
            #   DRACO_STANDARD_EDGEBREAKER_SUPPORTED
            cmake.definitions["DRACO_GLTF"] = False
            cmake.definitions["DRACO_JS_GLUE"] = False
            cmake.definitions["DRACO_MAYA_PLUGIN"] = False
            cmake.definitions["DRACO_TESTS"] = False
            cmake.definitions["DRACO_UNITY_PLUGIN"] = False
            cmake.definitions["DRACO_WASM"] = False

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if tools.scm.Version(self, self.version) < "1.4.0":
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "draco"))
        else:
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            if self.options.shared:
                tools.files.rm(self, 
                    os.path.join(self.package_folder, "lib"),
                    "*draco.a",
                )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "draco")
        self.cpp_info.set_property("cmake_target_name", "draco::draco")
        self.cpp_info.set_property("pkg_config_name", "draco")
        self.cpp_info.libs = ["draco"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
