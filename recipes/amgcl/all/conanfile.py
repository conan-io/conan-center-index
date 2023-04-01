from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.1"


class AmgclConan(ConanFile):
    name = "amgcl"
    description = (
        "AMGCL is a header-only C++ library for solving large sparse linear "
        "systems with algebraic multigrid (AMG) method."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ddemidov/amgcl"
    topics = ("mathematics", "opencl", "openmp", "cuda", "amg")
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "amgcl"),
                        dst=os.path.join(self.package_folder, "include", "amgcl"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "amgcl")
        self.cpp_info.set_property("cmake_target_name", "amgcl::amgcl")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
