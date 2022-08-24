from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"

class OatppLibresslConan(ConanFile):
    name = "oatpp-libressl"
    license = "Apache-2.0"
    homepage = "https://github.com/oatpp/oatpp-libressl"
    url = "https://github.com/conan-io/conan-center-index"
    description = "oat++ libressl library"
    topics = ("oat++", "oatpp", "libressl")
    settings = "os", "arch", "compiler", "build_type"
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

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("oatpp-libressl can not be built as shared library on Windows")

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("oatpp-libressl requires GCC >=5")

    def requirements(self):
        self.requires("oatpp/" + self.version)
        self.requires("libressl/3.2.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

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
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-libressl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-libressl"
        self.cpp_info.set_property("cmake_file_name", "oatpp-libressl")
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.set_property("cmake_target_name", "oatpp::oatpp-libressl")
        self.cpp_info.components["_oatpp-libressl"].names["cmake_find_package"] = "oatpp-libressl"
        self.cpp_info.components["_oatpp-libressl"].names["cmake_find_package_multi"] = "oatpp-libressl"
        self.cpp_info.components["_oatpp-libressl"].set_property("cmake_target_name", "oatpp::oatpp-libressl")
        self.cpp_info.components["_oatpp-libressl"].includedirs = [
            os.path.join("include", "oatpp-{}".format(self.version), "oatpp-libressl")
        ]
        self.cpp_info.components["_oatpp-libressl"].libdirs = [os.path.join("lib", "oatpp-{}".format(self.version))]
        self.cpp_info.components["_oatpp-libressl"].libs = ["oatpp-libressl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_oatpp-libressl"].system_libs = ["pthread"]
        self.cpp_info.components["_oatpp-libressl"].requires = ["oatpp::oatpp", "libressl::libressl"]
