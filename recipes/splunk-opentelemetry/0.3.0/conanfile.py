from conans import ConanFile, CMake, tools
import os
import glob


class SplunkOpentelemetryConan(ConanFile):
    name = "splunk-opentelemetry"
    version = "0.3.0"
    license = "Apache 2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/signalfx/splunk-otel-cpp"
    description = "Splunk's distribution of OpenTelemetry C++"
    topics = ("opentelemetry", "observability", "tracing")
    settings = {
      "os": "Linux",
      "compiler": None,
      "build_type": None,
      "arch": ["x86_64"]
    }
    generators = "cmake_find_package"
    requires = "grpc/1.37.1", "protobuf/3.17.1", "libcurl/7.79.1"
    exports_sources = [
      "src*",
      "include*",
      "opentelemetry-cpp*",
      "CMakeLists.txt"
    ]

    def config(self):
        if "libcxx" in self.settings.compiler.fields:
            self.settings.compiler.libcxx.remove("libstdc++")

    @property
    def _source_subfolder(self):
        return "sources"

    def _remove_unnecessary_package_files(self):
        cmake_pattern = os.path.join(self.package_folder, "lib", "cmake", "*", "*.cmake")
        pkgconfig_pattern = os.path.join(self.package_folder, "lib", "pkgconfig", "*.pc")

        for path in glob.glob(cmake_pattern):
            os.remove(path)

        for path in glob.glob(pkgconfig_pattern):
            os.remove(path)

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def _build_otel_cpp(self):
        cmake = CMake(self)
        prefix_paths = [
          self.deps_cpp_info["grpc"].rootpath,
          self.deps_cpp_info["protobuf"].rootpath,
        ]

        # Is there a better way?
        include_dirs = [
          "-isystem {}".format(os.path.join(self.deps_cpp_info["abseil"].rootpath, "include")),
          "-isystem {}".format(os.path.join(self.deps_cpp_info["grpc"].rootpath, "include"))
        ]

        defs = {
          "CMAKE_PREFIX_PATH": ";".join(prefix_paths),
          "WITH_OTLP": True,
          "WITH_OTLP_HTTP": False,
          "WITH_JAEGER": False,
          "WITH_ABSEIL": False,
          "BUILD_TESTING": False,
          "WITH_EXAMPLES": False,
          "CMAKE_CXX_FLAGS": " ".join(include_dirs)
        }
        cmake.configure(
          source_folder=os.path.join(
            self._source_subfolder,
            "opentelemetry-cpp"
          ),
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
          "SPLUNK_CPP_EXAMPLES": False,
        }
        cmake.configure(source_folder=self._source_subfolder, defs=defs)
        cmake.build()
        cmake.install()

        self._remove_unnecessary_package_files()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src="src")
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SplunkOpenTelemetry"
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
