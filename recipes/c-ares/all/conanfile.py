import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.29.1"


class CAresConan(ConanFile):
    name = "c-ares"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C library for asynchronous DNS requests"
    topics = ("conan", "c-ares", "dns")
    homepage = "https://c-ares.haxx.se/"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True
    }
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("c-ares-cares-{}".format(self.version.replace(".", "_")), self._source_subfolder)

    def _cmake_configure(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CARES_STATIC"] = not self.options.shared
        self._cmake.definitions["CARES_SHARED"] = self.options.shared
        self._cmake.definitions["CARES_BUILD_TESTS"] = False
        self._cmake.definitions["CARES_MSVC_STATIC_RUNTIME"] = False
        self._cmake.definitions["CARES_BUILD_TOOLS"] = self.options.tools
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._cmake_configure()
        cmake.build()

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()
        self.copy("*LICENSE.md", src=self._source_subfolder, dst="licenses", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libcares"
        self.cpp_info.components["cares"].names["cmake_find_package"] = "cares"
        self.cpp_info.components["cares"].names["cmake_find_package_multi"] = "cares"
        self.cpp_info.components["cares"].names["pkg_config"] = "libcares"
        self.cpp_info.components["cares"].libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.components["cares"].defines.append("CARES_STATICLIB")
        if self.settings.os == "Linux":
            self.cpp_info.components["cares"].system_libs.append("rt")
        elif self.settings.os == "Windows":
            self.cpp_info.components["cares"].system_libs.extend(["ws2_32", "Advapi32"])
        elif tools.is_apple_os(self.settings.os):
            self.cpp_info.components["cares"].system_libs.append("resolv")

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
