from os import path
import posixpath
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import (
    apply_conandata_patches, export_conandata_patches,
    get, copy, rename, rm, rmdir
    )
from conan.tools.scm import Version
from conan.tools.env import VirtualRunEnv
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

required_conan_version = ">=1.53.0"


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
        "with_fmus": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmi1/1.0.1")
        self.requires("fmi2/2.0.4")
        if self.version >= Version("3.0a2"):
            self.requires("fmi3/3.0.1")
        self.requires("expat/2.5.0")
        self.requires("minizip/1.2.13")
        self.requires("zlib/[>=1.2.11 <2]")
        # c99_snprintf -> should be externalised

    def validate(self):
        # https://github.com/modelon-community/fmi-library/issues/93
        if self.settings.arch not in ["x86", "x86_64"] and Version(self.version).major < 3:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support architecture "
                f"'{self.settings.arch}' on {self.settings.os}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):

        tc = CMakeToolchain(self)
        tc.variables["FMILIB_BUILD_STATIC_LIB"] = not self.options.shared
        tc.variables["FMILIB_BUILD_SHARED_LIB"] = self.options.shared
        tc.variables["FMILIB_BUILD_TESTS"] = self.options.with_fmus
        tc.variables["FMILIB_FMI_STANDARD_HEADERS"] = posixpath.join(self.build_folder, "fmis").replace("\\", "/")
        tc.variables["FMILIB_GENERATE_DOXYGEN_DOC"] = False

        # The variable is an option only if the following condition is true
        if not self.options.shared and not self.settings.os in ["Windows", "Macos"]:
            tc.variables["FMILIB_BUILD_FOR_SHARED_LIBS"] = self.options.get_safe("fPIC", False)

        if is_msvc(self):
            tc.variables["FMILIB_BUILD_WITH_STATIC_RTLIB"] = is_msvc_static_runtime(self)

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0026"] = "OLD"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0045"] = "OLD"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0046"] = "OLD"

        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

        vre = VirtualRunEnv(self)
        vre.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)

        # Rename c++ suffix to c to avoid CMake's confusion
        fmi2_folder = path.join(self.source_folder, "Test", "FMI2")
        rename(self, path.join(fmi2_folder, "fmi2_import_xml_test.cc"),
               path.join(fmi2_folder, "fmi2_import_xml_test.c"))

        copy(self, "fmiModel*.h", self.dependencies["fmi1"].cpp_info.components["modex"].includedirs[0],
             path.join(self.build_folder, "fmis", "FMI1"))
        copy(self, "fmiPlatformTypes.h", self.dependencies["fmi1"].cpp_info.components["cosim"].includedirs[0],
             path.join(self.build_folder, "fmis", "FMI1"))
        copy(self, "fmiFunctions.h", self.dependencies["fmi1"].cpp_info.components["cosim"].includedirs[0],
             path.join(self.build_folder, "fmis", "FMI1"))
        copy(self, "*.h", self.dependencies["fmi2"].cpp_info.includedirs[0],
             path.join(self.build_folder, "fmis", "FMI2"))

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, pattern="FMILIB_Acknowledgements.txt",
             dst=path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, pattern="*.fmu", dst=path.join(self.package_folder, "res", "fmus"),
             src=path.join(self.build_folder, "Testing"), keep_path=False)

        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="*.dll", dst=path.join(self.package_folder, "bin"),
             src=path.join(self.package_folder, "lib"), keep_path=False)
        rm(self, "*.dll", path.join(self.package_folder, "lib"))

        fix_apple_shared_install_name(self)

        rmdir(self, path.join(self.package_folder, "doc"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["fmilib_shared"]
        else:
            self.cpp_info.libs = ["fmilib"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

        if self.settings.os in ["Windows"]:
            self.cpp_info.system_libs.append("shlwapi")

        self.cpp_info.resdirs = ["res"]
        self.cpp_info.set_property("cmake_target_aliases", ["fmilibrary::fmilibrary"])
