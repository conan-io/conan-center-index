import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version


required_conan_version = ">=2.20"


class UnicodeRangesConan(ConanFile):
    name = "unicode-ranges"
    description = "C++23 validated UTF-8, UTF-16, and UTF-32 text types and algorithms"
    license = "MIT OR Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cristi1990an/unicode_ranges"
    topics = ("unicode", "utf-8", "utf-16", "utf-32", "text")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_icu": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_icu": False,
    }
    options_description = {
        "with_icu": "Enable ICU-backed locale-aware casing",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_icu:
            self.requires("icu/78.2")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <5]")

    def validate(self):
        check_min_cppstd(self, 23)

        minimum_versions = {
            "gcc": "14",
            "clang": "22",
            "msvc": "195",
        }
        compiler = str(self.settings.compiler)
        minimum = minimum_versions.get(compiler)
        if minimum and Version(self.settings.compiler.version) < minimum:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {compiler} {minimum} or newer"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        dependencies = CMakeDeps(self)
        dependencies.generate()

        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["UTF8_RANGES_BUILD_TESTS"] = False
        toolchain.cache_variables["UTF8_RANGES_BUILD_BENCHMARKS"] = False
        toolchain.cache_variables["UTF8_RANGES_ENABLE_ICU"] = bool(
            self.options.with_icu
        )
        toolchain.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        if self.options.get_safe("fPIC") is not None:
            toolchain.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(
                self.options.fPIC
            )
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "THIRD_PARTY_NOTICES.md",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "unicode_ranges")
        self.cpp_info.set_property(
            "cmake_target_name", "unicode_ranges::unicode_ranges"
        )
        self.cpp_info.libs = ["unicode_ranges"]
        self.cpp_info.bindirs = []

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")

        if self.options.with_icu:
            self.cpp_info.defines.append("UTF8_RANGES_ENABLE_ICU=1")
            self.cpp_info.requires.extend(("icu::icu-uc", "icu::icu-i18n"))
