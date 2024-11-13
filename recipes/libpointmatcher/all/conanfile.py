import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibpointmatcherConan(ConanFile):
    name = "libpointmatcher"
    description = (
        "An Iterative Closest Point (ICP) library for 2D and 3D mapping in Robotics"
    )
    license = "BSD-3-Clause"
    topics = ("robotics", "lidar", "point-cloud")
    homepage = "https://github.com/ethz-asl/libpointmatcher"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        # https://github.com/norlab-ulaval/libpointmatcher/blob/1.4.3/CMakeLists.txt#L240
        return {
            "gcc": "9",
            "clang": "5",
            "apple-clang": "7",
            "msvc": "190",
            "Visual Studio": "14",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            # Only static for msvc
            del self.options.shared
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0", transitive_headers=True)
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("libnabo/1.0.7")
        self.requires("yaml-cpp/0.7.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
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
        tc.cache_variables["USE_OPEN_MP"] = self.options.with_openmp
        tc.cache_variables["USE_OPEN_CL"] = False
        tc.cache_variables["SHARED_LIBS"] = self.options.get_safe("shared")
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_EVALUATIONS"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        if not self.settings.compiler.cppstd:
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "copyright",
            src=os.path.join(self.source_folder, "debian"),
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libpointmatcher")
        self.cpp_info.set_property("pkg_config_name", "libpointmatcher")
        sufix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"pointmatcher{sufix}"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m", "rt"]
