from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class PrometheusCppConan(ConanFile):
    name = "prometheus-cpp"
    description = "Prometheus Client Library for Modern C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jupp0r/prometheus-cpp"
    license = "MIT"
    topics = ("conan", "metrics", "prometheus", "networking")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_pull": [True, False],
        "with_push": [True, False],
        "with_compression": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_pull": True,
        "with_push": True,
        "with_compression": True,
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_pull:
            del self.options.with_compression

    def requirements(self):
        if self.options.with_pull:
            self.requires("civetweb/1.14")
        if self.options.with_push:
            self.requires("libcurl/7.77.0")
        if self.options.get_safe("with_compression"):
            self.requires("zlib/1.2.11")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_THIRDPARTY_LIBRARIES"] = False
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["OVERRIDE_CXX_STANDARD_FLAGS"] = not tools.valid_min_cppstd(self, 11)

        self._cmake.definitions["ENABLE_PULL"] = self.options.with_pull
        self._cmake.definitions["ENABLE_PUSH"] = self.options.with_push
        if self.options.with_pull:
            self._cmake.definitions["ENABLE_COMPRESSION"] = self.options.with_compression

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
        self.cpp_info.names["cmake_find_package"] = "prometheus-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "prometheus-cpp"

        self.cpp_info.components["prometheus-cpp-core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["prometheus-cpp-core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["prometheus-cpp-core"].names["pkg_config"] = "prometheus-cpp-core"
        self.cpp_info.components["prometheus-cpp-core"].libs = ["prometheus-cpp-core"]
        if self.settings.os == "Linux":
            self.cpp_info.components["prometheus-cpp-core"].system_libs = ["pthread", "rt"]

        if self.options.with_push:
            self.cpp_info.components["prometheus-cpp-push"].names["cmake_find_package"] = "push"
            self.cpp_info.components["prometheus-cpp-push"].names["cmake_find_package_multi"] = "push"
            self.cpp_info.components["prometheus-cpp-push"].names["pkg_config"] = "prometheus-cpp-push"
            self.cpp_info.components["prometheus-cpp-push"].libs = ["prometheus-cpp-push"]
            self.cpp_info.components["prometheus-cpp-push"].requires = [
                "prometheus-cpp-core",
                "libcurl::libcurl",
            ]
            if self.settings.os == "Linux":
                self.cpp_info.components["prometheus-cpp-push"].system_libs = ["pthread", "rt"]

        if self.options.with_pull:
            self.cpp_info.components["prometheus-cpp-pull"].names["cmake_find_package"] = "pull"
            self.cpp_info.components["prometheus-cpp-pull"].names["cmake_find_package_multi"] = "pull"
            self.cpp_info.components["prometheus-cpp-pull"].names["pkg_config"] = "prometheus-cpp-pull"
            self.cpp_info.components["prometheus-cpp-pull"].libs = ["prometheus-cpp-pull"]
            self.cpp_info.components["prometheus-cpp-pull"].requires = [
                "prometheus-cpp-core",
                "civetweb::civetweb-cpp"
            ]
            if self.options.with_compression:
                self.cpp_info.components["prometheus-cpp-pull"].requires.append("zlib::zlib")
            if self.settings.os == "Linux":
                self.cpp_info.components["prometheus-cpp-pull"].system_libs = ["pthread", "rt"]

