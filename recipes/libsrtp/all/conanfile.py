from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class ConanRecipe(ConanFile):
    name = "libsrtp"
    description = (
        "This package provides an implementation of the Secure Real-time Transport"
        "Protocol (SRTP), the Universal Security Transform (UST), and a supporting"
        "cryptographic kernel."
    )
    topics = ("conan", "libsrtp", "srtp")
    homepage = "https://github.com/cisco/libsrtp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False,
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
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
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["TEST_APPS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "install(TARGETS srtp2 DESTINATION lib)",
            (
                "include(GNUInstallDirs)\n"
                "install(TARGETS srtp2\n"
                "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}\n"
                "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}\n"
                "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})"
            ),
        )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        libsrtp_major = tools.Version(self.version).major
        self.cpp_info.names["pkg_config"] = "libsrtp{}".format(libsrtp_major if int(libsrtp_major) > 1 else "")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
