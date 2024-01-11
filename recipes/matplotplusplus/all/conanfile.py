import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout, CMake
from conan.tools.files import copy, get, rmdir, rm, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class MatplotplusplusCppConan(ConanFile):
    name = "matplotplusplus"
    description = "Matplot++: A C++ Graphics Library for Data Visualization"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alandefreitas/matplotplusplus"
    topics = ("visualization", "charts", "data-science", "charting-library", "plots", "graphics", "graphs",
              "data-visualization", "scientific-visualization", "scientific-computing", "data-analysis",
              "graphics-library", "matplot", "plot-categories", "contour-plots", "polar-plots")

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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cimg/3.3.2")
        self.requires("nodesoup/cci.20200905")
        self.requires("opengl/system")
        self.requires("glfw/3.3.8")
        # TODO: unvendor glad/0.1.36
        # Matplot++ also requires gnuplot to run, which is not available on CCI

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MATPLOTPP_BUILD_EXAMPLES"] = False
        tc.variables["MATPLOTPP_BUILD_TESTS"] = False
        tc.variables["MATPLOTPP_BUILD_INSTALLER"] = True
        tc.variables["MATPLOTPP_BUILD_PACKAGE"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("cimg", "cmake_target_name", "cimg")
        deps.set_property("nodesoup", "cmake_target_name", "nodesoup")
        deps.generate()

    def _patch_sources(self):
        rmdir(self, os.path.join(self.source_folder, "source", "3rd_party"))
        save(self, os.path.join(self.source_folder, "source", "3rd_party", "CMakeLists.txt"),
             "find_package(CImg REQUIRED CONFIG GLOBAL)\n"
             "find_package(nodesoup REQUIRED CONFIG GLOBAL)\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Matplot++")
        self.cpp_info.set_property("cmake_target_name", "Matplot++::matplot++")

        self.cpp_info.libs = ["matplot"]
        if self.settings.os == "Windows":
            self.cpp_info.defines.append("NOMINMAX")
