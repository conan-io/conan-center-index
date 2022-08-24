from conans import ConanFile, tools, CMake
import functools
import os

required_conan_version = ">=1.43.0"


class RTTRConan(ConanFile):
    name = "rttr"
    description = "Run Time Type Reflection library"
    topics = ("reflection", "rttr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rttrorg/rttr"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rtti": False,
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # No warnings as errors
        for target in ["rttr_core", "rttr_core_lib", "rttr_core_s", "rttr_core_lib_s"]:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "src", "rttr", "CMakeLists.txt"),
                "set_compiler_warnings({})".format(target), "",
            )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_DOCUMENTATION"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_UNIT_TESTS"] = False
        cmake.definitions["BUILD_WITH_RTTI"] = self.options.with_rtti
        cmake.definitions["BUILD_PACKAGE"] = False
        cmake.definitions["BUILD_RTTR_DYNAMIC"] = self.options.shared
        cmake.definitions["BUILD_STATIC"] = not self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        cmake_target = "Core" if self.options.shared else "Core_Lib"
        self.cpp_info.set_property("cmake_file_name", "rttr")
        self.cpp_info.set_property("cmake_target_name", "RTTR::{}".format(cmake_target))
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_rttr"].libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_rttr"].system_libs = ["dl", "pthread"]
        if self.options.shared:
            self.cpp_info.components["_rttr"].defines = ["RTTR_DLL"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "rttr"
        self.cpp_info.filenames["cmake_find_package_multi"] = "rttr"
        self.cpp_info.names["cmake_find_package"] = "RTTR"
        self.cpp_info.names["cmake_find_package_multi"] = "RTTR"
        self.cpp_info.components["_rttr"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_rttr"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_rttr"].set_property("cmake_target_name", "RTTR::{}".format(cmake_target))
