from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil


class Open62541Conan(ConanFile):
    name = "open62541"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Open source implementation of OPC UA (OPC Unified Architecture) aka IEC 62541 licensed under Mozilla Public License v2.0"
    topics = ("conan", "opcua", "iec62541")
    homepage = "http://open62541.org"
    license = "MPL-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithread": "ANY",
        "tls": ["openssl", "mbedtls-apache", "mbedtls-gpl", False],
        "enable_amalgamation": [True, False],
        "enable_historizing": [True, False],
        "enable_methodcalls": [True, False],
        "enable_nodemanagement": [True, False],
        "enable_subscriptions": [True, False],
        "enable_subscriptions_events": [True, False],
        "enable_discovery": [True, False],
        "enable_subscriptions_alarms_conditions": [True, False],
        "enable_discovery_multicast": [True, False],
        "enable_parsing": [True, False],
        "enable_da": [True, False],
        "enable_micro_emb_dev_profile": [True, False],
        "enable_websocket_server": [True, False],
        "enable_query": [True, False],
        "enable_immutable_nodes": [True, False],
        "enable_experiemental_historizing": [True, False],
        "force_cpp": [True, False],
        "enable_pubsub": [True, False],
        "enable_pubsub_eth_uadp": [True, False],
        "enable_pubsub_eth_uadp_xdp": [True, False],
        "enable_pubsub_deltaframes": [True, False],
        "enable_pubsub_informationmodel": [True, False],
        "enable_pubsub_informationmodel_methods": [True, False],
        "enable_pubsub_custom_publish_handling": [True, False],
        "enable_pubsub_eth_uadp_etf": [True, False],
        "enable_json_encoding": [True, False],
        "enable_pubsub_mqtt": [True, False],
        "enable_statuscode_descriptions": [True, False],
        "enable_typedescription": [True, False],
        "enable_nodeset_compiler_descriptions": [True, False],
        "enable_malloc_singleton": [True, False],
        "msvc_force_static_crt": [True, False],
        "enable_discovery_semaphore": [True, False],
        "debug_dump_pkgs": [True, False],
        "enable_hardening": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "multithread": False,
        "tls": "mbedtls-apache",
        "enable_amalgamation": False,
        "enable_historizing": False,
        "enable_methodcalls": True,
        "enable_nodemanagement": True,
        "enable_subscriptions": True,
        "enable_subscriptions_events": False,
        "enable_discovery": True,
        "enable_subscriptions_alarms_conditions": False,
        "enable_discovery_multicast": False,
        "enable_parsing": True,
        "enable_da": True,
        "enable_micro_emb_dev_profile": False,
        "enable_websocket_server": False,
        "enable_query": False,
        "enable_immutable_nodes": False,
        "enable_experiemental_historizing": False,
        "force_cpp": False,
        "enable_pubsub": False,
        "enable_pubsub_eth_uadp": False,
        "enable_pubsub_eth_uadp_xdp": False,
        "enable_pubsub_deltaframes": False,
        "enable_pubsub_informationmodel": False,
        "enable_pubsub_informationmodel_methods": False,
        "enable_pubsub_custom_publish_handling": False,
        "enable_pubsub_eth_uadp_etf": False,
        "enable_json_encoding": False,
        "enable_pubsub_mqtt": False,
        "enable_statuscode_descriptions": True,
        "enable_typedescription": True,
        "enable_nodeset_compiler_descriptions": True,
        "enable_malloc_singleton": False,
        "msvc_force_static_crt": True,
        "enable_discovery_semaphore": True,
        "debug_dump_pkgs": False,
        "enable_hardening": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self._ua_multithreaded() is None:
            raise ConanInvalidConfiguration("multithread configuration may be False, thread-safe, internal-threads or an integer" )

    def requirements(self):
        if self.options.tls == "openssl":
            self.requires("openssl/1.1.1g")

        if self.options.tls == "mbedtls-apache":
            self.requires("mbedtls/2.16.3-apache")

        if self.options.tls == "mbedtls-gpl":
            self.requires("mbedtls/2.16.3-gpl")

        if self.options.enable_websocket_server:
            raise ConanInvalidConfiguration("libwebsocket is not (yet) available on CCI")
            self.requires("libwebsockets/x.y.z")

    def build_requirements(self):
        if not tools.which("python") and not tools.which("python3"):
            raise ConanInvalidConfiguration("Python is required for building Open62541")
            self.build_requires("cpython/3.8.3")

    def source(self):
        archive_name = self.name + "-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)

    def _ua_multithreaded(self):
        if self.options.multithread in ("False", "thread-safe", "internal-threads"):
            return {
                "False": "0",
                "thread-safe": "100",
                "internal-threads": "200"
            }[str(self.options.multithread)]
        else:
            try:
                return str(int(self.options.multithread))
            except ValueError:
                return None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["UA_ARCHITECTURE"] = "win32" if self.settings.os == "Windows" else "posix"

        if self.options.tls == "openssl":
            self._cmake.definitions["UA_ENABLE_ENCRYPTION_OPENSSL"] = True

        if self.options.tls == "mbedtls-apache" or self.options.tls == "mbedtls-gpl":
            self._cmake.definitions["UA_ENABLE_ENCRYPTION_MBEDTLS"] = True

        self._cmake.definitions["UA_MULTITHREADING"] = self._ua_multithreaded()

        self._cmake.definitions["UA_ENABLE_AMALGAMATION"] = self.options.enable_amalgamation
        self._cmake.definitions["UA_ENABLE_HISTORIZING"] = self.options.enable_historizing
        self._cmake.definitions["UA_ENABLE_METHODCALLS"] = self.options.enable_methodcalls
        self._cmake.definitions["UA_ENABLE_NODEMANAGEMENT"] = self.options.enable_nodemanagement
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS"] = self.options.enable_subscriptions
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_EVENTS"] = self.options.enable_subscriptions_events
        self._cmake.definitions["UA_ENABLE_DISCOVERY"] = self.options.enable_discovery
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_ALARMS_CONDITIONS"] = self.options.enable_subscriptions_alarms_conditions
        self._cmake.definitions["UA_ENABLE_DISCOVERY_MULTICAST"] = self.options.enable_discovery_multicast
        self._cmake.definitions["UA_ENABLE_PARSING"] = self.options.enable_parsing
        self._cmake.definitions["UA_ENABLE_DA"] = self.options.enable_da
        self._cmake.definitions["UA_ENABLE_MICRO_EMB_DEV_PROFILE"] = self.options.enable_micro_emb_dev_profile
        self._cmake.definitions["UA_ENABLE_WEBSOCKET_SERVER"] = self.options.enable_websocket_server
        self._cmake.definitions["UA_ENABLE_QUERY"] = self.options.enable_query
        self._cmake.definitions["UA_ENABLE_IMMUTABLE_NODES"] = self.options.enable_immutable_nodes
        self._cmake.definitions["UA_ENABLE_EXPERIMENTAL_HISTORIZING"] = self.options.enable_experiemental_historizing
        self._cmake.definitions["UA_FORCE_32BIT"] = not(self.settings.arch == "armv8" or self.settings.arch == "x86_64")
        self._cmake.definitions["UA_FORCE_CPP"] = self.options.force_cpp
        self._cmake.definitions["UA_ENABLE_PUBSUB"] = self.options.enable_pubsub
        self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP"] = self.options.enable_pubsub_eth_uadp
        self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_XDP"] = self.options.enable_pubsub_eth_uadp_xdp
        self._cmake.definitions["UA_ENABLE_PUBSUB_DELTAFRAMES"] = self.options.enable_pubsub_deltaframes
        self._cmake.definitions["UA_ENABLE_PUBSUB_INFORMATIONMODEL"] = self.options.enable_pubsub_informationmodel
        self._cmake.definitions["UA_ENABLE_PUBSUB_INFORMATIONMODEL_METHODS"] = self.options.enable_pubsub_informationmodel_methods
        self._cmake.definitions["UA_ENABLE_PUBSUB_CUSTOM_PUBLISH_HANDLING"] = self.options.enable_pubsub_custom_publish_handling
        self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_ETF"] = self.options.enable_pubsub_eth_uadp_etf
        self._cmake.definitions["UA_ENABLE_JSON_ENCODING"] = self.options.enable_json_encoding
        self._cmake.definitions["UA_ENABLE_PUBSUB_MQTT"] = self.options.enable_pubsub_mqtt
        self._cmake.definitions["UA_ENABLE_STATUSCODE_DESCRIPTIONS"] = self.options.enable_statuscode_descriptions
        self._cmake.definitions["UA_ENABLE_TYPEDESCRIPTION"] = self.options.enable_typedescription
        self._cmake.definitions["UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS"] = self.options.enable_nodeset_compiler_descriptions
        self._cmake.definitions["UA_ENABLE_MALLOC_SINGLETON"] = self.options.enable_malloc_singleton
        self._cmake.definitions["UA_MSVC_FORCE_STATIC_CRT"] = self.options.msvc_force_static_crt
        self._cmake.definitions["UA_ENABLE_DISCOVERY_SEMAPHORE"] = self.options.enable_discovery_semaphore
        self._cmake.definitions["UA_DEBUG_DUMP_PKGS"] = self.options.debug_dump_pkgs
        self._cmake.definitions["UA_ENABLE_HARDENING"] = self.options.enable_hardening
        self._cmake.definitions["OPEN62541_VERSION"] = self.version


        self._cmake.definitions["UA_BUILD_EXAMPLES"] = False
        self._cmake.definitions["UA_BUILD_UNIT_TESTS"] = False
        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) <= "5":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "trace-pc-guard,", "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for f in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.remove(f)
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(f)

        self.copy(
          pattern = "*",
          src = os.path.join(self.package_folder, "share", "open62541", "tools"),
          dst = os.path.join(self.package_folder, "bin", "tools")
        )

        if self.settings.os == "Windows" and self.options.shared:
            shutil.move(os.path.join(self.package_folder, "open62541.dll"), os.path.join(self.package_folder, "bin"))


        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        self.info.options.multithreaded = self._ua_multithreaded()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.enable_amalgamation:
            self.cpp_info.defines.append("UA_ENABLE_AMALGAMATION")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
