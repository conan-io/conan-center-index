import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class LibBasisUniversalConan(ConanFile):
    name = "libbasisu"
    description = "Basis Universal Supercompressed GPU Texture Codec"
    homepage = "https://github.com/BinomialLLC/basis_universal"
    topics = ("conan", "basis", "textures", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "sse": [True, False],
        "x64": [True, False],
        "zstd": [True, False],
        "no_iterator_debug_level": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "sse": True,
        "x64": True,
        "zstd": True,
        "no_iterator_debug_level": True
    }
    short_paths = True

    _cmake = None

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
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_X64"] = self.options.x64
        self._cmake.definitions["SSE"] = self.options.sse
        self._cmake.definitions["ZSTD"] = self.options.zstd
        self._cmake.definitions["BASISU_NO_ITERATOR_DEBUG_LEVEL"] = self.options.no_iterator_debug_level

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _clear_vs_project_files(self):
        tools.remove_files_by_mask(self._source_subfolder, "*.sln")
        tools.remove_files_by_mask(self._source_subfolder, "*.vcxproj")
        tools.remove_files_by_mask(self._source_subfolder, "*.vcxproj.filters")
        
    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        self._clear_vs_project_files()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", self.name, "transcoder"), src=os.path.join(self._source_subfolder, "transcoder"))
        self.copy("*.h", dst=os.path.join("include", self.name, "encoder"), src=os.path.join(self._source_subfolder, "encoder"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = [self.name]
        self.cpp_info.names["cmake_find_package"] = self.name
        self.cpp_info.names["cmake_find_package_multi"] = self.name
        self.cpp_info.includedirs = ["include", os.path.join("include", self.name)]
