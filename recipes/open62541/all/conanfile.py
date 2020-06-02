import os
import sys
from conans import ConanFile, CMake, tools
from conans.tools import download, unzip
from conans.model.version import Version
from urllib.parse import urlparse
import shutil


class Open62541Conan(ConanFile):
    name = "open62541"
    license = "MPLv2"
    exports_sources = [
        "CMakeLists.txt",
        "patches/**"
    ]
    homepage = "https://open62541.org/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "open62541 is an open source and free implementation of OPC UA (OPC Unified Architecture) written in the common subset of the C99 and C++98 languages. The library is usable with all major compilers and provides the necessary tools to implement dedicated OPC UA clients and servers, or to integrate OPC UA-based communication into existing applications. open62541 library is platform independent. All platform-specific functionality is implemented via exchangeable plugins. Plugin implementations are provided for the major operating systems."
    requires = ("mbedtls/2.16.3-gpl")
    topics = (
        "OPC UA", "open62541", "sdk", "server/client", "c", "iec-62541",
        "industrial automation", "tsn", "time sensetive networks", "publish-subscirbe", "pubsub"
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "historize": [True, False],
        "logging_level": ["Fatal", "Error", "Warrning", "Info", "Debug", "Trace"],
        "subscription": [True, False],
        "subscription_events": [True, False],
        "methods": [True, False],
        "dynamic_nodes": [True, False],
        "single_header": [True, False],
        "multithreading": [True, False],
        "imutable_nodes": [True, False],
        "web_socket": [True, False],
        "discovery": [True, False],
        "discovery_semaphore": [True, False],
        "discovery_multicast": [True, False],
        "query": [True, False],
        "encription": [True, False],
        "json_support": [True, False],
        "pub_sub": ["None", "Simple", "Ethernet", "Ethernet_XDP"],
        "data_access": [True, False],
        "compiled_nodeset_descriptions": [True, False],
        "namescpae_zero": ["MINIMAL", "REDUCED", "FULL"],
        "embedded_profile": [True, False],
        "typenames": [True, False],
        "hardening": [True, False],
        "cpp_compatible": [True, False],
        "readable_statuscodes": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": True,
        "historize": False,
        "logging_level": "Info",
        "subscription": True,
        "subscription_events": False,
        "methods": True,
        "dynamic_nodes": True,
        "single_header": False,
        "multithreading": False,
        "imutable_nodes": False,
        "web_socket": False,
        "discovery": True,
        "discovery_semaphore": True,
        "discovery_multicast": False,
        "query": False,
        "encription": False,
        "json_support": False,
        "pub_sub": "None",
        "data_access": False,
        "compiled_nodeset_descriptions": True,
        "namescpae_zero": "REDUCED",
        "embedded_profile": False,
        "typenames": True,
        "hardening": False,
        "cpp_compatible": False,
        "readable_statuscodes": True
    }
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _download_deps(self, zip_link, dep_name):
        zip_name = dep_name + ".zip"
        download(zip_link, zip_name)
        dep_path = self._source_subfolder + "/deps/" + dep_name
        unzip(zip_name)
        full_path = str(urlparse(zip_link).path).split("/")
        dir_name = full_path[2] + "-" + full_path[4]
        dir_name = dir_name[:-4]
        files = os.listdir(dir_name)
        for f in files:
            shutil.move(os.path.join(dir_name, f), dep_path)
        os.unlink(zip_name)
        shutil.rmtree(dir_name)

    def _download_ua_nodes(self):
        link = ""
        if self.version == "1.0.0":
            link = "https://github.com/OPCFoundation/UA-Nodeset/archive/0777abd1bc407b4dbd79abc515864f8c3ce6812b.zip"
        elif self.version == "1.0.1":
            link = "https://github.com/OPCFoundation/UA-Nodeset/archive/0777abd1bc407b4dbd79abc515864f8c3ce6812b.zip"
        self._download_deps(zip_link=link, dep_name="ua-nodeset")

    def _download_mdnsd(self):
        link = ""
        if self.version == "1.0.0":
            link = "https://github.com/Pro/mdnsd/archive/8fe3a7e7e9d0a9196b126c64f0d1905569b83d40.zip"
        elif self.version == "1.0.1":
            link = "https://github.com/Pro/mdnsd/archive/f7f0dd543f12fa7bbf2b667cceb287b9c8184b7d.zip"
        self._download_deps(zip_link=link, dep_name="mdnsd")

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        if Version(self.version) <= "1.0.0":
            folder_name = "%s-%s" % (self.name, "1.0")
        else:
            folder_name = "%s-%s" % (self.name, self.version)
        os.rename(folder_name, self._source_subfolder)
        if Version(self.version) <= "1.0.1":
            self._download_ua_nodes()
            self._download_mdnsd()
        self._patch_sources()

    def _get_log_level(self):
        return {
            "Fatal": "600",
            "Error": "500",
            "Warrning": "400",
            "Info": "300",
            "Debug": "200",
            "Trace": "100",
            "PackageOption": "300"
        }.get(str(self.options.logging_level), "300")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.verbose = True
        version = Version(self.version)
        cmake.definitions["OPEN62541_VER_MAJOR"] = version.major(fill=False)
        cmake.definitions["OPEN62541_VER_MINOR"] = version.minor(fill=False)
        cmake.definitions["OPEN62541_VER_PATCH"] = version.patch()
        if self.settings.os != "Windows":
            cmake.definitions["POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["UA_LOGLEVEL"] = self._get_log_level()
        cmake.definitions["UA_ENABLE_SUBSCRIPTIONS"] = self.options.subscription
        cmake.definitions["UA_ENABLE_SUBSCRIPTIONS_EVENTS"] = self.options.subscription_events
        cmake.definitions["UA_ENABLE_METHODCALLS"] = self.options.methods
        cmake.definitions["UA_ENABLE_NODEMANAGEMENT"] = self.options.dynamic_nodes
        cmake.definitions["UA_ENABLE_AMALGAMATION"] = self.options.single_header
        cmake.definitions["UA_ENABLE_MULTITHREADING"] = self.options.multithreading
        cmake.definitions["UA_ENABLE_IMMUTABLE_NODES"] = self.options.imutable_nodes
        cmake.definitions["UA_ENABLE_WEBSOCKET_SERVER"] = self.options.web_socket
        cmake.definitions["UA_ENABLE_HISTORIZING"] = self.options.historize
        cmake.definitions["UA_ENABLE_DISCOVERY"] = self.options.discovery
        cmake.definitions["UA_ENABLE_DISCOVERY_MULTICAST"] = self.options.discovery_multicast
        cmake.definitions["UA_ENABLE_DISCOVERY_SEMAPHORE"] = self.options.discovery_semaphore
        cmake.definitions["UA_ENABLE_QUERY"] = self.options.query
        cmake.definitions["UA_ENABLE_ENCRYPTION"] = self.options.encription
        cmake.definitions["UA_ENABLE_JSON_ENCODING"] = self.options.json_support
        if self.options.pub_sub != "None":
            cmake.definitions["UA_ENABLE_PUBSUB"] = True
            if self.settings.os == "Linux" and self.options.pub_sub == "Ethernet":
                cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP"] = True
            elif self.settings.os == "Linux" and self.options.pub_sub == "Ethernet_XDP":
                cmake.definitions["UA_ENABLE_PUBSUB_ETH_UADP_XDP"] = True
            else:
                print("PubSub over Ethernet is not supported for your OS!")
        cmake.definitions["UA_ENABLE_DA"] = self.options.data_access
        if self.options.compiled_nodeset_descriptions == True:
            cmake.definitions["UA_ENABLE_NODESET_COMPILER_DESCRIPTIONS"] = self.options.compiled_nodeset_descriptions
            cmake.definitions["UA_NAMESPACE_ZERO"] = "FULL"
        else:
            cmake.definitions["UA_NAMESPACE_ZERO"] = self.options.namescpae_zero
        cmake.definitions["UA_ENABLE_MICRO_EMB_DEV_PROFILE"] = self.options.embedded_profile
        cmake.definitions["UA_ENABLE_TYPENAMES"] = self.options.typenames
        cmake.definitions["UA_ENABLE_STATUSCODE_DESCRIPTIONS"] = self.options.readable_statuscodes
        cmake.definitions["UA_ENABLE_HARDENING"] = self.options.hardening
        if self.settings.compiler == "Visual Studio" and self.options.shared == True:
            cmake.definitions["UA_MSVC_FORCE_STATIC_CRT"] = True
        if version > "1.0.1":
            cmake.definitions["UA_COMPILE_AS_CXX"] = self.options.cpp_compatible
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-CC0", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "open62541"
        self.cpp_info.names["cmake_find_package_multi"] = "open62541"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [
            "include",
            os.path.join("include", "plugin")
        ]
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
            self.cpp_info.includedirs.append(os.path.join("include", "win32"))
        else:
            self.cpp_info.includedirs.append(os.path.join("include", "posix"))
        self.cpp_info.builddirs = [
            "lib",
            os.path.join("lib", "cmake"),
            os.path.join("lib", "cmake", "open62541")
        ]
