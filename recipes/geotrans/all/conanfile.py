from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os

required_conan_version = ">=1.53.0"


class GeotransConan(ConanFile):
    name = "geotrans"
    license = "NGA GEOTRANS ToS (https://earth-info.nga.mil/php/download.php?file=wgs-terms)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://earth-info.nga.mil/"
    description = "MSP GEOTRANS is the NGA and DOD approved coordinate converter and datum translator."
    topics = ("geotrans", "geodesic", "geographic", "coordinate", "datum", "geodetic", "conversion", "transformation")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, filename=f"geotrans-{self.version}.tgz")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GEOTRANS_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "*.txt",
                   src=os.path.join(self.source_folder, "GEOTRANS3", "docs"),
                   dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["dtcc"].libs = ["MSPdtcc"]
        self.cpp_info.components["dtcc"].includedirs = [
            path[0] for path in os.walk("include")
        ]
        self.cpp_info.components["dtcc"].res = ["res"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["dtcc"].system_libs.append("pthread")
            self.cpp_info.components["dtcc"].system_libs.append("m")

        self.cpp_info.components["ccs"].libs = ["MSPCoordinateConversionService"]
        self.cpp_info.components["ccs"].requires = ["dtcc"]
        self.cpp_info.components["ccs"].includedirs = [
            path[0] for path in os.walk("include")
        ]
        self.cpp_info.components["ccs"].res = ["res"]

        mspccs_data_path = os.path.join(self.package_folder, "res")
        self.runenv_info.define_path("MSPCCS_DATA", mspccs_data_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.MSPCCS_DATA = mspccs_data_path
