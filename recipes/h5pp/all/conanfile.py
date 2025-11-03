from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.files import get
from conan.tools.files import copy
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"

class H5ppConan(ConanFile):
    name = "h5pp"
    description = "A C++17 wrapper for HDF5 with focus on simplicity"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DavidAce/h5pp"
    topics = ("hdf5", "binary", "storage", "header-only", "cpp17")
    license = "MIT"
    package_type="header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_eigen": [True, False],
        "with_spdlog": [True, False],
        "with_zlib" : [True, False],
        "with_quadmath": [True, False]
    }
    default_options = {
        "with_eigen": True,
        "with_spdlog": True,
        "with_zlib" : True,
        "with_quadmath": False
    }

    def requirements(self):
        self.requires("hdf5/[>=1.14.3 <1.15]")
        if self.options.with_eigen:
            self.requires("eigen/[>=3.4.0 <=5.0.0]")
        if self.options.with_spdlog:
            self.requires("spdlog/[>=1.13.0 <2]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.3 <2]")

    def layout(self):
        basic_layout(self,src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.with_zlib and not self.dependencies['hdf5'].options.with_zlib:
            raise ConanInvalidConfiguration("h5pp requires hdf5 to be built with zlib support")

    def source(self):
        get(self,**self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def package(self):
        includedir = os.path.join(self.source_folder, "include")
        copy(self, pattern="*", src=includedir, dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "h5pp")
        self.cpp_info.set_property("cmake_target_name", "h5pp::h5pp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.components["h5pp_headers"].set_property("cmake_target_name", "h5pp::headers")
        self.cpp_info.components["h5pp_headers"].bindirs = []
        self.cpp_info.components["h5pp_headers"].libdirs = []
        self.cpp_info.components["h5pp_deps"].set_property("cmake_target_name", "h5pp::deps")
        self.cpp_info.components["h5pp_deps"].bindirs = []
        self.cpp_info.components["h5pp_deps"].libdirs = []
        self.cpp_info.components["h5pp_deps"].requires = ["hdf5::hdf5"]
        self.cpp_info.components["h5pp_flags"].set_property("cmake_target_name", "h5pp::flags")
        self.cpp_info.components["h5pp_flags"].bindirs = []
        self.cpp_info.components["h5pp_flags"].libdirs = []

        if self.options.with_eigen:
            self.cpp_info.components["h5pp_deps"].requires.append("eigen::eigen")
            self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_EIGEN3")
        if self.options.with_spdlog:
            self.cpp_info.components["h5pp_deps"].requires.append("spdlog::spdlog")
            self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_SPDLOG")
            self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_FMT")
        if self.options.with_zlib:
            self.cpp_info.components["h5pp_deps"].requires.append("zlib::zlib")
        if self.options.with_quadmath:
            self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_FLOAT128")
            self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_QUADMATH")
            self.cpp_info.system_libs.append('quadmath')

        if (self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9") or \
           (self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") in ["libstdc++", "libstdc++11"]):
            self.cpp_info.components["h5pp_flags"].system_libs = ["stdc++fs"]
        if is_msvc(self):
            self.cpp_info.components["h5pp_flags"].defines.append("NOMINMAX")
            self.cpp_info.components["h5pp_flags"].cxxflags = ["/permissive-"]

