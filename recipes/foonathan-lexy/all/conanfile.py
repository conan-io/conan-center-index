from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, save, mkdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class FoonathanLexyConan(ConanFile):
    name = "foonathan-lexy"
    description = "lexy is a parser combinator library for C++17 and onwards."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foonathan/lexy"
    topics = ("parser", "parser-combinators", "grammar")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LEXY_BUILD_EXAMPLES"] = False
        tc.variables["LEXY_BUILD_TESTS"] = False
        tc.variables["LEXY_BUILD_PACKAGE"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        file_content = """
# Copyright (C) 2020-2022 Jonathan Müller and lexy contributors
# SPDX-License-Identifier: BSL-1.0

# lexy CMake configuration file.

@PACKAGE_INIT@

include ("${CMAKE_CURRENT_LIST_DIR}/@PROJECT_NAME@Targets.cmake")"""
        save(self, os.path.join(self.source_folder, "cmake", "lexyConfig.cmake.in"), file_content)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "lexy")
        self.cpp_info.set_property("cmake_target_name", "foonathan::lexy")

        self.cpp_info.components["lexy_core"].set_property("cmake_target_name", "foonathan::lexy::lexy_core")

        self.cpp_info.components["lexy_file"].set_property("cmake_target_name", "foonathan::lexy::lexy_file")
        self.cpp_info.components["lexy_file"].libs = ["lexy_file"]

        self.cpp_info.components["lexy_unicode"].set_property("cmake_target_name", "lexy::lexy_unicode")
        self.cpp_info.components["lexy_unicode"].defines.append("LEXY_HAS_UNICODE_DATABASE=1")

        self.cpp_info.components["lexy_ext"].set_property("cmake_target_name", "lexy::lexy_ext")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "lexy"
        self.cpp_info.filenames["cmake_find_package_multi"] = "lexy"
        self.cpp_info.names["cmake_find_package"] = "foonathan"
        self.cpp_info.names["cmake_find_package_multi"] = "foonathan"
        self.cpp_info.components["foonathan"].names["cmake_find_package"] = "lexy"
        self.cpp_info.components["foonathan"].names["cmake_find_package_multi"] = "lexy"