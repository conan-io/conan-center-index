from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


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
        "flatc": [True, False, "deprecated"],
        "flatbuffers": [True, False, "deprecated"],
        "options_from_context": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "flatc": "deprecated",
        "flatbuffers": "deprecated",
        "options_from_context": "deprecated",
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_flatc(self):
        # don't build flatc when it makes little sense or not supported
        return self.settings.os not in ["Android", "iOS", "watchOS", "tvOS", "Neutrino"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        self.copy(os.path.join("cmake", "FlatcTargets.cmake"))
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared or self.options.header_only:
            del self.options.fPIC
        if self.options.header_only:
            del self.options.shared
        # deprecated options
        for deprecated_option in ["flatc", "flatbuffers", "options_from_context"]:
            if self.options.get_safe(deprecated_option) != "deprecated":
                self.output.warn("{} option is deprecated, do not use".format(deprecated_option))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        if self.options.header_only and not self._has_flatc:
            self.info.header_only()
        # deprecated options
        del self.info.options.flatc
        del self.info.options.flatbuffers
        del self.info.options.options_from_context

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Prefer manual injection of current version in build(), otherwise it tries to call git
        tools.files.replace_in_file(self, cmakelists, "include(CMake/Version.cmake)", "")
        # No warnings as errors
        tools.files.replace_in_file(self, cmakelists, "/WX", "")
        tools.files.replace_in_file(self, cmakelists, "-Werror ", "")
        # Install dll to bin folder
        tools.files.replace_in_file(self, cmakelists,
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        self._cmake.definitions["FLATBUFFERS_INSTALL"] = True
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = not self.options.header_only and not self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = self._has_flatc
        self._cmake.definitions["FLATBUFFERS_STATIC_FLATC"] = False
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = False
        self._cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = not self.options.header_only and self.options.shared
        # Honor conan profile
        self._cmake.definitions["FLATBUFFERS_LIBCXX_WITH_CLANG"] = False
        # Mimic upstream CMake/Version.cmake removed in _patch_sources()
        version = tools.scm.Version(self.version)
        self._cmake.definitions["VERSION_MAJOR"] = version.major
        self._cmake.definitions["VERSION_MINOR"] = version.minor
        self._cmake.definitions["VERSION_PATCH"] = version.patch
        # To install relocatable shared libs on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Fix iOS/tvOS/watchOS
        if tools.apple.is_apple_os(self, self.settings.os):
            self._cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False

        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.copy(pattern="FlatcTargets.cmake",
                  dst=self._module_path,
                  src="cmake")
        self.copy(pattern="BuildFlatBuffers.cmake",
                  dst=self._module_path,
                  src=os.path.join(self._source_subfolder, "CMake"))

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
        self.cpp_info.set_property("cmake_target_name", "flatbuffers::{}".format(cmake_target))
        self.cpp_info.set_property("pkg_config_name", "flatbuffers")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if not self.options.header_only:
            self.cpp_info.components["libflatbuffers"].libs = tools.files.collect_libs(self, self)
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
            self.output.info("Appending PATH environment variable: {}".format(bindir))
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
        self.cpp_info.components["libflatbuffers"].set_property("cmake_file_name", "flatbuffers::{}".format(cmake_target))
        self.cpp_info.components["libflatbuffers"].set_property("pkg_config_name", "flatbuffers")
