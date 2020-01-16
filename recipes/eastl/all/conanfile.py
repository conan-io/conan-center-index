import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version


class Bzip2Conan(ConanFile):
    name = "eastl"
    description = "EASTL stands for Electronic Arts Standard Template Library. It is an extensive and robust implementation that has an emphasis on high performance."
    topics = ("conan", "eastl", "stl", "high-performance")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EASTL"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "Visual Studio": "14",
            "gcc": "6",
            "clang": "3.4"
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def requirements(self):
        self.requires("eabase/2.09.05")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "EASTL-{}".format(self.version)
        os.rename(folder_name, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.definitions["EASTSL_BUILD_BENCHMARK"] = False
        cmake.definitions["EASTL_BUILD_TESTS"] = False
        cmake.configure()
        return cmake

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
        self.copy("3RDPARTYLICENSES.TXT",
                  src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.name = "EASTL"
        self.cpp_info.libs = ["EASTL"]
        if self.settings.os in ("Android", "Linux", "Macos", "watchOS", "tvOS"):
            self.cpp_info.system_libs.append("pthread")
