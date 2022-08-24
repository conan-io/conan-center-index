from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
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
    options = {"fPIC": [True, False], "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}
    exports_sources = ["patches/**", "CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
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

    def requirements(self):
        self.requires("fmt/8.0.0")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("CppCommon-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CPPCOMMON_MODULE"] = "OFF"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.inl", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.h", dst=os.path.join("include", "plugins"), src=os.path.join(self._source_subfolder, "plugins"))

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.includedirs.append(os.path.join("include", "plugins"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "rt", "dl", "m"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["userenv", "rpcrt4"]
