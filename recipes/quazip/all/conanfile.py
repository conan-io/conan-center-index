from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.47.0"


class QuaZIPConan(ConanFile):
    name = "quazip"
    description = (
        "A simple C++ wrapper over Gilles Vollant's ZIP/UNZIP package "
        "that can be used to access ZIP archives."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stachenov/quazip"
    license = "LGPL-2.1-linking-exception"
    topics = ("zip", "unzip", "compress")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _qt_major(self):
        return tools.Version(self.deps_cpp_info["qt"].version).major

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

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("qt/5.15.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["QUAZIP_QT_MAJOR_VERSION"] = self._qt_major
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        quazip_major = tools.Version(self.version).major
        self.cpp_info.set_property("cmake_file_name", f"QuaZip-Qt{self._qt_major}")
        self.cpp_info.set_property("cmake_target_name", "QuaZip::QuaZip")
        self.cpp_info.set_property("pkg_config_name", f"quazip{quazip_major}-qt{self._qt_major}")
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"quazip{quazip_major}-qt{self._qt_major}{suffix}"]
        self.cpp_info.includedirs = [os.path.join("include", f"QuaZip-Qt{self._qt_major}-{self.version}")]
        if not self.options.shared:
            self.cpp_info.defines.append("QUAZIP_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = f"QuaZip-Qt{self._qt_major}"
        self.cpp_info.filenames["cmake_find_package_multi"] = f"QuaZip-Qt{self._qt_major}"
        self.cpp_info.names["cmake_find_package"] = "QuaZip"
        self.cpp_info.names["cmake_find_package_multi"] = "QuaZip"
        self.cpp_info.names["pkg_config"] = f"quazip{quazip_major}-qt{self._qt_major}"
