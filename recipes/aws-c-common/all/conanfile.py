from conans import CMake, ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class AwsCCommon(ConanFile):
    name = "aws-c-common"
    description = "Core c99 package for AWS SDK for C. Includes cross-platform primitives, configuration, data structures, and error handling."
    topics = ("conan", "aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-sdk-cpp"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "aws-c-common-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-common"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-common"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-common"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-common-lib"].names["cmake_find_package"] = "aws-c-common"
        self.cpp_info.components["aws-c-common-lib"].names["cmake_find_package_multi"] = "aws-c-common"
        self.cpp_info.components["aws-c-common-lib"].libs = ["aws-c-common"]
        if self.settings.os == "Linux":
            self.cpp_info.components["aws-c-common-lib"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["aws-c-common-lib"].system_libs = ["bcrypt", "ws2_32"]
        if not self.options.shared:
            if tools.is_apple_os(self.settings.os):
                self.cpp_info.components["aws-c-common-lib"].frameworks = ["CoreFoundation"]
        self.cpp_info.components["aws-c-common-lib"].builddirs = [os.path.join("lib", "cmake")]
