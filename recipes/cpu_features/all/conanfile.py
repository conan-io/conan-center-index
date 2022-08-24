from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class CpuFeaturesConan(ConanFile):
    name = "cpu_features"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cpu_features"
    description = "A cross platform C99 library to get cpu features at runtime."
    topics = ("cpu", "features", "cpuid")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake",
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.scm.Version(self, self.version) < "0.7.0":
            self._cmake.definitions["BUILD_PIC"] = self.options.get_safe("fPIC", True)
        if tools.scm.Version(self, self.version) >= "0.7.0":
            self._cmake.definitions["BUILD_TESTING"] = False
        # TODO: should be handled by CMake helper
        if tools.is_apple_os(self, self.settings.os) and self.settings.arch in ["armv8", "armv8_32", "armv8.3"]:
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        self._cmake.configure() # Does not support out of source builds
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CpuFeatures")
        self.cpp_info.set_property("cmake_target_name", "CpuFeatures::cpu_features")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libcpu_features"].libs = ["cpu_features"]
        self.cpp_info.components["libcpu_features"].includedirs = [os.path.join("include", "cpu_features")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libcpu_features"].system_libs = ["dl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CpuFeatures"
        self.cpp_info.names["cmake_find_package_multi"] = "CpuFeatures"
        self.cpp_info.components["libcpu_features"].names["cmake_find_package"] = "cpu_features"
        self.cpp_info.components["libcpu_features"].names["cmake_find_package_multi"] = "cpu_features"
        self.cpp_info.components["libcpu_features"].set_property("cmake_target_name", "CpuFeatures::cpu_features")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
