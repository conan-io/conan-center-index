from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os

required_conan_version = ">=1.43.0"


class AwsCSDKUtils(ConanFile):
    name = "aws-c-sdkutils"
    description = "aws c language sdk utility library."
    topics = ("aws", "amazon", "cloud", "utility")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-sdkutils"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt",
    generators = "cmake", "cmake_find_package_multi"
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-sdkutils"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-sdkutils")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-sdkutils")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-sdkutils"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-sdkutils"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-sdkutils-lib"].names["cmake_find_package"] = "aws-c-sdkutils"
        self.cpp_info.components["aws-c-sdkutils-lib"].names["cmake_find_package_multi"] = "aws-c-sdkutils"
        self.cpp_info.components["aws-c-sdkutils-lib"].set_property("cmake_target_name", "AWS::aws-c-sdkutils")

        self.cpp_info.components["aws-c-sdkutils-lib"].libs = ["aws-c-sdkutils"]
        self.cpp_info.components["aws-c-sdkutils-lib"].requires = ["aws-c-common::aws-c-common-lib"]

