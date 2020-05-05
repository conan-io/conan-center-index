from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class LiefConan(ConanFile):
    name = "lief"
    description = "Library to Instrument Executable Formats"
    topics = ("conan", "lief", "executable", "elf", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lief-project/LIEF"
    license = ("Apache-2.0",)
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
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "rang/3.1.0",
        "mbedtls/2.16.3-apache",
    )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_json:
            self.requires("nlohmann_json/3.7.3")
        if self.options.with_frozen:
            self.requires("frozen/1.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["LIEF_ART"] = self.options.with_art
        cmake.definitions["LIEF_DEX"] = self.options.with_dex
        cmake.definitions["LIEF_ELF"] = self.options.with_elf
        cmake.definitions["LIEF_OAT"] = self.options.with_oat
        cmake.definitions["LIEF_PE"] = self.options.with_pe
        cmake.definitions["LIEF_VDEX"] = self.options.with_vdex
        cmake.definitions["LIEF_MACHO"] = self.options.with_macho

        cmake.definitions["LIEF_ENABLE_JSON"] = self.options.with_json
        cmake.definitions["LIEF_C_API"] = self.options.with_c_api

        cmake.definitions["LIEF_EXAMPLES"] = False
        cmake.definitions["LIEF_LOGGING"] = False
        cmake.definitions["LIEF_PYTHON_API"] = False

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def _patch_sources(self):
        patches = [f for f in os.listdir("patches") if f.endswith('.patch')]
        for patch_file in sorted(patches):
            self.output.info("Applying " + patch_file)
            tools.patch(self._source_subfolder, os.path.join("patches", patch_file))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags += ["/FIiso646.h"]
