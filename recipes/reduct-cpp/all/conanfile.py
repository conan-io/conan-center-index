from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"

class ReductCPPConan(ConanFile):
    name = "reduct-cpp"
    description = "ReductStore Client SDK for C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/reductstore/reduct-cpp"
    topics = ("reductstore", "sdk", "http-client")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_std_chrono": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_std_chrono": False,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11.2",
            # spaceship operator(<=>) in std lib has been supported since clang 14
            "clang": "14",
            # spaceship operator(<=>) in std lib has been supported since apple-clang 14
            "apple-clang": "14",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        self.requires("fmt/11.0.2")
        self.requires("cpp-httplib/0.18.0")
        self.requires("nlohmann_json/3.11.3")
        self.requires("concurrentqueue/1.0.4")
        if not self.options.with_std_chrono:
            self.requires("date/3.0.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        # date::parse doesn't work well in gcc 14 or later due to C++20 std::chrono features.
        # with_std_chrono = True solves this problem.
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) >= "14" and not self.options.with_std_chrono:
            raise ConanInvalidConfiguration("gcc >= 14 requires option with_std_chrono=True")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["REDUCT_CPP_USE_STD_CHRONO"] = self.options.with_std_chrono
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        venv = VirtualBuildEnv(self)
        venv.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["reductcpp"]
