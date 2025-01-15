import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, copy, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class PyBind11Conan(ConanFile):
    name = "pybind11"
    description = "Seamless operability between C++11 and Python"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pybind/pybind11"
    topics = ("pybind11", "python", "binding", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("cpython/[~3.12]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cpython/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PYBIND11_INSTALL"] = True
        tc.variables["PYBIND11_TEST"] = False
        tc.variables["PYBIND11_CMAKECONFIG_INSTALL_DIR"] = "lib/cmake/pybind11"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        for filename in ["pybind11Targets.cmake", "pybind11Config.cmake", "pybind11ConfigVersion.cmake"]:
            rm(self, filename, os.path.join(self.package_folder, "lib", "cmake", "pybind11"))

        rmdir(self, os.path.join(self.package_folder, "share"))

        checked_target = "lto" if self.version < Version("2.11.0") else "pybind11"
        replace_in_file(self, os.path.join(self.package_folder, "lib", "cmake", "pybind11", "pybind11Common.cmake"),
                              f"if(TARGET pybind11::{checked_target})",
                              "if(FALSE)")
        replace_in_file(self, os.path.join(self.package_folder, "lib", "cmake", "pybind11", "pybind11Common.cmake"),
                              "add_library(",
                              "# add_library(")

        # Force find_package(Python) with the correct components to be re-run by pybind11
        replace_in_file(self, os.path.join(self.package_folder, "lib", "cmake", "pybind11", "pybind11NewTools.cmake"),
                        "if(NOT Python_FOUND AND NOT Python3_FOUND)",
                        "if(TRUE)")
        replace_in_file(self, os.path.join(self.package_folder, "lib", "cmake", "pybind11", "pybind11NewTools.cmake"),
                        "Python 3.", "Python3 3.")

    def package_info(self):
        cmake_base_path = os.path.join("lib", "cmake", "pybind11")
        self.cpp_info.set_property("cmake_target_name", "pybind11_all_do_not_use")
        self.cpp_info.components["headers"].includedirs = ["include"]
        self.cpp_info.components["pybind11_"].set_property("cmake_target_name", "pybind11::pybind11")
        self.cpp_info.components["pybind11_"].set_property("cmake_module_file_name", "pybind11")
        self.cpp_info.components["pybind11_"].builddirs = [cmake_base_path]
        self.cpp_info.components["pybind11_"].requires = ["headers"]
        cmake_file = os.path.join(cmake_base_path, "pybind11Common.cmake")
        self.cpp_info.set_property("cmake_build_modules", [cmake_file])
        self.cpp_info.components["embed"].requires = ["pybind11_"]
        self.cpp_info.components["module"].requires = ["pybind11_"]
        self.cpp_info.components["python_link_helper"].requires = ["pybind11_"]
        self.cpp_info.components["windows_extras"].requires = ["pybind11_"]
        self.cpp_info.components["lto"].requires = ["pybind11_"]
        self.cpp_info.components["thin_lto"].requires = ["pybind11_"]
        self.cpp_info.components["opt_size"].requires = ["pybind11_"]
        self.cpp_info.components["python2_no_register"].requires = ["pybind11_"]
