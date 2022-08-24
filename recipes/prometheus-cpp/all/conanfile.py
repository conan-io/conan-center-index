from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class PrometheusCppConan(ConanFile):
    name = "prometheus-cpp"
    description = "Prometheus Client Library for Modern C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jupp0r/prometheus-cpp"
    license = "MIT"
    topics = ("metrics", "prometheus", "networking")

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

    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
            self.requires("civetweb/1.15")
        if self.options.with_push:
            self.requires("libcurl/7.80.0")
        if self.options.get_safe("with_compression"):
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_THIRDPARTY_LIBRARIES"] = False
        cmake.definitions["ENABLE_TESTING"] = False
        cmake.definitions["OVERRIDE_CXX_STANDARD_FLAGS"] = not tools.valid_min_cppstd(self, 11)
        cmake.definitions["ENABLE_PULL"] = self.options.with_pull
        cmake.definitions["ENABLE_PUSH"] = self.options.with_push
        if self.options.with_pull:
            cmake.definitions["ENABLE_COMPRESSION"] = self.options.with_compression

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(os.path.join(self._source_subfolder, "LICENSE"), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "prometheus-cpp")

        self.cpp_info.components["prometheus-cpp-core"].set_property("cmake_target_name", "prometheus-cpp::core")
        self.cpp_info.components["prometheus-cpp-core"].set_property("pkg_config_name", "prometheus-cpp-core")
        self.cpp_info.components["prometheus-cpp-core"].libs = ["prometheus-cpp-core"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["prometheus-cpp-core"].system_libs = ["pthread", "rt"]

        if self.options.with_push:
            self.cpp_info.components["prometheus-cpp-push"].set_property("cmake_target_name", "prometheus-cpp::push")
            self.cpp_info.components["prometheus-cpp-push"].set_property("pkg_config_name", "prometheus-cpp-push")
            self.cpp_info.components["prometheus-cpp-push"].libs = ["prometheus-cpp-push"]
            self.cpp_info.components["prometheus-cpp-push"].requires = [
                "prometheus-cpp-core",
                "libcurl::libcurl",
            ]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["prometheus-cpp-push"].system_libs = ["pthread", "rt"]

        if self.options.with_pull:
            self.cpp_info.components["prometheus-cpp-pull"].set_property("cmake_target_name", "prometheus-cpp::pull")
            self.cpp_info.components["prometheus-cpp-pull"].set_property("pkg_config_name", "prometheus-cpp-pull")
            self.cpp_info.components["prometheus-cpp-pull"].libs = ["prometheus-cpp-pull"]
            self.cpp_info.components["prometheus-cpp-pull"].requires = [
                "prometheus-cpp-core",
                "civetweb::civetweb-cpp"
            ]
            if self.options.with_compression:
                self.cpp_info.components["prometheus-cpp-pull"].requires.append("zlib::zlib")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["prometheus-cpp-pull"].system_libs = ["pthread", "rt"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["prometheus-cpp-core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["prometheus-cpp-core"].names["cmake_find_package_multi"] = "core"
        if self.options.with_push:
            self.cpp_info.components["prometheus-cpp-push"].names["cmake_find_package"] = "push"
            self.cpp_info.components["prometheus-cpp-push"].names["cmake_find_package_multi"] = "push"
        if self.options.with_pull:
            self.cpp_info.components["prometheus-cpp-pull"].names["cmake_find_package"] = "pull"
            self.cpp_info.components["prometheus-cpp-pull"].names["cmake_find_package_multi"] = "pull"
