import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"

class AwsCIO(ConanFile):
    name = "aws-c-io"
    description = "IO and TLS for application protocols"
    topics = ("conan", "aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-io"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("aws-c-cal/0.5.11")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("s2n/1.0.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-io"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-io"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-io"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-io-lib"].names["cmake_find_package"] = "aws-c-io"
        self.cpp_info.components["aws-c-io-lib"].names["cmake_find_package_multi"] = "aws-c-io"
        self.cpp_info.components["aws-c-io-lib"].libs = ["aws-c-io"]
        self.cpp_info.components["aws-c-io-lib"].requires = ["aws-c-cal::aws-c-cal-lib"]

        if self.settings.os == "Macos":
            self.cpp_info.components["aws-c-io-lib"].frameworks.append("Security")
        if self.settings.os == "Windows":
            self.cpp_info.components["aws-c-io-lib"].system_libs = ["crypt32", "secur32", "shlwapi"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["aws-c-io-lib"].requires.append("s2n::s2n-lib")
