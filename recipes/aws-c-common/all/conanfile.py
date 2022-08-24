from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class AwsCCommon(ConanFile):
    name = "aws-c-common"
    description = "Core c99 package for AWS SDK for C. Includes cross-platform primitives, configuration, data structures, and error handling."
    topics = ("aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-common"
    license = "Apache-2.0",

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpu_extensions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpu_extensions": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.scm.Version(self, self.version) < "0.6.11":
            del self.options.cpu_extensions

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Static runtime + shared is not working for more recent releases")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["STATIC_CRT"] = "MT" in self.settings.compiler.runtime
        self._cmake.definitions["USE_CPU_EXTENSIONS"] = self.options.get_safe("cpu_extensions", False)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-common"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-common")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-common")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-common"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-common"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-common-lib"].set_property("cmake_target_name", "AWS::aws-c-common")
        self.cpp_info.components["aws-c-common-lib"].names["cmake_find_package"] = "aws-c-common"
        self.cpp_info.components["aws-c-common-lib"].names["cmake_find_package_multi"] = "aws-c-common"

        self.cpp_info.components["aws-c-common-lib"].libs = ["aws-c-common"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["aws-c-common-lib"].system_libs = ["dl", "m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["aws-c-common-lib"].system_libs = ["bcrypt", "ws2_32"]
            if tools.scm.Version(self, self.version) >= "0.6.13":
                self.cpp_info.components["aws-c-common-lib"].system_libs.append("shlwapi")
        if not self.options.shared:
            if tools.is_apple_os(self, self.settings.os):
                self.cpp_info.components["aws-c-common-lib"].frameworks = ["CoreFoundation"]
        self.cpp_info.components["aws-c-common-lib"].builddirs.append(os.path.join("lib", "cmake"))
