import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.cmake import  cmake_layout

required_conan_version = ">=2.0.9"

class SciplotConan(ConanFile):
    name = "sciplot"
    description = "A modern C++ scientific plotting library powered by gnuplot."
    version = "v0.3.1"
    license = "MIT"
    url = "https://github.com/sciplot/sciplot"
    homepage = "https://sciplot.github.io/"
    topics = ("plotting", "gnuplot", "scientific", "header-only")
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)
       
    def source(self):
        get(self, url=f"https://github.com/sciplot/sciplot/archive/refs/tags/{self.version}.tar.gz", strip_root=True)
        # get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
        # apply_conandata_patches(self)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "sciplot"), dst=os.path.join(self.package_folder, "include", "sciplot"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
      

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_target_name", "sciplot::sciplot")