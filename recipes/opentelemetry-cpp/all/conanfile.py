from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version

import os

required_conan_version = ">=2.2"

class OpenTelemetryCppConan(ConanFile):
    name = "opentelemetry-cpp"
    description = "The C++ OpenTelemetry API and SDK"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open-telemetry/opentelemetry-cpp"
    topics = ("opentelemetry", "telemetry", "tracing", "metrics", "logs")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_abi_v2": [True, False],
        "with_no_deprecated_code": [True, False],
        "with_stl": [True, False],
        "with_gsl": [True, False],
        "with_otlp_grpc": [True, False],
        "with_otlp_http": [True, False],
        "with_otlp_http_compression": [True, False],
        "with_otlp_file": [True, False],
        "with_zipkin": [True, False],
        "with_prometheus": [True, False],
        "with_elasticsearch": [True, False],
        "with_no_getenv": [True, False],
        "with_etw": [True, False],
        "with_async_export_preview": [True, False],
        "with_metrics_exemplar_preview": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,

        "with_abi_v2": False,
        "with_no_deprecated_code": False,
        # Enabling this causes stack overflow in the test_package
        "with_stl": False,
        "with_gsl": False,
        "with_otlp_grpc": False,
        # True because dependencies usually need this, and it would generate missing binaries for those
        "with_otlp_http": True,
        "with_otlp_http_compression": False,
        "with_otlp_file": False,
        "with_zipkin": True,
        "with_prometheus": False,
        "with_elasticsearch": False,
        "with_no_getenv": False,
        "with_etw": False,
        "with_async_export_preview": False,
        "with_metrics_exemplar_preview": False,
    }
    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            del self.options.with_etw

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _needs_proto(self):
        return self.options.with_otlp_grpc or self.options.with_otlp_http or self.options.get_safe("with_otlp_file")

    def requirements(self):
        if self.options.with_gsl:
            self.requires("ms-gsl/4.0.0")

        if self._needs_proto:
            self.requires("protobuf/5.27.0", transitive_headers=True, transitive_libs=True)

        if self.options.with_otlp_grpc:
            self.requires("grpc/1.67.1", transitive_headers=True, transitive_libs=True)

        if (self.options.with_zipkin or
           self.options.with_elasticsearch or
           self.options.with_otlp_http or
           self.options.get_safe("with_etw") or
           self.options.get_safe("with_otlp_file")
        ):
            self.requires("nlohmann_json/3.11.3")

        if (self.options.with_zipkin or
           self.options.with_elasticsearch or
           self.options.with_otlp_http
        ):
            self.requires("libcurl/[>=7.78.0 <9]")

        if self.options.with_otlp_http_compression:
            self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_prometheus:
            self.requires("prometheus-cpp/1.1.0")

    def validate(self):
        check_min_cppstd(self, 14)

        if self.settings.os != "Linux" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} supports building shared libraries only on Linux")

        if self.options.with_otlp_grpc:
            if not self.dependencies["grpc"].options.cpp_plugin:
                raise ConanInvalidConfiguration(f"{self.ref} requires grpc with cpp_plugin=True")

    def build_requirements(self):
        if self._needs_proto:
            self.tool_requires("opentelemetry-proto/1.7.0")
            self.tool_requires("protobuf/<host_version>")

        if self.options.with_otlp_grpc:
            self.tool_requires("grpc/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _stl_value(self):
        if self.options.with_stl:
            return "CXX" + str(self.settings.compiler.cppstd).replace("gnu", "")
        else:
            return False

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["WITH_BENCHMARK"] = False
        tc.cache_variables["WITH_EXAMPLES"] = False
        tc.cache_variables["WITH_NO_DEPRECATED_CODE"] = self.options.with_no_deprecated_code
        tc.cache_variables["WITH_STL"] = self._stl_value
        tc.cache_variables["WITH_GSL"] = self.options.with_gsl
        tc.cache_variables["WITH_OTLP_GRPC"] = self.options.with_otlp_grpc
        tc.cache_variables["WITH_OTLP_HTTP"] = self.options.with_otlp_http
        tc.cache_variables["WITH_OTLP_HTTP_COMPRESSION"] = self.options.with_otlp_http_compression
        if self.settings.os == "Linux":
            # So that the linker can pick up the correct openssl transitive dependency from libcurl
            # when building shared
            libdirs_host = [l for dependency in self.dependencies.host.values() for l in dependency.cpp_info.aggregated_components().libdirs]
            tc.cache_variables["CMAKE_BUILD_RPATH"] = ";".join(libdirs_host)
        if self.options.get_safe("with_otlp_file"):
            tc.cache_variables["WITH_OTLP_FILE"] = True
        if self._needs_proto:
            tc.cache_variables["OTELCPP_PROTO_PATH"] = self.dependencies.build["opentelemetry-proto"].conf_info.get("user.opentelemetry-proto:proto_root").replace("\\", "/")
        tc.cache_variables["WITH_ZIPKIN"] = self.options.with_zipkin
        tc.cache_variables["WITH_PROMETHEUS"] = self.options.with_prometheus
        tc.cache_variables["WITH_ELASTICSEARCH"] = self.options.with_elasticsearch
        tc.cache_variables["WITH_NO_GETENV"] = self.options.with_no_getenv
        if self.options.get_safe("with_etw"):
            # CMakeLists checks for definition, not value
            tc.cache_variables["WITH_ETW"] = True
        tc.cache_variables["WITH_ASYNC_EXPORT_PREVIEW"] = self.options.with_async_export_preview
        tc.cache_variables["WITH_METRICS_EXEMPLAR_PREVIEW"] = self.options.with_metrics_exemplar_preview
        tc.cache_variables["OPENTELEMETRY_INSTALL"] = True
        if self.options.get_safe("with_abi_v2"):
            tc.variables["WITH_ABI_VERSION_1"] = False
            tc.variables["WITH_ABI_VERSION_2"] = True
        tc.generate()

        deps = CMakeDeps(self)

        deps.generate()

    def _patch_sources(self):
        if self._needs_proto:
            protos_path = self.dependencies.build["opentelemetry-proto"].conf_info.get("user.opentelemetry-proto:proto_root").replace("\\", "/")
            protos_cmake_path = os.path.join(self.source_folder, "cmake", "opentelemetry-proto.cmake")

            if Version(self.version) < "1.22.0":
                replace_in_file(self, protos_cmake_path,
                                "if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/third_party/opentelemetry-proto/.git)",
                                "if(1)")
                replace_in_file(self, protos_cmake_path,
                                '"${CMAKE_CURRENT_SOURCE_DIR}/third_party/opentelemetry-proto")',
                                f'"{protos_path}")')
            else:
                replace_in_file(self, protos_cmake_path,
                                "elseif(EXISTS ${OPENTELEMETRY_PROTO_SUBMODULE}/.git)",
                                "elseif(1)")
                replace_in_file(self, protos_cmake_path,
                                'SOURCE_DIR ${OPENTELEMETRY_PROTO_SUBMODULE}',
                                f'SOURCE_DIR ${protos_path}')

        rmdir(self, os.path.join(self.source_folder, "api", "include", "opentelemetry", "nostd", "absl"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    @property
    def _http_client_name(self):
        return "opentelemetry_http_client_curl"

    @property
    def _otel_libraries(self):
        libraries = [
            "opentelemetry_common",
            "opentelemetry_exporter_in_memory",
            "opentelemetry_exporter_ostream_span",
            "opentelemetry_resources",
            "opentelemetry_trace",
            "opentelemetry_version",
        ]

        if self.options.with_otlp_http or self.options.with_elasticsearch or self.options.with_zipkin:
            # https://github.com/open-telemetry/opentelemetry-cpp/blob/v1.12.0/CMakeLists.txt#L452-L460
            libraries.append(self._http_client_name)
        if self._needs_proto:
            libraries.extend([
                "opentelemetry_proto",
                "opentelemetry_otlp_recordable",
                ])
            if self.options.with_otlp_grpc:
                libraries.append("opentelemetry_exporter_otlp_grpc")
                libraries.append("opentelemetry_exporter_otlp_grpc_metrics")
                libraries.append("opentelemetry_exporter_otlp_grpc_client")
                libraries.append("opentelemetry_proto_grpc")
                libraries.append("opentelemetry_exporter_otlp_grpc_log")
            if self.options.with_otlp_http:
                libraries.append("opentelemetry_exporter_otlp_http")
                libraries.append("opentelemetry_exporter_otlp_http_client")
                libraries.append("opentelemetry_exporter_otlp_http_metric")
                libraries.append("opentelemetry_exporter_otlp_http_log")
            if self.options.get_safe("with_otlp_file"):
                libraries.append("opentelemetry_exporter_otlp_file")
                libraries.append("opentelemetry_exporter_otlp_file_client")
                libraries.append("opentelemetry_exporter_otlp_file_metric")
                libraries.append("opentelemetry_exporter_otlp_file_log")
        if self.options.with_prometheus:
            libraries.append("opentelemetry_exporter_prometheus")
        if self.options.with_elasticsearch:
            libraries.append("opentelemetry_exporter_elasticsearch_logs")
        if self.options.with_zipkin:
            libraries.append("opentelemetry_exporter_zipkin_trace")
        libraries.append("opentelemetry_metrics")
        libraries.append("opentelemetry_exporter_ostream_metrics")
        libraries.extend([
            "opentelemetry_logs",
            "opentelemetry_exporter_ostream_logs",
        ])
        if self.options.get_safe("with_etw"):
            libraries.append("opentelemetry_exporter_etw")
        return libraries

    def package_info(self):
        self.cpp_info.set_property("cmake_additional_variables_prefixes", ["OPENTELEMETRY_CPP"])
        for lib in self._otel_libraries:
            self.cpp_info.components[lib].libs = [lib]
            unprefixed_name = lib.replace("opentelemetry_", "")
            self.cpp_info.components[lib].set_property("cmake_target_name", f"opentelemetry-cpp::{unprefixed_name}")

        self.cpp_info.components["api"].libs = []
        self.cpp_info.components["api"].defines.append(f"OPENTELEMETRY_ABI_VERSION_NO={2 if self.options.with_abi_v2 else 1}")
        self.cpp_info.components["opentelemetry_common"].requires.append("api")
        if self.options.with_stl:
            stl = str(self.settings.compiler.cppstd).replace("gnu", "")
            self.cpp_info.components["api"].defines.append(f"OPENTELEMETRY_STL_VERSION=20{stl}")

        self.cpp_info.components["opentelemetry_resources"].requires.extend([
            "opentelemetry_common",
        ])

        self.cpp_info.components["opentelemetry_trace"].requires.extend([
            "opentelemetry_common",
            "opentelemetry_resources",
        ])

        self.cpp_info.components["opentelemetry_exporter_ostream_span"].requires.append(
            "opentelemetry_trace",
        )

        self.cpp_info.components["opentelemetry_exporter_in_memory"].libs = []

        self.cpp_info.components["opentelemetry_logs"].requires.extend([
            "opentelemetry_resources",
            "opentelemetry_common",
        ])

        self.cpp_info.components["opentelemetry_exporter_ostream_logs"].requires.append(
            "opentelemetry_logs",
        )

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["opentelemetry_common"].system_libs.extend(["pthread"])

        if is_apple_os(self):
            self.cpp_info.components["opentelemetry_common"].frameworks.extend(["CoreFoundation"])

        if self.options.get_safe("with_otlp_http_compression"):
            self.cpp_info.components["opentelemetry_common"].defines.append("ENABLE_OTLP_COMPRESSION_PREVIEW")
        if self._stl_value:
            self.cpp_info.components["opentelemetry_common"].defines.append("HAVE_CPP_STDLIB")

        if self.options.with_gsl:
            self.cpp_info.components["opentelemetry_common"].defines.append("HAVE_GSL")
            self.cpp_info.components["opentelemetry_common"].requires.append("ms-gsl::_ms-gsl")

        if self.options.with_otlp_http or self.options.with_otlp_grpc:
            self.cpp_info.components["opentelemetry_proto"].requires.append("protobuf::protobuf")
            self.cpp_info.components["opentelemetry_otlp_recordable"].requires.extend([
                "opentelemetry_proto",
                "opentelemetry_resources",
                "opentelemetry_trace",
            ])

            self.cpp_info.components["opentelemetry_otlp_recordable"].requires.extend([
                "opentelemetry_logs",
            ])

        if self.options.with_otlp_grpc:
            self.cpp_info.components["opentelemetry_exporter_otlp_grpc_client"].requires.extend([
                "grpc::grpc++",
                "opentelemetry_proto",
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_grpc_client"].requires.append("opentelemetry_proto_grpc")

            self.cpp_info.components["opentelemetry_exporter_otlp_grpc"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_grpc_client"
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_grpc_metrics"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_grpc_client"
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_grpc_log"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_grpc_client",
            ])

        if (self.options.with_otlp_http or
            self.options.with_zipkin or
            self.options.with_elasticsearch
        ):
            self.cpp_info.components[self._http_client_name].requires.append("libcurl::libcurl")

        if self.options.with_otlp_http:
            self.cpp_info.components["opentelemetry_exporter_otlp_http_client"].requires.extend([
                self._http_client_name,
                "nlohmann_json::nlohmann_json",
                "opentelemetry_proto",
            ])

            if self.options.with_otlp_http_compression:
                self.cpp_info.components["opentelemetry_exporter_otlp_http_client"].requires.append("zlib::zlib")

            self.cpp_info.components["opentelemetry_exporter_otlp_http"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_http_client",
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_http_metric"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_http_client"
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_http_log"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_http_client",
            ])

        if self.options.get_safe("with_otlp_file"):
            self.cpp_info.components["opentelemetry_exporter_otlp_file_client"].requires.extend([
                "nlohmann_json::nlohmann_json",
                "opentelemetry_proto",
                "opentelemetry_common"
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_file"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_file_client",
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_file_log"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_file_client",
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_file_metric"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_file_client",
            ])

        if self.options.with_zipkin:
            self.cpp_info.components["opentelemetry_exporter_zipkin_trace"].requires.extend([
                self._http_client_name,
                "nlohmann_json::nlohmann_json",
                "opentelemetry_trace",
            ])

        if self.options.with_prometheus:
            self.cpp_info.components["opentelemetry_exporter_prometheus"].requires.extend([
                "prometheus-cpp::prometheus-cpp",
                "opentelemetry_trace",
            ])

        if self.options.get_safe("with_etw"):
            self.cpp_info.components["opentelemetry_exporter_etw"].libs = []
            self.cpp_info.components["opentelemetry_exporter_etw"].requires.append(
                "nlohmann_json::nlohmann_json",
            )
