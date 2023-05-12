from conan import ConanFile
from conan.tools.files import get, copy
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

    def validate(self):
        pass

    def source(self):
        pass

    def build(self):
        download_info = self.conan_data["sources"][self.version][str(
            self.settings.os)][str(self.settings.arch)]
        get(self, download_info["url"], strip_root=True,
            sha256=download_info["sha256"])

        '''
        NOTE: I'm not sure how exactly I should go about handling this:
        The link is:
        https://developer.arm.com/GetEula?Id=2821586b-44d0-4e75-a06d-4279cd97eaae

        But it returns a number of licenses concatenated together as HTML.
        '''
        # get(self, self.conan_data["sources"]
        #     [self.version]["License"], strip_root=True)

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
