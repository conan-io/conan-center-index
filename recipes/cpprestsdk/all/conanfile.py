from conan import ConanFile
from conan.tools import files
from conans import CMake
import os

required_conan_version = ">=1.52.0"


class CppRestSDKConan(ConanFile):
    name = "cpprestsdk"
    description = "A project for cloud-based client-server communication in native code using a modern asynchronous " \
                  "C++ API design"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Microsoft/cpprestsdk"
    topics = ("cpprestsdk", "rest", "client", "http", "https")
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_websockets": [True, False],
        "with_compression": [True, False],
        "pplx_impl": ["win", "winpplx"],
        "http_client_impl": ["winhttp", "asio"],
        "http_listener_impl": ["httpsys", "asio"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_websockets": True,
        "with_compression": True,
        "pplx_impl": "win",
        "http_client_impl": "winhttp",
        "http_listener_impl": "httpsys",
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        files.copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        files.export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.pplx_impl
            del self.options.http_client_impl
            del self.options.http_listener_impl

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.80.0")
        self.requires("openssl/1.1.1s")
        if self.options.with_compression:
            self.requires("zlib/1.2.13")
        if self.options.with_websockets:
            self.requires("websocketpp/0.8.2")

    def package_id(self):
        self.info.requires["boost"].minor_mode()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self, set_cmake_flags=True)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_SAMPLES"] = False
        self._cmake.definitions["WERROR"] = False
        self._cmake.definitions["CPPREST_EXCLUDE_WEBSOCKETS"] = not self.options.with_websockets
        self._cmake.definitions["CPPREST_EXCLUDE_COMPRESSION"] = not self.options.with_compression
        if self.options.get_safe("pplx_impl"):
            self._cmake.definitions["CPPREST_PPLX_IMPL"] = self.options.pplx_impl
        if self.options.get_safe("http_client_impl"):
            self._cmake.definitions["CPPREST_HTTP_CLIENT_IMPL"] = self.options.http_client_impl
        if self.options.get_safe("http_listener_impl"):
            self._cmake.definitions["CPPREST_HTTP_LISTENER_IMPL"] = self.options.http_listener_impl

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_clang_libcxx(self):
        if self.settings.compiler == 'clang' and str(self.settings.compiler.libcxx) in ['libstdc++', 'libstdc++11']:
            files.replace_in_file(self, os.path.join(self._source_subfolder, 'Release', 'CMakeLists.txt'),
                                  'libc++', 'libstdc++')

    def build(self):
        files.apply_conandata_patches(self)
        self._patch_clang_libcxx()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        files.copy(self, "license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cpprestsdk"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cpprestsdk")

        # cpprestsdk_boost_internal
        self.cpp_info.components["cpprestsdk_boost_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_boost_internal")
        self.cpp_info.components["cpprestsdk_boost_internal"].includedirs = []
        self.cpp_info.components["cpprestsdk_boost_internal"].requires = ["boost::boost"]
        # cpprestsdk_openssl_internal
        self.cpp_info.components["cpprestsdk_openssl_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_openssl_internal")
        self.cpp_info.components["cpprestsdk_openssl_internal"].includedirs = []
        self.cpp_info.components["cpprestsdk_openssl_internal"].requires = ["openssl::openssl"]
        # cpprest
        self.cpp_info.components["cpprest"].set_property("cmake_target_name", "cpprestsdk::cpprest")
        self.cpp_info.components["cpprest"].libs = files.collect_libs(self)
        self.cpp_info.components["cpprest"].requires = ["cpprestsdk_boost_internal", "cpprestsdk_openssl_internal"]
        if self.settings.os == "Linux":
            self.cpp_info.components["cpprest"].system_libs.append("pthread")
        elif self.settings.os == "Windows":
            if self.options.get_safe("http_client_impl") == "winhttp":
                self.cpp_info.components["cpprest"].system_libs.append("winhttp")
            if self.options.get_safe("http_listener_impl") == "httpsys":
                self.cpp_info.components["cpprest"].system_libs.append("httpapi")
            self.cpp_info.components["cpprest"].system_libs.append("bcrypt")
            if self.options.get_safe("pplx_impl") == "winpplx":
                self.cpp_info.components["cpprest"].defines.append("CPPREST_FORCE_PPLX=1")
            if self.options.get_safe("http_client_impl") == "asio":
                self.cpp_info.components["cpprest"].defines.append("CPPREST_FORCE_HTTP_CLIENT_ASIO")
            if self.options.get_safe("http_listener_impl") == "asio":
                self.cpp_info.components["cpprest"].defines.append("CPPREST_FORCE_HTTP_LISTENER_ASIO")
        elif self.settings.os == "Macos":
            self.cpp_info.components["cpprest"].frameworks.extend(["CoreFoundation", "Security"])
        if not self.options.shared:
            self.cpp_info.components["cpprest"].defines.extend(["_NO_ASYNCRTIMP", "_NO_PPLXIMP"])
        # cpprestsdk_zlib_internal
        if self.options.with_compression:
            self.cpp_info.components["cpprestsdk_zlib_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_zlib_internal")
            self.cpp_info.components["cpprestsdk_zlib_internal"].includedirs = []
            self.cpp_info.components["cpprestsdk_zlib_internal"].requires = ["zlib::zlib"]
            self.cpp_info.components["cpprest"].requires.append("cpprestsdk_zlib_internal")
        # cpprestsdk_websocketpp_internal
        if self.options.with_websockets:
            self.cpp_info.components["cpprestsdk_websocketpp_internal"].set_property("cmake_target_name", "cpprestsdk::cpprestsdk_websocketpp_internal")
            self.cpp_info.components["cpprestsdk_websocketpp_internal"].includedirs = []
            self.cpp_info.components["cpprestsdk_websocketpp_internal"].requires = ["websocketpp::websocketpp"]
            self.cpp_info.components["cpprest"].requires.append("cpprestsdk_websocketpp_internal")
