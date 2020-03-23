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
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    requires = (
        "boost/1.72.0",
        "double-conversion/3.1.5",
        "gflags/2.2.2",
        "glog/0.4.0",
        "libevent/2.1.11",
        "lz4/1.9.2",
        "openssl/1.1.1d",
        "zlib/1.2.11",
        "bzip2/1.0.8",
        "zstd/1.3.5",
        "snappy/1.1.7"
    )
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler_version = Version(self.settings.compiler.version)
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
        elif self.settings.os == "Macos" and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built by apple-clang as shared library")
        elif self.settings.os == "Windows" and \
             self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built on Windows as shared library")

    def requirements(self):
        if Version(self.version) >= "2019.01.01.00":
            self.requires("xz_utils/5.2.4")
            self.requires("libdwarf/20191104")
            self.requires("libsodium/1.0.18")
            if self.settings.os == "Linux":
                self.requires("libiberty/9.1.0")
                self.requires("libunwind/1.3.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CXX_STD"] = self.settings.get_safe("compiler.cppstd") or "c++14"
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["MSVC_ENABLE_ALL_WARNINGS"] = False
                self._cmake.definitions["MSVC_USE_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
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
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl"])
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])
        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
            self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
           Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.system_libs.append("atomic")
