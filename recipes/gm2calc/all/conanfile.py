import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class Gm2calcConan(ConanFile):
    name = "gm2calc"
    description = "C++ library to calculate the anomalous magnetic moment of the muon in the MSSM and 2HDM"
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GM2Calc/GM2Calc"
    topics = ("high-energy", "physics", "hep", "magnetic moment", "muon", "mssm", "2hdm")

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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0")
        self.requires("eigen/3.4.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "2.2.0":
            replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "EIGEN3", "Eigen3")
        # Fix src/slhaea.h:25:10: fatal error: boost/algorithm/string/classification.hpp: No such file or directory
        save(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
             "\ninclude_directories(${Boost_INCLUDE_DIRS})", append=True)
        # Disable examples, test and doc
        for subdir in ["examples", "test", "doc"]:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), f"add_subdirectory({subdir})", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GM2Calc")
        self.cpp_info.set_property("cmake_target_name", "GM2Calc::GM2Calc")
        self.cpp_info.set_property("pkg_config_name", "gm2calc")
        self.cpp_info.libs = ["gm2calc"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GM2Calc"
        self.cpp_info.names["cmake_find_package_multi"] = "GM2Calc"
