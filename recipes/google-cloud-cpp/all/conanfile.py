import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GoogleCloudCppConan(ConanFile):
    name = "google-cloud-cpp"
    description = "C++ Client Libraries for Google Cloud Services"
    license = "Apache-2.0"
    topics = (
        "google", "cloud", "google-cloud-storage", "google-cloud-platform",
        "google-cloud-pubsub", "google-cloud-spanner", "google-cloud-bigtable"
    )
    homepage = "https://github.com/googleapis/google-cloud-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    @property
    def _minimum_compiler_versions(self):
        return {
            "gcc": "5.4",
            "clang": "6",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/[>=20230125.3 <=20230802.1]", transitive_headers=True)
        self.requires("crc32c/1.1.2")
        self.requires("grpc/1.54.3")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("nlohmann_json/3.11.3")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("protobuf/3.21.12")
        # TODO: googleapis is hard to unvendorize, as it creates google-cloud-cpp:: targets
        #  and it's not trivial to replace them with the googleapis:: targets,
        #  there's not clean 1:1 mapping between them either way
        # self.requires("googleapis/cci.20220531")

    def build_requirements(self):
        self.tool_requires("grpc/<host_version>")
        self.tool_requires("protobuf/<host_version>")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Fails to compile for Windows as a DLL")

        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Recipe not prepared for cross-building (yet)")

        if self.settings.compiler.get_safe("cppstd"):
            if self.settings.compiler == "msvc":
                check_min_cppstd(self, 20)
            check_min_cppstd(self, 11)

        check_min_vs(self, "192")

        minimum_version = self._minimum_compiler_versions.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires {self.settings.compiler} >= {minimum_version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = 0
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_WERROR"] = False
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_MACOS_OPENSSL_CHECK"] = False
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_CCACHE"] = False
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_BIGTABLE"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_BIGQUERY"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_SPANNER"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_STORAGE"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_FIRESTORE"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_PUBSUB"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_IAM"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_LOGGING"] = True
        tc.cache_variables["GOOGLE_CLOUD_CPP_ENABLE_GENERATOR"] = False

        if is_msvc(self):
            tc.preprocessor_definitions["_SILENCE_CXX20_REL_OPS_DEPRECATION_WARNING"] = 1
            tc.preprocessor_definitions["_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING"] = 1
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if Version(self.version) < "1.33.0":
            # Do not override CMAKE_CXX_STANDARD if provided
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                textwrap.dedent("""\
                    set(CMAKE_CXX_STANDARD
                        11
                        CACHE STRING "Configure the C++ standard version for all targets.")"""),
                textwrap.dedent("""\
                    if(NOT "${CMAKE_CXX_STANDARD}")
                        set(CMAKE_CXX_STANDARD 11 CACHE STRING "Configure the C++ standard version for all targets.")
                    endif()
                    """))
        if self.version == "1.40.1":
            replace_in_file(self, os.path.join(self.source_folder, "google", "cloud", "internal", "openssl_util.h"),
                "#include <vector>", "#include <vector>\n#include <algorithm>")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["common"].requires = ["abseil::absl_any", "abseil::absl_flat_hash_map", "abseil::absl_memory", "abseil::absl_optional", "abseil::absl_time"]
        self.cpp_info.components["common"].libs = ["google_cloud_cpp_common"]
        self.cpp_info.components["common"].set_property("pkg_config_name", "google_cloud_cpp_common")

        self.cpp_info.components["experimental-bigquery"].requires = ["grpc_utils", "common", "cloud_bigquery_protos"]
        self.cpp_info.components["experimental-bigquery"].libs = ["google_cloud_cpp_bigquery"]
        self.cpp_info.components["experimental-bigquery"].set_property("pkg_config_name", "google_cloud_cpp_bigquery")

        self.cpp_info.components["bigtable"].requires = ["abseil::absl_memory", "bigtable_protos", "common", "grpc_utils", "grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["bigtable"].libs = ["google_cloud_cpp_bigtable"]
        self.cpp_info.components["bigtable"].set_property("pkg_config_name", "google_cloud_cpp_bigtable")

        if Version(self.version) < "1.40.1":  # FIXME: Probably this library was removed before
            self.cpp_info.components["experimental-firestore"].requires = ["common"]
            self.cpp_info.components["experimental-firestore"].libs = ["google_cloud_cpp_firestore"]
            self.cpp_info.components["experimental-firestore"].set_property("pkg_config_name", "google_cloud_cpp_firestore")

        self.cpp_info.components["bigtable_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos", "longrunning_operations_protos", "rpc_status_protos", "api_auth_protos"]
        self.cpp_info.components["bigtable_protos"].libs = ["google_cloud_cpp_bigtable_protos"]
        self.cpp_info.components["bigtable_protos"].set_property("pkg_config_name", "google_cloud_cpp_bigtable_protos")

        self.cpp_info.components["cloud_bigquery_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos", "rpc_status_protos", "api_http_protos"]
        self.cpp_info.components["cloud_bigquery_protos"].libs = ["google_cloud_cpp_cloud_bigquery_protos"]
        self.cpp_info.components["cloud_bigquery_protos"].set_property("pkg_config_name", "google_cloud_cpp_cloud_bigquery_protos")

        self.cpp_info.components["cloud_speech_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "longrunning_operations_protos", "rpc_status_protos"]
        self.cpp_info.components["cloud_speech_protos"].libs = ["google_cloud_cpp_cloud_speech_protos"]
        self.cpp_info.components["cloud_speech_protos"].set_property("pkg_config_name", "google_cloud_cpp_cloud_speech_protos")

        self.cpp_info.components["cloud_texttospeech_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos"]
        self.cpp_info.components["cloud_texttospeech_protos"].libs = ["google_cloud_cpp_cloud_texttospeech_protos"]
        self.cpp_info.components["cloud_texttospeech_protos"].set_property("pkg_config_name", "google_cloud_cpp_cloud_texttospeech_protos")

        self.cpp_info.components["iam_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos"]
        self.cpp_info.components["iam_protos"].libs = ["google_cloud_cpp_iam_protos"]
        self.cpp_info.components["iam_protos"].set_property("pkg_config_name", "google_cloud_cpp_iam_protos")

        self.cpp_info.components["pubsub_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos"]
        self.cpp_info.components["pubsub_protos"].libs = ["google_cloud_cpp_pubsub_protos"]
        self.cpp_info.components["pubsub_protos"].set_property("pkg_config_name", "google_cloud_cpp_pubsub_protos")

        self.cpp_info.components["spanner_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos", "longrunning_operations_protos", "rpc_status_protos"]
        self.cpp_info.components["spanner_protos"].libs = ["google_cloud_cpp_spanner_protos"]
        self.cpp_info.components["spanner_protos"].set_property("pkg_config_name", "google_cloud_cpp_spanner_protos")

        self.cpp_info.components["storage_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos"]
        self.cpp_info.components["storage_protos"].libs = ["google_cloud_cpp_storage_protos"]
        self.cpp_info.components["storage_protos"].set_property("pkg_config_name", "google_cloud_cpp_storage_protos")

        self.cpp_info.components["longrunning_operations_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "rpc_status_protos"]
        self.cpp_info.components["longrunning_operations_protos"].libs = ["google_cloud_cpp_longrunning_operations_protos"]
        self.cpp_info.components["longrunning_operations_protos"].set_property("pkg_config_name", "google_cloud_cpp_longrunning_operations_protos")

        self.cpp_info.components["api_http_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_http_protos"].libs = ["google_cloud_cpp_api_http_protos"]
        self.cpp_info.components["api_http_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_http_protos")

        self.cpp_info.components["api_annotations_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_http_protos"]
        self.cpp_info.components["api_annotations_protos"].libs = ["google_cloud_cpp_api_annotations_protos"]
        self.cpp_info.components["api_annotations_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_annotations_protos")

        self.cpp_info.components["api_auth_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
        self.cpp_info.components["api_auth_protos"].libs = ["google_cloud_cpp_api_auth_protos"]
        self.cpp_info.components["api_auth_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_auth_protos")

        self.cpp_info.components["api_client_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_client_protos"].libs = ["google_cloud_cpp_api_client_protos"]
        self.cpp_info.components["api_client_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_client_protos")

        self.cpp_info.components["api_distribution_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_distribution_protos"].libs = ["google_cloud_cpp_api_distribution_protos"]
        self.cpp_info.components["api_distribution_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_distribution_protos")

        self.cpp_info.components["api_field_behavior_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_field_behavior_protos"].libs = ["google_cloud_cpp_api_field_behavior_protos"]
        self.cpp_info.components["api_field_behavior_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_field_behavior_protos")

        self.cpp_info.components["api_label_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_label_protos"].libs = ["google_cloud_cpp_api_label_protos"]
        self.cpp_info.components["api_label_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_label_protos")

        self.cpp_info.components["api_launch_stage_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_launch_stage_protos"].libs = ["google_cloud_cpp_api_launch_stage_protos"]
        self.cpp_info.components["api_launch_stage_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_launch_stage_protos")

        self.cpp_info.components["api_metric_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_launch_stage_protos", "api_label_protos"]
        self.cpp_info.components["api_metric_protos"].libs = ["google_cloud_cpp_api_metric_protos"]
        self.cpp_info.components["api_metric_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_metric_protos")

        self.cpp_info.components["api_monitored_resource_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_launch_stage_protos", "api_label_protos"]
        self.cpp_info.components["api_monitored_resource_protos"].libs = ["google_cloud_cpp_api_monitored_resource_protos"]
        self.cpp_info.components["api_monitored_resource_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_monitored_resource_protos")

        self.cpp_info.components["api_resource_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["api_resource_protos"].libs = ["google_cloud_cpp_api_resource_protos"]
        self.cpp_info.components["api_resource_protos"].set_property("pkg_config_name", "google_cloud_cpp_api_resource_protos")

        self.cpp_info.components["devtools_cloudtrace_v2_trace_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_field_behavior_protos", "api_resource_protos", "rpc_status_protos"]
        self.cpp_info.components["devtools_cloudtrace_v2_trace_protos"].libs = ["google_cloud_cpp_devtools_cloudtrace_v2_trace_protos"]
        self.cpp_info.components["devtools_cloudtrace_v2_trace_protos"].set_property("pkg_config_name", "google_cloud_cpp_devtools_cloudtrace_v2_trace_protos")

        self.cpp_info.components["devtools_cloudtrace_v2_tracing_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "devtools_cloudtrace_v2_trace_protos", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "rpc_status_protos"]
        self.cpp_info.components["devtools_cloudtrace_v2_tracing_protos"].libs = ["google_cloud_cpp_devtools_cloudtrace_v2_tracing_protos"]
        self.cpp_info.components["devtools_cloudtrace_v2_tracing_protos"].set_property("pkg_config_name", "google_cloud_cpp_devtools_cloudtrace_v2_tracing_protos")

        cmp_logging_type_type_protos = None
        if Version(self.version) < "1.40.1":  # FIXME: Probably this library was removed before
            cmp_logging_type_type_protos = "logging_type_protos"
            self.cpp_info.components[cmp_logging_type_type_protos].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
            self.cpp_info.components[cmp_logging_type_type_protos].libs = ["google_cloud_cpp_logging_type_protos"]
            self.cpp_info.components[cmp_logging_type_type_protos].set_property("pkg_config_name", "google_cloud_cpp_logging_type_protos")
        else:
            cmp_logging_type_type_protos = "logging_type_type_protos"
            self.cpp_info.components[cmp_logging_type_type_protos].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
            self.cpp_info.components[cmp_logging_type_type_protos].libs = ["google_cloud_cpp_logging_type_type_protos"]
            self.cpp_info.components[cmp_logging_type_type_protos].set_property("pkg_config_name", "google_cloud_cpp_logging_type_type_protos")

        self.cpp_info.components["logging_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_distribution_protos", "api_field_behavior_protos", "api_metric_protos", "api_monitored_resource_protos", "api_resource_protos", cmp_logging_type_type_protos, "rpc_status_protos"]
        self.cpp_info.components["logging_protos"].libs = ["google_cloud_cpp_logging_protos"]
        self.cpp_info.components["logging_protos"].set_property("pkg_config_name", "google_cloud_cpp_logging_protos")

        self.cpp_info.components["monitoring_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_distribution_protos", "api_field_behavior_protos", "api_label_protos", "api_launch_stage_protos", "api_metric_protos", "api_monitored_resource_protos", "api_resource_protos", "rpc_status_protos", "type_calendar_period_protos"]
        self.cpp_info.components["monitoring_protos"].libs = ["google_cloud_cpp_monitoring_protos"]
        self.cpp_info.components["monitoring_protos"].set_property("pkg_config_name", "google_cloud_cpp_monitoring_protos")

        self.cpp_info.components["iam_v1_options_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
        self.cpp_info.components["iam_v1_options_protos"].libs = ["google_cloud_cpp_iam_v1_options_protos"]
        self.cpp_info.components["iam_v1_options_protos"].set_property("pkg_config_name", "google_cloud_cpp_iam_v1_options_protos")

        self.cpp_info.components["iam_v1_policy_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "type_expr_protos"]
        self.cpp_info.components["iam_v1_policy_protos"].libs = ["google_cloud_cpp_iam_v1_policy_protos"]
        self.cpp_info.components["iam_v1_policy_protos"].set_property("pkg_config_name", "google_cloud_cpp_iam_v1_policy_protos")

        self.cpp_info.components["iam_v1_iam_policy_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_options_protos", "iam_v1_policy_protos"]
        self.cpp_info.components["iam_v1_iam_policy_protos"].libs = ["google_cloud_cpp_iam_v1_iam_policy_protos"]
        self.cpp_info.components["iam_v1_iam_policy_protos"].set_property("pkg_config_name", "google_cloud_cpp_iam_v1_iam_policy_protos")

        self.cpp_info.components["rpc_error_details_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["rpc_error_details_protos"].libs = ["google_cloud_cpp_rpc_error_details_protos"]
        self.cpp_info.components["rpc_error_details_protos"].set_property("pkg_config_name", "google_cloud_cpp_rpc_error_details_protos")

        self.cpp_info.components["rpc_status_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "rpc_error_details_protos"]
        self.cpp_info.components["rpc_status_protos"].libs = ["google_cloud_cpp_rpc_status_protos"]
        self.cpp_info.components["rpc_status_protos"].set_property("pkg_config_name", "google_cloud_cpp_rpc_status_protos")

        self.cpp_info.components["type_calendar_period_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_calendar_period_protos"].libs = ["google_cloud_cpp_type_calendar_period_protos"]
        self.cpp_info.components["type_calendar_period_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_calendar_period_protos")

        self.cpp_info.components["type_color_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_color_protos"].libs = ["google_cloud_cpp_type_color_protos"]
        self.cpp_info.components["type_color_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_color_protos")

        self.cpp_info.components["type_date_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_date_protos"].libs = ["google_cloud_cpp_type_date_protos"]
        self.cpp_info.components["type_date_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_date_protos")

        self.cpp_info.components["type_datetime_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_datetime_protos"].libs = ["google_cloud_cpp_type_datetime_protos"]
        self.cpp_info.components["type_datetime_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_datetime_protos")

        self.cpp_info.components["type_dayofweek_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_dayofweek_protos"].libs = ["google_cloud_cpp_type_dayofweek_protos"]
        self.cpp_info.components["type_dayofweek_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_dayofweek_protos")

        self.cpp_info.components["type_expr_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_expr_protos"].libs = ["google_cloud_cpp_type_expr_protos"]
        self.cpp_info.components["type_expr_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_expr_protos")

        self.cpp_info.components["type_fraction_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_fraction_protos"].libs = ["google_cloud_cpp_type_fraction_protos"]
        self.cpp_info.components["type_fraction_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_fraction_protos")

        self.cpp_info.components["type_interval_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_interval_protos"].libs = ["google_cloud_cpp_type_interval_protos"]
        self.cpp_info.components["type_interval_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_interval_protos")

        self.cpp_info.components["type_latlng_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_latlng_protos"].libs = ["google_cloud_cpp_type_latlng_protos"]
        self.cpp_info.components["type_latlng_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_latlng_protos")

        self.cpp_info.components["type_localized_text_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_localized_text_protos"].libs = ["google_cloud_cpp_type_localized_text_protos"]
        self.cpp_info.components["type_localized_text_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_localized_text_protos")

        self.cpp_info.components["type_money_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_money_protos"].libs = ["google_cloud_cpp_type_money_protos"]
        self.cpp_info.components["type_money_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_money_protos")

        self.cpp_info.components["type_month_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_month_protos"].libs = ["google_cloud_cpp_type_month_protos"]
        self.cpp_info.components["type_month_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_month_protos")

        self.cpp_info.components["type_phone_number_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_phone_number_protos"].libs = ["google_cloud_cpp_type_phone_number_protos"]
        self.cpp_info.components["type_phone_number_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_phone_number_protos")

        self.cpp_info.components["type_postal_address_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_postal_address_protos"].libs = ["google_cloud_cpp_type_postal_address_protos"]
        self.cpp_info.components["type_postal_address_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_postal_address_protos")

        self.cpp_info.components["type_quaternion_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_quaternion_protos"].libs = ["google_cloud_cpp_type_quaternion_protos"]
        self.cpp_info.components["type_quaternion_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_quaternion_protos")

        self.cpp_info.components["type_timeofday_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
        self.cpp_info.components["type_timeofday_protos"].libs = ["google_cloud_cpp_type_timeofday_protos"]
        self.cpp_info.components["type_timeofday_protos"].set_property("pkg_config_name", "google_cloud_cpp_type_timeofday_protos")

        self.cpp_info.components["cloud_dialogflow_v2_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "longrunning_operations_protos", "rpc_status_protos", "type_latlng_protos"]
        self.cpp_info.components["cloud_dialogflow_v2_protos"].libs = ["google_cloud_cpp_cloud_dialogflow_v2_protos"]
        self.cpp_info.components["cloud_dialogflow_v2_protos"].set_property("pkg_config_name", "google_cloud_cpp_cloud_dialogflow_v2_protos")

        if Version(self.version) < "1.40.1":  # FIXME: Probably this library was removed before
            self.cpp_info.components["cloud_dialogflow_v2beta1_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "longrunning_operations_protos", "rpc_status_protos", "type_latlng_protos"]
            self.cpp_info.components["cloud_dialogflow_v2beta1_protos"].libs = ["google_cloud_cpp_cloud_dialogflow_v2beta1_protos"]
            self.cpp_info.components["cloud_dialogflow_v2beta1_protos"].set_property("pkg_config_name", "google_cloud_cpp_cloud_dialogflow_v2beta1_protos")

        self.cpp_info.components["grpc_utils"].requires = ["abseil::absl_function_ref", "abseil::absl_memory", "abseil::absl_time", "rpc_status_protos", "common", "grpc::grpc++", "grpc::grpc"]
        self.cpp_info.components["grpc_utils"].libs = ["google_cloud_cpp_grpc_utils"]
        self.cpp_info.components["grpc_utils"].set_property("pkg_config_name", "google_cloud_cpp_grpc_utils")

        self.cpp_info.components["experimental-iam"].requires = ["grpc_utils", "common", "iam_protos"]
        self.cpp_info.components["experimental-iam"].libs = ["google_cloud_cpp_iam"]
        self.cpp_info.components["experimental-iam"].set_property("pkg_config_name", "google_cloud_cpp_iam")

        self.cpp_info.components["experimental-logging"].requires = ["grpc_utils", "common", "logging_protos"]
        self.cpp_info.components["experimental-logging"].libs = ["google_cloud_cpp_logging"]
        self.cpp_info.components["experimental-logging"].set_property("pkg_config_name", "google_cloud_cpp_logging")

        self.cpp_info.components["pubsub"].requires = ["grpc_utils", "common", "pubsub_protos", "abseil::absl_flat_hash_map"]
        self.cpp_info.components["pubsub"].libs = ["google_cloud_cpp_pubsub"]
        self.cpp_info.components["pubsub"].set_property("pkg_config_name", "google_cloud_cpp_pubsub")

        self.cpp_info.components["spanner"].requires = ["abseil::absl_fixed_array", "abseil::absl_memory", "abseil::absl_numeric", "abseil::absl_strings", "abseil::absl_time", "grpc_utils", "common", "spanner_protos"]
        self.cpp_info.components["spanner"].libs = ["google_cloud_cpp_spanner"]
        self.cpp_info.components["spanner"].set_property("pkg_config_name", "google_cloud_cpp_spanner")

        self.cpp_info.components["storage"].requires = ["abseil::absl_memory", "abseil::absl_strings", "abseil::absl_str_format", "abseil::absl_time", "abseil::absl_variant", "common", "nlohmann_json::nlohmann_json", "crc32c::crc32c", "libcurl::libcurl", "openssl::ssl", "openssl::crypto"]
        self.cpp_info.components["storage"].libs = ["google_cloud_cpp_storage"]
        self.cpp_info.components["storage"].set_property("pkg_config_name", "google_cloud_cpp_storage")
