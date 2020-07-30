from conans import CMake, ConanFile, tools
import os
import string


class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    description = "The AWS SDK for C++ provides a modern C++ (version C++ 11 or later) interface for Amazon Web Services (AWS)."
    topics = ("conan", "aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt",
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type",
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rtti": [True, False],
        "use_virtual_operations": [True, False],
        "with_curl": [True, False],
        "enable_curl_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rtti": True,
        "use_virtual_operations": True,
        "with_curl": True,
        "enable_curl_logging": False,
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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 2003)
        if not self.options.with_curl:
            del self.options.enable_curl_logging

    def requirements(self):
        self.requires("aws-c-common/0.4.25")
        self.requires("aws-c-event-stream/0.1.5")
        self.requires("openssl/1.1.1g")
        self.requires("zlib/1.2.11")
        if self.options.with_curl:
            self.requires("libcurl/7.68.0")

    @property
    def _cmake_cpp_standard(self):
        return ''.join(c for c in str(self.settings.compiler.cppstd) if c in string.digits)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "aws-sdk-cpp-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_DEPS"] = False
        self._cmake.definitions["ENABLE_UNITY_BUILD"] = True
        self._cmake.definitions["ENABLE_RTTI"] = self.options.with_rtti
        self._cmake.definitions["FORCE_CURL"] = self.options.with_curl
        self._cmake.definitions["ENABLE_CURL_LOGGING"] = self.options.get_safe("enable_curl_logging")
        if self.settings.compiler.cppstd:
            self._cmake.definitions["CPP_STANDARD"] = self._cmake_cpp_standard

        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["SIMPLE_INSTALL"] = True
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["FORCE_SHARED_CRT"] = "MD" in str(self.settings.compiler.runtime)

        self._cmake.definitions["AUTORUN_UNIT_TESTS"] = False

        self._cmake.definitions["ANDROID_BUILD_CURL"] = False
        self._cmake.definitions["ANDROID_BUILD_OPENSSL"] = False
        self._cmake.definitions["ANDROID_BUILD_ZLIB"] = False

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "sdks.cmake"),
                              "sort_links(EXPORTS)", "# sort_links(EXPORTS)")
        for root, _, _ in os.walk(self._source_subfolder):
            cmakelists = os.path.join(root, "CMakeLists.txt")
            repl = "AWS::aws-c-event-stream"
            if os.path.isfile(cmakelists) and repl in tools.load(cmakelists):
                tools.replace_in_file(cmakelists, repl, "CONAN_PKG::aws-c-event-stream", strict=False)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "AWSSDK"
        self.cpp_info.names["cmake_find_package_multi"] = "AWSSDK"
