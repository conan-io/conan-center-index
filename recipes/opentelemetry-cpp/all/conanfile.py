from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import check_min_vs

import os
import textwrap

required_conan_version = ">=1.52.0"

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
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }
    short_paths = True

    @property
    def _minimum_cpp_standard(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20220623.0")
        self.requires("grpc/1.48.0")
        self.requires("libcurl/7.85.0")
        self.requires("nlohmann_json/3.11.2")
        self.requires("openssl/1.1.1q")
        if Version(self.version) <= "1.4.1":
            self.requires("opentelemetry-proto/0.11.0")
        else:
            self.requires("opentelemetry-proto/0.19.0")
        self.requires("protobuf/3.21.4")
        self.requires("thrift/0.17.0")
        if Version(self.version) >= "1.3.0":
            self.requires("boost/1.80.0")

    def validate(self):
        if self.info.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support architecture : {self.info.settings.arch}")

        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        check_min_vs(self, "192")

        if self.settings.os != "Linux" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} supports building shared libraries only on Linux")

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
        tc.variables["WITH_ABSEIL"] = True
        tc.variables["WITH_ETW"] = True
        tc.variables["WITH_EXAMPLES"] = False
        tc.variables["WITH_JAEGER"] = True
        tc.variables["WITH_OTLP"] = True
        tc.variables["WITH_ZIPKIN"] = True
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

        self.cpp_info.components[self._http_client_name].requires.extend(["libcurl::libcurl"])

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
            self._http_client_name,
            "openssl::openssl",
            "opentelemetry_resources",
            "thrift::thrift",
        ])
        if Version(self.version) >= "1.3.0":
            self.cpp_info.components["opentelemetry_exporter_jaeger_trace"].requires.extend([
                "boost::locale",
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
            self._http_client_name,
            "nlohmann_json::nlohmann_json",
            "opentelemetry_otlp_recordable",
        ])

        self.cpp_info.components["opentelemetry_exporter_zipkin_trace"].requires.extend([
            self._http_client_name,
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
