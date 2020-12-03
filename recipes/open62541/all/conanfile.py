import os
from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
import glob
import shutil
import yaml


class Open62541Conan(ConanFile):
    name = "open62541"
    license = "MPLv2"
    exports_sources = [
        "CMakeLists.txt",
        "patches/**"
    ]
    exports = "submoduledata.yml"
    homepage = "https://open62541.org/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "open62541 is an open source and free implementation of OPC UA (OPC Unified Architecture) written in the common subset of the C99 and C++98 languages. The library is usable with all major compilers and provides the necessary tools to implement dedicated OPC UA clients and servers, or to integrate OPC UA-based communication into existing applications. open62541 library is platform independent. All platform-specific functionality is implemented via exchangeable plugins. Plugin implementations are provided for the major operating systems."
    topics = (
        "OPC UA", "open62541", "sdk", "server/client", "c", "iec-62541",
        "industrial automation", "tsn", "time sensetive networks", "publish-subscirbe", "pubsub"
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "historize": ["Off", "On", "Experimental"],
        "logging_level": ["Fatal", "Error", "Warning", "Info", "Debug", "Trace"],
        "subscription": [True, False],
        "subscription_events": [True, False],
        "methods": [True, False],
        "dynamic_nodes": [True, False],
        "single_header": [True, False],
        "multithreading": ["Off", "Threadsafe", "Internal threads"],
        "imutable_nodes": [True, False],
        "web_socket": [True, False],
        "discovery": [True, False],
        "discovery_semaphore": [True, False],
        "discovery_multicast": [True, False],
        "query": [True, False],
        "encryption": ["None", "openssl", "mbedtls-apache", "mbedtls-gpl"],
        "json_support": [True, False],
        "pub_sub": ["None", "Simple", "Ethernet", "Ethernet_XDP"],
        "data_access": [True, False],
        "compiled_nodeset_descriptions": [True, False],
        "namespace_zero": ["MINIMAL", "REDUCED", "FULL"],
        "embedded_profile": [True, False],
        "typenames": [True, False],
        "hardening": [True, False],
        "cpp_compatible": [True, False],
        "readable_statuscodes": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": True,
        "historize": "Off",
        "logging_level": "Info",
        "subscription": True,
        "subscription_events": False,
        "methods": True,
        "dynamic_nodes": True,
        "single_header": False,
        "multithreading": "Off",
        "imutable_nodes": False,
        "web_socket": False,
        "discovery": True,
        "discovery_semaphore": True,
        "discovery_multicast": False,
        "query": False,
        "encryption": "None",
        "json_support": False,
        "pub_sub": "None",
        "data_access": True,
        "compiled_nodeset_descriptions": True,
        "namespace_zero": "FULL",
        "embedded_profile": False,
        "typenames": True,
        "hardening": False,
        "cpp_compatible": False,
        "readable_statuscodes": True
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if Version(self.version) >= "1.1.0":
            if self.options.encryption == "mbedtls-apache":
                self.requires("mbedtls/2.16.3-apache")
            elif self.options.encryption == "mbedtls-gpl":
                self.requires("mbedtls/2.16.3-gpl")
            elif self.options.encryption == "openssl":
                self.requires("openssl/1.1.1g")

            if self.options.web_socket:
                self.requires("libwebsockets/4.0.15")
        else:
            if self.options.encryption == "mbedtls-apache":
                self.requires("mbedtls/2.16.3-apache")
            elif self.options.encryption == "mbedtls-gpl":
                self.requires("mbedtls/2.16.3-gpl")
            elif self.options.encryption == "openssl":
                raise ConanInvalidConfiguration(
                    "Versions of Open62541 lower than 1.1.0 do not support openssl")
            if self.options.web_socket:
                raise ConanInvalidConfiguration(
                    "Versions of Open62541 lower than 1.1.0 do not fully support websockets")

        if self.options.discovery_multicast:
            self.requires("pro-mdnsd/0.8.4")

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def configure(self):
        if not self.options.subscription:
            if self.options.subscription_events:
                raise ConanInvalidConfiguration(
                    "Open62541 requires subscription option")

        if not self.options.discovery:
            if self.options.discovery_multicast or self.options.discovery_semaphore:
                raise ConanInvalidConfiguration(
                    "Open62541 requires discovery option")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not self.options.cpp_compatible:
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx

    def source(self):
        archive_name = self.name + "-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)

        submodule_filename = os.path.join(
            os.path.dirname(__file__), 'submoduledata.yml')
        with open(submodule_filename, 'r') as submodule_stream:
            submodules_data = yaml.load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                filename = os.path.basename(submodule["url"])
                archive_name = submodule["archive_pattern"].format(
                    version=os.path.splitext(filename.replace('v', ''))[0])

                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"]
                }

                tools.get(**submodule_data)
                submodule_source = os.path.join(self._source_subfolder, path)
                tools.rmdir(submodule_source)
                os.rename(archive_name, submodule_source)

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
            "Off": "0",
            "Threadsafe": "100",
            "Internal threads": "200"
        }.get(str(self.options.multithreading), "0")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        if self.settings.compiler == "clang" and not self.options.shared:
            raise ConanInvalidConfiguration(
                "Clang compiler can not be used to build a static library")

        self._cmake = CMake(self)
        self._cmake.verbose = True

        version = Version(self.version)
        self._cmake.definitions["OPEN62541_VER_MAJOR"] = version.major(
            fill=False)
        self._cmake.definitions["OPEN62541_VER_MINOR"] = version.minor(
            fill=False)
        self._cmake.definitions["OPEN62541_VER_PATCH"] = version.patch()

        self._cmake.definitions["UA_LOGLEVEL"] = self._get_log_level()
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS"] = self.options.subscription
        self._cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_EVENTS"] = self.options.subscription_events
        self._cmake.definitions["UA_ENABLE_METHODCALLS"] = self.options.methods
        self._cmake.definitions["UA_ENABLE_NODEMANAGEMENT"] = self.options.dynamic_nodes
        self._cmake.definitions["UA_ENABLE_AMALGAMATION"] = self.options.single_header
        self._cmake.definitions["UA_ENABLE_MULTITHREADING"] = self._get_multithreading_option(
        )
        self._cmake.definitions["UA_ENABLE_IMMUTABLE_NODES"] = self.options.imutable_nodes
        self._cmake.definitions["UA_ENABLE_WEBSOCKET_SERVER"] = self.options.web_socket
        if self.options.historize != "Off":
            self._cmake.definitions["UA_ENABLE_HISTORIZING"] = True
            if self.options.historize == "Experimental":
                self._cmake.definitions["UA_ENABLE_EXPERIMENTAL_HISTORIZING"] = True
        self._cmake.definitions["UA_ENABLE_DISCOVERY"] = self.options.discovery
        self._cmake.definitions["UA_ENABLE_DISCOVERY_MULTICAST"] = self.options.discovery_multicast
        self._cmake.definitions["UA_ENABLE_DISCOVERY_SEMAPHORE"] = self.options.discovery_semaphore
        self._cmake.definitions["UA_ENABLE_QUERY"] = self.options.query
        if self.options.encryption != "None":
            self._cmake.definitions["UA_ENABLE_ENCRYPTION"] = True
            if self.options.encryption == "openssl":
                self._cmake.definitions["UA_ENABLE_ENCRYPTION_OPENSSL"] = True
        self._cmake.definitions["UA_ENABLE_JSON_ENCODING"] = self.options.json_support
        if self.options.pub_sub != "None":
            self._cmake.definitions["UA_ENABLE_PUBSUB"] = True
            if self.settings.os == "Linux" and self.options.pub_sub == "Ethernet":
                self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP"] = True
            elif self.settings.os == "Linux" and self.options.pub_sub == "Ethernet_XDP":
                self._cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_XDP"] = True
            else:
                raise ConanInvalidConfiguration(
                    "PubSub over Ethernet is not supported for your OS!")
        self._cmake.definitions["UA_ENABLE_DA"] = self.options.data_access
        if self.options.compiled_nodeset_descriptions == True:
            self._cmake.definitions["UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS"] = self.options.compiled_nodeset_descriptions
            self._cmake.definitions["UA_NAMESPACE_ZERO"] = "FULL"
        else:
            self._cmake.definitions["UA_NAMESPACE_ZERO"] = self.options.namespace_zero
        self._cmake.definitions["UA_ENABLE_MICRO_EMB_DEV_PROFILE"] = self.options.embedded_profile
        self._cmake.definitions["UA_ENABLE_TYPENAMES"] = self.options.typenames
        self._cmake.definitions["UA_ENABLE_STATUSCODE_DESCRIPTIONS"] = self.options.readable_statuscodes
        self._cmake.definitions["UA_ENABLE_HARDENING"] = self.options.hardening
        if self.settings.compiler == "Visual Studio" and self.options.shared == True:
            self._cmake.definitions["UA_MSVC_FORCE_STATIC_CRT"] = True
        self._cmake.definitions["UA_COMPILE_AS_CXX"] = self.options.cpp_compatible

        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-CC0", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        for f in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.remove(f)
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(f)

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "open62541"
        self.cpp_info.names["cmake_find_package_multi"] = "open62541"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [
            "include",
            os.path.join("include", "plugin")
        ]
        if self.options.single_header:
            self.cpp_info.defines.append("UA_ENABLE_AMALGAMATION")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.includedirs.append(os.path.join("include", "win32"))
        else:
            self.cpp_info.includedirs.append(os.path.join("include", "posix"))
        self.cpp_info.builddirs = [
            "lib",
            os.path.join("lib", "cmake"),
            os.path.join("lib", "cmake", "open62541")
        ]
