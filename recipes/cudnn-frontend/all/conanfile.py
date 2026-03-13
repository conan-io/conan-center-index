import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class CuDNNFrontendConan(ConanFile):
    name = "cudnn-frontend"
    description = "cuDNN FE: the modern, open-source entry point to the NVIDIA cuDNN"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/cudnn-frontend"
    topics = ("linear-algebra", "gpu", "cuda", "deep-learning", "nvidia", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "7",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

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


    def requirements(self):
        self.requires("nlohmann_json/[>=3.11 <3.13]", transitive_headers=True)
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # Install via CMake to ensure headers are configured correctly
        tc = CMakeToolchain(self)
        tc.cache_variables["CUDNN_FRONTEND_SKIP_JSON_LIB"] = True
        tc.cache_variables["CUDNN_FRONTEND_BUILD_SAMPLES"] = False
        tc.cache_variables["CUDNN_FRONTEND_BUILD_TESTS"] = False
        tc.cache_variables["CUDNN_FRONTEND_BUILD_PYTHON_BINDINGS"] = False
        tc.generate()
        VirtualBuildEnv(self).generate()
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NvidiaCuDNNFrontend")
        self.cpp_info.set_property("cmake_target_name", "nvidia::cudnn-frontend::cudnn-frontend")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
