import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class CvPlotConan(ConanFile):
    name = "cvplot"
    description = "Fast modular OpenCV plotting library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Profactor/cv-plot"
    topics = ("plot", "opencv", "diagram", "plotting", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opencv/4.5.5")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "CvPlot", "inc"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "CvPlot")
        self.cpp_info.set_property("cmake_target_name", "CvPlot::CvPlot")
        self.cpp_info.set_property("cmake_find_mode", "both")

        self.cpp_info.defines.append("CVPLOT_HEADER_ONLY")

        self.cpp_info.names["cmake_find_package"] = "CvPlot"
        self.cpp_info.names["cmake_find_package_multi"] = "CvPlot"
