from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import rename, get
import glob
import os
import yaml

required_conan_version = ">=1.33.0"


class Open62541Conan(ConanFile):
    name = "open62541"
    license = "MPLv2"
    homepage = "https://open62541.org/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "open62541 is an open source and free implementation of OPC UA " \
                  "(OPC Unified Architecture) written in the common subset of the " \
                  "C99 and C++98 languages. The library is usable with all major " \
                  "compilers and provides the necessary tools to implement dedicated " \
                  "OPC UA clients and servers, or to integrate OPC UA-based communication " \
                  "into existing applications. open62541 library is platform independent. " \
                  "All platform-specific functionality is implemented via exchangeable " \
                  "plugins. Plugin implementations are provided for the major operating systems."
    topics = (
        "opc ua", "open62541", "sdk", "server/client", "c", "iec-62541",
        "industrial automation", "tsn", "time sensitive networks", "publish-subscirbe", "pubsub"
    )

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        # False: UA_ENABLE_HISTORIZING=Off
        # True: UA_ENABLE_HISTORIZING=On
        # Experimental: UA_ENABLE_HISTORIZING=On and UA_ENABLE_EXPERIMENTAL_HISTORIZING=On
        "historize": [True, False, "Experimental"],
        "logging_level": ["Fatal", "Error", "Warning", "Info", "Debug", "Trace"],
        # False: UA_ENABLE_SUBSCRIPTIONS=Off
        # True: UA_ENABLE_SUBSCRIPTIONS=On
        # With Events: deprecated. Use 'events' instead
        # events: UA_ENABLE_SUBSCRIPTIONS_EVENTS=On
        # alarms,conditions,events: UA_ENABLE_SUBSCRIPTIONS_EVENTS=On and UA_ENABLE_SUBSCRIPTIONS_ALARMS_CONDITIONS=On
        "subscription": [True, False, "With Events", "events", "alarms,conditions,events"],
        # False: UA_ENABLE_METHODCALLS=Off
        # True: UA_ENABLE_METHODCALLS=Onn
        "methods": [True, False],
        # False: UA_ENABLE_NODEMANAGEMENT=Off
        # True: UA_ENABLE_NODEMANAGEMENT=On
        "dynamic_nodes": [True, False],
        # False: UA_ENABLE_AMALGAMATION=Off
        # True: UA_ENABLE_AMALGAMATION=On
        "single_header": [True, False],
        # None: UA_MULTITHREADING=0
        # Threadsafe: UA_MULTITHREADING=100
        # Internal threads: UA_MULTITHREADING=200
        "multithreading": ["None", "Threadsafe", "Internal threads"],
        # False: UA_ENABLE_IMMUTABLE_NODES=Off
        # True: UA_ENABLE_IMMUTABLE_NODES=On
        "imutable_nodes": [True, False],
        # False: UA_ENABLE_WEBSOCKET_SERVER=Off
        # True: UA_ENABLE_WEBSOCKET_SERVER=On
        "web_socket": [True, False],
        # False: UA_ENABLE_DISCOVERY=Off
        # True: UA_ENABLE_DISCOVERY=On
        # With Multicast: Deprecated. Use 'multicast' instead
        # multicast: UA_ENABLE_DISCOVERY_MULTICAST=On
        # semaphore: UA_ENABLE_DISCOVERY_SEMAPHORE=On
        # multicast,semaphore: UA_ENABLE_DISCOVERY_MULTICAST=On and UA_ENABLE_DISCOVERY_SEMAPHORE=On
        "discovery": [True, False, "With Multicast", "multicast", "semaphore", "multicast,semaphore"],
        # Deprecated. Use discovery=semaphore instead
        "discovery_semaphore": [True, False],
        # False: UA_ENABLE_QUERY=Off
        # True: UA_ENABLE_QUERY=On
        "query": [True, False],
        # False: UA_ENABLE_ENCRYPTION=Off
        # openssl: UA_ENABLE_ENCRYPTION=On and UA_ENABLE_ENCRYPTION_OPENSSL=On
        # mbedtls: UA_ENABLE_ENCRYPTION=On
        # changed in 1.3.1 - UA_ENABLE_ENCRYPTION can be OFF, OPENSSL, MBEDTLS
        "encryption": [False, "openssl", "mbedtls"],
        # False: UA_ENABLE_JSON_ENCODING=Off
        # True: UA_ENABLE_JSON_ENCODING=On
        "json_support": [True, False],
        # False: UA_ENABLE_PUBSUB=Off
        # Simple: UA_ENABLE_PUBSUB=On
        # Ethernet: UA_ENABLE_PUBSUB=On and UA_ENABLE_PUBSUB_ETH_UADP=On
        # Ethernet_XDP: UA_ENABLE_PUBSUB=On and UA_ENABLE_PUBSUB_ETH_UADP_XDP=On
        "pub_sub": [False, "Simple", "Ethernet", "Ethernet_XDP"],
        # False: UA_ENABLE_PUBSUB_ENCRYPTION=Off
        # True: UA_ENABLE_PUBSUB_ENCRYPTION=On
        "pub_sub_encryption": [True, False],
        # False: UA_ENABLE_DA=Off
        # True: UA_ENABLE_DA=On
        "data_access": [True, False],
        # False: UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS=Off and UA_NAMESPACE_ZERO=options.namespace_zero
        # True: UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS=On and UA_NAMESPACE_ZERO=Full
        "compiled_nodeset_descriptions": [True, False],
        # UA_NAMESPACE_ZERO=option.namespace_zero (only if compiled_nodeset_descriptions=False)
        "namespace_zero": ["MINIMAL", "REDUCED", "FULL"],
        # UA_ENABLE_MICRO_EMB_DEV_PROFILE=embedded_profile
        "embedded_profile": [True, False],
        # UA_ENABLE_TYPENAMES=typenames
        "typenames": [True, False],
        # UA_ENABLE_HARDENING=hardening
        "hardening": [True, False],
        # UA_COMPILE_AS_CXX=cpp_compatible
        "cpp_compatible": [True, False],
        # UA_ENABLE_STATUSCODE_DESCRIPTIONS=readable_statuscodes
        "readable_statuscodes": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "historize": False,
        "logging_level": "Info",
        "subscription": True,
        "methods": True,
        "dynamic_nodes": True,
        "single_header": False,
        "multithreading": "None",
        "imutable_nodes": False,
        "web_socket": False,
        "discovery": "semaphore",
        "discovery_semaphore": True,
        "query": False,
        "encryption": False,
        "json_support": False,
        "pub_sub": False,
        "pub_sub_encryption": False,
        "data_access": True,
        "compiled_nodeset_descriptions": True,
        "namespace_zero": "FULL",
        "embedded_profile": False,
        "typenames": True,
        "hardening": True,
        "cpp_compatible": False,
        "readable_statuscodes": True
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    exports = "submoduledata.yml"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) >= "1.3.1":
            del self.options.embedded_profile

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cpp_compatible:
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx

        # Due to https://github.com/open62541/open62541/issues/4687 we cannot build with 1.2.2 + Windows + shared
        if tools.Version(self.version) >= "1.2.2" and self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("{0} {1} doesn't properly support shared lib on Windows".format(self.name,
                                                                                                            self.version))

        if self.options.subscription == "With Events":
            self.output.warning("`{name}:subscription=With Events` is deprecated. Use `{name}:subscription=events` instead".format(name=self.name))  # Deprecated in 1.2.2
            self.options.subscription = "events"

        if self.options.web_socket:
            self.options["libwebsockets"].with_ssl = self.options.encryption

    def requirements(self):
        if self.options.encryption == "mbedtls":
            self.requires("mbedtls/2.25.0")
        elif self.options.encryption == "openssl":
            self.requires("openssl/1.1.1o")
        if self.options.web_socket:
            self.requires("libwebsockets/4.2.0")
        if self.options.discovery == "With Multicast" or "multicast" in str(self.options.discovery):
            self.requires("pro-mdnsd/0.8.4")

    def validate(self):
        if not self.options.subscription:
            raise ConanInvalidConfiguration(
                "Open62541 requires subscription option")

        if not self.options.discovery:
            if self.options.discovery_semaphore:
                raise ConanInvalidConfiguration(
                    "Open62541 discovery sempahore option requires discovery option to be enabled")

        if tools.Version(self.version) < "1.1.0":
            if self.options.encryption == "openssl":
                raise ConanInvalidConfiguration(
                    "Lower Open62541 versions than 1.1.0 do not support openssl")

            if self.options.multithreading != "None":
                raise ConanInvalidConfiguration(
                    "Lower Open62541 versions than 1.1.0 do not fully support multithreading")

            if self.options.web_socket:
                raise ConanInvalidConfiguration(
                    "Lower Open62541 versions than 1.1.0 do not fully support websockets")

            if self.options.cpp_compatible:
                raise ConanInvalidConfiguration(
                    "Lower Open62541 versions than 1.1.0 are not cpp compatible due to -fpermisive flags")

        # FIXME: correct clang versions condition
        max_clang_version = "8" if tools.Version(self.version) < "1.1.0" else "9"
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) > max_clang_version:
            raise ConanInvalidConfiguration(
                "Open62541 supports Clang up to {} compiler version".format(max_clang_version))

        if self.settings.compiler == "clang":
            if tools.Version(self.settings.compiler.version) < "5":
                raise ConanInvalidConfiguration(
                    "Older clang compiler version than 5.0 are not supported")

        if self.options.pub_sub != False and self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "PubSub over Ethernet is not supported for your OS!")

        if self.options.web_socket:
            if self.options["libwebsockets"].with_ssl != self.options.encryption:
                raise ConanInvalidConfiguration(
                    "When web_socket is enabled, libwebsockets:with_ssl must have the value of open62541:encryption")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

        submodule_filename = os.path.join(
            self.recipe_folder, 'submoduledata.yml')
        with open(submodule_filename, 'r') as submodule_stream:
            submodules_data = yaml.safe_load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                filename = os.path.basename(submodule["url"])
                archive_name = submodule["archive_pattern"].format(
                    version=os.path.splitext(filename.replace('v', ''))[0])

                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"]
                }

                get(self, **submodule_data)
                submodule_source = os.path.join(self._source_subfolder, path)
                tools.files.rmdir(self, submodule_source)
                rename(self, archive_name, submodule_source)

    def _get_log_level(self):
        return {
            "Fatal": "600",
            "Error": "500",
            "Warning": "400",
            "Info": "300",
            "Debug": "200",
            "Trace": "100",
            "PackageOption": "300"
        }.get(str(self.options.logging_level), "300")

    def _get_multithreading_option(self):
        return {
            "None": "0",
            "Threadsafe": "100",
            "Internal threads": "200"
        }.get(str(self.options.multithreading), "0")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        version = tools.Version(self.version)
        self._cmake.definitions["OPEN62541_VER_MAJOR"] = version.major
        self._cmake.definitions["OPEN62541_VER_MINOR"] = version.minor
        self._cmake.definitions["OPEN62541_VER_PATCH"] = version.patch

        self._cmake.definitions["UA_LOGLEVEL"] = self._get_log_level()
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS"] = self.options.subscription != False
        if self.options.subscription != False:
            if "events" in str(self.options.subscription):
                self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_EVENTS"] = True
            if "alarms" in str(self.options.subscription) and "conditions" in str(self.options.subscription):
                self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_ALARMS_CONDITIONS"] = True
        self._cmake.definitions["UA_ENABLE_METHODCALLS"] = self.options.methods
        self._cmake.definitions["UA_ENABLE_NODEMANAGEMENT"] = self.options.dynamic_nodes
        self._cmake.definitions["UA_ENABLE_AMALGAMATION"] = self.options.single_header
        if version >= "1.1.3":
            self._cmake.definitions["UA_MULTITHREADING"] = self._get_multithreading_option(
            )
        self._cmake.definitions["UA_ENABLE_IMMUTABLE_NODES"] = self.options.imutable_nodes
        self._cmake.definitions["UA_ENABLE_WEBSOCKET_SERVER"] = self.options.web_socket
        self._cmake.definitions["UA_ENABLE_HISTORIZING"] = self.options.historize != False
        if self.options.historize != False:
            if self.options.historize == "Experimental":
                self._cmake.definitions["UA_ENABLE_EXPERIMENTAL_HISTORIZING"] = True
        self._cmake.definitions["UA_ENABLE_DISCOVERY"] = self.options.discovery != False
        if self.options.discovery != False:
            self._cmake.definitions["UA_ENABLE_DISCOVERY_MULTICAST"] = \
                self.options.discovery == "With Multicast" or "multicast" in str(self.options.discovery)
            self._cmake.definitions["UA_ENABLE_DISCOVERY_SEMAPHORE"] = \
                self.options.discovery_semaphore or "semaphore" in str(self.options.discovery)
        self._cmake.definitions["UA_ENABLE_QUERY"] = self.options.query
        if tools.Version(self.version) >= "1.3.1":
            if self.options.encryption == "openssl":
                self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = "OPENSSL"
            elif self.options.encryption == "mbedtls":
                self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = "MBEDTLS"
            else:
                self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = "OFF"
        else:
            self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = self.options.encryption != False
            if self.options.encryption != False:
                if self.options.encryption == "openssl":
                    self._cmake.definitions["UA_ENABLE_ENCRYPTION_OPENSSL"] = True
        self._cmake.definitions["UA_ENABLE_JSON_ENCODING"] = self.options.json_support
        self._cmake.definitions["UA_ENABLE_PUBSUB"] = self.options.pub_sub != False
        self._cmake.definitions["UA_ENABLE_PUBSUB_ENCRYPTION"] = self.options.pub_sub_encryption != False
        if self.options.pub_sub != False:
            if self.settings.os == "Linux" and self.options.pub_sub == "Ethernet":
                self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP"] = True
            elif self.settings.os == "Linux" and self.options.pub_sub == "Ethernet_XDP":
                self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_XDP"] = True
        self._cmake.definitions["UA_ENABLE_DA"] = self.options.data_access
        if self.options.compiled_nodeset_descriptions == True:
            self._cmake.definitions["UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS"] = self.options.compiled_nodeset_descriptions
            self._cmake.definitions["UA_NAMESPACE_ZERO"] = "FULL"
        else:
            self._cmake.definitions["UA_NAMESPACE_ZERO"] = self.options.namespace_zero
        if tools.Version(self.version) < "1.3.1":
            self._cmake.definitions["UA_ENABLE_MICRO_EMB_DEV_PROFILE"] = self.options.embedded_profile
        self._cmake.definitions["UA_ENABLE_TYPENAMES"] = self.options.typenames
        self._cmake.definitions["UA_ENABLE_STATUSCODE_DESCRIPTIONS"] = self.options.readable_statuscodes
        self._cmake.definitions["UA_ENABLE_HARDENING"] = self.options.hardening
        if self.settings.compiler == "Visual Studio" and self.options.shared == True:
            self._cmake.definitions["UA_MSVC_FORCE_STATIC_CRT"] = True
        self._cmake.definitions["UA_COMPILE_AS_CXX"] = self.options.cpp_compatible

        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if tools.Version(self.version) >= "1.3.1":
            os.unlink(os.path.join(self._source_subfolder, "tools", "cmake", "FindPython3.cmake"))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    @property
    def _tools_subfolder(self):
        return os.path.join(self._source_subfolder, "tools")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-CC0", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rm(self, os.path.join(
            self.package_folder, "bin"), '*.pdb')
        tools.files.rm(self, os.path.join(
            self.package_folder, "lib"), '*.pdb')

        for cmake_file in glob.glob(os.path.join(self.package_folder, self._module_subfolder, "*")):
            if not cmake_file.endswith(self._module_file_rel_path):
                os.remove(cmake_file)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        self.copy("generate_*.py", src=self._tools_subfolder, dst=os.path.join("res", "tools"))
        self.copy("nodeset_compiler/*", src=self._tools_subfolder, dst=os.path.join("res", "tools"))

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake", "open62541")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder, "open62541Macros.cmake")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "open62541"
        self.cpp_info.names["cmake_find_package_multi"] = "open62541"
        self.cpp_info.names["pkg_config"] = "open62541"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [
            "include",
            os.path.join("include", "open62541", "plugin")
        ]

        # required for creating custom servers from ua-nodeset
        self.user_info.tools_dir = os.path.join(self.package_folder, "res", "tools")
        self._chmod_plus_x(os.path.join(self.package_folder, "res", "tools", "generate_nodeid_header.py"))

        if self.options.single_header:
            self.cpp_info.defines.append("UA_ENABLE_AMALGAMATION")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.includedirs.append(os.path.join("include", "open62541", "win32"))
        else:
            self.cpp_info.includedirs.append(os.path.join("include", "open62541", "posix"))
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["pthread", "m", "rt"])
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules = [self._module_file_rel_path]
