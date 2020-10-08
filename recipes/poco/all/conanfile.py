from conans import ConanFile, CMake, tools
from conans.errors import ConanException, ConanInvalidConfiguration
from collections import namedtuple, OrderedDict
import os


class PocoConan(ConanFile):
    name = "poco"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pocoproject.org"
    topics = ("conan", "poco", "building", "networking", "server", "mobile", "embedded")
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    license = "BSL-1.0"
    description = "Modern, powerful open source C++ class libraries for building network- and internet-based " \
                  "applications that run on desktop, server, mobile and embedded systems."
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _PocoComponent = namedtuple("_PocoComponent", ("option", "default_option", "dependencies", "is_lib"))
    _poco_component_tree = {
        "mod_poco": _PocoComponent("enable_apacheconnector", False, ("PocoUtil", "PocoNet", ), False),  # also external apr and apr-util
        "PocoCppParser": _PocoComponent("enable_cppparser", False, ("PocoFoundation", ), False),
        # "PocoCppUnit": _PocoComponent("enable_cppunit", False, ("PocoFoundation", ), False)),
        "PocoCrypto": _PocoComponent("enable_crypto", True, ("PocoFoundation", ), True),    # also external openssl
        "PocoData": _PocoComponent("enable_data", True, ("PocoFoundation", ), True),
        "PocoDataMySQL": _PocoComponent("enable_data_mysql", False, ("PocoData", ), True),
        "PocoDataODBC": _PocoComponent("enable_data_odbc", False, ("PocoData", ), True),
        "PocoDataPostgreSQL": _PocoComponent("enable_data_postgresql", False, ("PocoData", ), True),    # also external postgresql
        "PocoDataSQLite": _PocoComponent("enable_data_sqlite", True, ("PocoData", ), True),  # also external sqlite3
        "PocoEncodings": _PocoComponent("enable_encodings", True, ("PocoFoundation", ), True),
        # "PocoEncodingsCompiler": _PocoComponent("enable_encodingscompiler", False, ("PocoNet", "PocoUtil", ), False),
        "PocoFoundation": _PocoComponent(None, "PocoFoundation", (), True),
        "PocoJSON": _PocoComponent("enable_json", True, ("PocoFoundation", ), True),
        "PocoJWT": _PocoComponent("enable_jwt", True, ("PocoJSON", "PocoCrypto", ), True),
        "PocoMongoDB": _PocoComponent("enable_mongodb", True, ("PocoNet", ), True),
        "PocoNet": _PocoComponent("enable_net", True, ("PocoFoundation", ), True),
        "PocoNetSSL": _PocoComponent("enable_netssl", True, ("PocoCrypto", "PocoUtil", "PocoNet", ), True),    # also external openssl
        "PocoNetSSLWin": _PocoComponent("enable_netssl_win", True, ("PocoNet", "PocoUtil", ), True),
        "PocoPDF": _PocoComponent("enable_pdf", False, ("PocoXML", "PocoUtil", ), True),
        "PocoPageCompiler": _PocoComponent("enable_pagecompiler", False, ("PocoNet", "PocoUtil", ), False),
        "PocoFile2Page": _PocoComponent("enable_pagecompiler_file2page", False, ("PocoNet", "PocoUtil", "PocoXML", "PocoJSON", ), False),
        "PocoPocoDoc": _PocoComponent("enable_pocodoc", False, ("PocoUtil", "PocoXML", "PocoCppParser", ), False),
        "PocoRedis": _PocoComponent("enable_redis", True, ("PocoNet", ), True),
        "PocoSevenZip": _PocoComponent("enable_sevenzip", False, ("PocoUtil", "PocoXML", ), True),
        "PocoUtil": _PocoComponent("enable_util", True, ("PocoFoundation", "PocoXML", "PocoJSON", ), True),
        "PocoXML": _PocoComponent("enable_xml", True, ("PocoFoundation", ), True),
        "PocoZip": _PocoComponent("enable_zip", True, ("PocoUtil", "PocoXML", ), True),
    }

    for comp in _poco_component_tree.values():
        if comp.option:
            options[comp.option] = [True, False]
            default_options[comp.option] = comp.default_option
    del comp

    @property
    def _poco_ordered_components(self):
        remaining_components = dict((compname, set(compopts.dependencies)) for compname, compopts in self._poco_component_tree.items())
        ordered_components = []
        while remaining_components:
            components_no_deps = set(compname for compname, compopts in remaining_components.items() if not compopts)
            if not components_no_deps:
                raise ConanException("The poco dependency tree is invalid and contains a cycle")
            for c in components_no_deps:
                remaining_components.pop(c)
            ordered_components.extend(components_no_deps)
            for rname in remaining_components.keys():
                remaining_components[rname] = remaining_components[rname].difference(components_no_deps)
        ordered_components.reverse()
        return ordered_components

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "poco-poco-{}-release".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.enable_netssl_win
        if tools.Version(self.version) < "1.9":
            del self.options.enable_encodings
        if tools.Version(self.version) < "1.10":
            del self.options.enable_data_postgresql
            del self.options.enable_jwt

    def configure(self):
        if self.options.enable_apacheconnector:
            raise ConanInvalidConfiguration("Apache connector not supported: https://github.com/pocoproject/poco/issues/1764")
        if self.options.enable_data_mysql:
            raise ConanInvalidConfiguration("MySQL not supported yet, open an issue here please: %s" % self.url)
        if self.options.get_safe("enable_data_postgresql", False):
            raise ConanInvalidConfiguration("PostgreSQL not supported yet, open an issue here please: %s" % self.url)
        for compopt in self._poco_component_tree.values():
            if not compopt.option:
                continue
            if self.options.get_safe(compopt.option, False):
                for compdep in compopt.dependencies:
                    if not self._poco_component_tree[compdep].option:
                        continue
                    if not self.options.get_safe(self._poco_component_tree[compdep].option, False):
                        raise ConanInvalidConfiguration("option {} requires also option {}".format(compopt.option, self._poco_component_tree[compdep].option))

    def requirements(self):
        self.requires("pcre/8.41")
        self.requires("zlib/1.2.11")
        if self.options.enable_xml:
            self.requires("expat/2.2.10")
        if self.options.enable_data_sqlite:
            self.requires("sqlite3/3.33.0")
        if self.options.enable_apacheconnector:
            self.requires("apr/1.7.0")
            self.requires("apr-util/1.6.1")
            raise ConanInvalidConfiguration("apache2 is not (yet) available on CCI")
            self.requires("apache2/x.y.z")
        if self.options.enable_netssl or \
                self.options.enable_crypto or \
                self.options.get_safe("enable_jwt", False):
            self.requires("openssl/1.1.1h")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) < "1.10.1":
            self._cmake.definitions["POCO_STATIC"] = not self.options.shared
        for comp in self._poco_component_tree.values():
            if not comp.option:
                continue
            self._cmake.definitions[comp.option.upper()] = self.options.get_safe(comp.option, False)
        self._cmake.definitions["POCO_UNBUNDLED"] = True
        self._cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":  # MT or MTd
            self._cmake.definitions["POCO_MT"] = "ON" if "MT" in str(self.settings.compiler.runtime) else "OFF"
        self.output.info(self._cmake.definitions)
        # On Windows, Poco needs a message (MC) compiler.
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.options.enable_data_sqlite:
            if self.options["sqlite3"].threadsafe == 0:
                raise ConanInvalidConfiguration("sqlite3 must be built with threadsafe enabled")
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    @property
    def _ordered_libs(self):
        libs = []
        for compname in self._poco_ordered_components:
            comp_options = self._poco_component_tree[compname]
            if comp_options.is_lib:
                if not comp_options.option:
                    libs.append(compname)
                elif self.options.get_safe(comp_options.option, False):
                    libs.append(compname)
        return libs

    def package_info(self):
        suffix = str(self.settings.compiler.runtime).lower()  \
                 if self.settings.compiler == "Visual Studio" and not self.options.shared \
                 else ("d" if self.settings.build_type == "Debug" else "")

        self.cpp_info.libs = list("{}{}".format(lib, suffix) for lib in self._ordered_libs)

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl", "rt"])

        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("POCO_NO_AUTOMATIC_LIBS")
        if not self.options.shared:
            self.cpp_info.defines.append("POCO_STATIC=ON")
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])
        self.cpp_info.names["cmake_find_package"] = "Poco"
        self.cpp_info.names["cmake_find_package_multi"] = "Poco"
