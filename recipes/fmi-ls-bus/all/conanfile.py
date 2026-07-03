from os import path
from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

required_conan_version = ">=2"


class PackageConan(ConanFile):
    name = "fmi-ls-bus"
    description = "FMI Layered Standard for Network Communication (FMI-LS-BUS)"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/modelica/fmi-ls-bus"
    topics = ("fmi", "fmi-ls-bus", "co-simulation", "network-communication", "can", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmi3/3.0.2")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            src=path.join(self.source_folder, "headers"),
            dst=path.join(self.package_folder, "include"),
        )
        copy(
            self,
            pattern="*.xsd",
            src=path.join(self.source_folder, "schema"),
            dst=path.join(self.package_folder, "res"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]
