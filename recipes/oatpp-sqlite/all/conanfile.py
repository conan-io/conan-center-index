from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class OatppsqliteConan(ConanFile):
    name = "oatpp-sqlite"
    license = "Apache-2.0"
    homepage = "https://github.com/oatpp/oatpp-sqlite"
    url = "https://github.com/conan-io/conan-center-index"
    description = "oat++ SQLite library"
    topics = ("conan", "oat++", "oatpp", "sqlite")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("oatpp-sqlite can not be built as shared library on Windows")

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("oatpp-sqlite requires GCC >=5")

    def requirements(self):
        self.requires("oatpp/" + self.version)
        self.requires("sqlite3/3.33.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("oatpp-sqlite-{0}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["OATPP_BUILD_TESTS"] = False
        self._cmake.definitions["OATPP_MODULES_LOCATION"] = "INSTALLED"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-sqlite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-sqlite"
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.components["_oatpp-sqlite"].names["cmake_find_package"] = "oatpp-sqlite"
        self.cpp_info.components["_oatpp-sqlite"].names["cmake_find_package_multi"] = "oatpp-sqlite"
        self.cpp_info.components["_oatpp-sqlite"].includedirs = [
            os.path.join("include", "oatpp-{}".format(self.version), "oatpp-sqlite")
        ]
        self.cpp_info.components["_oatpp-sqlite"].libdirs = [os.path.join("lib", "oatpp-{}".format(self.version))]
        self.cpp_info.components["_oatpp-sqlite"].libs = ["oatpp-sqlite"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_oatpp-sqlite"].system_libs = ["pthread"]
        self.cpp_info.components["_oatpp-sqlite"].requires = ["oatpp::oatpp", "sqlite3::sqlite3"]
