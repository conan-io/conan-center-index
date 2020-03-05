import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class EastlConan(ConanFile):
    name = "eastl"
    description = "EASTL stands for Electronic Arts Standard Template Library. " \
                  "It is an extensive and robust implementation that has an " \
                  "emphasis on high performance."
    topics = ("conan", "eastl", "stl", "high-performance")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EASTL"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.settings.compiler.cppstd:
            self.output.info("Settings c++ standard to {}".format(self._minimum_cpp_standard))
            self.settings.compiler.cppstd = self._minimum_cpp_standard

        unsupported_cppstd = ("98", "11")
        for cppstd in unsupported_cppstd:
            if cppstd in str(self.settings.compiler.cppstd):
                raise ConanInvalidConfiguration("EASTL requires c++ {} or newer".format(self._minimum_cpp_standard))

        if (self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5") or \
           (self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "3.4") or \
           (self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "14"):
            raise ConanInvalidConfiguration("Compiler is too old for c++ {}".format(self._minimum_cpp_standard))

    def requirements(self):
        self.requires("eabase/2.09.05")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "EASTL-{}".format(self.version)
        os.rename(folder_name, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["EASTL_BUILD_BENCHMARK"] = False
        self._cmake.definitions["EASTL_BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_path_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                   "include(CommonCppFlags)",
                                   "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("3RDPARTYLICENSES.TXT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "EASTL"
        self.cpp_info.names["cmake_find_package_multi"] = "EASTL"
        self.cpp_info.libs = ["EASTL"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("EASTL_DLL")
