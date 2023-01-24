from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"

class FruitConan(ConanFile):
    name = "fruit"
    description = "C++ dependency injection framework"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/fruit"
    topics = ("injection", "dependency", "DI")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "use_boost": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "use_boost": True,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if self.options.use_boost:
            self.tool_requires("boost/1.81.0")

    @property
    def _extracted_dir(self):
        return self.name + "-" + self.version

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FRUIT_USES_BOOST"] = self.options.use_boost
        tc.variables["FRUIT_ENABLE_COVERAGE"] = False
        tc.variables["RUN_TESTS_UNDER_VALGRIND"] = False
        tc.variables["FRUIT_ENABLE_CLANG_TIDY"] = False
        tc.generate()

        venv = VirtualBuildEnv(self)
        venv.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fruit"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
