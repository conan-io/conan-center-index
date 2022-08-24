import os
import re

from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None
    _cmake = None

    def requirements(self):
        self.requires("aws-libfabric/1.9.1amzncdi1.0")
        self.requires("aws-sdk-cpp/1.8.130")

    def configure(self):
        self.options["aws-libfabric"].shared = True
        self.options["aws-sdk-cpp"].shared = True

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This recipe currently only supports Linux. Feel free to contribute other platforms!")
        if not self.options["aws-libfabric"].shared or not self.options["aws-sdk-cpp"].shared:
            raise ConanInvalidConfiguration("Cannot build with static dependencies")
        if not getattr(self.options["aws-sdk-cpp"], "monitoring"):
            raise ConanInvalidConfiguration("This package requires the monitoring AWS SDK")
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        self._cmake.configure()
        return self._cmake

    def _detect_compilers(self):
        cmake_cache = tools.load(os.path.join(self.build_folder, "CMakeCache.txt"))
        cc = re.search("CMAKE_C_COMPILER:FILEPATH=(.*)", cmake_cache)[1]
        cxx = re.search("CMAKE_CXX_COMPILER:FILEPATH=(.*)", cmake_cache)[1]
        return cc, cxx

    def build(self):        
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # build aws-cpp-sdk-cdi
        cmake = self._configure_cmake()
        cmake.build()

        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            # configure autotools to find aws-cpp-sdk-cdi
            autotools.include_paths.append(os.path.join(self.build_folder, self._source_subfolder, "aws-cpp-sdk-cdi", "include"))
            autotools.library_paths.append(os.path.join(self.build_folder, "lib"))
            autotools.libs.append("aws-cpp-sdk-cdi")

            vars = autotools.vars
            cc, cxx = self._detect_compilers()
            vars["CC"] = cc
            vars["CXX"] = cxx
            if self.settings.build_type == "Debug":
                vars["DEBUG"] = "y"

            args = ["require_aws_sdk=no"]

            autotools.make(target="libsdk", vars=vars, args=args)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        config = "debug" if self.settings.build_type == "Debug" else "release"
        self.copy(pattern="*", dst="lib", src=os.path.join(self._source_subfolder, "build", config, "lib"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):        
        self.cpp_info.set_property("cmake_file_name", "aws-cdi-sdk")
        
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # TODO: Remove the namespace on CMake targets
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.filenames["cmake_find_package"] = "aws-cdi-sdk"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-cdi-sdk"

        cppSdk = self.cpp_info.components["aws-cpp-sdk-cdi"]
        cppSdk.libs = ["aws-cpp-sdk-cdi"]

        cppSdk.requires = ["aws-sdk-cpp::monitoring", "aws-libfabric::aws-libfabric"]
        
        cppSdk.set_property("cmake_target_name", "AWS::aws-cpp-sdk-cdi")
        cppSdk.set_property("pkg_config_name", "aws-cpp-sdk-cdi")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # TODO: Remove the namespace on CMake targets
        cppSdk.names["cmake_find_package"] = "aws-cpp-sdk-cdi"
        cppSdk.names["cmake_find_package_multi"] = "aws-cpp-sdk-cdi"
        cppSdk.names["pkg_config"] = "aws-cpp-sdk-cdi"

        cSdk = self.cpp_info.components["cdisdk"]
        cSdk.libs = ["cdisdk"]
        cSdk.requires = ["aws-cpp-sdk-cdi"]
        if self.settings.os == "Linux":
            cSdk.defines = ["_LINUX"]

        cSdk.set_property("cmake_target_name", "AWS::aws-cdi-sdk")
        cSdk.set_property("pkg_config_name", "aws-cdi-sdk")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # TODO: Remove the namespace on CMake targets
        cSdk.names["cmake_find_package"] = "aws-cdi-sdk"
        cSdk.names["cmake_find_package_multi"] = "aws-cdi-sdk"
        cSdk.names["pkg_config"] = "aws-cdi-sdk"

