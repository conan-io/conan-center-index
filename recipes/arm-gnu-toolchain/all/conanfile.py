from conan import ConanFile
from conan.tools.files import get, copy
from conan.errors import ConanException
import urllib.request
import os


required_conan_version = ">=1.50.0"


class ArmGnuToolchain(ConanFile):
    name = "arm-gnu-toolchain"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = ("Conan installer for the GNU Arm Embedded Toolchain")
    topics = ("gcc", "compiler", "embedded", "arm", "cortex", "cortex-m",
              "cortex-m0", "cortex-m0+", "cortex-m1", "cortex-m3", "cortex-m4",
              "cortex-m4f", "cortex-m7", "cortex-m23", "cortex-m55",
              "cortex-m35p", "cortex-m33")
    settings = "os", "arch", 'compiler', 'build_type'
    exports_sources = "toolchain.cmake"
    short_paths = True

    @property
    def download_info(self):
        version = self.version
        os = str(self.settings.os)
        arch = str(self.settings.arch)
        return self.conan_data.get("sources", {}).get(version, {}).get(os, {}).get(arch)

    @property
    def license_url(self):
        license_id = "ff19df33-da82-491a-ab50-c605d4589a26"
        license_base_url = "https://developer.arm.com/GetEula?Id="
        return license_base_url + license_id

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if not self.download_info:
            raise ConanException(
                "This package is not available for this operating system and architecture.")

    def source(self):
        pass

    def build(self):
        get(self,
            **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
            strip_root=True)

        # The below command is used instead of get() to get past 403 Forbidden
        # issues
        urllib.request.urlretrieve(self.license_url, "LICENSE")

    def package(self):
        destination = os.path.join(self.package_folder, "bin/")

        copy(self, pattern="arm-none-eabi/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="bin/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="include/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="lib/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="libexec/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="share/*", src=self.build_folder,
             dst=destination, keep_path=True)

        license_dir = os.path.join(self.package_folder, "licenses/")
        copy(self, pattern="LICENSE*", src=self.build_folder,
             dst=license_dir, keep_path=True)

        resource_dir = os.path.join(self.package_folder, "res/")
        copy(self, pattern="toolchain.cmake", src=self.build_folder,
             dst=resource_dir, keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin/bin")
        self.cpp_info.bindirs = [bin_folder]
        self.buildenv_info.append_path("PATH", bin_folder)

        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_name", "GENERIC")
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_processor", "ARM")
        self.conf_info.define("tools.build.cross_building:can_run", False)
        self.conf_info.define("tools.build:compiler_executables", {
            "c": "arm-none-eabi-gcc",
            "cpp": "arm-none-eabi-g++",
            "asm": "arm-none-eabi-as",
        })

        f = os.path.join(self.package_folder, "res/toolchain.cmake")
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", f)
