from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class DatadogOpenTracingConan(ConanFile):
    name = "dd-opentracing-cpp"
    description = "Monitoring service for cloud-scale applications based on OpenTracing "
    license = "Apache-2.0"
    topics = ("instrumentration", "monitoring", "security", "tracing")
    homepage = "https://github.com/DataDog/dd-opentracing-cpp"
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

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15",
            "clang": "3.4",
            "apple-clang": "7",
        }

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
        self.requires("opentracing-cpp/1.6.0")
        self.requires("zlib/1.2.11")
        self.requires("libcurl/7.80.0")
        self.requires("msgpack/3.3.0")
        self.requires("nlohmann_json/3.10.5")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("Datadog-opentracing requires C++14, which your compiler does not support.")
        else:
            self.output.warn("Datadog-opentracing requires C++14. Your compiler is unknown. Assuming it supports C++14.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_PLUGIN"] = False
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["dd_opentracing"].libs = ["dd_opentracing"]
        self.cpp_info.components["dd_opentracing"].defines.append(
            "DD_OPENTRACING_SHARED" if self.options.shared else "DD_OPENTRACING_STATIC"
        )
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["dd_opentracing"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed.
        #       Do not support these names in CMakeDeps, it was a mistake, upstream doesn't export targets
        self.cpp_info.names["cmake_find_package"] = "DataDogOpenTracing"
        self.cpp_info.names["cmake_find_package_multi"] = "DataDogOpenTracing"
        target_suffix = "" if self.options.shared else "-static"
        self.cpp_info.components["dd_opentracing"].names["cmake_find_package"] = "dd_opentracing" + target_suffix
        self.cpp_info.components["dd_opentracing"].names["cmake_find_package_multi"] = "dd_opentracing" + target_suffix
        self.cpp_info.components["dd_opentracing"].requires = [
            "opentracing-cpp::opentracing-cpp", "zlib::zlib", "libcurl::libcurl",
            "msgpack::msgpack", "nlohmann_json::nlohmann_json",
        ]
