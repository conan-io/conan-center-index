from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class AzureStorageCppConan(ConanFile):
    name = "azure-storage-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-storage-cpp"
    description = "Microsoft Azure Storage Client Library for C++"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("cpprestsdk/2.10.18")
        if self.settings.os != "Windows":
            self.requires("libxml2/2.9.10")
            self.requires("libuuid/1.0.3")
        if self.settings.os == "Macos":
            self.requires("libgettext/0.20.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["CMAKE_FIND_FRAMEWORK"] = "LAST"
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_SAMPLES"] = False

        if self.settings.os == "Macos":
            self._cmake.definitions["GETTEXT_LIB_DIR"] = self.deps_cpp_info["libgettext"].lib_paths[0]

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        cmake_lists = os.path.join(self._source_subfolder, "Microsoft.WindowsAzure.Storage", "CMakeLists.txt")
        tools.replace_in_file(cmake_lists, "UUID", "libuuid")
        tools.replace_in_file(cmake_lists, "LibXML2", "LibXml2")
        tools.replace_in_file(cmake_lists, "Casablanca", "cpprestsdk")
        tools.replace_in_file(cmake_lists, "CASABLANCA", "cpprestsdk")
        tools.replace_in_file(cmake_lists, " -stdlib=libc++", "")
        tools.replace_in_file(cmake_lists, " -std=c++11", "")

    def build(self):
        self._patch_sources()
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "AzureStorage"
        self.cpp_info.names["cmake_find_package_multi"] = "AzureStorage"

        self.cpp_info.libs = tools.collect_libs(self)
