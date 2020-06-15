from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil
import yaml



class Open62541Conan(ConanFile):
    name = "open62541"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Open source implementation of OPC UA (OPC Unified Architecture) aka IEC 62541 licensed under Mozilla Public License v2.0"
    topics = ("conan", "opcua", "iec62541")
    homepage = "http://open62541.org"
    license = "MPL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    exports = "submoduledata.yml"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithread": "ANY",                                                   # Level of multithreading (0-99: No Multithreading, 100-199: Thread-Safe API, >=200: Internal Threads
                                                                                # multithread configuration may be
                                                                                #       1.0 : False, True
                                                                                #       1.1 : False, thread-safe, internal-threads or an integer
        "tls": [False, "openssl", "mbedtls-apache", "mbedtls-gpl"],
        "with_libwebsockets": [True, False],                                    # Enable websocket support (uses libwebsockets)
        "enable_amalgamation": [True, False],                                   # Concatenate the library to a single file open62541.h/.c
        "enable_historizing": [True, False],                                    # Enable server and client to provide historical access
        "enable_methodcalls": [True, False],                                    # Enable the Method service set
        "enable_nodemanagement": [True, False],                                 # Enable dynamic addition and removal of nodes at runtime
        "enable_subscriptions": [True, False],                                  # Enable subscriptions support
        "enable_subscriptions_events": [True, False],                           # Enable the use of event subscriptions
        "enable_discovery": [True, False],                                      # Enable Discovery Service (LDS)
        "enable_discovery_multicast": [True, False],                            # Enable Discovery Service with multicast support (LDS-ME)
        "enable_micro_emb_dev_profile": [True, False],                          # Builds CTT Compliant Micro Embedded Device Server Profile
        "enable_query": [True, False],                                          # Enable query support in the client (most servers don't support it)
        "enable_immutable_nodes": [True, False],                                # Nodes in the information model are not edited but copied and replaced
        "enable_experimental_historizing": [True, False],                      # Enable client experimental historical access features
        "enable_pubsub": [True, False],                                         # Enable publish/subscribe
        "enable_pubsub_eth_uadp": [True, False],                                # Enable publish/subscribe UADP over Ethernet
        "enable_pubsub_deltaframes": [True, False],                             # Enable sending of delta frames with only the changes
        "enable_pubsub_informationmodel": [True, False],                        # Enable PubSub information model twin
        "enable_pubsub_informationmodel_methods": [True, False],                # Enable PubSub informationmodel methods
        "enable_pubsub_custom_publish_handling": [True, False],                 # Use a custom implementation for the publish callback handling
        "enable_json_encoding": [True, False],                                  # Enable Json encoding (EXPERIMENTAL)
        "enable_statuscode_descriptions": [True, False],                        # Enable conversion of StatusCode to human-readable error message
        "enable_typedescription": [True, False],                                # Add the type and member names to the UA_DataType structure
        "enable_nodeset_compiler_descriptions": [True, False],                  # Set node description attribute for nodeset compiler generated nodes
        "enable_malloc_singleton": [True, False],                               # Use a global variable pointer for malloc (and free, ...) that can be switched at runtime
        "msvc_force_static_crt": [True, False],                                 # Force linking with the static C-runtime library when compiling to static library with MSVC
        "enable_discovery_semaphore": [True, False],                            # Enable Discovery Semaphore support
        "debug_dump_pkgs": [True, False],                                       # Dump every package received by the server as hexdump format
        "enable_hardening": [True, False],                                      # Enable Hardening measures (e.g. Stack-Protectors and Fortify)
        "enable_subscriptions_alarms_conditions": [True, False],                # Enable the use of A&C. (EXPERIMENTAL)
        "enable_parsing": [True, False],                                        # Utility functions that require parsing (e.g. NodeId expressions)
        "force_cpp": [True, False],                                             # Force compilation with a C++ compiler
        "enable_da": [True, False],                                             # Enable OPC UA DataAccess (Part 8) definitions
        "enable_pubsub_eth_uadp_xdp": [True, False],                            # Enable Subscribe UADP over Ethernet using XDP
        "enable_pubsub_eth_uadp_etf": [True, False],                            # Use ETF implementation for the ETH_UADP publish
        "enable_pubsub_mqtt": [True, False],                                    # Enable publish/subscribe with mqtt (experimental)
        "namespace_zero": ["minimal", "reduced", "full"]                        # Completeness of the generated namespace zero (minimal/reduced/full)
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "multithread": False,
        "tls": "mbedtls-apache",
        "with_libwebsockets": False,
        "enable_amalgamation": False,
        "enable_historizing": False,
        "enable_methodcalls": True,
        "enable_nodemanagement": True,
        "enable_subscriptions": True,
        "enable_subscriptions_events": False,
        "enable_discovery": True,
        "enable_discovery_multicast": False,
        "enable_micro_emb_dev_profile": False,
        "enable_query": False,
        "enable_immutable_nodes": False,
        "enable_experimental_historizing": False,
        "enable_pubsub": False,
        "enable_pubsub_eth_uadp": False,
        "enable_pubsub_deltaframes": False,
        "enable_pubsub_informationmodel": False,
        "enable_pubsub_informationmodel_methods": False,
        "enable_pubsub_custom_publish_handling": False,
        "enable_json_encoding": False,
        "enable_statuscode_descriptions": True,
        "enable_typedescription": True,
        "enable_nodeset_compiler_descriptions": True,
        "enable_malloc_singleton": False,
        "msvc_force_static_crt": True,
        "enable_discovery_semaphore": True,
        "debug_dump_pkgs": False,
        "enable_hardening": True,
        "enable_subscriptions_alarms_conditions": False,
        "enable_parsing": True,
        "force_cpp": False,
        "enable_da": True,
        "enable_pubsub_eth_uadp_xdp": False,
        "enable_pubsub_eth_uadp_etf": False,
        "enable_pubsub_mqtt": False,
        "namespace_zero": "reduced"
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not self.options.force_cpp:
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx

    def configure(self):
        self.options["libwebsockets"].with_ssl = self.options.tls

        if not self.options.enable_pubsub and (self.options.enable_pubsub_mqtt                                      
          or self.options.enable_pubsub_informationmodel                        \
          or self.options.enable_pubsub_informationmodel_methods                \
          or self.options.enable_pubsub_custom_publish_handling                 \
          or self.options.enable_pubsub_eth_uadp_etf):
            raise ConanInvalidConfiguration("The option 'enable_pubsub' must be True, if pubsub is required." )

        if self.options.enable_discovery_multicast:
            self.options.enable_discovery = True

        if self.options.enable_experimental_historizing:
            self.options.enable_historizing = True

        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) <= "4":
            raise ConanInvalidConfiguration("clang compiler <= 4.0 not (yet) supported" )

        if self._ua_multithreaded() is None:
            raise ConanInvalidConfiguration("multithread configuration may be False, thread-safe, internal-threads or an integer" )

    def requirements(self):
        if self.options.tls == "openssl":
            self.requires("openssl/1.1.1g")
        elif self.options.tls == "mbedtls-apache":
            self.requires("mbedtls/2.16.3-apache")
        elif self.options.tls == "mbedtls-gpl":
            self.requires("mbedtls/2.16.3-gpl")

        if self.options.with_libwebsockets:
            self.requires("libwebsockets/4.0.15")

    def build_requirements(self):
        if not tools.which("python") and not tools.which("python3"):
            raise ConanInvalidConfiguration("Python is required for building Open62541")
            self.build_requires("cpython/3.8.3")

    def source(self):
        archive_name = self.name + "-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)

        submodule_filename = os.path.join(os.path.dirname(__file__), 'submoduledata.yml')
        with open(submodule_filename, 'r') as submodule_stream:
            submodules_data = yaml.load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
              filename = os.path.basename(submodule["url"])
              archive_name = submodule["archive_pattern"].format(version = os.path.splitext(filename)[0])

              submodule_data = {
                "url": submodule["url"],
                "sha256": submodule["sha256"]
              }

              tools.get(**submodule_data)
              submodule_source = os.path.join(self._source_subfolder, path)
              tools.rmdir(submodule_source)
              os.rename(archive_name, submodule_source)

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
            self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = True
            self._cmake.definitions["UA_ENABLE_ENCRYPTION_OPENSSL"] = True
        elif self.options.tls == "mbedtls-apache" or self.options.tls == "mbedtls-gpl":
            self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = True
            self._cmake.definitions["UA_ENABLE_ENCRYPTION_MBEDTLS"] = True


        self._cmake.definitions["UA_MULTITHREADING"] = self._ua_multithreaded()

        self._cmake.definitions["UA_ENABLE_AMALGAMATION"] = self.options.enable_amalgamation
        self._cmake.definitions["UA_ENABLE_HISTORIZING"] = self.options.enable_historizing
        self._cmake.definitions["UA_ENABLE_METHODCALLS"] = self.options.enable_methodcalls
        self._cmake.definitions["UA_ENABLE_NODEMANAGEMENT"] = self.options.enable_nodemanagement
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS"] = self.options.enable_subscriptions
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_EVENTS"] = self.options.enable_subscriptions_events
        self._cmake.definitions["UA_ENABLE_DISCOVERY"] = self.options.enable_discovery
        self._cmake.definitions["UA_ENABLE_DISCOVERY_MULTICAST"] = self.options.enable_discovery_multicast
        self._cmake.definitions["UA_ENABLE_MICRO_EMB_DEV_PROFILE"] = self.options.enable_micro_emb_dev_profile
        self._cmake.definitions["UA_ENABLE_QUERY"] = self.options.enable_query
        self._cmake.definitions["UA_ENABLE_IMMUTABLE_NODES"] = self.options.enable_immutable_nodes
        self._cmake.definitions["UA_ENABLE_EXPERIMENTAL_HISTORIZING"] = self.options.enable_experimental_historizing
        self._cmake.definitions["UA_ENABLE_PUBSUB"] = self.options.enable_pubsub
        self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP"] = self.options.enable_pubsub_eth_uadp
        self._cmake.definitions["UA_ENABLE_PUBSUB_DELTAFRAMES"] = self.options.enable_pubsub_deltaframes
        self._cmake.definitions["UA_ENABLE_PUBSUB_INFORMATIONMODEL"] = self.options.enable_pubsub_informationmodel
        self._cmake.definitions["UA_ENABLE_PUBSUB_INFORMATIONMODEL_METHODS"] = self.options.enable_pubsub_informationmodel_methods
        self._cmake.definitions["UA_ENABLE_PUBSUB_CUSTOM_PUBLISH_HANDLING"] = self.options.enable_pubsub_custom_publish_handling
        self._cmake.definitions["UA_ENABLE_JSON_ENCODING"] = self.options.enable_json_encoding
        self._cmake.definitions["UA_ENABLE_STATUSCODE_DESCRIPTIONS"] = self.options.enable_statuscode_descriptions
        self._cmake.definitions["UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS"] = self.options.enable_nodeset_compiler_descriptions
        self._cmake.definitions["UA_ENABLE_MALLOC_SINGLETON"] = self.options.enable_malloc_singleton
        self._cmake.definitions["UA_MSVC_FORCE_STATIC_CRT"] = self.options.msvc_force_static_crt
        self._cmake.definitions["UA_ENABLE_DISCOVERY_SEMAPHORE"] = self.options.enable_discovery_semaphore
        self._cmake.definitions["UA_DEBUG_DUMP_PKGS"] = self.options.debug_dump_pkgs
        self._cmake.definitions["UA_ENABLE_HARDENING"] = self.options.enable_hardening
        self._cmake.definitions["OPEN62541_VERSION"] = self.version
        self._cmake.definitions["UA_DEBUG" ] = self.settings.build_type == "Debug"
        self._cmake.definitions["UA_ENABLE_WEBSOCKET_SERVER"] = self.options.with_libwebsockets
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_ALARMS_CONDITIONS"] = self.options.enable_subscriptions_alarms_conditions
        self._cmake.definitions["UA_ENABLE_PARSING"] = self.options.enable_parsing
        self._cmake.definitions["UA_ENABLE_DA"] = self.options.enable_da
        self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_XDP"] = self.options.enable_pubsub_eth_uadp_xdp
        self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_ETF"] = self.options.enable_pubsub_eth_uadp_etf
        self._cmake.definitions["UA_ENABLE_PUBSUB_MQTT"] = self.options.enable_pubsub_mqtt
        self._cmake.definitions["UA_FORCE_32BIT"] = not(self.settings.arch == "armv8" or self.settings.arch == "x86_64")
        self._cmake.definitions["UA_FORCE_CPP"] = self.options.force_cpp
        self._cmake.definitions["UA_ENABLE_TYPEDESCRIPTION"] = self.options.enable_typedescription
        self._cmake.definitions["UA_NAMESPACE_ZERO"] = self.options.namespace_zero

        self._cmake.definitions["UA_BUILD_EXAMPLES"] = False
        self._cmake.definitions["UA_BUILD_UNIT_TESTS"] = False
        self._cmake.verbose = True
        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

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
