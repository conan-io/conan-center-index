import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

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

    short_paths = True

    def export_sources(self):
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["protobuf"].shared = True
            self.options["googleapis"].shared = True
            self.options["grpc-proto"].shared = True
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
            not self.dependencies["googleapis"].options.shared or \
            not self.dependencies["grpc-proto"].options.shared or \
            not self.dependencies["grpc"].options.shared):
            raise ConanInvalidConfiguration(
                "If built as shared, protobuf, googleapis, grpc-proto, and grpc must be shared as well."
                " Please, use `protobuf/*:shared=True`, `googleapis/*:shared=True`, `grpc-proto/*:shared=True`,"
                " and `grpc/*:shared=True`",
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def requirements(self):
        self.requires("protobuf/3.21.9", transitive_headers=True)
        self.requires("grpc/1.50.1", transitive_headers=True)
        self.requires("nlohmann_json/3.10.0")
        self.requires("crc32c/1.1.1")
        self.requires("abseil/20220623.0", transitive_headers=True)
        self.requires("libcurl/7.88.1")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/1.2.13")
        # `google-cloud-cpp` contains code generated from the proto files.
        # Working with older versions of these protos almost always will fail, as
        # at least some of the RPCs included in the GRPC-generator stubs will be
        # missing.
        # Working with newer versions of these protos almost always will work. There
        # are very few breaking changes on the proto files.
        self.requires(f"googleapis/{self._GOOGLEAPIS_VERSIONS[self.version]}", transitive_headers=True)

    def build_requirements(self):
        # For the grpc-cpp-plugin executable
        self.tool_requires("grpc/1.50.1")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_google-cloud-cpp_INCLUDE"] = os.path.join(self.source_folder, "conan_cmake_project_include.cmake")
        tc.variables["BUILD_TESTING"] = False
        tc.variables["GOOGLE_CLOUD_CPP_ENABLE_MACOS_OPENSSL_CHECK"] = False
        tc.variables["GOOGLE_CLOUD_CPP_ENABLE"] = ",".join(self._components())
        tc.generate()
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
            replace_in_file(self, os.path.join(self.source_folder, "cmake/CompileProtos.cmake"),
                            "$<TARGET_FILE:protobuf::protoc>",
                            '${CMAKE_COMMAND} -E env "DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}" $<TARGET_FILE:protobuf::protoc>')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    _GOOGLEAPIS_VERSIONS = {
        "2.5.0": "cci.20221108",
        "2.10.1": "cci.20230501",
    }

    _GA_COMPONENTS_BASE = {"bigquery", "bigtable", "iam", "pubsub", "spanner", "storage"}
    _GA_COMPONENTS_VERSION_2_5_0 = {
        "accessapproval",
        "accesscontextmanager",
        "apigateway",
        "apigeeconnect",
        "appengine",
        "artifactregistry",
        "asset",
        "assuredworkloads",
        "automl",
        "baremetalsolution",
        "batch",
        "beyondcorp",
        "billing",
        "binaryauthorization",
        "certificatemanager",
        "channel",
        "cloudbuild",
        "composer",
        "connectors",
        "contactcenterinsights",
        "container",
        "containeranalysis",
        "datacatalog",
        "datamigration",
        "dataplex",
        "dataproc",
        "datastream",
        "debugger",
        "deploy",
        "dialogflow_cx",
        "dialogflow_es",
        "dlp",
        "documentai",
        "edgecontainer",
        "eventarc",
        "filestore",
        "functions",
        "gameservices",
        "gkehub",
        "iap",
        "ids",
        "iot",
        "kms",
        "language",
        "logging",
        "managedidentities",
        "memcache",
        "monitoring",
        "networkconnectivity",
        "networkmanagement",
        "notebooks",
        "optimization",
        "orgpolicy",
        "osconfig",
        "oslogin",
        "policytroubleshooter",
        "privateca",
        "profiler",
        "recommender",
        "redis",
        "resourcemanager",
        "resourcesettings",
        "retail",
        "run",
        "scheduler",
        "secretmanager",
        "securitycenter",
        "servicecontrol",
        "servicedirectory",
        "servicemanagement",
        "serviceusage",
        "shell",
        "speech",
        "storagetransfer",
        "talent",
        "tasks",
        "texttospeech",
        "tpu",
        "trace",
        "translate",
        "video",
        "videointelligence",
        "vision",
        "vmmigration",
        "vmwareengine",
        "vpcaccess",
        "webrisk",
        "websecurityscanner",
        "workflows",
    }
    _GA_COMPONENTS_VERSION_2_10_1 = {
        'advisorynotifications',
        'alloydb',
        'apikeys',
        'confidentialcomputing',
        'gkemulticloud',
        'sql',
        'storageinsights',
    }
    _GA_COMPONENTS_VERSION = {
        '2.5.0': _GA_COMPONENTS_VERSION_2_5_0,
        '2.10.1': _GA_COMPONENTS_VERSION_2_10_1,
    }

    def _components(self):
        result = self._GA_COMPONENTS_BASE
        for v in self._GA_COMPONENTS_VERSION.keys():
            if v > Version(self):
                continue
            result = result.union(self._GA_COMPONENTS_VERSION[v])
        # Some protos do not compile due to inconvenient system macros clashing with proto enum values.
        # Protobuf can workaround these problems, but the current version in Conan index (protobuf/3.21.4)
        # do not contain the fixes for these cases.
        # TODO - review after protobuf >= 3.22.x
        result.remove('asset')
        result.remove('channel')
        result.remove('storagetransfer')
        # Some of the macros are platform specific.
        if self.settings.os == "Android":
            result.remove('accesscontextmanager')
            result.remove('talent')
        # TODO - certificatemanager crashes the gRPC code generator. Add it back after gRPC >= 1.53.x
        result.remove('certificatemanager')
        return result

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, path=os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, path=os.path.join(self.package_folder, "lib", "pkgconfig"))

    _INTERFACE_COMPONENTS = {
        'dialogflow_es_protos',
        'logging_types_protos',
        'speech_protos',
        'texttospeech_protos',
    }
    def _add_proto_component(self, component):
        PROTOS_SHARED_REQUIRES=["googleapis::googleapis", "grpc::grpc++", "grpc::_grpc", "protobuf::libprotobuf"]
        self.cpp_info.components[component].requires = PROTOS_SHARED_REQUIRES
        self.cpp_info.components[component].names["pkg_config"] = f"google_cloud_cpp_{component}"
        # Starting with 2.10.1 a small number of `*_protos` libraries require
        # special treatment to avoid ODR violations
        if Version(self) >= '2.10.1' and component == 'dialogflow_es_protos':
            self.cpp_info.components[component].libs = ['google_cloud_cpp_cloud_dialogflow_v2_protos']
            return
        if Version(self) >= '2.10.1' and component == 'logging_types_protos':
            self.cpp_info.components[component].libs = ['google_cloud_cpp_logging_type_type_protos']
            return
        if Version(self) >= '2.10.1' and component == 'speech_protos':
            self.cpp_info.components[component].libs = ['google_cloud_cpp_cloud_speech_protos']
            return
        if Version(self) >= '2.10.1' and component == 'texttospeech_protos':
            self.cpp_info.components[component].libs = ['google_cloud_cpp_cloud_texttospeech_protos']
            return
        self.cpp_info.components[component].libs = [f"google_cloud_cpp_{component}"]

    def _add_grpc_component(self, component, protos, extra=None):
        SHARED_REQUIRES=["grpc_utils", "common", "grpc::grpc++", "grpc::_grpc", "protobuf::libprotobuf", "abseil::absl_memory"]
        self.cpp_info.components[component].requires = (extra or []) + [protos] + SHARED_REQUIRES
        self.cpp_info.components[component].libs = [f"google_cloud_cpp_{component}"]
        self.cpp_info.components[component].names["pkg_config"] = f"google_cloud_cpp_{component}"

    def package_info(self):
        self.cpp_info.components["common"].requires = ["abseil::absl_any", "abseil::absl_flat_hash_map", "abseil::absl_memory", "abseil::absl_optional", "abseil::absl_time"]
        self.cpp_info.components["common"].libs = ["google_cloud_cpp_common"]
        self.cpp_info.components["common"].names["pkg_config"] = "google_cloud_cpp_common"

        self.cpp_info.components["rest_internal"].requires = ["common", "libcurl::libcurl", "openssl::ssl", "openssl::crypto", "zlib::zlib"]
        self.cpp_info.components["rest_internal"].libs = ["google_cloud_cpp_rest_internal"]
        self.cpp_info.components["rest_internal"].names["pkg_config"] = "google_cloud_cpp_common"

        # A small number of gRPC-generated stubs are used directly in the common components
        # shared by all gRPC-based libraries.  These bust be defined without reference to `grpc_utils`.
        GRPC_UTILS_REQUIRED_PROTOS=["iam_protos", "longrunning_operations_protos", "rpc_error_details_protos", "rpc_status_protos"]
        for component in GRPC_UTILS_REQUIRED_PROTOS:
            self._add_proto_component(component)

        self.cpp_info.components["grpc_utils"].requires = GRPC_UTILS_REQUIRED_PROTOS + ["common", "abseil::absl_function_ref", "abseil::absl_memory", "abseil::absl_time", "grpc::grpc++", "grpc::_grpc"]
        self.cpp_info.components["grpc_utils"].libs = ["google_cloud_cpp_grpc_utils"]
        self.cpp_info.components["grpc_utils"].names["pkg_config"] = "google_cloud_cpp_grpc_utils"

        for component in self._components():
            # bigquery proto library predates the adoption of more consistent naming
            if component == 'bigquery':
                self._add_proto_component("cloud_bigquery_protos")
                self._add_grpc_component(component, "cloud_bigquery_protos")
                continue
            if component == 'dialogflow_es':
                self._add_proto_component("cloud_dialogflow_v2_protos")
                self._add_grpc_component(component, "cloud_dialogflow_v2_protos")
                continue
            # `storage` is the only component that does not depend on a matching `*_protos` library
            protos=f"{component}_protos"
            if component != 'storage' and component not in GRPC_UTILS_REQUIRED_PROTOS:
                self._add_proto_component(protos)
            # The components in self._GA_COMPONENTS_BASE are hand-crafted and need custom
            # definitions (see below)
            if component in self._GA_COMPONENTS_BASE:
                continue
            self._add_grpc_component(component, protos)

        self._add_grpc_component("bigquery", "cloud_bigquery_protos")
        self._add_grpc_component("bigtable", "bigtable_protos")
        self._add_grpc_component("iam", "iam_protos")
        self._add_grpc_component("pubsub", "pubsub_protos", ["abseil::absl_flat_hash_map"])
        self._add_grpc_component("spanner", "spanner_protos",  ["abseil::absl_fixed_array", "abseil::absl_numeric", "abseil::absl_strings", "abseil::absl_time"])

        self.cpp_info.components["storage"].requires = ["rest_internal", "common", "nlohmann_json::nlohmann_json", "abseil::absl_memory", "abseil::absl_strings", "abseil::absl_str_format", "abseil::absl_time", "abseil::absl_variant", "crc32c::crc32c", "libcurl::libcurl", "openssl::ssl", "openssl::crypto", "zlib::zlib"]
        self.cpp_info.components["storage"].libs = ["google_cloud_cpp_storage"]
        self.cpp_info.components["storage"].names["pkg_config"] = "google_cloud_cpp_storage"
