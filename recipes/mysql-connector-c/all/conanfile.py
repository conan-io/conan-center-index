from conans import ConanFile, CMake, tools
import os
import glob



class MysqlConnectorCConan(ConanFile):
    name = "mysql-connector-c"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C development."
    topics = ("conan", "mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/connector/c/"
    license = "GPL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "with_ssl": [True, False], "with_zlib": [True, False]}
    default_options = {'shared': False, 'with_ssl': True, 'with_zlib': True}
    _source_subfolder = "source_subfolder"

    def requirements(self):
        if self.options.with_ssl:
            self.requires.add("openssl/1.0.2u")

        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11")

    def source(self):
        archive_name = self.name + "-" + self.version + "-src"
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)

        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")

        os.rename(sources_cmake, sources_cmake_orig)
        os.rename("CMakeLists.txt", sources_cmake)
        
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        cmake.definitions["DISABLE_STATIC"] = self.options.shared
        cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards

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
        os.rename(os.path.join(self.package_folder, "COPYING"), os.path.join(self.package_folder, "licenses", "COPYING"))
        os.rename(os.path.join(self.package_folder, "COPYING-debug"), os.path.join(self.package_folder, "licenses", "COPYING-debug"))
        os.remove(os.path.join(self.package_folder, "README"))
        os.remove(os.path.join(self.package_folder, "README-debug"))
        for f in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.remove(f)
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(f)
        tools.rmdir(os.path.join(self.package_folder, "docs"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.bindirs = ['lib']
