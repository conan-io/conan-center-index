import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, get

class SentilConan(ConanFile):
    name = "sentil"
    version = "0.3.0"
    license = "MIT OR Apache-2.0"
    description = "C ABI for SENTIL, runtime verification for Signal Temporal Logic and its probabilistic extension PrSTL"
    homepage = "https://github.com/sedislab/SENTIL"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("runtime-verification", "temporal-logic", "stl", "prstl", "formal-methods")
    settings = "os", "arch", "compiler", "build_type"

    _assets = {
        ("Linux", "x86_64"): "linux-x86_64",
        ("Macos", "x86_64"): "macos-x86_64",
        ("Macos", "armv8"): "macos-arm64",
        ("Windows", "x86_64"): "windows-x86_64",
    }

    def _platform(self):
        return self._assets.get((str(self.settings.os), str(self.settings.arch)))

    def validate(self):
        if self._platform() is None:
            raise ConanInvalidConfiguration(
                f"SENTIL has no prebuilt bundle for {self.settings.os}/{self.settings.arch}. "
                "The released platforms are Linux x86_64, macOS x86_64, macOS armv8, and Windows x86_64."
            )

    def build(self):
        get(self, **self.conan_data["sources"][self.version][self._platform()], strip_root=True)

    def package(self):
        licenses = os.path.join(self.package_folder, "licenses")
        base = f"https://raw.githubusercontent.com/sedislab/SENTIL/v{self.version}"
        for name in ("LICENSE-MIT", "LICENSE-APACHE"):
            download(self, f"{base}/{name}", os.path.join(licenses, name))
        copy(self, "*.h", os.path.join(self.build_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", os.path.join(self.build_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*", os.path.join(self.build_folder, "lib"),
             os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["sentil"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.set_property("pkg_config_name", "sentil")
        self.cpp_info.set_property("cmake_file_name", "Sentil")
        self.cpp_info.set_property("cmake_target_name", "Sentil::sentil")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["m", "pthread", "dl"]