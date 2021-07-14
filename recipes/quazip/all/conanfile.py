from conans import ConanFile, CMake, tools
import os

class QuaZIPConan(ConanFile):
    name = "quazip"
    description = "A simple C++ wrapper over Gilles Vollant's ZIP/UNZIP package\
                    that can be used to access ZIP archives."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stachenov/quazip"
    license = "LGPL-2.1-linking-exception"
    topics = ("conan", "zip", "unzip", "compress")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("qt/5.15.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs=[os.path.join('include', 'QuaZip-Qt5-{}'.format(self.version))]
        if not self.options.shared:
            self.cpp_info.defines.append("QUAZIP_STATIC")

        self.cpp_info.filenames["cmake_find_package"] = "QuaZip-Qt5"
        self.cpp_info.filenames["cmake_find_package_multi"] = "QuaZip-Qt5"
        self.cpp_info.names["cmake_find_package"] = "QuaZip"
        self.cpp_info.names["cmake_find_package_multi"] = "QuaZip"
