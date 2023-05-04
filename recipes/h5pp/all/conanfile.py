from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class H5ppConan(ConanFile):
    name = "h5pp"
    description = "A C++17 wrapper for HDF5 with focus on simplicity"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DavidAce/h5pp"
    topics = ("hdf5", "binary", "storage", "header-only", "cpp17")
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "with_eigen": [True, False],
        "with_spdlog": [True, False],
    }
    default_options = {
        "with_eigen": True,
        "with_spdlog": True,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7.4",
            "Visual Studio": "15.7",
            "msvc": "191",
            "clang": "6",
            "apple-clang": "10",
        }

    def config_options(self):
        if Version(self.version) < "1.10.0":
            # These dependencies are always required before h5pp 1.10.0:
            #   * h5pp < 1.10.0 includes any version of headers indiscriminately (e.g. system headers),
            #     and can't tell if the the corresponding library will be linked. This makes the,
            #     build and /link steps non-deterministic.
            #   * h5pp >= 1.10.0 fixes the issue with H5PP_USE_<LIB> preprocessor flags, to make sure
            #     that including the headers is intentional.
            del self.options.with_eigen
            del self.options.with_spdlog

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "1.10.0":
            self.requires("hdf5/1.12.1")
        else:
            self.requires("hdf5/1.13.1")

        if Version(self.version) < "1.10.0" or self.options.get_safe('with_eigen'):
            self.requires("eigen/3.4.0")
        if Version(self.version) < "1.10.0" or self.options.get_safe('with_spdlog'):
            self.requires("spdlog/1.11.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self,**self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if Version(self.version) < "1.9.0":
            includedir = os.path.join(self.source_folder, "h5pp", "include")
        else:
            includedir = os.path.join(self.source_folder, "include")
        copy(self, "*", src=includedir, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "h5pp")
        self.cpp_info.set_property("cmake_target_name", "h5pp::h5pp")
        self.cpp_info.components["h5pp_headers"].set_property("cmake_target_name", "h5pp::headers")
        self.cpp_info.components["h5pp_deps"].set_property("cmake_target_name", "h5pp::deps")
        self.cpp_info.components["h5pp_flags"].set_property("cmake_target_name", "h5pp::flags")
        self.cpp_info.components["h5pp_deps"].requires = ["hdf5::hdf5"]

        if Version(self.version) >= "1.10.0":
            if self.options.with_eigen:
                self.cpp_info.components["h5pp_deps"].requires.append("eigen::eigen")
                self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_EIGEN3")
            if self.options.with_spdlog:
                self.cpp_info.components["h5pp_deps"].requires.append("spdlog::spdlog")
                self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_SPDLOG")
                self.cpp_info.components["h5pp_flags"].defines.append("H5PP_USE_FMT")
        else:
            self.cpp_info.components["h5pp_deps"].requires.append("eigen::eigen")
            self.cpp_info.components["h5pp_deps"].requires.append("spdlog::spdlog")

        if (self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9") or \
           (self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") in ["libstdc++", "libstdc++11"]):
            self.cpp_info.components["h5pp_flags"].system_libs = ["stdc++fs"]
        if is_msvc(self):
            self.cpp_info.components["h5pp_flags"].defines.append("NOMINMAX")
            self.cpp_info.components["h5pp_flags"].cxxflags = ["/permissive-"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "h5pp"
        self.cpp_info.names["cmake_find_package_multi"] = "h5pp"
        self.cpp_info.components["h5pp_headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["h5pp_headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["h5pp_deps"].names["cmake_find_package"] = "deps"
        self.cpp_info.components["h5pp_deps"].names["cmake_find_package_multi"] = "deps"
        self.cpp_info.components["h5pp_flags"].names["cmake_find_package"] = "flags"
        self.cpp_info.components["h5pp_flags"].names["cmake_find_package_multi"] = "flags"
