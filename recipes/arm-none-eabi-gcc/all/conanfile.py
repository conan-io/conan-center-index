from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, download
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0"

valid_archs = ["armv6", "armv7", "armv7hf", "armv8", "armv8.1", "armv9"]

class PackageConan(ConanFile):
    name = "arm-none-eabi-gcc"
    description = "embedded compiler for arm based microcontrollers on baremetal systems"
    license = " GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index/recipes/arm-none-eabi-gcc"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    topics = ("arm", "embedded", "compiler suite", "pre-built")
    package_type = "application"
    settings = "os", "arch"

    def layout(self):
        pass

    def validate(self):
        if self.settings.os != "Macos" and self.settings.os != "Windows" and self.settings.os != "Linux":
            raise ConanInvalidConfiguration("your operating system is not supported")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("your system architecture is not supported")

    # do not cache as source, instead, use build folder
    def source(self):
        download(self, "https://www.gnu.org/licenses/gpl-3.0.html", "LICENSE", verify=False)

    # download the source here, then copy to package folder
    def build(self):
        strip_root = False if self.settings.os == "Windows" else True
        get(self, **self.conan_data["sources"][str(self.version)][str(self.settings.os)], strip_root = strip_root)

    # copy all needed files to the package folder
    def package(self):
        dirs_to_copy = ["arm-none-eabi", "bin", "include", "lib", "libexec"]
        for dir in dirs_to_copy:
            copy(self, pattern=f"{dir}/*", src=self.build_folder, dst=self.package_folder, keep_path=True)
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs.append(os.path.join(self.package_folder, "arm-none-eabi", "bin"))
        # folders not used for pre-built binaries
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        self.conf_info.define("tools.build:compiler_executables", {
                                  "c": "arm-none-eabi-gcc",
                                  "cpp":"arm-none-eabi-g++",
                                  "ld": "arm-none-eabi-ld",
                                  "asm": "arm-none-eabi-as",
                                  "objcopy": "arm-none-eabi-objcopy",
                                  "objdump": "arm-none-eabi-objdump",
                                  "size": "arm-none-eabi-size",
                                  "readelf": "arm-none-eabi-readelf",
                              })

