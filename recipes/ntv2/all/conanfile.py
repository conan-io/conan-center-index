from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.46.0"


class Ntv2Conan(ConanFile):
    name = "ntv2"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aja-video/ntv2"
    description = "AJA NTV2 SDK"
    topics = "video, hardware"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        for suffix in ["so", "lib", "a", "dylib", "bc"]:
            copy(self,
                 f"*.{suffix}",
                 src=os.path.join(self.build_folder, "ajalibraries", "ajantv2"),
                 dst=os.path.join(self.package_folder, "lib"),
                 keep_path=False)
        if self.settings.os == "Windows" and self.options.shared:
            copy(self,
                "*.dll",
                src=os.path.join(self.build_folder, "ajalibraries", "ajantv2"),
                dst=os.path.join(self.package_folder, "bin"),
                keep_path=False)
        for lib in ["ajaanc", "ajacc", "ajantv2"]:
            copy(self,
                 "*",
                 src=os.path.join(self.source_folder, "ajalibraries", lib, "includes"),
                 dst=os.path.join(self.package_folder, "include", lib))
        copy(self, "ajalibraries/**/*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "ajalibraries/**/*.hh", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

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
