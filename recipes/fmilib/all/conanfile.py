from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches,
    get, rm, rmdir
    )
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import posixpath

required_conan_version = ">=2.0.9"


class PackageConan(ConanFile):
    name = "fmilib"
    description = "C library for importing FMUs"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/modelon-community/fmi-library"
    topics = ("fmi", "fmi-standard", "fmu")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fmus": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_fmus": False
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmi1/1.0.1")
        self.requires("fmi2/2.0.4")
        self.requires("fmi3/3.0.1")
        self.requires("expat/2.7.3")
        self.requires("minizip/[>1.2.13 <2]")
        self.requires("zlib/[>1.2.13 <2]")

    def build_requirements(self):
        if self.options.with_fmus:
            self.test_requires("catch2/2.13.8")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FMILIB_EXTERNAL_LIBS"] = True
        tc.variables["FMILIB_BUILD_STATIC_LIB"] = not self.options.shared
        tc.variables["FMILIB_BUILD_SHARED_LIB"] = self.options.shared
        tc.variables["FMILIB_BUILD_TESTS"] = self.options.with_fmus
        tc.variables["FMILIB_FMI_STANDARD_HEADERS"] = posixpath.join(self.source_folder, "src", "fmis").replace("\\", "/")
        tc.variables["FMILIB_GENERATE_DOXYGEN_DOC"] = False

        if not self.options.shared and not self.settings.os in ["Windows", "Macos"]:
            tc.variables["FMILIB_BUILD_FOR_SHARED_LIBS"] = self.options.get_safe("fPIC", False)

        if is_msvc(self):
            tc.variables["FMILIB_BUILD_WITH_STATIC_RTLIB"] = is_msvc_static_runtime(self)

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("minizip", "cmake_file_name", "MiniZip")
        deps.set_property("zlib", "cmake_file_name", "ZLIB")

        deps.set_property("expat", "cmake_target_name", "expat")
        deps.set_property("minizip", "cmake_target_name", "minizip")
        deps.set_property("zlib", "cmake_target_name", "zlib")
        deps.generate()

        # This is needed if with_fmus=True
        vre = VirtualRunEnv(self)
        vre.generate(scope="build")

    def build(self):
        copy(self, "fmiModel*.h", self.dependencies["fmi1"].cpp_info.components["modex"].includedirs[0],
             os.path.join(self.source_folder, "src", "fmis", "FMI1"))
        copy(self, "fmiPlatformTypes.h", self.dependencies["fmi1"].cpp_info.components["cosim"].includedirs[0],
             os.path.join(self.source_folder, "src", "fmis", "FMI1"))
        copy(self, "fmiFunctions.h", self.dependencies["fmi1"].cpp_info.components["cosim"].includedirs[0],
             os.path.join(self.source_folder, "src", "fmis", "FMI1"))
        copy(self, "*.h", self.dependencies["fmi2"].cpp_info.includedirs[0],
             os.path.join(self.source_folder, "src", "fmis", "FMI2"))
        copy(self, "*.h", self.dependencies["fmi3"].cpp_info.includedirs[0],
             os.path.join(self.source_folder, "src", "fmis", "FMI3"))

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="FMILIB_Acknowledgements.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, pattern="*.fmu", dst=os.path.join(self.package_folder, "res", "fmus"),
             src=os.path.join(self.build_folder, "Testing"), keep_path=False)

        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.package_folder, "lib"), keep_path=False)
        rm(self, "*.dll", os.path.join(self.package_folder, "lib"))

        fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self.package_folder, "doc"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["fmilib_shared"]
        else:
            self.cpp_info.libs = ["fmilib"]

        self.cpp_info.resdirs = ["res"]
        self.cpp_info.set_property("cmake_target_aliases", ["fmilibrary::fmilibrary"])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

        if self.settings.os in ["Windows"]:
            self.cpp_info.system_libs.append("shlwapi")
