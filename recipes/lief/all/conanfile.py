import os
from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration


class LiefConan(ConanFile):
    name = "lief"
    description = "Library to Instrument Executable Formats"
    topics = ("conan", "lief", "executable", "elf")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lief-project/LIEF"
    license = "Apache-2.0"
    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake",
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_c_api": [True, False],
        "with_frozen": [True, False],
        "with_json": [True, False],
        "with_art": [True, False],
        "with_dex": [True, False],
        "with_elf": [True, False],
        "with_macho": [True, False],
        "with_oat": [True, False],
        "with_pe": [True, False],
        "with_vdex": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_frozen": True,
        "with_json": True,
        "with_c_api": True,
        "with_art": True,
        "with_dex": True,
        "with_elf": True,
        "with_macho": True,
        "with_oat": True,
        "with_pe": True,
        "with_vdex": True,
    }

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
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version.value) <= 14 and self.options.shared:
            raise ConanInvalidConfiguration("{} {} does not support Visual Studio <= 14 with shared:True".format(self.name, self.version))

    def requirements(self):
        self.requires("rang/3.1.0")
        self.requires("mbedtls/2.16.3-apache")
        if self.options.with_json:
            self.requires("nlohmann_json/3.9.1")
        if self.options.with_frozen:
            self.requires("frozen/1.0.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "LIEF-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIEF_ART"] = self.options.with_art
        self._cmake.definitions["LIEF_DEX"] = self.options.with_dex
        self._cmake.definitions["LIEF_ELF"] = self.options.with_elf
        self._cmake.definitions["LIEF_OAT"] = self.options.with_oat
        self._cmake.definitions["LIEF_PE"] = self.options.with_pe
        self._cmake.definitions["LIEF_VDEX"] = self.options.with_vdex
        self._cmake.definitions["LIEF_MACHO"] = self.options.with_macho
        self._cmake.definitions["LIEF_ENABLE_JSON"] = self.options.with_json
        self._cmake.definitions["LIEF_DISABLE_FROZEN"] = not self.options.with_frozen
        self._cmake.definitions["LIEF_C_API"] = self.options.with_c_api
        self._cmake.definitions["LIEF_EXAMPLES"] = False
        self._cmake.definitions["LIEF_TESTS"] = False
        self._cmake.definitions["LIEF_DOC"] = False
        self._cmake.definitions["LIEF_LOGGING"] = False
        self._cmake.definitions["LIEF_PYTHON_API"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
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
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "lief"
        self.cpp_info.names["cmake_find_package"] = "LIEF"
        self.cpp_info.names["cmake_find_package_multi"] = "LIEF"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines = ["_GLIBCXX_USE_CXX11_ABI=1"]
        if self.options.shared:
            self.cpp_info.defines.append("LIEF_IMPORT")
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags += ["/FIiso646.h"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.system_libs = ["ws2_32"]
