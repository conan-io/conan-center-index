from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class CppCommon(ConanFile):
    name = "cppcommon"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chronoxor/CppCommon"
    description = "C++ Common Library contains reusable components and patterns" \
        " for error and exceptions handling, filesystem manipulations, math," \
        " string format and encoding, shared memory, threading, time management" \
        " and others."
    topics = ("conan", "utils", "library")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["fmt/7.0.3", "stduuid/1.0"]
    generators = "cmake"
    exports_sources = ["patches/**", "CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "Visual Studio": 16,
        }

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CPPCOMMON_MODULE"] = "OFF"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("CppCommon-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("Visual Studio x86 builds are not supported.")

        if self.options.shared:
            del self.options.fPIC

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("cppcommon requires C++17, which your compiler does not support.")
        else:
            self.output.warn("cppcommon requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def build(self):
        self._patch()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.includedirs.append(os.path.join("include", "plugins"))

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["rt", "dl"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["userenv", "rpcrt4"]
