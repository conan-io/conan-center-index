import os
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
        "abseil/20210324.2",
        "grpc/1.37.1",
        "libcurl/7.79.1",
        "nlohmann_json/3.10.4",
        "opentelemetry-proto/0.11.0",
        "openssl/1.1.1l",
        "protobuf/3.17.1",
        "thrift/0.14.2"
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

        if self.settings.os == "Macos" and self.options.shared:
            raise ConanInvalidConfiguration("Building as shared libraries is not supported on MacOS")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

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
          "WITH_ABSEIL": True,
          "WITH_OTLP": True,
          "WITH_JAEGER": True,
          "WITH_EXAMPLES": False,
          "BUILD_TESTING": False
        }
        self._cmake.configure(defs=defs, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
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
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

        # Note: tools.collect_libs will produce the wrong lib order
        self.cpp_info.libs = [
          "opentelemetry_version",
          "opentelemetry_exporter_otlp_grpc",
          "opentelemetry_exporter_otlp_http",
          "opentelemetry_exporter_jaeger_trace",
          "opentelemetry_exporter_ostream_span",
          "opentelemetry_otlp_recordable",
          "opentelemetry_proto",
          "opentelemetry_trace",
          "opentelemetry_resources",
          "opentelemetry_common",
          "http_client_curl"
        ]
