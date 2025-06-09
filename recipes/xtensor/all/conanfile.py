from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


class XtensorConan(ConanFile):
    name = "xtensor"
    package_type = "header-library"
    description = "C++ tensors with broadcasting and lazy computing"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtensor"
    topics = ("numpy", "multidimensional-arrays", "tensors")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "xsimd": [True, False],
        "tbb": [True, False],
        "openmp": [True, False],
    }
    default_options = {
        "xsimd": True,
        "tbb": False,
        "openmp": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/xtensor-stack/xtensor?tab=readme-ov-file#dependencies
        if Version(self.version) < "0.26.0":
            self.requires("xtl/0.7.5")
        else:
            self.requires("xtl/0.8.0")
        self.requires("nlohmann_json/3.11.3")
        if self.options.xsimd:
            if Version(self.version) < "0.24.0":
                self.requires("xsimd/7.5.0")
            elif Version(self.version) < "0.26.0":
                self.requires("xsimd/13.0.0")
            else:
                self.requires("xsimd/13.2.0")
        if self.options.tbb:
            self.requires("onetbb/2021.10.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.options.tbb and self.options.openmp:
            raise ConanInvalidConfiguration(
                "The options 'tbb' and 'openmp' can not be used together."
            )

        check_min_cppstd(self, 14 if Version(self.version) < "0.26.0" else 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xtensor")
        self.cpp_info.set_property("cmake_target_name", "xtensor")
        self.cpp_info.set_property("pkg_config_name", "xtensor")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.xsimd:
            self.cpp_info.defines.append("XTENSOR_USE_XSIMD")
        if self.options.tbb:
            self.cpp_info.defines.append("XTENSOR_USE_TBB")
        if self.options.openmp:
            self.cpp_info.defines.append("XTENSOR_USE_OPENMP")
