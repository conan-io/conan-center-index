from enum import auto
from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.35.0"

class AwsCdiSdkConan(ConanFile):
    name = "aws-cdi-sdk"
    description = "AWS Cloud Digital Interface (CDI) SDK"
    topics = ("aws", "communication", "framework", "service")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-cdi-sdk"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    requires = "aws-libfabric/1.9.1amzncdi1.0", "aws-sdk-cpp/1.8.130"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None
    _cmake = None

    def configure(self):
        self.options["aws-sdk-cpp"].monitoring = True
        self.options["aws-sdk-cpp"].shared = True
        self.options["aws-libfabric"].shared = True


    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("The aws-cdi-sdk package cannot be built on Windows.")
        elif (self.settings.compiler == "gcc"
                and tools.Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration("""Doesn't support gcc5 / shared.
            See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744""")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CPP_STANDARD"] = self._cmake.definitions.get("CONAN_CMAKE_CXX_STANDARD", "11")
        self._cmake.configure()
        return self._cmake

    def build(self):        
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # build aws-cpp-sdk-cdi
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()

        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            vars = autotools.vars
            # configure autotools to find aws-cpp-sdk-cdi
            vars["CXXFLAGS"] += " -I{}".format(os.path.join(self.package_folder, 'include'))
            vars["LDFLAGS"] += " -L{}".format(os.path.join(self.package_folder, 'lib'))
            vars["LIBS"] += ' -laws-cpp-sdk-cdi'
            if self.settings.build_type == 'Debug':
                vars["DEBUG"] = 'y'
            autotools.make(target='lib', vars=vars)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        config = "debug" if self.settings.build_type == "Debug" else "release"
        self.copy(pattern="*", dst="lib", src=os.path.join(self._source_subfolder, "build", config, "lib"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()
        if self.settings.os == "Linux":
            self.cpp_info.defines = ["_LINUX"]
        self.cpp_info.requires = ["aws-sdk-cpp::monitoring", "aws-libfabric::aws-libfabric"]

