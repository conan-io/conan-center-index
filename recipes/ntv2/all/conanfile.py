import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conans import tools

required_conan_version = ">=1.43.0"


class Ntv2Conan(ConanFile):
    name = "ntv2"
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

        for suffix in ["so", "lib", "a", "dylib", "bc"]:
            self.copy(
                f"*.{suffix}", src=os.path.join("ajalibraries", "ajantv2"), dst="lib", keep_path=False)
        if self.settings.os == "Windows" and self.options.shared:
            self.copy(
                "*.dll", src=os.path.join("ajalibraries", "ajantv2"), dst="bin", keep_path=False)
        for lib in ["ajaanc", "ajacc", "ajantv2"]:
            self.copy("*", src=os.path.join(self._source_subfolder,
                      "ajalibraries", lib, "includes"), dst=os.path.join("include", lib))
        self.copy("ajalibraries/**/*.h",
                  src=self._source_subfolder, dst="include")
        self.copy("ajalibraries/**/*.hh",
                  src=self._source_subfolder, dst="include")

    def package_info(self):
        lib_name = "ajantv2shared" if self.options.shared else "ajantv2"
        if self.settings.build_type == "Debug":
            lib_name += "d"
        self.cpp_info.libs = [lib_name]
        self.cpp_info.includedirs = [
            os.path.join("include", "ajalibraries"),
            os.path.join("include", "ajalibraries", "ajabase"),
            os.path.join("include", "ajalibraries", "ajantv2", "includes"),
            os.path.join("include", "ajalibraries", "ajaanc", "includes")
        ]

        if self.settings.os in ("Linux", "FreeBSD"):

            self.cpp_info.defines = ["AJALinux",
                                     "AJA_LINUX", "NTV2_USE_STDINT"]
            self.cpp_info.includedirs.extend([
                os.path.join("include", "ajalibraries",
                             "ajantv2", "src", "lin"),
                os.path.join("include", "ajalibraries",
                             "ajabase", "pnp", "linux"),
                os.path.join("include", "ajalibraries",
                             "ajabase", "system", "linux")
            ])
            self.cpp_info.system_libs = ["pthread", "rt"]
            if self.options.shared:
                self.cpp_info.system_libs.append("dl")

        elif self.settings.os == "Macos":

            self.cpp_info.defines = ["AJAMac", "AJA_MAC"]
            if self.options.shared:
                self.cpp_info.defines.extend(["AJADLL", "AJA_WINDLL"])
            self.cpp_info.includedirs.extend([
                os.path.join("include", "ajalibraries",
                             "ajantv2", "src", "mac"),
                os.path.join("include", "ajalibraries",
                             "ajabase", "pnp", "mac"),
                os.path.join("include", "ajalibraries",
                             "ajabase", "system", "mac")
            ])
            self.cpp_info.frameworks = [
                "CoreFoundation", "Foundation", "IoKit"]

        elif self.settings.os == "Windows":

            self.cpp_info.defines = ["AJAWindows", "AJA_WINDOWS", "MSWindows"]
            self.cpp_info.includedirs.extend([
                os.path.join("include", "ajalibraries",
                             "ajantv2", "src", "win"),
                os.path.join("include", "ajalibraries",
                             "ajabase", "pnp", "windows"),
                os.path.join("include", "ajalibraries",
                             "ajabase", "system", "windows")
            ])
            self.cpp_info.system_libs = [
                "advapi32", "comctl32", "netapi32",
                "odbc32", "psapi", "rpcrt4", "setupapi", "shell32",
                "shlwapi", "user32", "winmm", "ws2_32", "wsock32"
            ]

        self.cpp_info.defines.append(
            "AJADLL_BUILD" if self.options.shared else "AJASTATIC")
