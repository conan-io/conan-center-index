from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag, VCVars
from conan.tools.scm import Version
from collections import namedtuple
import os

required_conan_version = ">=1.50.0"


class PocoConan(ConanFile):
    name = "poco"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pocoproject.org"
    topics = ("building", "networking", "server", "mobile", "embedded")
    license = "BSL-1.0"
    description = (
        "Modern, powerful open source C++ class libraries for building "
        "network- and internet-based applications that run on desktop, server, "
        "mobile and embedded systems."
    )

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_fork": [True, False],
        "enable_active_record": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_fork": True,
        "enable_active_record": "deprecated",
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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.enable_fork
        else:
            del self.options.enable_netssl_win
        if Version(self.version) < "1.9.0":
            del self.options.enable_encodings
        if Version(self.version) < "1.10.0":
            del self.options.enable_data_mysql
            del self.options.enable_data_postgresql
            del self.options.enable_jwt
        if Version(self.version) < "1.11.0":
            del self.options.enable_activerecord
            del self.options.enable_activerecord_compiler
        if Version(self.version) < "1.12.0":
            del self.options.enable_prometheus

    def configure(self):
        if self.options.enable_active_record != "deprecated":
            self.output.warn("enable_active_record option is deprecated, use 'enable_activerecord' instead")
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_xml:
            util_dependencies = self._poco_component_tree["Util"].dependencies
            self._poco_component_tree["Util"] = self._poco_component_tree["Util"]._replace(dependencies = [x for x in util_dependencies if x != "XML"])
        if not self.options.enable_json:
            util_dependencies = self._poco_component_tree["Util"].dependencies
            self._poco_component_tree["Util"] = self._poco_component_tree["Util"]._replace(dependencies = [x for x in util_dependencies if x != "JSON"])
        if Version(self.version) >= "1.12.0":
            foundation_external_dependencies = self._poco_component_tree["Foundation"].external_dependencies
            self._poco_component_tree["Foundation"] = self._poco_component_tree["Foundation"]._replace(external_dependencies = list(map(lambda x: 'pcre2::pcre2' if x == 'pcre::pcre' else x, foundation_external_dependencies)))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "1.12.0":
            self.requires("pcre/8.45")
        else:
            self.requires("pcre2/10.40")
        self.requires("zlib/1.2.12")
        if self.options.enable_xml:
            self.requires("expat/2.4.8")
        if self.options.enable_data_sqlite:
            self.requires("sqlite3/3.39.3")
        if self.options.enable_apacheconnector:
            self.requires("apr/1.7.0")
            self.requires("apr-util/1.6.1")
        if self.options.enable_netssl or self.options.enable_crypto or \
           self.options.get_safe("enable_jwt"):
            self.requires("openssl/1.1.1q")
        if self.options.enable_data_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.9")
        if self.options.get_safe("enable_data_postgresql"):
            self.requires("libpq/14.2")
        if self.options.get_safe("enable_data_mysql"):
            self.requires("libmysqlclient/8.0.29")

    def package_id(self):
        del self.info.options.enable_active_record

    def validate(self):
        if self.info.options.enable_apacheconnector:
            # FIXME: missing apache2 recipe + few issues
            raise ConanInvalidConfiguration("Apache connector not supported: https://github.com/pocoproject/poco/issues/1764")
        if is_msvc(self) and self.info.options.shared and is_msvc_static_runtime(self):
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
        if self.info.options.enable_data_sqlite:
            if self.dependencies["sqlite3"].options.threadsafe == 0:
                raise ConanInvalidConfiguration("sqlite3 must be built with threadsafe enabled")
        if self.info.options.enable_netssl and self.options.get_safe("enable_netssl_win", False):
            raise ConanInvalidConfiguration("Conflicting enable_netssl[_win] settings")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def _dep_include_paths(self, dep):
        dep_info = self.dependencies[dep]
        return [os.path.join(dep_info.package_folder, dir).replace("\\", "/") for dir in dep_info.cpp_info.includedirs]

    def _dep_lib_paths(self, dep):
        dep_info = self.dependencies[dep]
        return [os.path.join(dep_info.package_folder, dir).replace("\\", "/") for dir in dep_info.cpp_info.libdirs]

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_BUILD_TYPE"] = self.settings.build_type
        if Version(self.version) < "1.10.1":
            tc.variables["POCO_STATIC"] = not self.options.shared
        for comp in self._poco_component_tree.values():
            if comp.option:
                tc.variables[comp.option.upper()] = self.options.get_safe(comp.option, False)
        tc.variables["POCO_UNBUNDLED"] = True
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        if is_msvc(self):
            tc.variables["POCO_MT"] = is_msvc_static_runtime(self)
        if self.options.get_safe("enable_data_postgresql", False):
            tc.variables["PostgreSQL_ROOT_DIR"] = self.dependencies["libpq"].package_folder.replace("\\", "/")
            tc.variables["PostgreSQL_ROOT_INCLUDE_DIRS"] = ";".join(self._dep_include_paths("libpq"))
            tc.variables["PostgreSQL_ROOT_LIBRARY_DIRS"] = ";".join(self._dep_lib_paths("libpq"))
        if self.options.get_safe("enable_data_mysql", False):
            tc.variables["MYSQL_ROOT_DIR"] = self.dependencies["libmysqlclient"].package_folder.replace("\\", "/")
            tc.variables["MYSQL_ROOT_INCLUDE_DIRS"] = ";".join(self._dep_include_paths("libmysqlclient"))
            tc.variables["MYSQL_INCLUDE_DIR"] = ";".join(self._dep_include_paths("libmysqlclient"))
            tc.variables["MYSQL_ROOT_LIBRARY_DIRS"] = ";".join(self._dep_lib_paths("libmysqlclient"))
        if self.options.enable_apacheconnector:
            tc.variables["APR_ROOT_DIR"] = self.dependencies["apr"].package_folder.replace("\\", "/")
            tc.variables["APR_ROOT_INCLUDE_DIRS"] = ";".join(self._dep_include_paths("apr"))
            tc.variables["APR_ROOT_LIBRARY_DIRS"] = ";".join(self._dep_lib_paths("apr"))
            tc.variables["APRUTIL_ROOT_DIR"] = self.dependencies["apr-util"].package_folder.replace("\\", "/")
            tc.variables["APRUTIL_ROOT_INCLUDE_DIRS"] = ";".join(self._dep_include_paths("apr-util"))
            tc.variables["APRUTIL_ROOT_LIBRARY_DIRS"] = ";".join(self._dep_lib_paths("apr-util"))
        # Disable fork
        if not self.options.get_safe("enable_fork", True):
            tc.variables["POCO_NO_FORK_EXEC"] = True
        # Disable automatic linking on MSVC
        tc.preprocessor_definitions["POCO_NO_AUTOMATIC_LIBS"] = "1"
        # Picked up from conan v1 CMake wrapper, don't know the rationale
        if Version(self.version) >= "1.11.0":
            tc.preprocessor_definitions["XML_DTD"] = "1"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if is_msvc(self):
            # On Windows, Poco needs a message (MC) compiler.
            vcvars = VCVars(self)
            vcvars.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # mysql
        if self.options.get_safe("enable_data_mysql"):
            mysql_cpp_info = self.dependencies["libmysqlclient"].cpp_info
            mysql_config_file = mysql_cpp_info.get_property("cmake_file_name") or "libmysqlclient"
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                "find_package(MySQL REQUIRED)",
                f"find_package({mysql_config_file} REQUIRED CONFIG)\nset(MYSQL_FOUND TRUE)",
            )
            mysql_target_name = mysql_cpp_info.get_property("cmake_target_name") or "libmysqlclient::libmysqlclient"
            replace_in_file(
                self,
                os.path.join(self.source_folder, "Data", "MySQL", "CMakeLists.txt"),
                "MySQL::client",
                mysql_target_name,
            )
        # libpq
        if self.options.get_safe("enable_data_postgresql"):
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                "find_package(PostgreSQL REQUIRED)",
                "find_package(PostgreSQL REQUIRED)\nset(POSTGRESQL_FOUND TRUE)",
            )
            replace_in_file(
                self,
                os.path.join(self.source_folder, "Data", "PostgreSQL", "CMakeLists.txt"),
                "PostgreSQL::client",
                "PostgreSQL::PostgreSQL",
            )
        # Ensure to use FindEXPAT.cmake instead of expat-config.cmake
        # (side effect of CMAKE_FIND_PACKAGE_PREFER_CONFIG ON, see https://github.com/conan-io/conan/issues/10387)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "XML", "CMakeLists.txt"),
            "find_package(EXPAT REQUIRED)",
            "find_package(EXPAT REQUIRED MODULE)",
        )

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
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Poco")
        self.cpp_info.set_property("cmake_target_name", "Poco::Poco")

        self.cpp_info.filenames["cmake_find_package"] = "Poco"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Poco"
        self.cpp_info.names["cmake_find_package"] = "Poco"
        self.cpp_info.names["cmake_find_package_multi"] = "Poco"

        suffix = msvc_runtime_flag(self).lower() \
                 if is_msvc(self) and not self.options.shared \
                 else ("d" if self.settings.build_type == "Debug" else "")

        for compname, comp in self._poco_component_tree.items():
            if comp.option is None or self.options.get_safe(comp.option):
                conan_component = f"poco_{compname.lower()}"
                requires = [f"poco_{dependency.lower()}" for dependency in comp.dependencies] + comp.external_dependencies
                self.cpp_info.components[conan_component].set_property("cmake_target_name", f"Poco::{compname}")
                self.cpp_info.components[conan_component].set_property("cmake_file_name", compname)
                self.cpp_info.components[conan_component].names["cmake_find_package"] = compname
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = compname
                if comp.is_lib:
                    self.cpp_info.components[conan_component].libs = [f"Poco{compname}{suffix}"]
                self.cpp_info.components[conan_component].requires = requires

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["poco_foundation"].system_libs.extend(["pthread", "dl", "rt"])

        if is_msvc(self):
            self.cpp_info.components["poco_foundation"].defines.append("POCO_NO_AUTOMATIC_LIBS")
        if not self.options.shared:
            self.cpp_info.components["poco_foundation"].defines.append("POCO_STATIC=ON")
            if self.settings.os == "Windows":
                self.cpp_info.components["poco_foundation"].system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])
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
