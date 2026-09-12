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

    def _cargo_profile(self):
        return (
            "release"
            if str(self.settings.build_type) in ["Release", "RelWithDebInfo", "MinSizeRel"]
            else "debug"
        )

    def _library_patterns(self):
        os_name = str(self.settings.os)
        if self.options.shared:
            if os_name == "Windows":
                return [("nwau_c_abi.dll", "bin"), ("nwau_c_abi.lib", "lib")]
            if os_name == "Macos":
                return [("libnwau_c_abi*.dylib", "lib")]
            return [("libnwau_c_abi.so*", "lib")]
        if os_name == "Windows":
            return [("nwau_c_abi.lib", "lib")]
        return [("libnwau_c_abi.a", "lib")]

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
        )

    def build(self):
        profile_args = []
        if self._cargo_profile() == "release":
            profile_args.append("--release")

        self.run(
            "cargo build {} --locked -p nwau-c-abi".format(" ".join(profile_args)),
            cwd=os.path.join(self.source_folder, "rust"),
        )

    def package(self):
        artifact_dir = os.path.join(
            self.source_folder, "rust", "target", self._cargo_profile()
        )

        copy(
            self,
            "nwau_abi.h",
            src=os.path.join(
                self.source_folder, "rust", "crates", "nwau-c-abi", "include"
            ),
            dst=os.path.join(self.package_folder, "include"),
        )
        for pattern, folder in self._library_patterns():
            copy(
                self,
                pattern,
                src=artifact_dir,
                dst=os.path.join(self.package_folder, folder),
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
