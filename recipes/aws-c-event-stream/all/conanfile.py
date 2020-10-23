from conans import CMake, ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class AwsCEventStream(ConanFile):
    name = "aws-c-event-stream"
    description = "C99 implementation of the vnd.amazon.eventstream content-type"
    topics = ("conan", "aws", "eventstream", "content", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-event-stream"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt", "aws_eventstream_target.cmake", "patches/*"
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
        self.requires("aws-c-common/0.4.25")
        self.requires("aws-checksums/0.1.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "aws-c-event-stream-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_BINARIES"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "AWS::aws-c-common",
                              "CONAN_PKG::aws-c-common")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "AWS::aws-checksums",
                              "CONAN_PKG::aws-checksums")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-event-stream"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-event-stream"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-event-stream"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-event-stream-lib"].names["cmake_find_package"] = "aws-c-event-stream"
        self.cpp_info.components["aws-c-event-stream-lib"].names["cmake_find_package_multi"] = "aws-c-event-stream"
        self.cpp_info.components["aws-c-event-stream-lib"].libs = ["aws-c-event-stream"]
        self.cpp_info.components["aws-c-event-stream-lib"].requires = ["aws-c-common::aws-c-common", "aws-checksums::aws-checksums"]
