from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.53.0"


class FiberTaskingLibConan(ConanFile):
    name = "fibertaskinglib"
    description = "enabling task-based multi-threading. It allows execution of task graphs with arbitrary dependencies."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RichieSams/FiberTaskingLib"
    topics = ("coroutine", "fiber", "task-scheduler")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_cpp17": [True, False],
    }
    default_options = {
        "with_cpp17": False,
    }

    @property
    def _min_cppstd(self):
        return "17" if self.options.with_cpp17 else "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "12",
                "Visual Studio": "16",
                "msvc": "192",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FTL_BUILD_TESTS"] = False
        tc.variables["FTL_BUILD_BENCHMARKS"] = False
        tc.variables["FTL_BUILD_EXAMPLES"] = False
        tc.variables["FTL_CPP_17"] = self.options.with_cpp17
        tc.generate()
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

    def package_info(self):
        self.cpp_info.libs = ["ftl", "boost_context"]

        self.cpp_info.set_property("cmake_file_name", "FiberTaskingLib")
        self.cpp_info.set_property("cmake_target_name", "FiberTaskingLib::FiberTaskingLib")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
