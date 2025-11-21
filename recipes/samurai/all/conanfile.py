from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "samurai"
    description = "Intervals coupled with algebra of set to handle adaptive mesh refinement and operators on it"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hpc-maths/samurai"
    topics = ("scientific computing", "adaptive mesh refinement", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cli11/2.3.2")
        self.requires("fmt/10.1.1")
        self.requires("highfive/[>=2.7.1 <3]")
        self.requires("pugixml/1.14")
        self.requires("xsimd/13.0.0")
        self.requires("xtensor/0.24.7")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
