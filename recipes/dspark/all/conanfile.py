from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.62.0"


class DSParkConan(ConanFile):
    name = "dspark"
    description = ("Header-only audio DSP framework in pure C++20 with zero "
                   "external dependencies: filters, dynamics, reverbs, physical "
                   "analog models, pitch tools, EBU R128 metering and more.")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CristianMoresi/DSPark"
    topics = ("audio", "dsp", "header-only", "filters", "effects", "loudness")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        for module in ("Core", "Effects", "Analysis", "IO", "Music"):
            copy(self, "*.h",
                 os.path.join(self.source_folder, module),
                 os.path.join(self.package_folder, "include", "DSPark", module))
        copy(self, "DSPark.h", self.source_folder,
             os.path.join(self.package_folder, "include", "DSPark"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "DSPark")
        self.cpp_info.set_property("cmake_target_name", "DSPark::DSPark")
