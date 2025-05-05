import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, \
    save, mkdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OpenvrConan(ConanFile):
    name = "openvr"
    description = (
        "API and runtime that allows access to VR hardware from applications "
        "have specific knowledge of the hardware they are targeting."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/openvr"
    topics = ("vr", "virtual reality")

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
        self.requires("jsoncpp/1.9.5", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                f"OpenVR can't be compiled by {self.settings.compiler} {self.settings.compiler.version}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED"] = self.options.shared
        tc.cache_variables["BUILD_UNIVERSAL"] = False
        # Let Conan handle the stdlib setting, even if we are using libc++
        tc.cache_variables["USE_LIBCXX"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Honor fPIC=False
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-fPIC", "")
        # Unvendor jsoncpp
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "jsoncpp.cpp", "")
        rmdir(self, os.path.join(self.source_folder, "src", "json"))
        # Add jsoncpp dependency from Conan
        save(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
             "find_package(jsoncpp REQUIRED CONFIG)\n"
             "target_link_libraries(${LIBNAME} JsonCpp::JsonCpp)",
             append=True)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _lib_name(self):
        if self.settings.os == "Windows" and self.settings.arch == "x86_64":
            return "openvr_api64"
        return "openvr_api"

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            os.rename(os.path.join(self.package_folder, "lib", f"{self._lib_name}.dll"),
                      os.path.join(self.package_folder, "bin", f"{self._lib_name}.dll"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "openvr")
        self.cpp_info.libs = [self._lib_name]
        self.cpp_info.includedirs.append(os.path.join("include", "openvr"))

        if not self.options.shared:
            self.cpp_info.defines.append("OPENVR_BUILD_STATIC")
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["Foundation", "CoreFoundation"])
