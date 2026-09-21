from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os


required_conan_version = ">=2.1"


class KokkosConan(ConanFile):
    name = "kokkos"
    description = "C++ performance portability programming model for parallel execution and memory abstraction"
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://kokkos.org/"
    topics = ("high-performance-computing", "parallel-computing", "programming-model")
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
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["Kokkos_ENABLE_TESTS"] = False
        tc.cache_variables["Kokkos_ENABLE_EXAMPLES"] = False
        tc.cache_variables["Kokkos_ENABLE_BENCHMARKS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Kokkos")

        self.cpp_info.components["kokkoscore"].set_property("cmake_target_name", "Kokkos::kokkoscore")
        self.cpp_info.components["kokkoscore"].libs = ["kokkoscore"]
        self.cpp_info.components["kokkoscore"].defines.append("KOKKOS_DEPENDENCE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["kokkoscore"].system_libs.extend(["dl", "pthread"])

        self.cpp_info.components["kokkoscontainers"].set_property("cmake_target_name", "Kokkos::kokkoscontainers")
        self.cpp_info.components["kokkoscontainers"].libs = ["kokkoscontainers"]
        self.cpp_info.components["kokkoscontainers"].requires = ["kokkoscore"]

        self.cpp_info.components["kokkosalgorithms"].set_property("cmake_target_name", "Kokkos::kokkosalgorithms")
        self.cpp_info.components["kokkosalgorithms"].libs = ["kokkosalgorithms"]
        self.cpp_info.components["kokkosalgorithms"].requires = ["kokkoscore"]

        self.cpp_info.components["kokkossimd"].set_property("cmake_target_name", "Kokkos::kokkossimd")
        self.cpp_info.components["kokkossimd"].libs = ["kokkossimd"]
        self.cpp_info.components["kokkossimd"].requires = ["kokkoscore"]

        self.cpp_info.components["kokkos"].includedirs = []
        self.cpp_info.components["kokkos"].libdirs = []
        self.cpp_info.components["kokkos"].set_property("cmake_target_name", "Kokkos::kokkos")
        self.cpp_info.components["kokkos"].set_property("cmake_target_aliases", ["Kokkos::all_libs"])
        self.cpp_info.components["kokkos"].requires = ["kokkoscore", "kokkoscontainers", "kokkosalgorithms", "kokkossimd"]
