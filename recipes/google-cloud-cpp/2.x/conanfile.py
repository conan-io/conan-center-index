import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

# Load the generated component dependency information.
#
# `google-cloud-cpp` has well over 200 components. Conan cannot use the CMake
# files generated by `google-cloud-cpp`. Manually maintaining this dependency
# information is error prone and fairly tedious. A helper script in this
# directory reproduces the algorithms used by `google-cloud-cpp` to generate its
# dependency information. With each new revision of `google-cloud-cpp` the
# script will be used to generate a new file with the component dependency
# information. The expectation is that maintaining this script will be easier
# than writing long lists of dependencies by hand.
import components_2_12_0
import components_2_15_1
import components_2_19_0

required_conan_version = ">=1.56.0"


class GoogleCloudCppConan(ConanFile):
    name = "google-cloud-cpp"
    description = "C++ Client Libraries for Google Cloud Services"
    license = "Apache-2.0"
    topics = (
        "google",
        "cloud",
        "google-cloud-storage",
        "google-cloud-platform",
        "google-cloud-pubsub",
        "google-cloud-spanner",
        "google-cloud-bigtable",
    )
    homepage = "https://github.com/googleapis/google-cloud-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports = ["components_2_12_0.py",
               "components_2_15_1.py",
               "components_2_19_0.py",
               ]

    short_paths = True

    _GA_COMPONENTS = {
        '2.12.0': components_2_12_0.COMPONENTS,
        '2.15.1': components_2_15_1.COMPONENTS,
        '2.19.0': components_2_19_0.COMPONENTS,
    }
    _PROTO_COMPONENTS = {
        '2.12.0': components_2_12_0.PROTO_COMPONENTS,
        '2.15.1': components_2_15_1.PROTO_COMPONENTS,
        '2.19.0': components_2_19_0.PROTO_COMPONENTS,
    }
    _PROTO_COMPONENT_DEPENDENCIES = {
        "2.12.0": components_2_12_0.DEPENDENCIES,
        "2.15.1": components_2_15_1.DEPENDENCIES,
        "2.19.0": components_2_19_0.DEPENDENCIES,
    }
    # Some components require custom dependency definitions.
    _REQUIRES_CUSTOM_DEPENDENCIES = {
        "bigquery", "bigtable", "iam", "oauth2", "pubsub", "spanner", "storage",
    }

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["protobuf"].shared = True
            self.options["grpc"].shared = True

    def validate(self):
        # As-of 2022-03, google-cloud-cpp only supports "Visual Studio >= 2019",
        # and Visual Studio < 2019 is out of mainline support.
        # The wikipedia page says this maps to 192* for the MSVC version:
        #   https://en.wikipedia.org/wiki/Microsoft_Visual_C%2B%2B
        check_min_vs(self, "192")
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported by Visual Studio")

        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration(
                "Recipe not prepared for cross-building (yet)"
            )

        if str(self.version) not in self._GA_COMPONENTS:
            print(f"{type(self.version)} {self.version}")
            raise ConanInvalidConfiguration(
                f"The components are unknown for version {self.version}. Expected one of {self._GA_COMPONENTS.keys()}"
            )

        if str(self.version) not in self._PROTO_COMPONENTS:
            raise ConanInvalidConfiguration(
                f"The proto components are unknown for version {self.version}. Expected one of {self._PROTO_COMPONENTS.keys()}"
            )

        if str(self.version) not in self._PROTO_COMPONENT_DEPENDENCIES:
            raise ConanInvalidConfiguration(
                f"The inter-component components are unknown for version {self.version}. Expected one of {self._PROTO_COMPONENT_DEPENDENCIES.keys()}"
            )

        if (
            self.settings.compiler == "clang"
            and Version(self.settings.compiler.version) < "6.0"
        ):
            raise ConanInvalidConfiguration("Clang version must be at least 6.0.")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

        if (
            self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) < "5.4"
        ):
            raise ConanInvalidConfiguration("Building requires GCC >= 5.4")

        if self.info.options.shared and \
           (not self.dependencies["protobuf"].options.shared or \
            not self.dependencies["grpc"].options.shared):
            raise ConanInvalidConfiguration(
                "If built as shared, protobuf, and grpc must be shared as well."
                " Please, use `protobuf/*:shared=True`, and `grpc/*:shared=True`.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def requirements(self):
        # These must remain pinned in conan index.
        self.requires("protobuf/3.21.12", transitive_headers=True)
        self.requires("abseil/20230125.3", transitive_headers=True)
        self.requires("grpc/1.54.3", transitive_headers=True)
        self.requires("nlohmann_json/3.11.3")
        self.requires("crc32c/1.1.2")
        # The rest require less pinning.
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")

    def build_requirements(self):
        # For the `grpc-cpp-plugin` executable, and indirectly `protoc`
        if not self._is_legacy_one_profile:
            self.tool_requires("grpc/<host_version>")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["GOOGLE_CLOUD_CPP_ENABLE_MACOS_OPENSSL_CHECK"] = False
        tc.variables["GOOGLE_CLOUD_CPP_ENABLE_WERROR"] = False
        tc.variables["GOOGLE_CLOUD_CPP_ENABLE"] = ",".join(self._components())
        tc.generate()
        VirtualBuildEnv(self).generate()
        if self._is_legacy_one_profile:
            VirtualRunEnv(self).generate(scope="build")
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # This was informed by comments in the grpc port. On macOS `Make` will
        # run commands via `/bin/sh`. `/bin/sh` is subject to System Integrity
        # Protections.  In particular, the system will purge the DYLD_LIBRARY_PATH
        # enviroment variables:
        #     https://developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/RuntimeProtections/RuntimeProtections.html
        settings_build = getattr(self, "settings_build", self.settings)
        if settings_build.os == "Macos":
            if Version(self.version) < '2.12.0':
                replace_in_file(self, os.path.join(self.source_folder, "cmake/CompileProtos.cmake"),
                                "$<TARGET_FILE:protobuf::protoc>",
                                '${CMAKE_COMMAND} -E env "DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}" $<TARGET_FILE:protobuf::protoc>')
            else:
                replace_in_file(self, os.path.join(self.source_folder, "cmake/CompileProtos.cmake"),
                                "${Protobuf_PROTOC_EXECUTABLE} ARGS",
                                '${CMAKE_COMMAND} -E env "DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}" ${Protobuf_PROTOC_EXECUTABLE} ARGS')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _generate_proto_requires(self, component):
        deps = self._PROTO_COMPONENT_DEPENDENCIES.get(self.version, dict())
        return deps.get(component, [])

    _SKIPPED_COMPONENTS = {
        # Some protos do not compile due to inconvenient system macros clashing
        # with proto enum values. Protobuf can workaround these problems, but
        # the current version in Conan index (protobuf/3.21.4) do not contain
        # the fixes for these cases.
        # TODO - review after protobuf >= 4.23.x
        'asset',
        'channel',
        'storagetransfer',
        # TODO - certificatemanager crashes the gRPC code generator. Add it back
        # after gRPC >= 1.53.x
        'certificatemanager',
    }

    def _components(self):
        result = self._GA_COMPONENTS.get(str(self.version), []).copy()
        for c in self._SKIPPED_COMPONENTS:
            result.remove(c)
        # TODO - these do not build on Android due to conflicts between OS
        # macros and Proto enums. Revisit after Protobuf >= 4.23.x
        if self.settings.os == "Android":
            result.remove('accesscontextmanager')
            result.remove('talent')
        return result

    def _proto_components(self):
        result = self._PROTO_COMPONENTS.get(self.version, []).copy()
        for c in self._SKIPPED_COMPONENTS:
            result.remove(c + '_protos')
        # TODO - these do not build on Android due to conflicts between OS
        # macros and Proto enums. Revisit after Protobuf >= 4.23.x
        if self.settings.os == "Android":
            result.remove('accesscontextmanager_protos')
            result.remove('talent_protos')
        if Version(self.version) >= '2.15.1':
            # This was converted to an interface library starting on 2.15.1
            result.remove('logging_type_type_protos')
            # These were removed (as they are not used) starting on 2.15.1
            result.remove('devtools_source_v1_source_context_protos')
        return result

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, path=os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, path=os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _add_proto_component(self, component):
        self.cpp_info.components[component].requires = self._generate_proto_requires(component)
        self.cpp_info.components[component].libs = [f"google_cloud_cpp_{component}"]
        self.cpp_info.components[component].names["pkg_config"] = f"google_cloud_cpp_{component}"

    def _add_grpc_component(self, component, protos, extra=None):
        SHARED_REQUIRES=["grpc_utils", "common", "grpc::grpc++", "grpc::_grpc", "protobuf::libprotobuf", "abseil::absl_memory"]
        self.cpp_info.components[component].requires = (extra or []) + [protos] + SHARED_REQUIRES
        self.cpp_info.components[component].libs = [f"google_cloud_cpp_{component}"]
        self.cpp_info.components[component].names["pkg_config"] = f"google_cloud_cpp_{component}"

    # The compute librar(ies) do not use gRPC, and they have many components
    # with dependencies between them
    def _add_compute_component(self, component, protos):
        SHARED_REQUIRES=["rest_protobuf_internal", "rest_internal", "common"]
        # Common components shared by other compute components
        COMPUTE_COMMON_COMPONENTS = [
            'compute_global_operations',
            'compute_global_organization_operations',
            'compute_region_operations',
            'compute_zone_operations',
        ]
        requires = [protos]
        if component not in COMPUTE_COMMON_COMPONENTS:
            requires = requires + COMPUTE_COMMON_COMPONENTS
        self.cpp_info.components[component].requires = requires + SHARED_REQUIRES
        self.cpp_info.components[component].libs = [f"google_cloud_cpp_{component}"]
        self.cpp_info.components[component].names["pkg_config"] = f"google_cloud_cpp_{component}"

    def package_info(self):
        self.cpp_info.components["common"].requires = ["abseil::absl_any", "abseil::absl_flat_hash_map", "abseil::absl_memory", "abseil::absl_optional", "abseil::absl_time"]
        self.cpp_info.components["common"].libs = ["google_cloud_cpp_common"]
        self.cpp_info.components["common"].names["pkg_config"] = "google_cloud_cpp_common"

        self.cpp_info.components["rest_internal"].requires = ["common", "libcurl::libcurl", "openssl::ssl", "openssl::crypto", "zlib::zlib"]
        self.cpp_info.components["rest_internal"].libs = ["google_cloud_cpp_rest_internal"]
        self.cpp_info.components["rest_internal"].names["pkg_config"] = "google_cloud_cpp_rest_internal"

        # A small number of gRPC-generated stubs are used directly in the common components
        # shared by all gRPC-based libraries.  These must be defined without reference to `grpc_utils`.
        if Version(self.version) >= '2.15.1':
            GRPC_UTILS_REQUIRED_PROTOS = {
                "iam_credentials_v1_iamcredentials_protos",
                "iam_v1_policy_protos",
                "longrunning_operations_protos",
                "rpc_error_details_protos",
                "rpc_status_protos",
            }
        else:
            GRPC_UTILS_REQUIRED_PROTOS = {
                "iam_protos",
                "longrunning_operations_protos",
                "rpc_error_details_protos",
                "rpc_status_protos",
            }
        for component in GRPC_UTILS_REQUIRED_PROTOS:
            self._add_proto_component(component)

        self.cpp_info.components["grpc_utils"].requires = list(GRPC_UTILS_REQUIRED_PROTOS) + ["common", "abseil::absl_function_ref", "abseil::absl_memory", "abseil::absl_time", "grpc::grpc++", "grpc::_grpc"]
        self.cpp_info.components["grpc_utils"].libs = ["google_cloud_cpp_grpc_utils"]
        self.cpp_info.components["grpc_utils"].names["pkg_config"] = "google_cloud_cpp_grpc_utils"

        for component in self._proto_components():
            if Version(self.version) >= '2.15.1' and component == 'storage_protos':
                # Starting with v2.15.1 the `storage_protos` are compiled only
                # when needed. They are not used in Conan because they are only
                # needed for an experimental library, supporting an allow-listed
                # service.
                continue
            if component not in GRPC_UTILS_REQUIRED_PROTOS:
                self._add_proto_component(component)

        # Interface libraries for backwards compatibility
        if Version(self.version) < '2.15.1':
            self.cpp_info.components["dialogflow_es_protos"].requires = ["cloud_dialogflow_v2_protos"]
            self.cpp_info.components["logging_type_protos"].requires = ["logging_type_type_protos"]
            self.cpp_info.components["speech_protos"].requires = ["cloud_speech_protos"]
            self.cpp_info.components["texttospeech_protos"].requires = ["cloud_texttospeech_protos"]
            self.cpp_info.components["trace_protos"].requires = [
                "devtools_cloudtrace_v2_trace_protos",
                "devtools_cloudtrace_v2_tracing_protos",
            ]
            self._add_grpc_component("bigquery", "cloud_bigquery_protos")
        else:
            self.cpp_info.components["cloud_bigquery_protos"].requires = ["bigquery_protos"]
            self.cpp_info.components["cloud_dialogflow_v2_protos"].requires = ["dialogflow_es_protos"]
            self.cpp_info.components["cloud_speech_protos"].requires = ["speech_protos"]
            self.cpp_info.components["cloud_texttospeech_protos"].requires = ["texttospeech_protos"]
            self.cpp_info.components["devtools_cloudtrace_v2_trace_protos"].requires = ["trace_protos"]
            self.cpp_info.components["devtools_cloudtrace_v2_tracing_protos"].requires = ["trace_protos"]
            self.cpp_info.components["logging_type_type_protos"].requires = ["logging_type_protos"]

        for component in self._components():
            protos=f"{component}_protos"
            # bigquery proto library predates the adoption of more consistent naming
            if component == 'bigquery' and Version(self.version) < '2.15.1':
                self._add_proto_component("cloud_bigquery_protos")
                self._add_grpc_component(component, "cloud_bigquery_protos")
                continue
            if component == 'dialogflow_es' and Version(self.version) < '2.15.1':
                self._add_proto_component("cloud_dialogflow_v2_protos")
                self._add_grpc_component(component, "cloud_dialogflow_v2_protos")
                continue
            # `compute` components do not depend on gRPC
            if component.startswith("compute_"):
                self._add_compute_component(component, protos)
                continue
            # `storage` is the only component that does not depend on a matching `*_protos` library
            if component in self._REQUIRES_CUSTOM_DEPENDENCIES:
                continue
            self._add_grpc_component(component, protos)

        self._add_grpc_component("bigtable", "bigtable_protos")
        self._add_grpc_component("iam", "iam_protos")
        self._add_grpc_component("pubsub", "pubsub_protos", ["abseil::absl_flat_hash_map"])
        self._add_grpc_component("spanner", "spanner_protos",  ["abseil::absl_fixed_array", "abseil::absl_numeric", "abseil::absl_strings", "abseil::absl_time"])

        if Version(self.version) >= '2.19.0':
            self.cpp_info.components["rest_protobuf_internal"].requires = ["rest_internal", "grpc_utils", "common"]
            self.cpp_info.components["rest_protobuf_internal"].libs = ["google_cloud_cpp_rest_protobuf_internal"]
            self.cpp_info.components["rest_protobuf_internal"].names["pkg_config"] = "google_cloud_cpp_rest_protobuf_internal"
            # The `google-cloud-cpp::compute` interface library groups all the compute
            # libraries in a single target.
            self.cpp_info.components["compute"].requires = [c for c in self._components() if c.startswith("compute_")]
            # The `google-cloud-cpp::oauth2` library does not depend on gRPC or any protos.
            self.cpp_info.components["oauth2"].requires = ["rest_internal", "common", "nlohmann_json::nlohmann_json", "libcurl::libcurl", "openssl::ssl", "openssl::crypto", "zlib::zlib"]
            self.cpp_info.components["oauth2"].libs = ["google_cloud_cpp_oauth2"]
            self.cpp_info.components["oauth2"].names["pkg_config"] = "google_cloud_cpp_oauth2"

        self.cpp_info.components["storage"].requires = ["rest_internal", "common", "nlohmann_json::nlohmann_json", "abseil::absl_memory", "abseil::absl_strings", "abseil::absl_str_format", "abseil::absl_time", "abseil::absl_variant", "crc32c::crc32c", "libcurl::libcurl", "openssl::ssl", "openssl::crypto", "zlib::zlib"]
        self.cpp_info.components["storage"].libs = ["google_cloud_cpp_storage"]
        self.cpp_info.components["storage"].names["pkg_config"] = "google_cloud_cpp_storage"
