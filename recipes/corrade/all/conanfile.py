import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, check_min_vs

required_conan_version = ">=1.52.0"


class CorradeConan(ConanFile):
    name = "corrade"
    description = "Corrade is a multiplatform utility library written in C++11/C++14."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics/corrade"
    topics = ("magnum", "filesystem", "console", "environment", "os")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "with_interconnect": [True, False],
        "with_main": [True, False],
        "with_pluginmanager": [True, False],
        "with_testsuite": [True, False],
        "with_utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_deprecated": True,
        "with_interconnect": True,
        "with_main": True,
        "with_pluginmanager": True,
        "with_testsuite": True,
        "with_utility": True,
    }

    def export_sources(self):
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_vs(self, 190)
        if not self.options.with_utility and (
            self.options.with_testsuite or self.options.with_interconnect or self.options.with_pluginmanager
        ):
            raise ConanInvalidConfiguration(
                "Component 'utility' is required for 'test_suite', 'interconnect' and 'plugin_manager'"
            )

    def build_requirements(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            self.tool_requires(f"corrade/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)

        tc.variables["BUILD_DEPRECATED"] = self.options.build_deprecated
        tc.variables["WITH_INTERCONNECT"] = self.options.with_interconnect
        tc.variables["WITH_MAIN"] = self.options.with_main
        tc.variables["WITH_PLUGINMANAGER"] = self.options.with_pluginmanager
        tc.variables["WITH_TESTSUITE"] = self.options.with_testsuite
        tc.variables["WITH_UTILITY"] = self.options.with_utility
        tc.variables["WITH_RC"] = self.options.with_utility

        # Corrade uses suffix on the resulting "lib"-folder when running cmake.install()
        # Set it explicitly to empty, else Corrade might set it implicitly (eg. to "64")
        tc.variables["LIB_SUFFIX"] = ""

        if is_msvc(self):
            if check_min_vs(self, 193, raise_invalid=False):
                tc.variables["MSVC2019_COMPATIBILITY"] = True
            elif check_min_vs(self, 192, raise_invalid=False):
                tc.variables["MSVC2017_COMPATIBILITY"] = True
            elif check_min_vs(self, 191, raise_invalid=False):
                tc.variables["MSVC2015_COMPATIBILITY"] = True

        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        share_cmake = os.path.join(self.package_folder, "share", "cmake", "Corrade")
        copy(self, "UseCorrade.cmake",
             src=share_cmake,
             dst=os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "CorradeLibSuffix.cmake",
             src=share_cmake,
             dst=os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "*.cmake",
            src=os.path.join(self.export_sources_folder, "cmake"),
            dst=os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Corrade")
        self.cpp_info.set_property("cmake_target_name", "Corrade::Corrade")

        suffix = "-d" if self.settings.build_type == "Debug" else ""

        cmake_modules = [
            # Reproduces the variables and calls performed by the FindCorrade.cmake provided by the library
            os.path.join("lib", "cmake", "conan-corrade-vars.cmake"),
            # Autodetects LIB_SUFFIX (either "64" or "")
            os.path.join("lib", "cmake", "CorradeLibSuffix.cmake"),
            # Exports build flags and macros
            os.path.join("lib", "cmake", "UseCorrade.cmake"),
        ]
        self.cpp_info.set_property("cmake_build_modules", cmake_modules)
        self.cpp_info.components["_corrade"].build_modules["cmake_find_package"] = cmake_modules
        self.cpp_info.components["_corrade"].build_modules["cmake_find_package_multi"] = cmake_modules

        if self.options.with_main:
            self.cpp_info.components["main"].set_property("cmake_target_name", "Corrade::Main")
            self.cpp_info.components["main"].names["cmake_find_package"] = "Main"
            self.cpp_info.components["main"].names["cmake_find_package_multi"] = "Main"
            if self.settings.os == "Windows":
                self.cpp_info.components["main"].libs = ["CorradeMain" + suffix]
            self.cpp_info.components["main"].requires = ["_corrade"]

        if self.options.with_utility:
            self.cpp_info.components["utility"].set_property("cmake_target_name", "Corrade::Utility")
            self.cpp_info.components["utility"].names["cmake_find_package"] = "Utility"
            self.cpp_info.components["utility"].names["cmake_find_package_multi"] = "Utility"
            self.cpp_info.components["utility"].libs = ["CorradeUtility" + suffix]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["utility"].system_libs = ["m", "dl"]
            self.cpp_info.components["utility"].requires = ["_corrade"]

            # This one is statically linked into utility
            # self.cpp_info.components["containers"].set_property("cmake_target_name", "Corrade::Containers")
            # self.cpp_info.components["containers"].names["cmake_find_package"] = "Containers"
            # self.cpp_info.components["containers"].names["cmake_find_package_multi"] = "Containers"
            # self.cpp_info.components["containers"].libs = ["CorradeContainers" + suffix]

        if self.options.with_interconnect:
            self.cpp_info.components["interconnect"].set_property("cmake_target_name", "Corrade::Interconnect")
            self.cpp_info.components["interconnect"].names["cmake_find_package"] = "Interconnect"
            self.cpp_info.components["interconnect"].names["cmake_find_package_multi"] = "Interconnect"
            self.cpp_info.components["interconnect"].libs = ["CorradeInterconnect" + suffix]
            self.cpp_info.components["interconnect"].requires = ["utility"]

        if self.options.with_pluginmanager:
            self.cpp_info.components["plugin_manager"].set_property("cmake_target_name", "Corrade::PluginManager")
            self.cpp_info.components["plugin_manager"].names["cmake_find_package"] = "PluginManager"
            self.cpp_info.components["plugin_manager"].names["cmake_find_package_multi"] = "PluginManager"
            self.cpp_info.components["plugin_manager"].libs = ["CorradePluginManager" + suffix]
            self.cpp_info.components["plugin_manager"].requires = ["utility"]

        if self.options.with_testsuite:
            self.cpp_info.components["test_suite"].set_property("cmake_target_name", "Corrade::TestSuite")
            self.cpp_info.components["test_suite"].names["cmake_find_package"] = "TestSuite"
            self.cpp_info.components["test_suite"].names["cmake_find_package_multi"] = "TestSuite"
            self.cpp_info.components["test_suite"].libs = ["CorradeTestSuite" + suffix]
            self.cpp_info.components["test_suite"].requires = ["utility"]

        if self.options.with_utility:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bindir}")
            self.env_info.PATH.append(bindir)

        # pkg_config: Add more explicit naming to generated files (avoid filesystem collision).
        for key, component in self.cpp_info.components.items():
            component.set_property("pkg_config_name", f"{self.name}_{key}")

        self.cpp_info.names["cmake_find_package"] = "Corrade"
        self.cpp_info.names["cmake_find_package_multi"] = "Corrade"
