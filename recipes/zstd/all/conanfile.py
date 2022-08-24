from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class ZstdConan(ConanFile):
    name = "zstd"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/zstd"
    description = "Zstandard - Fast real-time compression algorithm"
    topics = ("zstd", "compression", "algorithm", "decoder")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threading": True,
    }

    generators = "cmake"
    _cmake = None

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ZSTD_BUILD_PROGRAMS"] = False
        self._cmake.definitions["ZSTD_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["ZSTD_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ZSTD_MULTITHREAD_SUPPORT"] = self.options.threading
        if tools.Version(self.version) < "1.4.3":
            # Generate a relocatable shared lib on Macos
            self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Don't force PIC
        if tools.Version(self.version) >= "1.4.5":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "build", "cmake", "lib", "CMakeLists.txt"),
                                  "POSITION_INDEPENDENT_CODE On", "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        zstd_cmake = "libzstd_shared" if self.options.shared else "libzstd_static"
        self.cpp_info.set_property("cmake_file_name", "zstd")
        self.cpp_info.set_property("cmake_target_name", "zstd::{}".format(zstd_cmake))
        self.cpp_info.set_property("pkg_config_name", "libzstd")
        self.cpp_info.components["zstdlib"].set_property("pkg_config_name", "libzstd")
        self.cpp_info.components["zstdlib"].names["cmake_find_package"] = zstd_cmake
        self.cpp_info.components["zstdlib"].names["cmake_find_package_multi"] = zstd_cmake
        self.cpp_info.components["zstdlib"].set_property("cmake_target_name", "zstd::{}".format(zstd_cmake))
        self.cpp_info.components["zstdlib"].libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["zstdlib"].system_libs.append("pthread")
