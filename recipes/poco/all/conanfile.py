from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from collections import namedtuple
import os

required_conan_version = ">=1.43.0"


class PocoConan(ConanFile):
    name = "poco"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pocoproject.org"
    topics = ("building", "networking", "server", "mobile", "embedded")
    license = "BSL-1.0"
    description = "Modern, powerful open source C++ class libraries for building network- and internet-based " \
                  "applications that run on desktop, server, mobile and embedded systems."

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_fork": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_fork": True,
    }

    _PocoComponent = namedtuple("_PocoComponent", ("option", "default_option", "dependencies", "external_dependencies", "is_lib"))
    _poco_component_tree = {
        "mod_poco": _PocoComponent("enable_apacheconnector", False, ["Util", "Net"], ["apr::apr", "apr-util::apr-util"], False),
        "CppParser": _PocoComponent("enable_cppparser", False, ["Foundation"], [], False),
        # "CppUnit": _PocoComponent("enable_cppunit", False, ["Foundation"], [], False)),
        "Crypto": _PocoComponent("enable_crypto", True, ["Foundation"], ["openssl::openssl"], True),
        "Data": _PocoComponent("enable_data", True, ["Foundation"], [], True),
        "DataMySQL": _PocoComponent("enable_data_mysql", True, ["Data"], ["apr::apr", "apr-util::apr-util", "libmysqlclient::libmysqlclient"], True),
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
        "ActiveRecord": _PocoComponent("enable_active_record", True, ["Foundation", "Data"], [], True),
    }

    for comp in _poco_component_tree.values():
        if comp.option:
            options[comp.option] = [True, False]
            default_options[comp.option] = comp.default_option
    del comp

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.enable_fork
        else:
            del self.options.enable_netssl_win
        if tools.Version(self.version) < "1.9":
            del self.options.enable_encodings
        if tools.Version(self.version) < "1.10":
            del self.options.enable_data_mysql
            del self.options.enable_data_postgresql
            del self.options.enable_jwt
        if tools.Version(self.version) < "1.11":
            del self.options.enable_active_record

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_xml:
            util_dependencies = self._poco_component_tree["Util"].dependencies
            self._poco_component_tree["Util"] = self._poco_component_tree["Util"]._replace(dependencies = [x for x in util_dependencies if x != "XML"])
        if not self.options.enable_json:
            util_dependencies = self._poco_component_tree["Util"].dependencies
            self._poco_component_tree["Util"] = self._poco_component_tree["Util"]._replace(dependencies = [x for x in util_dependencies if x != "JSON"])

    def requirements(self):
        self.requires("pcre/8.45")
        self.requires("zlib/1.2.11")
        if self.options.enable_xml:
            self.requires("expat/2.4.1")
        if self.options.enable_data_sqlite:
            self.requires("sqlite3/3.36.0")
        if self.options.enable_apacheconnector:
            self.requires("apr/1.7.0")
            self.requires("apr-util/1.6.1")
            # FIXME: missing apache2 recipe
            raise ConanInvalidConfiguration("apache2 is not (yet) available on CCI")
        if self.options.enable_netssl or \
                self.options.enable_crypto or \
                self.options.get_safe("enable_jwt", False):
            self.requires("openssl/1.1.1l")
        if self.options.enable_data_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.9")
        if self.options.get_safe("enable_data_postgresql", False):
            self.requires("libpq/13.4")
        if self.options.get_safe("enable_data_mysql", False):
            self.requires("apr/1.7.0")
            self.requires("apr-util/1.6.1")
            self.requires("libmysqlclient/8.0.25")

    def validate(self):
        if self.options.enable_apacheconnector:
            raise ConanInvalidConfiguration("Apache connector not supported: https://github.com/pocoproject/poco/issues/1764")
        if self.settings.compiler == "Visual Studio":
            if self.options.shared and "MT" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration("Cannot build shared poco libraries with MT(d) runtime")
        for compopt in self._poco_component_tree.values():
            if not compopt.option:
                continue
            if self.options.get_safe(compopt.option, False):
                for compdep in compopt.dependencies:
                    if not self._poco_component_tree[compdep].option:
                        continue
                    if not self.options.get_safe(self._poco_component_tree[compdep].option, False):
                        raise ConanInvalidConfiguration("option {} requires also option {}".format(compopt.option, self._poco_component_tree[compdep].option))
        if self.options.enable_data_sqlite:
            if self.options["sqlite3"].threadsafe == 0:
                raise ConanInvalidConfiguration("sqlite3 must be built with threadsafe enabled")
        if self.options.enable_netssl and self.options.get_safe("enable_netssl_win", False):
            raise ConanInvalidConfiguration("Conflicting enable_netssl[_win] settings")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
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
        if self.options.get_safe("enable_data_postgresql", False):
            self._cmake.definitions["PostgreSQL_ROOT_DIR"] = self.deps_cpp_info["libpq"].rootpath
            self._cmake.definitions["PostgreSQL_ROOT_INCLUDE_DIRS"] = ";".join(self.deps_cpp_info["libpq"].include_paths)
            self._cmake.definitions["PostgreSQL_ROOT_LIBRARY_DIRS"] = ";".join(self.deps_cpp_info["libpq"].lib_paths)
        if self.options.get_safe("enable_data_mysql", False):
            self._cmake.definitions["MYSQL_ROOT_DIR"] = self.deps_cpp_info["libmysqlclient"].rootpath
            self._cmake.definitions["MYSQL_ROOT_INCLUDE_DIRS"] = ";".join(self.deps_cpp_info["libmysqlclient"].include_paths)
            self._cmake.definitions["MYSQL_INCLUDE_DIR"] = ";".join(self.deps_cpp_info["libmysqlclient"].include_paths)
            self._cmake.definitions["MYSQL_ROOT_LIBRARY_DIRS"] = ";".join(self.deps_cpp_info["libmysqlclient"].lib_paths)
            self._cmake.definitions["APR_ROOT_DIR"] = self.deps_cpp_info["apr"].rootpath
            self._cmake.definitions["APR_ROOT_INCLUDE_DIRS"] = ";".join(self.deps_cpp_info["apr"].include_paths)
            self._cmake.definitions["APR_ROOT_LIBRARY_DIRS"] = ";".join(self.deps_cpp_info["apr"].lib_paths)
            self._cmake.definitions["APRUTIL_ROOT_DIR"] = self.deps_cpp_info["apr-util"].rootpath
            self._cmake.definitions["APRUTIL_ROOT_INCLUDE_DIRS"] = ";".join(self.deps_cpp_info["apr-util"].include_paths)
            self._cmake.definitions["APRUTIL_ROOT_LIBRARY_DIRS"] = ";".join(self.deps_cpp_info["apr-util"].lib_paths)

        self.output.info(self._cmake.definitions)
        # Disable fork
        if not self.options.get_safe("enable_fork", True):
            self._cmake.definitions["POCO_NO_FORK_EXEC"] = True
        # On Windows, Poco needs a message (MC) compiler.
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Poco")
        self.cpp_info.set_property("cmake_target_name", "Poco::Poco")

        self.cpp_info.filenames["cmake_find_package"] = "Poco"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Poco"
        self.cpp_info.names["cmake_find_package"] = "Poco"
        self.cpp_info.names["cmake_find_package_multi"] = "Poco"

        suffix = str(self.settings.compiler.runtime).lower()  \
                 if self.settings.compiler == "Visual Studio" and not self.options.shared \
                 else ("d" if self.settings.build_type == "Debug" else "")

        for compname, comp in self._poco_component_tree.items():
            if comp.option is None or self.options.get_safe(comp.option):
                conan_component = "poco_{}".format(compname.lower())
                requires = ["poco_{}".format(dependency.lower()) for dependency in comp.dependencies] + comp.external_dependencies
                self.cpp_info.components[conan_component].set_property("cmake_target_name", "Poco::{}".format(compname))
                self.cpp_info.components[conan_component].set_property("cmake_file_name", compname)
                self.cpp_info.components[conan_component].names["cmake_find_package"] = compname
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = compname
                if comp.is_lib:
                    self.cpp_info.components[conan_component].libs = ["Poco{}{}".format(compname, suffix)]
                self.cpp_info.components[conan_component].requires = requires

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["poco_foundation"].system_libs.extend(["pthread", "dl", "rt"])

        if self.settings.compiler == "Visual Studio":
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
