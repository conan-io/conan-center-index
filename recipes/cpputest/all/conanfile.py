from conans import CMake
from conan import ConanFile
from conan import tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class CppUTestConan(ConanFile):
    name = "cpputest"
    description = (
        "CppUTest is a C /C++ based unit xUnit test framework for unit testing "
        "and for test-driving your code. It is written in C++ but is used in C "
        "and C++ projects and frequently used in embedded systems but it works "
        "for any C/C++ project."
    )
    license = "BSD-3-Clause"
    topics = ("testing", "unit-testing")
    homepage = "https://cpputest.github.io"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_extensions": [True, False],
        "with_leak_detection": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_extensions": True,
        "with_leak_detection": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["STD_C"] = "ON"
        self._cmake.definitions["STD_CPP"] = "ON"
        self._cmake.definitions["C++11"] = "ON"
        self._cmake.definitions["MEMORY_LEAK_DETECTION"] = self.options.with_leak_detection
        self._cmake.definitions["EXTENSIONS"] = self.options.with_extensions
        self._cmake.definitions["LONGLONG"] = "ON"
        self._cmake.definitions["COVERAGE"] = "OFF"
        self._cmake.definitions["TESTS"] = "OFF"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "CppUTest"))

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "CppUTest": "CppUTest::CppUTest",
                "CppUTestExt": "CppUTest::CppUTestExt",
            }
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CppUTest")
        self.cpp_info.set_property("pkg_config_name", "cpputest")

        self.cpp_info.components["CppUTest"].set_property("cmake_target_name", "CppUTest")
        self.cpp_info.components["CppUTest"].libs = ["CppUTest"]
        if self.settings.os == "Windows":
            self.cpp_info.components["CppUTest"].system_libs.append("winmm")
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["CppUTest"].system_libs.append("pthread")

        if self.options.with_extensions:
            self.cpp_info.components["CppUTestExt"].set_property("cmake_target_name", "CppUTestExt")
            self.cpp_info.components["CppUTestExt"].libs = ["CppUTestExt"]
            self.cpp_info.components["CppUTestExt"].requires = ["CppUTest"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "CppUTest"
        self.cpp_info.names["cmake_find_package_multi"] = "CppUTest"
        self.cpp_info.names["pkg_config"] = "cpputest"
        self.cpp_info.components["CppUTest"].names["cmake_find_package"] = "CppUTest"
        self.cpp_info.components["CppUTest"].names["cmake_find_package_multi"] = "CppUTest"
        self.cpp_info.components["CppUTest"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["CppUTest"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_extensions:
            self.cpp_info.components["CppUTestExt"].names["cmake_find_package"] = "CppUTestExt"
            self.cpp_info.components["CppUTestExt"].names["cmake_find_package_multi"] = "CppUTestExt"
            self.cpp_info.components["CppUTestExt"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["CppUTestExt"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
