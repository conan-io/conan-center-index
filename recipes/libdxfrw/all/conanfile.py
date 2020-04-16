from conans import ConanFile, CMake, tools


class LibdxfrwConan(ConanFile):
    name = "libdxfrw"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ library to read/write DXF and read DWG files"
    topics = ("dxf", "dwg", "cad")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake"
    homepage = "https://github.com/LibreCAD/libdxfrw"

    def _get_libdxfrw_folder(self):
        return "libdxfrw-" + self.version

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.replace_in_file(self._get_libdxfrw_folder() + "/CMakeLists.txt", "set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)",
                              '''set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
        print(self.source_folder)
        cmake.configure(source_folder=self._get_libdxfrw_folder())
        return cmake

    def package_info(self):
        self.cpp_info.libs = ["dxfrw"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*", src="install/bin", dst="bin")
        self.copy("*",
                  src="install/lib",
                  dst="lib",
                  excludes=('cmake', 'pkgconfig'))
        self.copy("*", src="install/include", dst="include")
        self.copy("COPYING", src=self._get_libdxfrw_folder(), dst="licenses")
