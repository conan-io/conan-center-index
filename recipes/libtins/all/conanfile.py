from conans import tools, CMake, ConanFile
import os


class LibTinsConan(ConanFile):
    name = "libtins"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/libtins"
    description = "High-level, multiplatform C++ network packet sniffing and crafting library."
    license = "BSD-2-Clause"
    topics = ("pcap", "packets", "network", "packet-analyser", "packet-parsing", "libpcap", "sniffing")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ack_tracker": [True, False],
        "with_wpa2": [True, False],
        "with_dot11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ack_tracker": True,
        "with_wpa2": True,
        "with_dot11": True,
    }
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

    def requirements(self):
        self.requires("libpcap/1.10.0")
        if self.options.with_ack_tracker:
            self.requires("boost/1.75.0")
        if self.options.with_wpa2:
            self.requires("openssl/1.1.1j")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBTINS_BUILD_EXAMPLES"] = False
        self._cmake.definitions["LIBTINS_BUILD_TESTS"] = False

        self._cmake.definitions["LIBTINS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["LIBTINS_ENABLE_CXX11"] = tools.valid_min_cppstd(self, 11)
        self._cmake.definitions["LIBTINS_ENABLE_ACK_TRACKER"] = self.options.with_ack_tracker
        self._cmake.definitions["LIBTINS_ENABLE_WPA2"] = self.options.with_wpa2
        self._cmake.definitions["LIBTINS_ENABLE_DOT11"] = self.options.with_dot11

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(os.path.join(self._source_subfolder, "LICENSE"), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: official CMake imported target is not namespaced
        self.cpp_info.names["cmake_find_package"] = "libtins"
        self.cpp_info.names["cmake_find_package_multi"] = "libtins"
        self.cpp_info.names["pkg_config"] = "libtins"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("TINS_STATIC")
