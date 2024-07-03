import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir

required_conan_version = ">=1.53.0"


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
        if self.options.cxx and self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["REPROC++"] = self.options.cxx
        tc.variables["REPROC_MULTITHREADED"] = self.options.multithreaded
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
        # The C++ component should have its separate reproc++-config.cmake file,
        # but it's currently not supported by Conan
        self.cpp_info.set_property("cmake_file_name", "reproc")

        self.cpp_info.components["reproc_c"].set_property("pkg_config_name", "reproc")
        self.cpp_info.components["reproc_c"].set_property("cmake_target_name", "reproc")
        self.cpp_info.components["reproc_c"].libs = ["reproc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["reproc_c"].system_libs.append("rt")
            if self.options.multithreaded:
                self.cpp_info.components["reproc_c"].system_libs.append("pthread")

        self.cpp_info.components["reproc_cxx"].set_property("pkg_config_name", "reproc++")
        self.cpp_info.components["reproc_cxx"].set_property("cmake_target_name", "reproc++")
        self.cpp_info.components["reproc_cxx"].libs = ["reproc++"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["reproc_cxx"].system_libs.append("rt")
            if self.options.multithreaded:
                self.cpp_info.components["reproc_cxx"].system_libs.append("pthread")
