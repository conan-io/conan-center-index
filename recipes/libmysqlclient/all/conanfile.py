from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob



class libMysqlClientCConan(ConanFile):
    name = "libmysqlclient"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C development."
    topics = ("conan", "mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/mysql/"
    license = "GPL-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "with_ssl": [True, False], "with_zlib": [True, False]}
    default_options = {'shared': False, 'with_ssl': True, 'with_zlib': True}
    _source_subfolder = "source_subfolder"

    def requirements(self):
        if self.options.with_ssl:
            self.requires.add("openssl/1.1.1d")

        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11")

    def source(self):
        archive_name = "mysql-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)
        
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "INCLUDE(cmake/boost.cmake)", "", strict=True)
        
        for lib in ["icu", "libevent", "re2", "rapidjson", "lz4", "protobuf"]:
            tools.rmdir(os.path.join(self._source_subfolder, "extra", lib))
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "INCLUDE(%s)" % lib, "", strict=True)
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "MYSQL_CHECK_%s()" % lib.upper(), "", strict=True)
            
        for dir in ['client', 'man']:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "ADD_SUBDIRECTORY(%s)" % dir, "", strict=True)
            tools.rmdir(os.path.join(self._source_subfolder, dir))
            
        tools.rmdir(os.path.join(self._source_subfolder, "extra", "libedit"))
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "MYSQL_CHECK_EDITLINE()", "", strict=True)

        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")

        os.rename(sources_cmake, sources_cmake_orig)
        os.rename("CMakeLists.txt", sources_cmake)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.options.shared:
            raise ConanInvalidConfiguration("libmysqlclient cannot be built as static library")

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        cmake.definitions["WITHOUT_SERVER"] = True
        cmake.definitions["WITH_UNIT_TESTS"] = False
        cmake.definitions["ENABLED_PROFILING"] = False
        cmake.definitions["WIX_DIR"] = False

        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MD" or self.settings.compiler.runtime == "MDd":
                cmake.definitions["WINDOWS_RUNTIME_MD"] = True

        if self.options.with_ssl:
            cmake.definitions["WITH_SSL"] = "system"

        if self.options.with_zlib:
            cmake.definitions["WITH_ZLIB"] = "system"

        cmake.configure(source_dir=self._source_subfolder)
        return cmake
    
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        
    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        os.mkdir(os.path.join(self.package_folder, "licenses"))
        os.rename(os.path.join(self.package_folder, "LICENSE"), os.path.join(self.package_folder, "licenses", "LICENSE"))
        os.remove(os.path.join(self.package_folder, "README"))
        for f in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.remove(f)
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(f)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "docs"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
