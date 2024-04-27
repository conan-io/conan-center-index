from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version

import os

required_conan_version = ">=1.59.0"


class fastgltf(ConanFile):
    name = "fastgltf"
    description = "A modern C++17 glTF 2.0 library focused on speed, correctness, and usability"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/spnda/fastgltf"
    topics = ("gltf", "simd", "cpp17")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_small_vector": [True, False],
        "disable_custom_memory_pool": [True, False],
        "use_64bit_float": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_small_vector": False,
        "disable_custom_memory_pool": False,
        "use_64bit_float": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if Version(self.version) <= "0.6.0":
            del self.options.disable_custom_memory_pool
            del self.options.use_64bit_float

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder='src')

    def requirements(self):
        self.requires("simdjson/3.2.0")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
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
        if Version(self.version) <= "0.7.0":
            tc.variables["FASTGLTF_DOWNLOAD_SIMDJSON"] = False
        if self.options.enable_small_vector:
            tc.variables["FASTGLTF_USE_CUSTOM_SMALLVECTOR"] = True
        if self.options.get_safe("disable_custom_memory_pool"):
            tc.variables["FASTGLTF_DISABLE_CUSTOM_MEMORY_POOL"] = True
        if self.options.get_safe("use_64bit_float"):
            tc.variables["FASTGLTF_USE_64BIT_FLOAT"] = True
        if Version(self.version) >= "0.7.0":
            tc.variables["FASTGLTF_COMPILE_AS_CPP20"] = "20" in str(self.settings.get_safe("compiler.cppstd"))
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["fastgltf"]
        if "20" in str(self.settings.get_safe("compiler.cppstd")):
            self.cpp_info.defines.append("FASTGLTF_CPP_20")
