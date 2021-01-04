from conans import CMake, ConanFile, tools
import os


class LZ4Conan(ConanFile):
    name = "lz4"
    description = "Extremely Fast Compression algorithm"
    license = ("BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lz4/lz4"
    topics = ("conan", "lz4", "compression")
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "{0}-{1}".format(self.name, self.version)
        os.rename(extracted_folder, self._source_subfolder)

    @property
    def _cmakelists_subfolder(self):
        if tools.Version(self.version) < "1.9.3":
            subfolder = os.path.join("contrib", "cmake_unofficial")
        else:
            subfolder = os.path.join("build", "cmake")
        return os.path.join(self._source_subfolder, subfolder).replace("\\", "/")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CONAN_LZ4_CMAKELISTS_SUBFOLDER"] = self._cmakelists_subfolder
        self._cmake.definitions["LZ4_BUILD_CLI"] = False
        self._cmake.definitions["LZ4_BUILD_LEGACY_LZ4C"] = False
        self._cmake.definitions["LZ4_BUNDLED_MODE"] = False
        self._cmake.definitions["LZ4_POSITION_INDEPENDENT_LIB"] = self.options.get_safe("fPIC", True)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "liblz4"
        self.cpp_info.libs = ["lz4"]
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.defines.append("LZ4_DLL_IMPORT=1")
