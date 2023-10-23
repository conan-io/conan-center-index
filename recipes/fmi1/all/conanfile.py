from os import path
from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy, get, load, save
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

    def _extract_copyright(self):
        fmiFunctions_h = load(self, path.join(self.source_folder, "cosim", "fmiFunctions.h"))
        copyright_start = "Copyright(c)"
        copyright_end = "DAMAGE."
        start_index = fmiFunctions_h.find(copyright_start)
        stop_index = fmiFunctions_h.find(copyright_end)
        if start_index == -1 or stop_index == -1:
            raise ConanException("Could not extract license from fmiFunctions.h file.")
        return fmiFunctions_h[start_index:stop_index+len(copyright_end)]

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
        pass

    def package(self):
        save(self, path.join(self.package_folder, "licenses", "LICENSE"), self._extract_copyright())
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
