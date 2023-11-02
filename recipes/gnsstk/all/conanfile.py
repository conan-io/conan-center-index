import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import get, copy, rmdir, save, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GNSSTkConan(ConanFile):
    name = "gnsstk"
    description = (
        "The GNSSTk core library provides a number of models and algorithms found in GNSS textbooks and classic papers, "
        "such as solving for the user position or estimating atmospheric refraction. "
        "Common data formats such as RINEX are supported as well."
    )
    license = "LGPL-3.0-only", "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SGL-UT/gnsstk"
    topics = ("gnss", "gps", "rinex")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_ext": [True, False],
        "versioned_header":  [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_ext": True,
        "versioned_header": False,
    }
    options_description = {
        "build_ext": "Build the ext library, in addition to the core library.",
        "versioned_header": "Install header files into maj/min versioned directory.",
    }


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
            # https://github.com/SGL-UT/gnsstk/blob/v14.0.0/BuildSetup.cmake#L54
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # https://github.com/SGL-UT/gnsstk/blob/v14.0.0/CMakeLists.txt#L41-L51
        tc.cache_variables["BUILD_EXT"] = self.options.build_ext
        tc.cache_variables["VERSIONED_HEADER_INSTALL"] = self.options.versioned_header
        tc.cache_variables["USE_RPATH"] = False
        tc.generate()

    def _patch_sources(self):
        # Disable examples
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")
        # Disable tests
        save(self, os.path.join(self.source_folder, "core", "tests", "CMakeLists.txt"), "")
        # Disable warnings as errors
        replace_in_file(self, os.path.join(self.source_folder, "BuildSetup.cmake"),
                        "-Werror=return-type -Werror=deprecated", "")
        # Do not force shared library
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        " SHARED ", " ")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license in ["LICENSE.md", "COPYING.LESSER.md", "COPYING.md"]:
            copy(self, license, dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # https://github.com/SGL-UT/gnsstk/blob/stable/GNSSTKConfig.cmake.in
        self.cpp_info.set_property("cmake_file_name", "GNSSTk")
        self.cpp_info.set_property("cmake_target_name", "gnsstk")
        self.cpp_info.libs = ["gnsstk"]

        if self.options.versioned_header:
            versioned_dir = f"gnsstk{Version(self.version).major}"
            self.cpp_info.includedirs.append(os.path.join("include", versioned_dir))
            self.cpp_info.includedirs.append(os.path.join("include", versioned_dir, "gnsstk"))
        else:
            self.cpp_info.includedirs.append(os.path.join("include", "gnsstk"))

        if self.settings.os != "Windows":
            self.cpp_info.defines.append("GNSSTK_STATIC_DEFINE")
        if self.options.build_ext:
            self.cpp_info.defines.append("BUILD_EXT")
