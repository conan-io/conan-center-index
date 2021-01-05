import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"

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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "6",
            "apple-clang": "8",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++14 support. The current compiler {} {} does not support it.".format(
                    self.name, self.settings.compiler, self.settings.compiler.version))

        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture")
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" and \
                "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Folly could not be build with runtime MT")
        elif self.settings.os == "Macos" and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built by apple-clang as shared library")
        elif self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built on Windows as a shared library")
        elif Version(self.version) >= "2020.08.10.00" and self.settings.compiler == "Visual Studio" and \
                not self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built on Windows as a static library")
        elif Version(self.version) >= "2020.08.10.00" and self.settings.compiler == "clang" and \
                self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built by clang as a shared library")

        self._strip_options_requirements()

    def _strip_options_requirements(self):
        self.options["boost"].header_only = False
        for boost_comp in self._required_boost_components:
            setattr(self.options["boost"], "without_{}".format(boost_comp), False)

    @property
    def _required_boost_components(self):
        return ["context", "filesystem", "program_options", "regex", "system", "thread"]

    # Freeze max. CMake version at 3.16.2 to fix the Linux build
    def build_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if Version(self.version) <= "2020.08.10.00":
                self.build_requires("cmake/3.16.2")

    def requirements(self):
        self.requires("boost/1.74.0")
        self.requires("bzip2/1.0.8")
        self.requires("double-conversion/3.1.5")
        self.requires("gflags/2.2.2")
        self.requires("glog/0.4.0")
        self.requires("libevent/2.1.12")
        self.requires("lz4/1.9.2")
        self.requires("openssl/1.1.1i")
        self.requires("snappy/1.1.8")
        self.requires("zlib/1.2.11")
        self.requires("zstd/1.4.5")
        if Version(self.version) >= "2019.01.01.00":
            self.requires("libdwarf/20191104")
            self.requires("libsodium/1.0.18")
            self.requires("xz_utils/5.2.4")
            if self.settings.os == "Linux":
                self.requires("libiberty/9.1.0")
                self.requires("libunwind/1.3.1")
        if Version(self.version) >= "2020.08.10.00":
            self.requires("fmt/7.0.3")

    def _validate_dependency_graph(self):
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("Folly requires these boost components: {}".format(", ".join(self._required_boost_components)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
            self._cmake.definitions["CXX_STD"] = self.settings.get_safe(
                "compiler.cppstd") or "c++14"
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["MSVC_ENABLE_ALL_WARNINGS"] = False
                self._cmake.definitions["MSVC_USE_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
            self._cmake.configure()
        return self._cmake

    def build(self):
        self._validate_dependency_graph()
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "folly"
        self.cpp_info.filenames["cmake_find_package_multi"] = "folly"
        self.cpp_info.names["cmake_find_package"] = "Folly"
        self.cpp_info.names["cmake_find_package_multi"] = "Folly"
        self.cpp_info.names["pkg_config"] = "libfolly"
        self.cpp_info.components["libfolly"].names["cmake_find_package"] = "folly"
        self.cpp_info.components["libfolly"].names["cmake_find_package_multi"] = "folly"
        self.cpp_info.components["libfolly"].names["pkg_config"] = "libfolly"
        self.cpp_info.components["libfolly"].libs = tools.collect_libs(self)
        self.cpp_info.components["libfolly"].requires = [
            "boost::boost",
            "bzip2::bzip2",
            "double-conversion::double-conversion",
            "gflags::gflags",
            "glog::glog",
            "libevent::libevent",
            "lz4::lz4",
            "openssl::openssl",
            "snappy::snappy",
            "zlib::zlib",
            "zstd::zstd"
        ]
        if Version(self.version) >= "2019.01.01.00":
            self.cpp_info.components["libfolly"].requires.extend([
                "libdwarf::libdwarf",
                "libsodium::libsodium",
                "xz_utils::xz_utils"
            ])
            if self.settings.os == "Linux":
                self.cpp_info.components["libfolly"].requires.extend([
                    "libiberty::libiberty",
                    "libunwind::libunwind"
                ])
        if Version(self.version) >= "2020.08.10.00":
            self.cpp_info.components["libfolly"].requires.append("fmt::fmt")
        if self.settings.os == "Linux":
            self.cpp_info.components["libfolly"].system_libs.extend(["pthread", "dl", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["libfolly"].system_libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])
        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
            self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
            Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.components["libfolly"].system_libs.append("atomic")
