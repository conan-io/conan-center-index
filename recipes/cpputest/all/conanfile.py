from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.52.0"


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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STD_C"] = True
        tc.variables["STD_CPP"] = True
        tc.variables["C++11"] = True
        tc.variables["MEMORY_LEAK_DETECTION"] = self.options.with_leak_detection
        tc.variables["EXTENSIONS"] = self.options.with_extensions
        tc.variables["LONGLONG"] = True
        tc.variables["COVERAGE"] = False
        tc.variables["TESTS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "CppUTest"))

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
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

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
