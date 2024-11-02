from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class XxHashConan(ConanFile):
    name = "xxhash"
    description = "Extremely fast non-cryptographic hash algorithm"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Cyan4973/xxHash"
    topics = ("hash", "algorithm", "fast", "checksum", "hash-functions")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "utility": [True, False],
    }
    default_options = {
        "shared": False,
        "header_only": False,
        "fPIC": True,
        "utility": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared and self.options.header_only:
            raise ConanException("Options 'shared' and 'header_only' cannot both be true at once.")
        if self.options.shared or self.options.header_only:
            self.options.rm_safe("fPIC")
        if self.options.shared:
            self.options.rm_safe("header_only")
        elif self.options.header_only:
            self.options.rm_safe("shared")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _run_cmake(self):
        return not self.options.get_safe("header_only") or self.options.utility

    def generate(self):
        if self._run_cmake():
            tc = CMakeToolchain(self)
            tc.variables["XXHASH_BUNDLED_MODE"] = False
            tc.variables["XXHASH_BUILD_XXHSUM"] = self.options.utility
            # Fix CMake configuration if target is iOS/tvOS/watchOS
            tc.cache_variables["CMAKE_MACOSX_BUNDLE"] = False
            # Generate a relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            tc.generate()

    def build(self):
        if self._run_cmake():
            apply_conandata_patches(self)
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "cmake_unofficial"))
            cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self._run_cmake():
            cmake = CMake(self)
            cmake.install()
            if self.options.get_safe("header_only"):
                rmdir(self, os.path.join(self.package_folder, "lib"))
            else:
                rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
                rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        else:
            copy(self, "xxhash.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xxHash")
        self.cpp_info.set_property("cmake_target_name", "xxHash::xxhash")
        self.cpp_info.set_property("pkg_config_name", "libxxhash")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        if not self.options.get_safe("shared"):
            self.cpp_info.components["libxxhash"].defines.append("XXH_STATIC_LINKING_ONLY")
        if self.options.get_safe("header_only"):
            self.cpp_info.components["libxxhash"].defines.append("XXH_INLINE_ALL")
        else:
            self.cpp_info.components["libxxhash"].libs.append("xxhash")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "xxHash"
        self.cpp_info.names["cmake_find_package_multi"] = "xxHash"
        self.cpp_info.names["pkg_config"] = "libxxhash"
        self.cpp_info.components["libxxhash"].names["cmake_find_package"] = "xxhash"
        self.cpp_info.components["libxxhash"].names["cmake_find_package_multi"] = "xxhash"
        self.cpp_info.components["libxxhash"].set_property("cmake_target_name", "xxHash::xxhash")

        if self.options.utility:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
