from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, download
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class IridescenceConan(ConanFile):
    name = "small_gicp"
    description = "Efficient and parallelized algorithms for point cloud registration"
    license = "MIT AND BSD" # BSD is from nanoflann
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/koide3/small_gicp"
    topics = ("point-cloud", "icp", "registration", "scan-matching", "pcl")

    package_type = "library" # TODO: could add a header_only option as well
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tbb": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tbb": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
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
        self.requires("eigen/3.4.0", transitive_headers=True)
        if not is_msvc(self):
            # '#pragma omp' is used in public headers
            self.requires("llvm-openmp/17.0.6", transitive_headers=True, transitive_libs=True)
        if self.options.with_tbb:
            self.requires("onetbb/2021.10.0", transitive_headers=True, transitive_libs=True)
        # The project vendors nanoflann, but it has been heavily extended and should be kept intact

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        download(self, "https://github.com/jlblancoc/nanoflann/blob/568ae53f5fcd82d5398bb1b32144fa22028518d5/COPYING", "LICENSE.nanoflann")
        download(self, "https://github.com/strasdat/Sophus/blob/593db47500ea1a2de5f0e6579c86147991509c59/LICENSE.txt", "LICENSE.sophus")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_HELPER"] = True
        tc.variables["BUILD_WITH_OPENMP"] = True
        tc.variables["BUILD_WITH_TBB"] = self.options.with_tbb
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.nanoflann", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.sophus", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    @property
    def _openmp_flags(self):
        # Based on https://github.com/Kitware/CMake/blob/v3.28.1/Modules/FindOpenMP.cmake#L104-L135
        if self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            return ["-Qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]
        if is_msvc(self):
            return ["-openmp"]
        return None

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "small_gicp")
        self.cpp_info.set_property("cmake_target_name", "small_gicp::small_gicp")

        self.cpp_info.libs = ["small_gicp"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: drop after https://github.com/conan-io/conan-center-index/pull/22353 is merged
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "rt"])
        self.cpp_info.cflags = self._openmp_flags
        self.cpp_info.cxxflags = self._openmp_flags
