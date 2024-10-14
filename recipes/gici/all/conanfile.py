import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GiciConan(ConanFile):
    name = "gici"
    description = ("GNSS/INS/Camera Integrated Navigation Library (GICI-LIB) is a software package "
                   "for Global Navigation Satellite System (GNSS), Inertial Navigation System (INS), "
                   "and Camera integrated navigation.")
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chichengcn/gici-open"
    topics = ("gnss", "navigation", "state-estimation", "factor-graphs", "rtk", "ppp", "ins", "visual-odometry")

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
        # For std::index_sequence in ceres
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Used in a public header in gici/imu/imu_types.h
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        # svo/common/types.h
        self.requires("opencv/4.9.0", transitive_headers=True, transitive_libs=True)
        # gici/utility/option.h
        self.requires("yaml-cpp/0.8.0", transitive_headers=True, transitive_libs=True)
        # gici/utility/option.h
        self.requires("glog/0.6.0", transitive_headers=True, transitive_libs=True)
        # gici/imu/imu_error.h
        self.requires("ceres-solver/2.1.0", transitive_headers=True, transitive_libs=True)  # 2.2.0 is not compatible

        # The vendored rtklib in the project is modified and cannot be unvendored
        # TODO: add CCI recipes and unvendor
        # libcvd
        # rpg_vikit
        # rpg_svo

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os != "Linux":
            # stream/streamer.cpp includes linux/videodev2.h
            raise ConanInvalidConfiguration(f"{self.name} only supports Linux")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        # The project does not export any CMake config or a pkg-config files.
        self.cpp_info.libs = ["gici"]
        self.cpp_info.resdirs = ["res"]

        # Vendored libs
        self.cpp_info.includedirs.append(os.path.join("include", "gici", "third_party"))
        self.cpp_info.libs.extend(["rtklib", "vikit_common", "svo", "fast"])

        # Unofficial, for convenience
        self.runenv_info.define_path("GICI_DATA", os.path.join(self.package_folder, "res"))
