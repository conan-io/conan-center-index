from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class EastlConan(ConanFile):
    name = "eastl"
    description = "EASTL stands for Electronic Arts Standard Template Library. " \
                  "It is an extensive and robust implementation that has an " \
                  "emphasis on high performance."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EASTL"
    topics = ("stl", "high-performance")
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
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "msvc": "190",
            "gcc": "5",
            "clang": "3.2",
            "apple-clang": "4.3",
        }

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

    def requirements(self):
        self.requires("eabase/2.09.06", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        mininum_compiler_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if mininum_compiler_version and Version(self.settings.compiler.version) < mininum_compiler_version:
            raise ConanInvalidConfiguration(f"Compiler is too old for c++ {self._min_cppstd}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EASTL_BUILD_BENCHMARK"] = False
        tc.variables["EASTL_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="3RDPARTYLICENSES.TXT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["EASTL"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("EA_DLL")
