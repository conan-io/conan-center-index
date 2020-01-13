import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration


class FollyConan(ConanFile):
    name = "folly"
    description = "An open-source C++ components library developed and used at Facebook"
    topics = ("conan", "folly", "facebook", "components", "core", "efficiency")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/folly"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    requires = (
        "boost/1.71.0",
        "double-conversion/3.1.5",
        "gflags/2.2.2",
        "glog/0.4.0",
        "libevent/2.1.11",
        "lz4/1.9.2",
        "openssl/1.1.1d",
        "zlib/1.2.11",
        "zstd/1.4.3",
        "snappy/1.1.7",
        "bzip2/1.0.8",
        "libsodium/1.0.18",
        "xz_utils/5.2.4",
        "libdwarf/20191104",
        "fmt/6.1.1",
        "libunwind/1.3.1"
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)
        if self.settings.os == "Windows" and \
            self.settings.compiler == "Visual Studio" and \
            compiler_version < "15":
            raise ConanInvalidConfiguration("Folly could not be built by Visual Studio < 14")
        elif self.settings.os == "Windows" and \
            self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture")
        elif self.settings.os == "Windows" and \
             self.settings.compiler == "Visual Studio" and \
             "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Folly could not be build with runtime MT")
        elif self.settings.os == "Linux" and \
            self.settings.compiler == "clang" and \
            compiler_version < "6.0":
            raise ConanInvalidConfiguration("Folly could not be built by Clang < 6.0")
        elif self.settings.os == "Linux" and \
            self.settings.compiler == "gcc" and \
            compiler_version < "5":
            raise ConanInvalidConfiguration("Folly could not be built by GCC < 5")
        elif self.settings.os == "Macos" and \
             self.settings.compiler == "apple-clang" and \
             compiler_version < "8.0":
            raise ConanInvalidConfiguration("Folly could not be built by apple-clang < 8.0")

    def requirements(self):
        if self.settings.os == "Linux" or \
           self.settings.compiler == "gcc":
            self.requires("libiberty/9.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + '-' + self.version + '.00'
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(os.path.join(self._source_subfolder, 'CMake', 'folly-deps.cmake'), \
            'find_package(fmt CONFIG REQUIRED)', 'find_package(fmt REQUIRED)')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'CMake', 'folly-deps.cmake'), \
            'find_package(Gflags MODULE)', 'find_package(gflags MODULE)')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self) + ["folly"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl"])
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])
        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
           Version(self.settings.compiler.version.value) == "6" and self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
           Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.system_libs.append("atomic")

