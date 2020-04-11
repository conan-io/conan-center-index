from conans import ConanFile, CMake, tools


class LibdxfrwConan(ConanFile):
    name = "libdxfrw"
    version = "1.0.0"
    license = "GPL2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ library to read/write DXF and read DWG files"
    topics = ("dxf", "dwg")
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
    libdxfrw_folder = "libdxfrw-" + version

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
        print(self.source_folder)
        cmake.configure(source_folder=self.libdxfrw_folder)
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
        self.copy("COPYING", src=self.libdxfrw_folder, dst="licenses")
