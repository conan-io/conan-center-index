from from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"

class AwsCrtCpp(ConanFile):
    name = "aws-crt-cpp"
    description = "C++ wrapper around the aws-c-* libraries. Provides Cross-Platform Transport Protocols and SSL/TLS implementations for C++."
    topics = ("aws", "amazon", "cloud", "wrapper")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-crt-cpp"
    license = "Apache-2.0",
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

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("aws-c-event-stream/0.2.7")
        self.requires("aws-c-common/0.6.19")
        self.requires("aws-c-io/0.10.20")
        self.requires("aws-c-http/0.6.13")
        self.requires("aws-c-auth/0.6.11")
        self.requires("aws-c-mqtt/0.7.10")
        self.requires("aws-c-s3/0.1.37")
        self.requires("aws-checksums/0.1.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_DEPS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "aws-crt-cpp"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-crt-cpp")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-crt-cpp")

        self.cpp_info.filenames["cmake_find_package"] = "aws-crt-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-crt-cpp"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-crt-cpp-lib"].names["cmake_find_package"] = "aws-crt-cpp"
        self.cpp_info.components["aws-crt-cpp-lib"].names["cmake_find_package_multi"] = "aws-crt-cpp"
        self.cpp_info.components["aws-crt-cpp-lib"].libs = ["aws-crt-cpp"]
        self.cpp_info.components["aws-crt-cpp-lib"].requires = [
            "aws-c-event-stream::aws-c-event-stream-lib",
            "aws-c-common::aws-c-common-lib",
            "aws-c-io::aws-c-io-lib",
            "aws-c-http::aws-c-http-lib",
            "aws-c-auth::aws-c-auth-lib",
            "aws-c-mqtt::aws-c-mqtt-lib",
            "aws-c-s3::aws-c-s3-lib",
            "aws-checksums::aws-checksums-lib"
        ]
