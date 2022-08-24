from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class AwsCS3(ConanFile):
    name = "aws-c-s3"
    description = "C99 implementation of the S3 client"
    topics = ("aws", "amazon", "cloud", "s3")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-s3"
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
        self.requires("aws-c-common/0.6.19")
        self.requires("aws-c-io/0.10.20")
        self.requires("aws-c-http/0.6.13")
        self.requires("aws-c-auth/0.6.11")
        if tools.Version(self.version) >= "0.1.36":
            self.requires("aws-checksums/0.1.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-s3"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-s3")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-s3")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-s3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-s3"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-s3-lib"].names["cmake_find_package"] = "aws-c-s3"
        self.cpp_info.components["aws-c-s3-lib"].names["cmake_find_package_multi"] = "aws-c-s3"
        self.cpp_info.components["aws-c-s3-lib"].set_property("cmake_target_name", "AWS::aws-c-s3")

        self.cpp_info.components["aws-c-s3-lib"].libs = ["aws-c-s3"]
        self.cpp_info.components["aws-c-s3-lib"].requires = [
            "aws-c-common::aws-c-common-lib",
            "aws-c-io::aws-c-io-lib",
            "aws-c-http::aws-c-http-lib",
            "aws-c-auth::aws-c-auth-lib"
        ]
        if tools.Version(self.version) >= "0.1.36":
            self.cpp_info.components["aws-c-s3-lib"].requires.append("aws-checksums::aws-checksums-lib")
