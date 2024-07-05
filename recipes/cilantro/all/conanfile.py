import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CilantroConan(ConanFile):
    name = "cilantro"
    description = "A lean C++ library for working with point cloud data"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "github.com/kzampog/cilantro"
    topics = ("point-cloud", "3d", "clustering", "registration", "segmentation", "convex-hull", "3d-reconstruction",
              "ransac", "visualization", "iterative-closest-point", "spectral-clustering", "model-fitting")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "march_native": [True, False],
        "non_deterministic_parallelism": [True, False],
        "with_openmp": [True, False],
        "with_pangolin": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "march_native": False,
        "non_deterministic_parallelism": True,
        "with_openmp": False,  # TODO: enabled after #22353 is merged
        "with_pangolin": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "6",
            "gcc": "7",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["qhull/*"].reentrant = True
        # self.options["qhull/*"].cpp = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("spectra/1.0.1", transitive_headers=True, transitive_libs=True)
        self.requires("nanoflann/1.5.2", transitive_headers=True, transitive_libs=True)
        self.requires("tinyply/2.3.4", transitive_headers=True, transitive_libs=True)
        # TODO: qhullcpp component is not available on CCI
        # https://github.com/conan-io/conan-center-index/issues/16321
        # Using a vendored version of qhullcpp in the meantime
        self.requires("qhull/8.0.1", transitive_headers=True, transitive_libs=True)
        if self.options.with_openmp:
            # '#pragma omp' is used in public headers
            self.requires("llvm-openmp/18.1.8", transitive_headers=True, transitive_libs=True)
        if self.options.with_pangolin:
            self.requires("pangolin/0.9.1", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if not self.dependencies["qhull"].options.reentrant:
            raise ConanInvalidConfiguration("-o qhull:reentrant=True is required")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["ENABLE_NATIVE_BUILD_OPTIMIZATIONS"] = self.options.march_native
        tc.variables["ENABLE_NON_DETERMINISTIC_PARALLELISM"] = self.options.non_deterministic_parallelism
        tc.variables["CMAKE_PROJECT_cilantro_INCLUDE"] = "conan_deps.cmake"
        tc.variables["CMAKE_OpenMP_FIND_REQUIRED"] = self.options.with_openmp
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_OpenMP"] = not self.options.with_openmp
        tc.variables["CMAKE_Pangolin_FIND_REQUIRED"] = self.options.with_pangolin
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Pangolin"] = not self.options.with_pangolin
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't embed absolute RPATHs in the shared library
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set_target_properties(${PROJECT_NAME} PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)",
                        'set_target_properties(${PROJECT_NAME} PROPERTIES INSTALL_RPATH "$ORIGIN")')
        # Unvendor 3rd-party dependencies
        for pkg in ["Spectra", "nanoflann", "tinyply", "libqhull_r"]:
            rmdir(self, os.path.join(self.source_folder, "include", "cilantro", "3rd_party", pkg))
        for pkg in ["tinyply", "libqhull_r"]:
            rmdir(self, os.path.join(self.source_folder, "src", "3rd_party", pkg))

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
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cilantro")
        self.cpp_info.set_property("cmake_target_name", "cilantro")
        self.cpp_info.libs = ["cilantro"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
