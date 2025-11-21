from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from collections import namedtuple
import os

required_conan_version = ">=2.1"


class PocoConan(ConanFile):
    name = "poco"
    description = (
        "Modern, powerful open source C++ class libraries for building "
        "network- and internet-based applications that run on desktop, server, "
        "mobile and embedded systems."
    )
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pocoproject.org"
    topics = ("building", "networking", "server", "mobile", "embedded")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_fork": [True, False],
        "enable_active_record": [True, False, "deprecated"],
        "log_debug": [True, False],
        "with_sql_parser": [True, False],
        "comp_foundation_sharedlibrary_debug_suffix": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_fork": True,
        "enable_active_record": "deprecated",
        "log_debug": False,
        "with_sql_parser": True,
        "comp_foundation_sharedlibrary_debug_suffix": True,
    }

    _PocoComponent = namedtuple("_PocoComponent", ("option", "default_option", "dependencies", "external_dependencies", "is_lib"))
    _poco_component_tree = {
        "mod_poco": _PocoComponent("enable_apacheconnector", False, ["Util", "Net"], ["apr::apr", "apr-util::apr-util"], False),
        "CppParser": _PocoComponent("enable_cppparser", False, ["Foundation"], [], False),
        # "CppUnit": _PocoComponent("enable_cppunit", False, ["Foundation"], [], False)),
        "Crypto": _PocoComponent("enable_crypto", True, ["Foundation"], ["openssl::openssl"], True),
        "Data": _PocoComponent("enable_data", True, ["Foundation"], [], True),
        "DataMySQL": _PocoComponent("enable_data_mysql", True, ["Data"], ["libmysqlclient::libmysqlclient"], True),
        "DataODBC": _PocoComponent("enable_data_odbc", False, ["Data"], [], True), # requires odbc but conditional, see package_info()
        "DataPostgreSQL": _PocoComponent("enable_data_postgresql", True, ["Data"], ["libpq::libpq"], True),
        "DataSQLite": _PocoComponent("enable_data_sqlite", True, ["Data"], ["sqlite3::sqlite3"], True),
        "Encodings": _PocoComponent("enable_encodings", True, ["Foundation"], [], True),
        # "EncodingsCompiler": _PocoComponent("enable_encodingscompiler", False, ["Net", "Util"], [], False),
        "Foundation": _PocoComponent(None, "Foundation", [], ["pcre::pcre", "zlib::zlib"], True),
        "JSON": _PocoComponent("enable_json", True, ["Foundation"], [], True),
        "JWT": _PocoComponent("enable_jwt", True, ["JSON", "Crypto"], [], True),
        "MongoDB": _PocoComponent("enable_mongodb", True, ["Net"], [], True),
        "Net": _PocoComponent("enable_net", True, ["Foundation"], [], True),
        "NetSSL": _PocoComponent("enable_netssl", True, ["Crypto", "Util", "Net"], [], True),
        "NetSSLWin": _PocoComponent("enable_netssl_win", False, ["Net", "Util"], [], True),
        "PDF": _PocoComponent("enable_pdf", False, ["XML", "Util"], [], True),
        "PageCompiler": _PocoComponent("enable_pagecompiler", False, ["Net", "Util"], [], False),
        "File2Page": _PocoComponent("enable_pagecompiler_file2page", False, ["Net", "Util", "XML", "JSON"], [], False),
        "PocoDoc": _PocoComponent("enable_pocodoc", False, ["Util", "XML", "CppParser"], [], False),
        "Redis": _PocoComponent("enable_redis", True, ["Net"], [], True),
        "SevenZip": _PocoComponent("enable_sevenzip", False, ["Util", "XML"], [], True),
        "Util": _PocoComponent("enable_util", True, ["Foundation", "XML", "JSON"], [], True),
        "XML": _PocoComponent("enable_xml", True, ["Foundation"], ["expat::expat"], True),
        "Zip": _PocoComponent("enable_zip", True, ["Util", "XML"], [], True),
        "ActiveRecord": _PocoComponent("enable_activerecord", True, ["Foundation", "Data"], [], True),
        "ActiveRecordCompiler": _PocoComponent("enable_activerecord_compiler", False, ["Util", "XML"], [], False),
        "Prometheus": _PocoComponent("enable_prometheus", False, ["Foundation", "Net"], [], True),
    }

    for comp in _poco_component_tree.values():
        if comp.option:
            options[comp.option] = [True, False]
            default_options[comp.option] = comp.default_option
    del comp

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.enable_fork
        else:
            del self.options.enable_netssl_win
        if self.settings.build_type != "Debug":
            del self.options.comp_foundation_sharedlibrary_debug_suffix

    def configure(self):
        if self.options.enable_active_record != "deprecated":
            self.output.warning("enable_active_record option is deprecated, use 'enable_activerecord' instead")
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_xml:
            util_dependencies = self._poco_component_tree["Util"].dependencies
            self._poco_component_tree["Util"] = self._poco_component_tree["Util"]._replace(dependencies = [x for x in util_dependencies if x != "XML"])
        if not self.options.enable_json:
            util_dependencies = self._poco_component_tree["Util"].dependencies
            self._poco_component_tree["Util"] = self._poco_component_tree["Util"]._replace(dependencies = [x for x in util_dependencies if x != "JSON"])

        foundation_external_dependencies = self._poco_component_tree["Foundation"].external_dependencies
        self._poco_component_tree["Foundation"] = self._poco_component_tree["Foundation"]._replace(external_dependencies = list(map(lambda x: 'pcre2::pcre2' if x == 'pcre::pcre' else x, foundation_external_dependencies)))
        if Version(self.version) >= "1.14.0":
            self._poco_component_tree["Foundation"].external_dependencies.append("utf8proc::utf8proc")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pcre2/[>=10.42 <11]")
        if Version(self.version) >= "1.14.0":
            self.requires("utf8proc/[>=2.8.0 <3]")
        self.requires("zlib/[>=1.2.11 <2]", transitive_headers=True)
        if self.options.enable_xml:
            self.requires("expat/[>=2.6.2 <3]", transitive_headers=True)
        if self.options.enable_data_sqlite:
            self.requires("sqlite3/[>=3.45.0 <4]")
        if self.options.enable_apacheconnector:
            self.requires("apr/1.7.4")
            self.requires("apr-util/1.6.1")
        if self.options.enable_netssl or self.options.enable_crypto or \
           self.options.get_safe("enable_jwt"):
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
        if self.options.enable_data_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.11")
        if self.options.get_safe("enable_data_postgresql"):
            self.requires("libpq/15.4")
        if self.options.get_safe("enable_data_mysql"):
            self.requires("libmysqlclient/8.1.0")

    def package_id(self):
        del self.info.options.enable_active_record
        del self.info.options.log_debug

    def validate_build(self):
        check_min_cppstd(self, 17)

    def validate(self):
        #  1.13.3: https://github.com/pocoproject/poco/blob/d6bd48a94c5f03e3c69cac1b024fdad5120e3a7b/Foundation/CMakeLists.txt#L125-L128
        #  1.14.2: https://github.com/pocoproject/poco/blob/96d182a99303fb068575294b36f0cc20da2e7b25/Foundation/CMakeLists.txt#L130
        check_min_cppstd(self, 14)

        if self.options.enable_apacheconnector:
            # FIXME: missing apache2 recipe + few issues
            raise ConanInvalidConfiguration("Apache connector not supported: https://github.com/pocoproject/poco/issues/1764")
        if is_msvc(self) and self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Cannot build shared poco libraries with MT(d) runtime")
        for compopt in self._poco_component_tree.values():
            if not compopt.option:
                continue
            if self.options.get_safe(compopt.option, False):
                for compdep in compopt.dependencies:
                    if not self._poco_component_tree[compdep].option:
                        continue
                    if not self.options.get_safe(self._poco_component_tree[compdep].option, False):
                        raise ConanInvalidConfiguration(f"option {compopt.option} requires also option {self._poco_component_tree[compdep].option}")
        if self.options.enable_data_sqlite:
            if self.dependencies["sqlite3"].options.threadsafe == 0:
                raise ConanInvalidConfiguration("sqlite3 must be built with threadsafe enabled")
        if self.options.enable_netssl and self.options.get_safe("enable_netssl_win", False):
            raise ConanInvalidConfiguration("Conflicting enable_netssl[_win] settings")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_BUILD_TYPE"] = self.settings.build_type
        for comp in self._poco_component_tree.values():
            if comp.option:
                tc.variables[comp.option.upper()] = self.options.get_safe(comp.option, False)
        tc.variables["POCO_UNBUNDLED"] = True
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        if is_msvc(self):
            tc.variables["POCO_MT"] = is_msvc_static_runtime(self)
        if not self.options.enable_apacheconnector:
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_APR"] = True
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_APRUTIL"] = True
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Apache2"] = True
        # Disable fork
        if not self.options.get_safe("enable_fork", True):
            tc.variables["POCO_NO_FORK_EXEC"] = True
        if self.options.get_safe("with_sql_parser", None) is False:
            tc.variables["POCO_DATA_NO_SQL_PARSER"] = True
        # Disable automatic linking on MSVC
        tc.preprocessor_definitions["POCO_NO_AUTOMATIC_LIBS"] = "1"
        # Picked up from conan v1 CMake wrapper, don't know the rationale
        tc.preprocessor_definitions["XML_DTD"] = "1"
        # Disable SharedLibrary::suffix() including "d" as part of the platform-specific filename suffix
        if not self.options.get_safe("comp_foundation_sharedlibrary_debug_suffix", True):
            tc.preprocessor_definitions["POCO_NO_SHARED_LIBRARY_DEBUG_SUFFIX"] = "1"

        if self.options.get_safe("enable_data_mysql"):
            tc.cache_variables["MYSQL_FOUND"] = True
        if self.options.get_safe("enable_data_postgresql"):
            tc.cache_variables["POSTGRESQL_FOUND"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("expat", "cmake_target_name", "EXPAT::EXPAT")
        deps.set_property("expat", "cmake_find_mode", "config")
        deps.set_property("libmysqlclient", "cmake_file_name", "mysql")
        deps.set_property("libmysqlclient", "cmake_target_name", "MySQL::client")
        deps.set_property("libmysqlclient", "cmake_additional_variables_prefixes", ["MYSQL"])
        deps.set_property("libmysqlclient", "cmake_find_mode", "config")
        deps.set_property("libpq", "cmake_target_name", "PostgreSQL::PostgreSQL")
        deps.set_property("libpq", "cmake_target_aliases", ["PostgreSQL::client"])
        deps.set_property("libpq", "cmake_file_name", "PostgreSQL")
        deps.set_property("pcre2::pcre2-8", "cmake_target_name", "Pcre2::Pcre2")
        deps.set_property("utf8proc", "cmake_target_name", "Utf8Proc::Utf8Proc")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        # INFO: missing headers https://github.com/pocoproject/poco/issues/4378
        if self.options.get_safe("with_sql_parser", False):
            copy(
                self,
                "*.h",
                os.path.join(self.source_folder, "Data", "src"),
                os.path.join(self.package_folder, "include"),
            )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Poco")
        self.cpp_info.set_property("cmake_target_name", "Poco::Poco")

        suffix = msvc_runtime_flag(self).lower() \
                 if is_msvc(self) and not self.options.shared \
                 else ("d" if self.settings.build_type == "Debug" else "")

        for compname, comp in self._poco_component_tree.items():
            if comp.option is None or self.options.get_safe(comp.option):
                conan_component = f"poco_{compname.lower()}"
                requires = [f"poco_{dependency.lower()}" for dependency in comp.dependencies] + comp.external_dependencies
                self.cpp_info.components[conan_component].set_property("cmake_target_name", f"Poco::{compname}")
                self.cpp_info.components[conan_component].set_property("cmake_file_name", compname)
                if comp.is_lib:
                    self.cpp_info.components[conan_component].libs = [f"Poco{compname}{suffix}"]
                self.cpp_info.components[conan_component].requires = requires

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["poco_foundation"].system_libs.extend(["pthread", "dl", "rt"])

        if self.options.log_debug:
            self.cpp_info.components["poco_foundation"].defines.append("POCO_LOG_DEBUG")

        if is_msvc(self):
            self.cpp_info.components["poco_foundation"].defines.append("POCO_NO_AUTOMATIC_LIBS")
        if not self.options.shared:
            self.cpp_info.components["poco_foundation"].defines.append("POCO_STATIC=ON")
            if self.settings.os == "Windows":
                self.cpp_info.components["poco_foundation"].system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])
        if self.options.enable_net:
            if not self.options.shared and self._is_mingw:
                self.cpp_info.components["poco_net"].system_libs.extend(["mswsock"])
        if self.options.enable_data_odbc:
            if self.settings.os == "Windows":
                self.cpp_info.components["poco_dataodbc"].system_libs.extend(["odbc32", "odbccp32"])
            else:
                self.cpp_info.components["poco_dataodbc"].requires.append("odbc::odbc")
        self.cpp_info.components["poco_foundation"].defines.append("POCO_UNBUNDLED")
        if self.options.enable_util:
            if not self.options.enable_json:
                self.cpp_info.components["poco_util"].defines.append("POCO_UTIL_NO_JSONCONFIGURATION")
            if not self.options.enable_xml:
                self.cpp_info.components["poco_util"].defines.append("POCO_UTIL_NO_XMLCONFIGURATION")
