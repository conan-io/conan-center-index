import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"


class UTConan(ConanFile):
    name = "boost-ext-ut"
    description = ("C++20 single header/single module, "
                   "macro-free micro Unit Testing Framework")
    topics = ("ut", "header-only", "unit-test", "test", "tdd", "bdd")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boost-ext.github.io/ut/"
    license = "BSL-1.0"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True
    options = { "disable_module": [True, False], }
    default_options = { "disable_module": False, }

    @property
    def _minimum_cpp_standard(self):
        return 17 if self.settings.compiler in ["clang", "gcc"] and Version(self.version) <= "1.1.8" else 20

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "11" if Version(self.version) < "1.1.8" else "12",
            "clang": "9",
            "gcc": "9",
        }

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if Version(self.version) <= "1.1.8":
            del self.options.disable_module
        elif is_msvc(self):
            self.options.disable_module = True

    def layout(self):
        cmake_layout(self)

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        if Version(self.version) <= "1.1.8" and is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.name} version 1.1.8 may not be built with MSVC. "
                                            "Please use at least version 1.1.9 with MSVC.")

        if is_msvc(self):
            check_min_vs(self, "192")
            if not self.options.get_safe("disable_module", True):
                self.output.warn("The 'disable_module' option must be enabled when using MSVC.")
        if not is_msvc(self):
            min_version = self._minimum_compilers_version.get(
                str(self.settings.compiler))
            if not min_version:
                self.output.warn(f"{self.name} recipe lacks information about the {self.settings.compiler} "
                                 "compiler support.")
            else:
                if Version(self.settings.compiler.version) < min_version:
                    raise ConanInvalidConfiguration(
                        f"{self.name} requires C++{self._minimum_cpp_standard} support. "
                        f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BOOST_UT_BUILD_BENCHMARKS"] = False
        tc.cache_variables["BOOST_UT_BUILD_EXAMPLES"] = False
        tc.cache_variables["BOOST_UT_BUILD_TESTS"] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.cache_variables["PROJECT_DISABLE_VERSION_SUFFIX"] = True
        disable_module = self.options.get_safe("disable_module")
        if disable_module:
            tc.cache_variables["BOOST_UT_DISABLE_MODULE"] = disable_module
        tc.generate()
    
    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ut")
        self.cpp_info.set_property("cmake_target_name", "boost::ut")

        self.cpp_info.names["cmake_find_package"] = "boost"
        self.cpp_info.names["cmake_find_package_multi"] = "boost"
        self.cpp_info.filenames["cmake_find_package"] = "ut"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ut"
        self.cpp_info.components["ut"].names["cmake_find_package"] = "ut"
        self.cpp_info.components["ut"].names["cmake_find_package_multi"] = "ut"

        if Version(self.version) > "1.1.8":
            self.cpp_info.components["ut"].includedirs = [os.path.join("include", "ut-" + self.version, "include")]

        if self.options.get_safe("disable_module"):
            self.cpp_info.components["ut"].defines = ["BOOST_UT_DISABLE_MODULE=1"]
