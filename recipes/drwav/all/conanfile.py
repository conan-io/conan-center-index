from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.46.0"


class DrwavConan(ConanFile):
    name = "drwav"
    description = "WAV audio loader and writer."
    homepage = "https://mackron.github.io/dr_wav"
    topics = ("audio", "wav", "wave", "sound")
    license = ("Unlicense", "MIT-0")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "no_conversion_api": [True, False],
        "no_stdio": [True, False],
        "no_wchar": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "no_conversion_api": False,
        "no_stdio": False,
        "no_wchar": False
    }
    exports_sources = ["CMakeLists.txt", "dr_wav.c"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DRWAV_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["NO_CONVERSION_API"] = self.options.no_conversion_api
        tc.variables["NO_STDIO"] = self.options.no_stdio
        tc.variables["NO_WCHAR"] = self.options.no_wchar
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dr_wav"]
        if self.options.shared:
            self.cpp_info.defines.append("DRWAV_DLL")
        if self.options.no_conversion_api:
            self.cpp_info.defines.append("DR_WAV_NO_CONVERSION_API")
        if self.options.no_stdio:
            self.cpp_info.defines.append("DR_WAV_NO_STDIO")
        if self.options.no_wchar:
            self.cpp_info.defines.append("DR_WAV_NO_WCHAR")     
