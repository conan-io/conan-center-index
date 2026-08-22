import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version


class PackageConan(ConanFile):
    name = "reproc"
    description = "A cross-platform C99 process library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DaanDeMeyer/reproc"
    topics = ("process-management", "process", "cross-platform")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx": [True, False],
        "multithreaded": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
        "multithreaded": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.cxx:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.cxx:
            check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            # drain.hpp:55:43: error: ‘stream’ is not a class, namespace, or enumeration
            raise ConanInvalidConfiguration("GCC < 6 is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["REPROC++"] = self.options.cxx
        tc.variables["REPROC_MULTITHREADED"] = self.options.multithreaded
        tc.variables["REPROC_TEST"] = False
        tc.variables["REPROC_EXAMPLES"] = False
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        cmake_config_name = "reproc++" if self.options.cxx else "reproc"
        self.cpp_info.set_property("cmake_file_name", cmake_config_name)

        self.cpp_info.components["reproc_c"].set_property("pkg_config_name", "reproc")
        self.cpp_info.components["reproc_c"].set_property("cmake_target_name", "reproc")
        self.cpp_info.components["reproc_c"].libs = ["reproc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["reproc_c"].system_libs.append("rt")
            if self.options.multithreaded:
                self.cpp_info.components["reproc_c"].system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.components["reproc_c"].system_libs.append("Ws2_32")

        if self.options.cxx:
            self.cpp_info.components["reproc_cxx"].set_property("pkg_config_name", "reproc++")
            self.cpp_info.components["reproc_cxx"].set_property("cmake_target_name", "reproc++")
            self.cpp_info.components["reproc_cxx"].libs = ["reproc++"]
            self.cpp_info.components["reproc_cxx"].requires = ["reproc_c"]
