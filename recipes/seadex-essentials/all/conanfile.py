from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.59"

class SeadexEssentialsConan(ConanFile):
    name = "seadex-essentials"
    description = "essentials is a small c++ library that offers very basic capabilities for applications and libraries."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://essentials.seadex.de/"
    topics = ("utility", "C++", "library")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "spdlog/*:header_only": True
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.shared = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9.1":
            self.options["libstdc++"].cxx_abi = "11"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("spdlog/1.11.0")
        self.requires("fmt/9.1.0")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9.1":
            self.requires("libstdc++/11.1.0")
        elif self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "9.0":
            self.requires("libc++/12.0.1")
            self.requires("libc++fs/12.0.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.shared:
            tc.variables["BUILD_SHARED_LIBS"] = "ON"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses") )
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["essentials"]
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9.1":
            self.cpp_info.system_libs.append("stdc++fs")
        elif self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "9.0":
            self.cpp_info.system_libs.append("c++fs")
