from conans import CMake, ConanFile, tools
import os


class AwsCCommon(ConanFile):
    name = "aws-c-common"
    description = "Core c99 package for AWS SDK for C. Includes cross-platform primitives, configuration, data structures, and error handling."
    topics = ("conan", "aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt"
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

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-c-common"))

    def package_info(self):
        self.cpp_info.libs = ["aws-c-common"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread", "rt"]
        if not self.options.shared:
            if tools.is_apple_os(self.settings.os):
                self.cpp_info.frameworks = ["CoreFoundation"]
        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]
