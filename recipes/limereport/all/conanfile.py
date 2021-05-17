from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class LimereportConan(ConanFile):
    name = "limereport"
    description = "Report generator for Qt Framework"
    homepage = "https://poppler.freedesktop.org/"
    topics = ("conan", "limereport", "pdf", "report","qt")
    license = "LGPL-3.0", "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zint": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zint": True,
        "qt:qtscript": True,
        "qt:qtquickcontrols": True,
        "qt:qtquickcontrols2": True,
        "qt:qtsvg": True,
        "qt:qttools": True,
        "qt:qtwinextras": True
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


    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "8"
        }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("libpng/1.6.37")


    def requirements(self):
        self.requires("qt/5.15.2")


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("limereport-{}".format(self.version), self._source_subfolder)


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.options.shared == False:
            self._cmake.definitions["LIMEREPORT_STATIC"] = True
        if self.settings.os == "Windows":
            self._cmake.definitions["WINDOWS_BUILD"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake



    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        qt_major = tools.Version(self.deps_cpp_info["qt"].version).major
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = ["Limereport-qt{}".format(qt_major)]
        self.cpp_info.names["cmake_find_package_multi"] = ["Limereport-qt{}".format(qt_major)]

