import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get


class NwauCAbiConan(ConanFile):
    name = "nwau-c-abi"
    license = "Apache-2.0"
    author = "edithatogo"
    url = "https://github.com/edithatogo/mchs"
    homepage = "https://github.com/edithatogo/mchs"
    description = "C ABI scaffold for MCHS/NWAU interoperability."
    topics = ("health-economics", "nwau", "c-abi", "rust")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_type = "library"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os not in ["Linux", "Macos", "Windows"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} supports Linux, Macos, and Windows only."
            )

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
        )

    def build(self):
        self.run(
            "cargo build --release --locked -p nwau-c-abi",
            cwd=os.path.join(self.source_folder, "rust"),
        )

    def package(self):
        copy(
            self,
            "nwau_abi.h",
            src=os.path.join(
                self.source_folder, "rust", "crates", "nwau-c-abi", "include"
            ),
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "libnwau_c_abi.a",
            src=os.path.join(self.source_folder, "rust", "target", "release"),
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "libnwau_c_abi.so*",
            src=os.path.join(self.source_folder, "rust", "target", "release"),
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "libnwau_c_abi*.dylib",
            src=os.path.join(self.source_folder, "rust", "target", "release"),
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "nwau_c_abi.lib",
            src=os.path.join(self.source_folder, "rust", "target", "release"),
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "nwau_c_abi.dll",
            src=os.path.join(self.source_folder, "rust", "target", "release"),
            dst=os.path.join(self.package_folder, "bin"),
            keep_path=False,
        )
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.libs = ["nwau_c_abi"]
        self.cpp_info.set_property("cmake_file_name", "nwau-c-abi")
        self.cpp_info.set_property("cmake_target_name", "nwau-c-abi::nwau-c-abi")
