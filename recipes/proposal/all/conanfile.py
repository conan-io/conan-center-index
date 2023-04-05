import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, copy
from conan.tools.cmake import CMake, CMakeToolchain
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class PROPOSALConan(ConanFile):
    name = "proposal"
    homepage = "https://github.com/tudo-astroparticlephysics/PROPOSAL"
    license = "LGPL-3.0"
    exports_sources = "CMakeLists.txt"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    description = "monte Carlo based lepton and photon propagator"
    topics = ("propagator", "lepton", "photon", "stochastic")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_python": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_python": False,
    }

    generators = "CMakeDeps"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("cubicinterpolation/0.1.4")
        #TODO: Add note why transitive_headers are necessary
        self.requires("spdlog/1.9.2", transitive_headers=True)
        self.requires("nlohmann_json/3.10.5")
        if self.options.with_python:
            self.requires("pybind11/2.9.1")

    @property
    def _minimum_compilers_version(self):
        return {"Visual Studio": "15", "gcc": "5", "clang": "5", "apple-clang": "5"}

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Can not build shared library on Visual Studio."
            )
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "14")

        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False
        )
        if not minimum_version:
            self.output.warn(
                "PROPOSAL requires C++14. Your compiler is unknown. Assuming it supports C++14."
            )
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "PROPOSAL requires gcc >= 5, clang >= 5 or Visual Studio >= 15 as a compiler!"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_PYTHON"] = self.options.with_python
        tc.cache_variables["BUILD_DOCUMENTATION"] = False
        tc.generate()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PROPOSAL")
        self.cpp_info.set_property("cmake_target_name", "PROPOSAL::PROPOSAL")
        self.cpp_info.libs = ["PROPOSAL"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "PROPOSAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PROPOSAL"
