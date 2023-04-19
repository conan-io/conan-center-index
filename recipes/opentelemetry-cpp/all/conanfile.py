from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import check_min_vs

import os
import textwrap

required_conan_version = ">=1.53.0"

class OpenTelemetryCppConan(ConanFile):
    name = "opentelemetry-cpp"
    description = "The C++ OpenTelemetry API and SDK"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open-telemetry/opentelemetry-cpp"
    topics = ("opentelemetry", "telemetry", "tracing", "metrics", "logs")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_no_deprecated_code": [True, False],
        "with_stl": [True, False],
        "with_gsl": [True, False],
        "with_abseil": [True, False],
        "with_otlp": [True, False],
        "with_otlp_grpc": [True, False],
        "with_otlp_http": [True, False],
        "with_zipkin": [True, False],
        "with_prometheus": [True, False],
        "with_elasticsearch": [True, False],
        "with_zpages": [True, False],
        "with_jaeger": [True, False],
        "with_no_getenv": [True, False],
        "with_etw": [True, False],
        "with_logs_preview": [True, False],
        "with_async_export_preview": [True, False],
        "with_metrics_exemplar_preview": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,

        "with_no_deprecated_code": False,
        "with_stl": False,
        "with_gsl": False,
        "with_abseil": True,
        "with_otlp": True,
        "with_otlp_grpc": True,
        "with_otlp_http": True,
        "with_zipkin": True,
        "with_prometheus": False,
        "with_elasticsearch": False,
        "with_zpages": False,
        "with_jaeger": True,
        "with_no_getenv": False,
        "with_etw": False,
        "with_logs_preview": False,
        "with_async_export_preview": False,
        "with_metrics_exemplar_preview": False,
    }
    short_paths = True

    @property
    def _minimum_cpp_standard(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if not self.options.with_otlp:
            self.options.rm_safe("with_otlp_grpc")
            self.options.rm_safe("with_otlp_http")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_gsl:
            self.requires("ms-gsl/4.0.0")

        if self.options.with_abseil:
            self.requires("abseil/20220623.0")

        if self.options.with_otlp:
            self.requires("protobuf/3.21.4")
            if Version(self.version) <= "1.4.1":
                self.requires("opentelemetry-proto/0.11.0")
            else:
                self.requires("opentelemetry-proto/0.19.0")

            if self.options.get_safe("with_otlp_grpc"):
                self.requires("grpc/1.50.1")

        if (self.options.with_zipkin or
           self.options.with_elasticsearch or
           self.options.get_safe("with_otlp_http") or
           self.options.with_etw
        ):
           self.requires("nlohmann_json/3.11.2")
           self.requires("openssl/1.1.1t")

        if (self.options.with_zipkin or
           self.options.with_elasticsearch or
           self.options.get_safe("with_otlp_http")
        ):
           self.requires("libcurl/7.87.0")

        if self.options.with_prometheus:
            self.requires("prometheus-cpp/1.1.0")

        if self.options.with_jaeger:
            self.requires("thrift/0.17.0")

            if Version(self.version) >= "1.3.0":
                self.requires("boost/1.81.0")

    @property
    def _required_boost_components(self):
        return ["locale"] if self.options.with_jaeger and Version(self.version) >= "1.3.0" else []

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        check_min_vs(self, "192")

        if self.settings.os != "Linux" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} supports building shared libraries only on Linux")

        if self.options.get_safe("with_otlp_grpc") and not self.options.with_otlp:
            raise ConanInvalidConfiguration("Option 'with_otlp_grpc' requires 'with_otlp'")

        if self.options.get_safe("with_otlp_http") and not self.options.with_otlp:
            raise ConanInvalidConfiguration("Option 'with_otlp_http' requires 'with_otlp'")

        if not self.dependencies["grpc"].options.cpp_plugin:
            raise ConanInvalidConfiguration(f"{self.ref} requires grpc with cpp_plugin=True")

        boost_required_comp = any(self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
                                       for boost_comp in self._required_boost_components)

        if boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires boost with these components: "
                f"{', '.join(self._required_boost_components)}"
            )

    def build_requirements(self):
        self.tool_requires("protobuf/3.21.4")
        self.tool_requires("grpc/1.50.1")

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            set(OPENTELEMETRY_CPP_INCLUDE_DIRS ${opentelemetry-cpp_INCLUDE_DIRS}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_RELEASE}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_RELWITHDEBINFO}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_MINSIZEREL}
                                               ${opentelemetry-cpp_INCLUDE_DIRS_DEBUG})
            set(OPENTELEMETRY_CPP_LIBRARIES opentelemetry-cpp::opentelemetry-cpp)
        """)
        save(self, module_file, content)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_BENCHMARK"] = False

        tc.variables["WITH_NO_DEPRECATED_CODE"] = self.options.with_no_deprecated_code
        tc.variables["WITH_STL"] = self.options.with_stl
        tc.variables["WITH_GSL"] = self.options.with_gsl
        tc.variables["WITH_ABSEIL"] = self.options.with_abseil
        tc.variables["WITH_OTLP"] = self.options.with_otlp
        tc.variables["WITH_OTLP_GRPC"] = self.options.get_safe("with_otlp_grpc")
        tc.variables["WITH_OTLP_HTTP"] = self.options.get_safe("with_otlp_http")
        tc.variables["WITH_ZIPKIN"] = self.options.with_zipkin
        tc.variables["WITH_PROMETHEUS"] = self.options.with_prometheus
        tc.variables["WITH_ELASTICSEARCH"] = self.options.with_elasticsearch
        tc.variables["WITH_ZPAGES"] = self.options.with_zpages
        tc.variables["WITH_JAEGER"] = self.options.with_jaeger
        tc.variables["WITH_NO_GETENV"] = self.options.with_no_getenv
        tc.variables["WITH_ETW"] = self.options.with_etw
        tc.variables["WITH_LOGS_PREVIEW"] = self.options.with_logs_preview
        tc.variables["WITH_ASYNC_EXPORT_PREVIEW"] = self.options.with_async_export_preview
        tc.variables["WITH_METRICS_EXEMPLAR_PREVIEW"] = self.options.with_metrics_exemplar_preview

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        protos_path = self.deps_user_info["opentelemetry-proto"].proto_root.replace("\\", "/")
        protos_cmake_path = os.path.join(
            self.source_folder,
            "cmake",
            "opentelemetry-proto.cmake")
        if Version(self.version) >= "1.1.0":
            replace_in_file(self,
                protos_cmake_path,
                "if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/third_party/opentelemetry-proto/.git)",
                "if(1)")
        replace_in_file(self,
            protos_cmake_path,
            "set(PROTO_PATH \"${CMAKE_CURRENT_SOURCE_DIR}/third_party/opentelemetry-proto\")",
            f"set(PROTO_PATH \"{protos_path}\")")
        rmdir(self, os.path.join(self.source_folder, "api", "include", "opentelemetry", "nostd", "absl"))

        apply_conandata_patches(self)

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
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._otel_cmake_variables_path)
        )

    @property
    def _module_subfolder(self):
        return os.path.join(self.package_folder, "lib", "cmake")

    @property
    def _otel_cmake_variables_path(self):
        return os.path.join(self._module_subfolder,
                            f"conan-official-{self.name}-variables.cmake")

    @property
    def _otel_build_modules(self):
        return [self._otel_cmake_variables_path]

    @property
    def _http_client_name(self):
        return "http_client_curl" if Version(self.version) < "1.3.0" else "opentelemetry_http_client_curl"

    @property
    def _otel_libraries(self):
        libraries = [
            self._http_client_name,
            "opentelemetry_common",
            "opentelemetry_exporter_in_memory",
            "opentelemetry_exporter_ostream_span",
            "opentelemetry_resources",
            "opentelemetry_trace",
            "opentelemetry_version",
        ]

        if self.options.with_otlp:
            libraries.extend([
                "opentelemetry_proto",
                "opentelemetry_otlp_recordable",
                ])

            if self.options.get_safe("with_otlp_grpc"):
                libraries.append("opentelemetry_exporter_otlp_grpc")

                if Version(self.version) >= "1.5.0":
                    libraries.append("opentelemetry_exporter_otlp_grpc_metrics")

                if Version(self.version) >= "1.7.0":
                    libraries.append("opentelemetry_exporter_otlp_grpc_client")

                if self.options.with_logs_preview:
                    libraries.append("opentelemetry_exporter_otlp_grpc_log")

            if self.options.get_safe("with_otlp_http"):
                libraries.append("opentelemetry_exporter_otlp_http")

                if Version(self.version) >= "1.1.0":
                    libraries.append("opentelemetry_exporter_otlp_http_client")

                if Version(self.version) >= "1.5.0":
                    libraries.append("opentelemetry_exporter_otlp_http_metric")

                if self.options.with_logs_preview:
                    libraries.append("opentelemetry_exporter_otlp_http_log")

        if self.options.with_prometheus:
            libraries.append("opentelemetry_exporter_prometheus")

        if self.options.with_elasticsearch and self.options.with_logs_preview:
            libraries.append("opentelemetry_exporter_elasticsearch_logs")

        if self.options.with_zipkin:
            libraries.append("opentelemetry_exporter_zipkin_trace")

        if self.options.with_jaeger:
            libraries.append("opentelemetry_exporter_jaeger_trace")

        if Version(self.version) >= "1.2.0":
            libraries.append("opentelemetry_metrics")

        if Version(self.version) >= "1.4.0":
            libraries.append("opentelemetry_exporter_ostream_metrics")

        if self.options.with_logs_preview:
            libraries.extend([
                "opentelemetry_logs",
                "opentelemetry_exporter_ostream_logs",
            ])

        if self.settings.os == "Windows" and self.options.with_etw:
            libraries.append("opentelemetry_exporter_etw")

        return libraries

    def package_info(self):
        for lib in self._otel_libraries:
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].builddirs.append(self._module_subfolder)
            self.cpp_info.components[lib].build_modules["cmake_find_package"] = self._otel_build_modules
            self.cpp_info.components[lib].build_modules["cmake_find_package_multi"] = self._otel_build_modules

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

        if self.options.with_logs_preview:
            self.cpp_info.components["opentelemetry_logs"].requires.extend([
                "opentelemetry_resources",
                "opentelemetry_common",
            ])

            self.cpp_info.components["opentelemetry_exporter_ostream_logs"].requires.append(
                "opentelemetry_logs",
            )

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["opentelemetry_common"].system_libs.extend(["pthread"])

        if self.options.with_stl:
            self.cpp_info.components["opentelemetry_common"].defines.append("HAVE_CPP_STDLIB")

        if self.options.with_gsl:
            self.cpp_info.components["opentelemetry_common"].defines.append("HAVE_GSL")
            self.cpp_info.components["opentelemetry_common"].requires.append("ms-gsl::_ms-gsl")

        if self.options.with_abseil:
            self.cpp_info.components["opentelemetry_common"].defines.append("HAVE_ABSEIL")
            self.cpp_info.components["opentelemetry_common"].requires.append("abseil::abseil")

        if self.options.with_otlp:
            self.cpp_info.components["opentelemetry_proto"].requires.extend([
                "opentelemetry-proto::opentelemetry-proto",
                "protobuf::protobuf",
            ])

            self.cpp_info.components["opentelemetry_otlp_recordable"].requires.extend([
                "opentelemetry_proto",
                "opentelemetry_resources",
                "opentelemetry_trace",
            ])

        if self.options.get_safe("with_otlp_grpc"):
            if Version(self.version) >= "1.5.0" and Version(self.version) < "1.7.0":
                self.cpp_info.components["opentelemetry_exporter_otlp_grpc_metrics"].requires.extend([
                    "grpc::grpc++",
                    "opentelemetry_otlp_recordable",
                ])

            if Version(self.version) <= "1.7.0":
                self.cpp_info.components["opentelemetry_exporter_otlp_grpc"].requires.extend([
                    "grpc::grpc++",
                    "opentelemetry_otlp_recordable",
                ])

            if Version(self.version) >= "1.7.0":
                self.cpp_info.components["opentelemetry_exporter_otlp_grpc_client"].requires.extend([
                    "grpc::grpc++",
                    "opentelemetry_proto",
                ])

                self.cpp_info.components["opentelemetry_exporter_otlp_grpc"].requires.extend([
                    "opentelemetry_otlp_recordable",
                    "opentelemetry_exporter_otlp_grpc_client"
                ])

                self.cpp_info.components["opentelemetry_exporter_otlp_grpc_metrics"].requires.extend([
                    "opentelemetry_otlp_recordable",
                    "opentelemetry_exporter_otlp_grpc_client"
                ])

            if self.options.with_logs_preview:
                self.cpp_info.components["opentelemetry_exporter_otlp_grpc_log"].requires.extend([
                    "opentelemetry_otlp_recordable",
                    "opentelemetry_exporter_otlp_grpc_client",
                ])

        if (self.options.get_safe("with_otlp_http") or
            self.options.with_zipkin or
            self.options.with_elasticsearch
        ):
            self.cpp_info.components[self._http_client_name].requires.append("libcurl::libcurl")

        if self.options.get_safe("with_otlp_http"):
            self.cpp_info.components["opentelemetry_exporter_otlp_http_client"].requires.extend([
                self._http_client_name,
                "nlohmann_json::nlohmann_json",
                "opentelemetry_proto",
            ])

            self.cpp_info.components["opentelemetry_exporter_otlp_http"].requires.extend([
                "opentelemetry_otlp_recordable",
                "opentelemetry_exporter_otlp_http_client",
            ])

            if Version(self.version) >= "1.5.0":
                self.cpp_info.components["opentelemetry_exporter_otlp_http_metric"].requires.extend([
                    "opentelemetry_otlp_recordable",
                    "opentelemetry_exporter_otlp_http_client"
                ])

            if self.options.with_logs_preview:
                self.cpp_info.components["opentelemetry_exporter_otlp_http_log"].requires.extend([
                    "opentelemetry_otlp_recordable",
                    "opentelemetry_exporter_otlp_http_client",
                ])

        if self.options.with_zipkin:
            self.cpp_info.components["opentelemetry_exporter_zipkin_trace"].requires.extend([
                self._http_client_name,
                "nlohmann_json::nlohmann_json",
                "opentelemetry_trace",
            ])

        if self.options.with_jaeger:
            self.cpp_info.components["opentelemetry_exporter_jaeger_trace"].requires.extend([
                self._http_client_name,
                "openssl::openssl",
                "opentelemetry_resources",
                "thrift::thrift",
            ])

            if Version(self.version) >= "1.3.0":
                self.cpp_info.components["opentelemetry_exporter_jaeger_trace"].requires.append(
                    "boost::locale"
                )

        if self.settings.os == "Windows" and self.options.with_etw:
            self.cpp_info.components["opentelemetry_exporter_etw"].libs = []
            self.cpp_info.components["opentelemetry_exporter_etw"].requires.append(
                "nlohmann_json::nlohmann_json",
            )

