from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class UnleashConan(ConanFile):
    name = "unleash-client-cpp"
    description = "Unleash Client SDK for C++ projects."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aruizs/unleash-client-cpp/"
    topics = ("unleash", "feature", "flag", "toggle")
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
        return "17"

    @property
    def _compilers_min_version(self):
        return {
            "Visual Studio": "15",  # Should we check toolset?
            "msvc": "191",
            "gcc": "7",
            "clang": "4.0",
            "apple-clang": "3.8",
            "intel": "17",
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
        self.requires("cpr/1.10.5")
        self.requires("nlohmann_json/3.11.3")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        min_version = self._compilers_min_version.get(str(self.settings.compiler), False)
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["ENABLE_TESTING_COVERAGE"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["unleash"]
        self.cpp_info.set_property("cmake_file_name", "unleash")
        self.cpp_info.set_property("cmake_target_name", "unleash::unleash")
