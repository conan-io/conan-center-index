from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class SplunkOpentelemetryConan(ConanFile):
    name = "splunk-opentelemetry"
    license = "Apache 2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/signalfx/splunk-otel-cpp"
    description = "Splunk's distribution of OpenTelemetry C++"
    topics = ("opentelemetry", "observability", "tracing")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    requires = "grpc/1.37.1", "protobuf/3.17.1", "libcurl/7.79.1"
    exports_sources = "CMakeLists.txt"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("OS not supported")

        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Architecture not supported")

    @property
    def _source_subdir(self):
        return "sources"

    def _remove_unnecessary_package_files(self):
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subdir
        )

    def _build_otel_cpp(self):
        otel_cpp_srcdir = os.path.join(
            self._source_subdir,
            "opentelemetry-cpp"
        )
        tools.replace_in_file(
            os.path.join(otel_cpp_srcdir, "CMakeLists.txt"),
            "project(opentelemetry-cpp)",
            """project(opentelemetry-cpp)
               include({}/conanbuildinfo.cmake)
               conan_basic_setup()""".format(self.build_folder)
        )
        cmake = CMake(self)

        defs = {
          "WITH_OTLP": True,
          "WITH_OTLP_HTTP": False,
          "WITH_JAEGER": False,
          "WITH_ABSEIL": False,
          "BUILD_TESTING": False,
          "WITH_EXAMPLES": False
        }
        cmake.configure(
          source_folder=otel_cpp_srcdir,
          defs=defs,
          build_folder="otelcpp_build"
        )
        cmake.build()
        cmake.install()

    def build(self):
        self._build_otel_cpp()
        cmake = CMake(self)
        defs = {
          "SPLUNK_CPP_WITH_JAEGER_EXPORTER": False,
          "SPLUNK_CPP_EXAMPLES": False
        }
        cmake.configure(defs=defs)
        cmake.build()
        cmake.install()

        self._remove_unnecessary_package_files()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subdir)
        self.copy("*.h", dst="include", src="src")
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SplunkOpenTelemetry"
        self.cpp_info.names["cmake_find_package_multi"] = "SplunkOpenTelemetry"
        self.cpp_info.components["opentelemetry-cpp"].requires = [
          "grpc::grpc",
          "protobuf::protobuf",
          "libcurl::libcurl"
        ]

        otel_libs = [
          "opentelemetry_version",
          "opentelemetry_exporter_otlp_grpc",
          "opentelemetry_otlp_recordable",
          "opentelemetry_proto",
          "opentelemetry_exporter_ostream_span",
          "opentelemetry_zpages",
          "opentelemetry_trace",
          "opentelemetry_resources",
          "opentelemetry_common",
          "http_client_curl",
        ]

        self.cpp_info.components["opentelemetry-cpp"].libs = otel_libs
        self.cpp_info.components["SplunkOpenTelemetry"].requires = [
          "opentelemetry-cpp"
        ]
        self.cpp_info.components["SplunkOpenTelemetry"].libs = [
          "SplunkOpenTelemetry"
        ]
