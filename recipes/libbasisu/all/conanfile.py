import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration

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
        "use_sse4": [True, False],
        "with_zstd": [True, False],
        "enable_encoder": [True, False],
        "custom_iterator_debug_level": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "use_sse4": False,
        "with_zstd": True,
        "enable_encoder": True,
        "custom_iterator_debug_level": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _use_custom_iterator_debug_level(self):
        return self.options.get_safe("custom_iterator_debug_level", default=self.default_options["custom_iterator_debug_level"])
 
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler != "Visual Studio":
            del self.options.custom_iterator_debug_level

    def _minimum_compiler_version(self) -> bool:
        return {
            "Visual Studio": "15",
            "gcc": "5.4",
            "clang": "3.9",
            "apple-clang": "10"
        }

    def validate(self):
        min_version = self._minimum_compiler_version().get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        elif tools.Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration("{} {} does not support compiler with version {} {}, minimum supported compiler version is {} ".format(self.name, self.version, self.settings.compiler, self.settings.compiler.version, min_version))
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SSE4"] = self.options.use_sse4
        self._cmake.definitions["ZSTD"] = self.options.with_zstd
        self._cmake.definitions["ENABLE_ENCODER"] = self.options.enable_encoder
        self._cmake.definitions["NO_ITERATOR_DEBUG_LEVEL"] = not self._use_custom_iterator_debug_level()
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake
 
    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", self.name, "transcoder"), src=os.path.join(self._source_subfolder, "transcoder"))
        if self.options.enable_encoder:
            self.copy("*.h", dst=os.path.join("include", self.name, "encoder"), src=os.path.join(self._source_subfolder, "encoder"))
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = self.name
        self.cpp_info.names["cmake_find_package_multi"] = self.name
        self.cpp_info.includedirs = ["include", os.path.join("include", self.name)]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        self.cpp_info.defines.append("BASISU_NO_ITERATOR_DEBUG_LEVEL={}".format("1" if self._use_custom_iterator_debug_level() else "0"))
