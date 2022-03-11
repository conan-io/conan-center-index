from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class SzipConan(ConanFile):
    name = "szip"
    description = "C Implementation of the extended-Rice lossless compression " \
                  "algorithm, suitable for use with scientific data."
    license = "Szip License"
    topics = ("szip", "compression", "decompression")
    homepage = "https://support.hdfgroup.org/doc_resource/SZIP/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encoding": [True, False],
        "enable_large_file": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoding": False,
        "enable_large_file": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SZIP_ENABLE_ENCODING"] = self.options.enable_encoding
        self._cmake.definitions["SZIP_EXTERNALLY_CONFIGURED"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["SZIP_BUILD_FRAMEWORKS"] = False
        self._cmake.definitions["SZIP_PACK_MACOSX_FRAMEWORK"] = False
        self._cmake.definitions["SZIP_ENABLE_LARGE_FILE"] = self.options.enable_large_file
        if tools.cross_building(self, skip_x64_x86=True) and self.options.enable_large_file:
            # Assume it works, otherwise raise in 'validate' function
            self._cmake.definitions["TEST_LFS_WORKS_RUN"] = True
            self._cmake.definitions["TEST_LFS_WORKS_RUN__TRYRUN_OUTPUT"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"szip-shared" if self.options.shared else "szip-static": "szip::szip"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "szip")
        self.cpp_info.set_property("cmake_target_name", "szip-shared" if self.options.shared else "szip-static")
        self.cpp_info.libs = tools.collect_libs(self)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
