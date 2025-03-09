import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, check_max_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import get, copy, rmdir, save, replace_in_file, export_conandata_patches, apply_conandata_patches, mkdir, rename
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_ext": True,
    }
    options_description = {
        "build_ext": "Build the ext library, in addition to the core library.",
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        # https://github.com/SGL-UT/gnsstk/blob/v14.0.0/BuildSetup.cmake#L54
        check_min_cppstd(self, 11)
        # https://github.com/SGL-UT/gnsstk/pull/8
        check_max_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        apply_conandata_patches(self)
        # Disable examples and tests
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "core", "tests", "CMakeLists.txt"), "")
        # Disable warnings as errors
        replace_in_file(self, os.path.join(self.source_folder, "BuildSetup.cmake"),
                        "-Werror=return-type -Werror=deprecated", "")
        # Allow static library output
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        " SHARED ", " ")

    def generate(self):
        tc = CMakeToolchain(self)
        # https://github.com/SGL-UT/gnsstk/blob/v14.0.0/CMakeLists.txt#L41-L51
        tc.variables["BUILD_EXT"] = self.options.build_ext
        tc.variables["VERSIONED_HEADER_INSTALL"] = True
        tc.variables["USE_RPATH"] = False  # Adds install directory to RPATH otherwise
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license in ["LICENSE.md", "COPYING.LESSER.md", "COPYING.md"]:
            copy(self, license, dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "lib", "gnsstk.dll"),
                   os.path.join(self.package_folder, "bin", "gnsstk.dll"))

    def package_info(self):
        # https://github.com/SGL-UT/gnsstk/blob/stable/GNSSTKConfig.cmake.in
        self.cpp_info.set_property("cmake_file_name", "GNSSTk")
        self.cpp_info.set_property("cmake_target_name", "gnsstk")
        self.cpp_info.libs = ["gnsstk"]

        versioned_dir = f"gnsstk{Version(self.version).major}"
        # For compatibility with the default VERSIONED_HEADER_INSTALL=FALSE option
        self.cpp_info.includedirs.append(os.path.join("include", versioned_dir))
        # The examples use the headers without a directory prefix
        self.cpp_info.includedirs.append(os.path.join("include", versioned_dir, "gnsstk"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.settings.os != "Windows":
            self.cpp_info.defines.append("GNSSTK_STATIC_DEFINE")
        if self.options.build_ext:
            self.cpp_info.defines.append("BUILD_EXT")
