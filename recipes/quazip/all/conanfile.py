from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

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

    @property
    def _qt_major_version(self):
        return tools.Version(self.deps_cpp_info["qt"].version).major

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("qt/6.2.3")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["QUAZIP_QT_MAJOR_VERSION"] = self._qt_major_version
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
        self.cpp_info.includedirs=[os.path.join('include', 'QuaZip-Qt{}-{}'.format(self._qt_major_version, self.version))]
        if not self.options.shared:
            self.cpp_info.defines.append("QUAZIP_STATIC")

        self.cpp_info.filenames["cmake_find_package"] = 'QuaZip-Qt{}'.format(self._qt_major_version, self.version)
        self.cpp_info.filenames["cmake_find_package_multi"] = 'QuaZip-Qt{}'.format(self._qt_major_version, self.version)
        self.cpp_info.names["cmake_find_package"] = "QuaZip"
        self.cpp_info.names["cmake_find_package_multi"] = "QuaZip"
