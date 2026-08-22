from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.50.0"


class PackageConan(ConanFile):
    name = "psyinf-gmtl"
    description = "The Generic Math Template Library. A math library designed to be high-performance, extensible, and generic."
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/psyinf/gmtl"
    topics = ("linear-algebra", "collision", "vector", "matrix", "template", "math", "header-only")
    settings = "os", "arch", "compiler", "build_type" 
    no_copy_source = True 
   
    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.names["cmake_find_package"] = "gmtl"
        self.cpp_info.names["cmake_find_package_multi"] = "gmtl"
        
        self.cpp_info.set_property("cmake_file_name", "gmtl")
        self.cpp_info.set_property("cmake_target_name", "gmtl::gmtl")
        self.cpp_info.set_property("pkg_config_name", "gmtl")

  
