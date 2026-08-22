from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class DrflacConan(ConanFile):
    name = "drflac"
    description = "FLAC audio decoder."
    homepage = "https://mackron.github.io/dr_flac"
    topics = ("audio", "flac", "sound")
    license = ("Unlicense", "MIT-0")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "buffer_size": ["ANY"],
        "no_crc": [True, False],
        "no_ogg": [True, False],
        "no_simd": [True, False],
        "no_stdio": [True, False],
        "no_wchar": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "buffer_size": 0, # zero means the default buffer size is used
        "no_crc": False,
        "no_ogg": False,
        "no_simd": False,
        "no_stdio": False,
        "no_wchar": False,
    }
    exports_sources = ["CMakeLists.txt", "dr_flac.c"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.12.39":
            del self.options.no_wchar

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DRFLAC_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["BUFFER_SIZE"] = self.options.buffer_size
        tc.variables["NO_CRC"] = self.options.no_crc
        tc.variables["NO_OGG"] = self.options.no_ogg
        tc.variables["NO_SIMD"] = self.options.no_simd
        tc.variables["NO_STDIO"] = self.options.no_stdio
        tc.variables["NO_WCHAR"] = self.options.get_safe("no_wchar", False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dr_flac"]
        if self.options.shared:
            self.cpp_info.defines.append("DRFLAC_DLL")
        if self.options.buffer_size != "0":
            self.cpp_info.defines.append("DR_FLAC_BUFFER_SIZE={}".format(self.options.buffer_size))
        if self.options.no_crc:
            self.cpp_info.defines.append("DR_FLAC_NO_CRC")
        if self.options.no_ogg:
            self.cpp_info.defines.append("DR_FLAC_NO_OGG")
        if self.options.no_simd:
            self.cpp_info.defines.append("DR_FLAC_NO_SIMD")
        if self.options.no_stdio:
            self.cpp_info.defines.append("DR_FLAC_NO_STDIO")
        if self.options.get_safe("no_wchar", False):
            self.cpp_info.defines.append("DR_FLAC_NO_WCHAR")
