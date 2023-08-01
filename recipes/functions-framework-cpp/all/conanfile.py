import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class FunctionsFrameworkCppConan(ConanFile):
    name = "functions-framework-cpp"
    description = "An open source FaaS (Functions as a Service) framework"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GoogleCloudPlatform/functions-framework-cpp"
    topics = ("google", "cloud", "functions-as-a-service", "faas-framework")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "msvc": "191",
            "clang": "7",
            "apple-clang": "11",
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

    def requirements(self):
        self.requires("abseil/20230125.3")
        self.requires("boost/1.82.0")
        self.requires("nlohmann_json/3.11.2")

    @property
    def _required_boost_components(self):
        return ["program_options"]

    def validate(self):
        miss_boost_required_comp = any(
            self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
            for boost_comp in self._required_boost_components
        )
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                "{0} requires non-header-only boost with these components: {1}".format(
                    self.name, ", ".join(self._required_boost_components)
                )
            )

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("Fails to build for Visual Studio as a DLL")

        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Recipe not prepared for cross-building (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["FUNCTIONS_FRAMEWORK_CPP_TEST_EXAMPLES"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "functions_framework_cpp")
        self.cpp_info.set_property("cmake_target_name", "functions-framework-cpp::framework")
        self.cpp_info.set_property("pkg_config_name", "functions_framework_cpp")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["framework"].libs = ["functions_framework_cpp"]
        self.cpp_info.components["framework"].requires = [
            "abseil::absl_time",
            "boost::headers",
            "boost::program_options",
            "nlohmann_json::nlohmann_json",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["framework"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "functions_framework_cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "functions_framework_cpp"
        self.cpp_info.components["framework"].set_property("cmake_target_name", "functions-framework-cpp::framework")
        self.cpp_info.components["framework"].set_property("pkg_config_name", "functions_framework_cpp")
