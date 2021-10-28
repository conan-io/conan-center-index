from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class DracoConan(ConanFile):
    name = "draco"
    description = "Draco is a library for compressing and decompressing 3D " \
                  "geometric meshes and point clouds. It is intended to " \
                  "improve the storage and transmission of 3D graphics."
    license = "Apache-2.0"
    topics = ("draco", "3d", "graphics", "mesh",
              "compression", "decompression")
    homepage = "https://google.github.io/draco/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "target": ["draco", "encode_and_decode", "encode_only", "decode_only"],
        "enable_point_cloud_compression": [True, False],
        "enable_mesh_compression": [True, False],
        "enable_standard_edgebreaker": [True, False],
        "enable_predictive_edgebreaker": [True, False],
        "enable_backwards_compatibility": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "target": "draco",
        "enable_point_cloud_compression": True,
        "enable_mesh_compression": True,
        "enable_standard_edgebreaker": True,
        "enable_predictive_edgebreaker": True,
        "enable_backwards_compatibility": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if not self.options.enable_mesh_compression:
            del self.options.enable_standard_edgebreaker
            del self.options.enable_predictive_edgebreaker
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build(target=self._get_target())

    def _configure_cmake(self):
        cmake = CMake(self)

        # use different cmake definitions based on package version
        if tools.Version(self.version) < "1.4.0":
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

    def _get_target(self):
        if tools.Version(self.version) < "1.4.0":
            return {
                "decode_only": "dracodec",
                "draco": "draco",
                "encode_and_decode": "draco",
                "encode_only": "dracoenc"
            }.get(str(self.options.target))

        if self.settings.os == "Windows":
            return "draco"

        if self.options.shared:
            return "draco_shared"

        return "draco_static"

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        self.copy(pattern="*.h", dst="include",
                  src=os.path.join(self._source_subfolder, "src"))
        self.copy(pattern="*.h", dst=os.path.join("include", "draco"),
                  src=os.path.join(self._build_subfolder, "draco"))

        build_lib_dir = os.path.join(self._build_subfolder, "lib")
        build_bin_dir = os.path.join(self._build_subfolder, "bin")
        self.copy(pattern="*.a", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib",
                  src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib",
                  src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=build_lib_dir,
                  keep_path=False, symlinks=True)
        self.copy(pattern="*.dll", dst="bin",
                  src=build_bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Draco"
        self.cpp_info.names["cmake_find_package_multi"] = "Draco"
        self.cpp_info.names["pkg_config"] = "draco"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
