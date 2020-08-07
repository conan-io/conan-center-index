import os
from conans import ConanFile, tools, CMake


class ZziplibConan(ConanFile):
    name = "zziplib"
    description = "The ZZIPlib provides read access on ZIP-archives and unpacked data. It features an additional simplified API following the standard Posix API for file access."
    topics = ("conan", "zip", "archive", "decompression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gdraheim/zziplib"
    license = "GPL-2.0-or-later"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")

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
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared

        cmake.definitions["ZZIPCOMPAT"] = not tools.os_info.is_windows

        cmake.definitions["ZZIPSDL"] = False
        cmake.definitions["ZZIPBINS"] = False
        cmake.definitions["ZZIPTEST"] = False
        cmake.definitions["ZZIPDOCS"] = False

        cmake.configure()

        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="COPYING.LIB", dst="licenses", src=self._source_subfolder)
        os.rename(os.path.join(self.package_folder, "licenses", "COPYING.LIB"), os.path.join(self.package_folder, "licenses", "License.txt"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
