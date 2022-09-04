from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.3"


class FlatbuffersConan(ConanFile):
    name = "flatbuffers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://google.github.io/flatbuffers"
    topics = ("flatbuffers", "serialization", "rpc", "json-parser")
    description = "Memory Efficient Serialization Library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
    }

    @property
    def _has_flatc(self):
        # don't build flatc when it makes little sense or not supported
        return self.settings.os not in ["Android", "iOS", "watchOS", "tvOS", "Neutrino"]

    def export_sources(self):
        copy(self, os.path.join("cmake", "FlatcTargets.cmake"), self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared or self.options.header_only:
            del self.options.fPIC
        if self.options.header_only:
            del self.options.shared

    def package_id(self):
        if self.options.header_only and not self._has_flatc:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FLATBUFFERS_BUILD_TESTS"] = False
        tc.variables["FLATBUFFERS_INSTALL"] = True
        tc.variables["FLATBUFFERS_BUILD_FLATLIB"] = not self.options.header_only and not self.options.shared
        tc.variables["FLATBUFFERS_BUILD_FLATC"] = self._has_flatc
        tc.variables["FLATBUFFERS_STATIC_FLATC"] = False
        tc.variables["FLATBUFFERS_BUILD_FLATHASH"] = False
        tc.variables["FLATBUFFERS_BUILD_SHAREDLIB"] = not self.options.header_only and self.options.shared
        # Honor conan profile
        tc.variables["FLATBUFFERS_LIBCXX_WITH_CLANG"] = False
        # Mimic upstream CMake/Version.cmake removed in _patch_sources()
        version = Version(self.version)
        tc.variables["VERSION_MAJOR"] = version.major
        tc.variables["VERSION_MINOR"] = version.minor
        tc.variables["VERSION_PATCH"] = version.patch
        # For msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # Relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Fix iOS/tvOS/watchOS
        if is_apple_os(self):
            tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        # Inject at least C++11 standard (would be more elegant to rely on cxx_std_11 compile feature upstream)
        if not valid_min_cppstd(self, 11):
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Prefer manual injection of current version in build(), otherwise it tries to call git
        replace_in_file(self, cmakelists, "include(CMake/Version.cmake)", "")
        # No warnings as errors
        replace_in_file(self, cmakelists, "/WX", "")
        replace_in_file(self, cmakelists, "-Werror ", "")
        # Install dll to bin folder
        replace_in_file(self, cmakelists,
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        copy(self, "FlatcTargets.cmake",
                   src=os.path.join(self.source_folder, os.pardir, "cmake"),
                   dst=os.path.join(self.package_folder, self._module_path))
        copy(self, "BuildFlatBuffers.cmake",
                   src=os.path.join(self.source_folder, "CMake"),
                   dst=os.path.join(self.package_folder, self._module_path))

    @property
    def _module_path(self):
        return os.path.join("lib", "cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "FlatBuffers")
        self.cpp_info.set_property("cmake_file_name", "Flatbuffers")
        cmake_target = "flatbuffers"
        if not self.options.header_only and self.options.shared:
            cmake_target += "_shared"
        self.cpp_info.set_property("cmake_target_name", f"flatbuffers::{cmake_target}")
        self.cpp_info.set_property("pkg_config_name", "flatbuffers")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if not self.options.header_only:
            self.cpp_info.components["libflatbuffers"].libs = collect_libs(self)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libflatbuffers"].system_libs.append("m")

        # Provide flatbuffers::flatc target and CMake functions from BuildFlatBuffers.cmake
        build_modules = [
            os.path.join(self._module_path, "FlatcTargets.cmake"),
            os.path.join(self._module_path, "BuildFlatBuffers.cmake"),
        ]
        self.cpp_info.set_property("cmake_build_modules", build_modules)
        if self._has_flatc:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bindir}")
            self.env_info.PATH.append(bindir)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "FlatBuffers"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Flatbuffers"
        self.cpp_info.names["cmake_find_package"] = "flatbuffers"
        self.cpp_info.names["cmake_find_package_multi"] = "flatbuffers"
        self.cpp_info.components["libflatbuffers"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["libflatbuffers"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["libflatbuffers"].build_modules["cmake_find_package"] = build_modules
        self.cpp_info.components["libflatbuffers"].build_modules["cmake_find_package_multi"] = build_modules
        self.cpp_info.components["libflatbuffers"].set_property("cmake_file_name", f"flatbuffers::{cmake_target}")
        self.cpp_info.components["libflatbuffers"].set_property("pkg_config_name", "flatbuffers")
