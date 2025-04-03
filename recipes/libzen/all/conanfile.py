from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class LibzenConan(ConanFile):
    name = "libzen"
    license = "ZLIB"
    homepage = "https://github.com/MediaArea/ZenLib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Small C++ derivate classes to have an easier life"
    topics = ("c++", "helper", "util")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_unicode": [True, False],
        "enable_large_files": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_unicode": True,
        "enable_large_files": True,
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_UNICODE"] = self.options.enable_unicode
        tc.variables["LARGE_FILES"] = self.options.enable_large_files
        # Export symbols for msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "0.4.41": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Enable WIN32 shared libraries
        replace_in_file(self, os.path.join(self.source_folder, "Project", "CMake", "CMakeLists.txt"),
                        "set(BUILD_SHARED_LIBS OFF)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Project", "CMake"))
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ZenLib")
        self.cpp_info.set_property("cmake_target_name", "zen")
        self.cpp_info.set_property("pkg_config_name", "libzen")
        suffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                suffix = "d"
            elif is_apple_os(self):
                suffix = "_debug"
        self.cpp_info.libs = [f"zen{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.options.enable_unicode:
            self.cpp_info.defines.extend(["UNICODE", "_UNICODE"])
        if self.options.shared:
            self.cpp_info.defines.append("LIBZEN_SHARED")
