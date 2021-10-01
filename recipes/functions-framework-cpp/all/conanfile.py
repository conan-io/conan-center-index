import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class FunctionsFrameworkCppConan(ConanFile):
    name = "functions-framework-cpp"
    description = "An open source FaaS (Functions as a Service) framework"
    license = "Apache-2.0"
    topics = "google", "cloud", "functions-as-a-service", "faas-framework"
    homepage = "https://github.com/GoogleCloudPlatform/functions-framework-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "clang": "7",
            "apple-clang": "11",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++17, which your compiler does not support.".format(
                        self.name
                    )
                )
        else:
            self.output.warn(
                "{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(
                    self.name
                )
            )

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Fails to compile for Windows as a DLL")

        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration(
                "Recipe not prepared for cross-building (yet)"
            )

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def requirements(self):
        self.requires("abseil/20210324.2")
        self.requires("boost/1.77.0")
        self.requires("nlohmann_json/3.10.2")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["FUNCTIONS_FRAMEWORK_CPP_TEST_EXAMPLES"] = False

        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # The package is not installing the `*.so` file:
        #     https://github.com/GoogleCloudPlatform/functions-framework-cpp/issues/331
        # create this manually:
        if self.settings.os != "Windows" and self.options.shared:
            src, dst = (".so.1.0.0", ".so") if self.settings.os != "Macos" else (".1.0.0.dylib", ".dylib")
            os.link(
                os.path.join(
                    self.package_folder, "lib", "libfunctions_framework_cpp" + src
                ),
                os.path.join(
                    self.package_folder, "lib", "libfunctions_framework_cpp" + dst
                ),
            )

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "functions_framework_cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "functions_framework_cpp"
        self.cpp_info.names["cmake_find_package"] = "functions-framework-cpp"

        self.cpp_info.components["framework"].libs = ["functions_framework_cpp"]
        self.cpp_info.components["framework"].requires = [
            "abseil::absl_time",
            "boost::headers",
            "boost::program_options",
            "nlohmann_json::nlohmann_json",
        ]
        self.cpp_info.components["framework"].set_property(
            "pkg_config_name", "functions_framework_cpp"
        )
