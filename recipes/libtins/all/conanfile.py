from conans import tools, CMake, ConanFile
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibTinsConan(ConanFile):
    name = "libtins"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/libtins"
    description = "High-level, multiplatform C++ network packet sniffing and crafting library."
    license = "BSD-2-Clause"
    topics = ("pcap", "packets", "network", "packet-analyser", "packet-parsing", "libpcap", "sniffing")

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

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
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
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libpcap/1.10.1")
        if self.options.with_ack_tracker:
            self.requires("boost/1.79.0")
        if self.options.with_wpa2:
            self.requires("openssl/1.1.1q")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # Use Findlibpcap.cmake from cmake_find_package
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "FIND_PACKAGE(PCAP REQUIRED)",
                              "find_package(libpcap REQUIRED)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "${PCAP_LIBRARY}",
                              "libpcap::libpcap")

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
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(os.path.join(self._source_subfolder, "LICENSE"), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"libtins": "libtins::libtins"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libtins")
        self.cpp_info.set_property("cmake_target_name", "libtins")
        self.cpp_info.set_property("pkg_config_name", "libtins")
        self.cpp_info.libs = ["tins"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("TINS_STATIC")
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
