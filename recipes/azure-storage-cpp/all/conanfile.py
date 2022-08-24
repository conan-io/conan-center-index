from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class AzureStorageCppConan(ConanFile):
    name = "azure-storage-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-storage-cpp"
    description = "Microsoft Azure Storage Client Library for C++"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compiler_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def requirements(self):
        self.requires("cpprestsdk/2.10.18")
        if self.settings.os != "Windows":
            self.requires("boost/1.76.0")
            self.requires("libxml2/2.9.10")
            self.requires("libuuid/1.0.3")
        if self.settings.os == "Macos":
            self.requires("libgettext/0.20.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["CMAKE_FIND_FRAMEWORK"] = "LAST"
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_SAMPLES"] = False
        if not self.settings.compiler.cppstd:
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = self._minimum_cpp_standard

        if self.settings.os == "Macos":
            self._cmake.definitions["GETTEXT_LIB_DIR"] = self.deps_cpp_info["libgettext"].lib_paths[0]

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

        # FIXME: Visual Studio 2015 & 2017 are supported but CI of CCI lacks several Win SDK components
        # https://github.com/conan-io/conan-center-index/issues/4195
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "16":
            raise ConanInvalidConfiguration("Visual Studio < 2019 not yet supported in this recipe")
        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "rpcrt4", "xmllite", "bcrypt"]
            if not self.options.shared:
                self.cpp_info.defines = ["_NO_WASTORAGE_API"]
