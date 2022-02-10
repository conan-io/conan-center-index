import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conans import tools

required_conan_version = ">=1.43.0"

class Ntv2Conan(ConanFile):
    name = "ntv2"
    version = "16.1"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aja-video/ntv2"
    description = "AJA NTV2 SDK"
    topics = "video, hardware"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "CMakeToolchain"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        self.copy(os.path.join(self._source_subfolder, 'LICENSE'), 'licenses')

        for suffix in ["so", "lib", "a", "dylib", "bc", "dll"]:
            self.copy(f"*.{suffix}", src=os.path.join("ajalibraries", "ajantv2"), dst="lib")
        for lib in ["ajaanc", "ajacc", "ajantv2"]:
            self.copy("*", src=os.path.join(self._source_subfolder, "ajalibraries", lib, "includes"), dst=os.path.join("include", lib))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "ajalibraries", "ajabase"), dst=os.path.join("include", "ajabase"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "ajalibraries", "ajantv2", "src", "lin"), dst=os.path.join("include", "ajantv2", "lin"))

    def package_info(self):
        lib_name = "ajantv2shared" if self.options.shared else "ajantv2"
        if self.settings.build_type == "Debug":
            lib_name += "d"
        self.cpp_info.libs = [lib_name]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.defines = ["AJALinux", "AJA_LINUX", "NTV2_USE_STDINT"]
        elif self.settings.os == "Darwin":
            self.cpp_info.defines = ["AJAMac", "AJA_MAC"]
        elif self.settings.os == "Windows":
            self.cpp_info.defines = ["AJAWindows", "AJA_WINDOWS"]
        self.cpp_info.includedirs.extend([os.path.join("include", "ajantv2"), os.path.join("include", "ajantv2", "lin")])
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "rt"]
            if self.options.shared:
                self.cpp_info.system_libs.append("dl")

