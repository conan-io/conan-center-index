from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class S2n(ConanFile):
    name = "s2n"
    description = "An implementation of the TLS/SSL protocols"
    topics = ("conan", "aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/s2n-tls"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("openssl/1.1.1l")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Not supported (yet)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["UNSAFE_TREAT_WARNINGS_AS_ERRORS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "s2n"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "s2n"
        self.cpp_info.filenames["cmake_find_package_multi"] = "s2n"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["s2n-lib"].names["cmake_find_package"] = "s2n"
        self.cpp_info.components["s2n-lib"].names["cmake_find_package_multi"] = "s2n"
        self.cpp_info.components["s2n-lib"].libs = ["s2n"]
        self.cpp_info.components["s2n-lib"].requires = ["openssl::crypto"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["s2n-lib"].system_libs = ["m", "pthread"]
