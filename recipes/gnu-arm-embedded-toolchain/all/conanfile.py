from conan import ConanFile
from conan.tools.files import get, copy, check_sha256, unzip
from conan.errors import ConanException
from urllib.parse import urlparse
import urllib.request
import os


required_conan_version = ">=1.50.0"


class ArmGnuToolchain(ConanFile):
    name = "arm-gnu-toolchain"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = ("Conan installer for the GNU Arm Embedded Toolchain")
    topics = ("gcc", "compiler", "embedded", "ARM", "cortex", "cortex-m",
              "cortex-m0", "cortex-m0+", "cortex-m1", "cortex-m3", "cortex-m4",
              "cortex-m4f", "cortex-m7", "cortex-m23", "cortex-m55",
              "cortex-m35p", "cortex-m33")
    settings = "os", "arch"
    short_paths = True

    @property
    def download_info(self):
        version = self.version
        os = str(self.settings.os)
        arch = str(self.settings.arch)
        return self.conan_data.get("sources", {}).get(version, {}).get(os, {}).get(arch)

    def validate(self):
        if not self.download_info:
            raise ConanException(
                "This package is not available for this operating system and architecture.")

    def source(self):
        pass

    def build(self):
        url = self.download_info["url"]
        url = url + "?rev=" + self.download_info["rev"]
        url = url + "&hash=" + self.download_info["hash"]
        filename = os.path.basename(urlparse(url).path)

        # using urlretrieve over conan.tools.files.get because get results in
        # a 405 forbidden error whereas urlretrieve does not
        urllib.request.urlretrieve(url, filename)
        check_sha256(self, filename, self.download_info["sha256"])
        unzip(self, filename, strip_root=True)

        '''
        NOTE: I'm not sure how exactly I should go about handling this:
        The link is:
        https://developer.arm.com/GetEula?Id=<ID>

        But it returns a number of licenses concatenated together as HTML.
        '''
        # get(self, self.conan_data["sources"]
        #     [self.version]["License"])

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

        # license_dir = os.path.join(self.package_folder, "license/")
        # self.copy(pattern="GetEula*", src=self.build_folder,
        #           dst=license_dir, keep_path=True)

    def package_info(self):
        # Add bin directory to PATH
        bin_folder = os.path.join(self.package_folder, "bin/bin")

        self.buildenv_info.append_path("PATH", bin_folder)

        self.cpp_info.bindirs = [bin_folder]

        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_name", "GENERIC")
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_processor", "ARM")
        self.conf_info.define("tools.build.cross_building:can_run", False)

        tc_path = os.path.join(self.package_folder, "toolchain.cmake")
        self.conf_info.append(
            "tools.cmake.cmaketoolchain:user_toolchain", [tc_path])

        self.conf_info.define("tools.build:compiler_executables", {
            "c": "arm-none-eabi-gcc",
            "cpp": "arm-none-eabi-g++",
            "asm": "arm-none-eabi-as",
        })
