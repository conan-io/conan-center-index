import os
import textwrap
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


class OpenTelemetryCppConan(ConanFile):
    name = "opentelemetry-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open-telemetry/opentelemetry-cpp"
    description = "The C++ OpenTelemetry API and SDK"
    requires = [
        "abseil/20211102.0",
        "grpc/1.44.0",
        "libcurl/7.80.0",
        "nlohmann_json/3.10.5",
        "openssl/1.1.1m",
        "opentelemetry-proto/0.11.0",
        "protobuf/3.19.2",
        "thrift/0.14.2",
    ]
    topics = ("opentelemetry", "telemetry", "tracing", "metrics", "logs")
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }
    exports_sources = "CMakeLists.txt"

    short_paths = True
    _cmake = None

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Architecture not supported")

        if (self.settings.compiler == "Visual Studio" and
           tools.Version(self.settings.compiler.version) < "16"):
            raise ConanInvalidConfiguration("Visual Studio 2019 or higher required")

        if self.settings.os != "Linux" and self.options.shared:
            raise ConanInvalidConfiguration("Building shared libraries is only supported on Linux")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            set(OPENTELEMETRY_CPP_INCLUDE_DIRS ${opentelemetry-cpp_INCLUDE_DIRS}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_RELEASE}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_RELWITHDEBINFO}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_MINSIZEREL}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_DEBUG})
            set(OPENTELEMETRY_CPP_LIBRARIES opentelemetry-cpp::opentelemetry-cpp)
        """)
        tools.save(module_file, content)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        defs = {
          "BUILD_TESTING": False,
          "WITH_ABSEIL": True,
          "WITH_ETW": True,
          "WITH_EXAMPLES": False,
          "WITH_JAEGER": True,
          "WITH_OTLP": True,
          "WITH_ZIPKIN": True,
        }
        self._cmake.configure(defs=defs, build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        protos_path = self.deps_cpp_info["opentelemetry-proto"].res_paths[0].replace("\\", "/")
        protos_cmake_path = os.path.join(
            self._source_subfolder,
            "cmake",
            "opentelemetry-proto.cmake")
        tools.replace_in_file(
            protos_cmake_path,
            "set(PROTO_PATH \"${CMAKE_CURRENT_SOURCE_DIR}/third_party/opentelemetry-proto\")",
            f"set(PROTO_PATH \"{protos_path}\")")
        tools.rmdir(os.path.join(self._source_subfolder, "api", "include", "opentelemetry", "nostd", "absl"))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._otel_cmake_variables_path)
        )

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _otel_cmake_variables_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-variables.cmake".format(self.name))

    @property
    def _otel_build_modules(self):
        return [self._otel_cmake_variables_path]

    @property
    def _otel_libraries(self):
        libraries = [
            "http_client_curl",
            "opentelemetry_common",
            "opentelemetry_exporter_in_memory",
            "opentelemetry_exporter_jaeger_trace",
            "opentelemetry_exporter_ostream_span",
            "opentelemetry_exporter_otlp_grpc",
            "opentelemetry_exporter_otlp_http",
            "opentelemetry_exporter_zipkin_trace",
            "opentelemetry_otlp_recordable",
            "opentelemetry_proto",
            "opentelemetry_resources",
            "opentelemetry_trace",
            "opentelemetry_version",
        ]
        if self.settings.os == "Windows":
            libraries.extend([
                "opentelemetry_exporter_etw",
            ])
        return libraries

    def package_info(self):
        for lib in self._otel_libraries:
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].builddirs.append(self._module_subfolder)
            self.cpp_info.components[lib].build_modules["cmake_find_package"] = self._otel_build_modules
            self.cpp_info.components[lib].build_modules["cmake_find_package_multi"] = self._otel_build_modules

        self.cpp_info.components["http_client_curl"].requires.extend(["libcurl::libcurl"])

        self.cpp_info.components["opentelemetry_common"].defines.append("HAVE_ABSEIL")
        self.cpp_info.components["opentelemetry_common"].requires.extend([
            "abseil::abseil",
        ])

        if self.settings.os == "Windows":
            self.cpp_info.components["opentelemetry_exporter_etw"].libs = []
            self.cpp_info.components["opentelemetry_exporter_etw"].requires.extend([
                "nlohmann_json::nlohmann_json",
            ])

        self.cpp_info.components["opentelemetry_exporter_in_memory"].libs = []

        self.cpp_info.components["opentelemetry_exporter_jaeger_trace"].requires.extend([
            "http_client_curl",
            "openssl::openssl",
            "opentelemetry_resources",
            "thrift::thrift",
        ])

        self.cpp_info.components["opentelemetry_exporter_ostream_span"].requires.extend([
            "opentelemetry_trace",
        ])

        self.cpp_info.components["opentelemetry_exporter_otlp_grpc"].requires.extend([
            "grpc::grpc++",
            "opentelemetry_otlp_recordable",
            "protobuf::protobuf",
        ])

        self.cpp_info.components["opentelemetry_exporter_otlp_http"].requires.extend([
            "http_client_curl",
            "nlohmann_json::nlohmann_json",
            "opentelemetry_otlp_recordable",
        ])

        self.cpp_info.components["opentelemetry_exporter_zipkin_trace"].requires.extend([
            "http_client_curl",
            "nlohmann_json::nlohmann_json",
            "opentelemetry_trace",
        ])

        self.cpp_info.components["opentelemetry_otlp_recordable"].requires.extend([
            "opentelemetry_proto",
            "opentelemetry_resources",
            "opentelemetry_trace",
        ])

        self.cpp_info.components["opentelemetry_proto"].requires.extend([
            "opentelemetry-proto::opentelemetry-proto",
            "protobuf::protobuf",
        ])

        self.cpp_info.components["opentelemetry_resources"].requires.extend([
            "opentelemetry_common",
        ])

        self.cpp_info.components["opentelemetry_trace"].requires.extend([
            "opentelemetry_common",
            "opentelemetry_resources",
        ])

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["opentelemetry_common"].system_libs.extend(["pthread"])
