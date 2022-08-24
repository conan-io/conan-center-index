from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class FunctionsFrameworkCppConan(ConanFile):
    name = "functions-framework-cpp"
    description = "An open source FaaS (Functions as a Service) framework"
    license = "Apache-2.0"
    topics = ("google", "cloud", "functions-as-a-service", "faas-framework")
    homepage = "https://github.com/GoogleCloudPlatform/functions-framework-cpp"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package_multi", "cmake_find_package"
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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

    def requirements(self):
        self.requires("abseil/20211102.0")
        self.requires("boost/1.78.0")
        self.requires("nlohmann_json/3.10.5")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "clang": "7",
            "apple-clang": "11",
        }

    @property
    def _required_boost_components(self):
        return ["program_options"]

    def validate(self):
        miss_boost_required_comp = \
            any(getattr(self.options["boost"],
                        "without_{}".format(boost_comp),
                        True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                "{0} requires non-header-only boost with these components: {1}".format(
                    self.name, ", ".join(self._required_boost_components)
                )
            )

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 17)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("Fails to build for Visual Studio as a DLL")

        if hasattr(self, "settings_build") and tools.build.cross_building(self, self):
            raise ConanInvalidConfiguration(
                "Recipe not prepared for cross-building (yet)"
            )

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["FUNCTIONS_FRAMEWORK_CPP_TEST_EXAMPLES"] = False

        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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
        self.cpp_info.names["pkg_config"] = "functions_framework_cpp"
        self.cpp_info.components["framework"].set_property("cmake_target_name", "functions-framework-cpp::framework")
        self.cpp_info.components["framework"].set_property("pkg_config_name", "functions_framework_cpp")
