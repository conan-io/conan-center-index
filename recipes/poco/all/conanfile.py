import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class PocoConan(ConanFile):
    name = "poco"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pocoproject.org"
    topics = ("conan", "poco", "building", "networking", "server", "mobile", "embedded")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    license = "BSL-1.0"
    description = "Modern, powerful open source C++ class libraries for building network- and internet-based " \
                  "applications that run on desktop, server, mobile and embedded systems."
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "enable_xml": [True, False],
               "enable_json": [True, False],
               "enable_mongodb": [True, False],
               "enable_pdf": [True, False],
               "enable_util": [True, False],
               "enable_net": [True, False],
               "enable_netssl": [True, False],
               "enable_netssl_win": [True, False],
               "enable_crypto": [True, False],
               "enable_data": [True, False],
               "enable_data_sqlite": [True, False],
               "enable_data_mysql": [True, False],
               "enable_data_odbc": [True, False],
               "enable_encodings": [True, False],
               "enable_jwt": [True, False],
               "enable_sevenzip": [True, False],
               "enable_zip": [True, False],
               "enable_apacheconnector": [True, False],
               "enable_cppparser": [True, False],
               "enable_pocodoc": [True, False],
               "enable_pagecompiler": [True, False],
               "enable_pagecompiler_file2page": [True, False],
               "enable_redis": [True, False],
               "force_openssl": [True, False],
               "enable_tests": [True, False],
               "poco_unbundled": [True, False],
               "cxx_14": [True, False]
              }
    default_options = {
                "shared": False,
                "fPIC": True,
                "enable_xml": True,
                "enable_json": True,
                "enable_mongodb": True,
                "enable_pdf": False,
                "enable_util": True,
                "enable_net": True,
                "enable_netssl": True,
                "enable_netssl_win": True,
                "enable_crypto": True,
                "enable_data": True,
                "enable_data_sqlite": True,
                "enable_data_mysql": False,
                "enable_data_odbc": False,
                "enable_encodings": True,
                "enable_jwt": True,
                "enable_sevenzip": False,
                "enable_zip": True,
                "enable_apacheconnector": False,
                "enable_cppparser": False,
                "enable_pocodoc": False,
                "enable_pagecompiler": False,
                "enable_pagecompiler_file2page": False,
                "enable_redis": True,
                "force_openssl": True,
                "enable_tests": False,
                "poco_unbundled": False,
                "cxx_14": False
            }

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

    def configure(self):
        if self.options.enable_apacheconnector:
            raise ConanInvalidConfiguration("Apache connector not supported: https://github.com/pocoproject/poco/issues/1764")
        if self.options.enable_data_mysql:
            raise ConanInvalidConfiguration("MySQL not supported yet, open an issue here please: %s" % self.url)

    def requirements(self):
        if self.options.enable_netssl or \
           self.options.enable_netssl_win or \
           self.options.enable_crypto or \
           self.options.force_openssl or \
           self.options.enable_jwt:
            self.requires.add("openssl/1.0.2t")

    def _patch(self):
        if self.settings.compiler == "Visual Studio":
            replace = "POCO_INSTALL_PDB(${target_name})"
            tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "PocoMacros.cmake"), replace, "# " + replace)
            if self.options.shared:
                self.output.warn("Adding ws2_32 dependency...")
                replace = 'Net Util Foundation Crypt32.lib'
                if Version(self.version) >= "1.10.0":
                    replace = 'Poco::Net Poco::Util Crypt32.lib'
                tools.replace_in_file(os.path.join(self._source_subfolder, "NetSSL_Win", "CMakeLists.txt"), replace, replace + " ws2_32 ")

                replace = 'Foundation ${OPENSSL_LIBRARIES}'
                if Version(self.version) >= "1.10.0":
                    replace = 'Poco::Foundation OpenSSL::SSL OpenSSL::Crypto'
                tools.replace_in_file(os.path.join(self._source_subfolder, "Crypto", "CMakeLists.txt"), replace, replace + " ws2_32 Crypt32.lib")

        # Poco 1.9.x - CMAKE_SOURCE_DIR is required in many places
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"), os.path.join(self._source_subfolder, "CMakeListsOriginal.cmake"))
        os.rename("CMakeLists.txt", os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def _configure_cmake(self):
        cmake = CMake(self, parallel=None)
        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if option_name == "shared":
                cmake.definitions["POCO_STATIC"] = "OFF" if activated else "ON"
            elif not option_name == "fPIC":
                cmake.definitions[option_name.upper()] = "ON" if activated else "OFF"

        cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":  # MT or MTd
            cmake.definitions["POCO_MT"] = "ON" if "MT" in str(self.settings.compiler.runtime) else "OFF"
        self.output.info(cmake.definitions)
        cmake.configure(build_dir=self._build_subfolder, source_dir=os.path.join("..", self._source_subfolder))
        return cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        libs = [("enable_mongodb", "PocoMongoDB"),
                ("enable_pdf", "PocoPDF"),
                ("enable_netssl", "PocoNetSSL"),
                ("enable_netssl_win", "PocoNetSSLWin"),
                ("enable_net", "PocoNet"),
                ("enable_crypto", "PocoCrypto"),
                ("enable_data_sqlite", "PocoDataSQLite"),
                ("enable_data_mysql", "PocoDataMySQL"),
                ("enable_data_odbc", "PocoDataODBC"),
                ("enable_data", "PocoData"),
                ("enable_sevenzip", "PocoSevenZip"),
                ("enable_zip", "PocoZip"),
                ("enable_apacheconnector", "PocoApacheConnector"),
                ("enable_util", "PocoUtil"),
                ("enable_xml", "PocoXML"),
                ("enable_json", "PocoJSON"),
                ("enable_redis", "PocoRedis")]

        suffix = str(self.settings.compiler.runtime).lower()  \
                 if self.settings.compiler == "Visual Studio" and not self.options.shared \
                 else ("d" if self.settings.build_type=="Debug" else "")
        for flag, lib in libs:
            if getattr(self.options, flag):
                if self.settings.os == "Windows" and flag == "enable_netssl" and self.options.enable_netssl_win:
                    continue

                if self.settings.os != "Windows" and flag == "enable_netssl_win":
                    continue

                self.cpp_info.libs.append("%s%s" % (lib, suffix))

        self.cpp_info.libs.append("PocoFoundation%s" % suffix)

        # in linux we need to link also with these libs
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "dl", "rt"])

        if not self.options.shared:
            self.cpp_info.defines.extend(["POCO_STATIC=ON", "POCO_NO_AUTOMATIC_LIBS"])
            if self.settings.compiler == "Visual Studio":
                self.cpp_info.libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])
        self.cpp_info.names["cmake_find_package"] = "Poco"
        self.cpp_info.names["cmake_find_package_multi"] = "Poco"
