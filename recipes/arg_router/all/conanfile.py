import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class ArgRouterConan(ConanFile):
    name = "arg_router"
    license = "BSL-1.0"
    homepage = "https://github.com/cmannett85/arg_router"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ command line argument parsing and routing."
    topics = ("cpp", "command-line", "argument-parser", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _min_compilers_version(self):
        return {
            "apple-clang": "10",
            "clang": "5",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0")
        self.requires("span-lite/0.10.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._min_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["INSTALLATION_ONLY"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "arg_router")
        self.cpp_info.set_property("cmake_target_name", "arg_router::arg_router")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = ["boost::headers", "span-lite::span-lite"]
