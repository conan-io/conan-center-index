from os import path
from conan import ConanFile
from conan.tools.files import (
    get, copy, apply_conandata_patches, export_conandata_patches)
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "fmi1"
    description = "Functional Mock-up Interface (FMI) for Co-Simulation"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://fmi-standard.org"
    topics = ("fmi-standard", "co-simulation", "model-exchange", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True  # True OK because patch only adds new file

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["co-simulation"],
            destination="cosim", strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["model-exchange"],
            destination="modex", strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=path.join(self.package_folder, "licenses"),
            src=self.source_folder
        )
        for comp in ["modex", "cosim"]:
            copy(
                self,
                pattern="*.h",
                src=path.join(self.source_folder, comp),
                dst=path.join(self.package_folder, "include", comp)
            )
            copy(
                self,
                pattern="*.xsd",
                src=path.join(self.source_folder, comp),
                dst=path.join(self.package_folder, "res", comp)
            )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        self.cpp_info.components["cosim"].set_property("cmake_target_name", "fmi1::cosim")
        self.cpp_info.components["cosim"].includedirs = ["include/cosim"]
        self.cpp_info.components["cosim"].resdirs = ["res/cosim"]
        self.cpp_info.components["modex"].set_property("cmake_target_name", "fmi1::modex")
        self.cpp_info.components["modex"].includedirs = ["include/modex"]
        self.cpp_info.components["modex"].resdirs = ["res/modex"]
