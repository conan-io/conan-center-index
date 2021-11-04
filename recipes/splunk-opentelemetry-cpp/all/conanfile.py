from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class SplunkOpentelemetryConan(ConanFile):
    name = "splunk-opentelemetry-cpp"
    license = "Apache 2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/signalfx/splunk-otel-cpp"
    description = "Splunk's distribution of OpenTelemetry C++"
    topics = ("opentelemetry", "observability", "tracing")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"
    requires = "opentelemetry-cpp/1.0.1"
    exports_sources = "CMakeLists.txt"
    _cmake = None

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Architecture not supported")

    @property
    def _source_subdir(self):
        return "sources"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _remove_unnecessary_package_files(self):
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subdir
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        defs = {
          "SPLUNK_CPP_WITH_JAEGER_EXPORTER": False,
          "SPLUNK_CPP_EXAMPLES": False
        }
        self._cmake.configure(defs=defs, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subdir)
        cmake = self._configure_cmake()
        cmake.install()
        self._remove_unnecessary_package_files()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SplunkOpenTelemetry"
        self.cpp_info.names["cmake_find_package_multi"] = "SplunkOpenTelemetry"
        self.cpp_info.libs = ["SplunkOpenTelemetry"]
