from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class AwsCAuth(ConanFile):
    name = "aws-c-auth"
    description = "C99 library implementation of AWS client-side authentication: standard credentials providers and signing."
    topics = ("aws", "amazon", "cloud", "authentication", "credentials", "providers", "signing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-auth"
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
        self.requires("aws-c-cal/0.5.13")
        self.requires("aws-c-io/0.10.20")
        self.requires("aws-c-http/0.6.13")
        if tools.Version(self.version) >= "0.6.5":
            self.requires("aws-c-sdkutils/0.1.2")

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-auth"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-auth")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-auth")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-auth"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-auth"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-auth-lib"].names["cmake_find_package"] = "aws-c-auth"
        self.cpp_info.components["aws-c-auth-lib"].names["cmake_find_package_multi"] = "aws-c-auth"
        self.cpp_info.components["aws-c-auth-lib"].set_property("cmake_target_name", "AWS::aws-c-auth")

        self.cpp_info.components["aws-c-auth-lib"].libs = ["aws-c-auth"]
        self.cpp_info.components["aws-c-auth-lib"].requires = [
            "aws-c-common::aws-c-common-lib",
            "aws-c-cal::aws-c-cal-lib",
            "aws-c-io::aws-c-io-lib",
            "aws-c-http::aws-c-http-lib"
        ]
        if tools.Version(self.version) >= "0.6.5":
            self.cpp_info.components["aws-c-auth-lib"].requires.append("aws-c-sdkutils::aws-c-sdkutils-lib")
