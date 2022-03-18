from conans import CMake, ConanFile, tools
import functools
import os

required_conan_version = ">=1.36.0"


class LZ4Conan(ConanFile):
    name = "lz4"
    description = "Extremely Fast Compression algorithm"
    license = ("BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lz4/lz4"
    topics = ("lz4", "compression")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("xxhash/0.8.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _cmakelists_subfolder(self):
        if tools.Version(self.version) < "1.9.3":
            subfolder = os.path.join("contrib", "cmake_unofficial")
        else:
            subfolder = os.path.join("build", "cmake")
        return os.path.join(self._source_subfolder, subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # remove bundled xxhash
        tools.remove_files_by_mask(os.path.join(self._source_subfolder, "lib"), "xxhash.*")
        tools.replace_in_file(
            os.path.join(self._cmakelists_subfolder, "CMakeLists.txt"),
            "\"${LZ4_LIB_SOURCE_DIR}/xxhash.c\"",
            "",
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_LZ4_CMAKELISTS_SUBFOLDER"] = self._cmakelists_subfolder.replace("\\", "/")
        cmake.definitions["LZ4_BUILD_CLI"] = False
        cmake.definitions["LZ4_BUILD_LEGACY_LZ4C"] = False
        cmake.definitions["LZ4_BUNDLED_MODE"] = False
        cmake.definitions["LZ4_POSITION_INDEPENDENT_LIB"] = self.options.get_safe("fPIC", True)
        # Generate a relocatable shared lib on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "liblz4")
        self.cpp_info.libs = ["lz4"]
        if self._is_msvc and self.options.shared:
            self.cpp_info.defines.append("LZ4_DLL_IMPORT=1")

        self.cpp_info.names["pkg_config"] = "liblz4"
