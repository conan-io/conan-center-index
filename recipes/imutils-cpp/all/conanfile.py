from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools import files
from conan.tools import scm
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches
from conan.tools.build import check_min_cppstd

import os

required_conan_version = ">=1.50.0"

class ImutilsCppConan(ConanFile):
    name = "imutils-cpp"
    description = "This is a cpp version of popular python computer vision library imutils."
    license = "Apache-2.0"
    topics = ("opencv", "imutils", "computer vision", )
    homepage = "https://github.com/thedevmanek/imutils-cpp"
    url = "https://github.com/conan-io/conan-center-index"
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
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "15.7",
            "msvc": "19.14",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("opencv/4.5.5")
        self.requires("libcurl/7.84.0")
        self.requires("openssl/1.1.1q")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and scm.Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["CMAKE_CXX_STANDARD"] = self._minimum_cpp_standard
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        files.copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["imutils_cpp"]

        self.cpp_info.set_property("cmake_file_name", "imutils_cpp")
        self.cpp_info.set_property("cmake_target_name", "imutils_cpp::imutils_cpp")

        self.cpp_info.requires.append("opencv::opencv")
        self.cpp_info.requires.append("libcurl::libcurl")

        # TODO: Remove after Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "imutils_cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "imutils_cpp"
