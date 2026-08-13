import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class GivpConan(ConanFile):
    name = "givp"
    license = "MIT"
    homepage = "https://github.com/Arnime/givp"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "GRASP-ILS-VND with Path Relinking optimizer for continuous and "
        "mixed-integer black-box optimization."
    )
    topics = "optimization", "metaheuristic", "grasp", "ils", "vnd", "header-only"
    package_type = "header-library"

    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="cpp")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["GIVP_BUILD_TESTS"] = False
        toolchain.variables["GIVP_BUILD_BENCHMARKS"] = False
        toolchain.variables["GIVP_BUILD_FUZZ"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "givp")
        self.cpp_info.set_property("cmake_target_name", "givp::givp")
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
