import os
from from conan import ConanFile, tools
from conans import CMake


class LibqrencodeConan(ConanFile):
    name = "libqrencode"
    description = "A fast and compact QR Code encoding library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fukuchi/libqrencode"
    license = "LGPL-2.1-or-later"
    topics = ("conan", "graphics")
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    requires = (
        "libiconv/1.15",
        "libpng/1.6.37",
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("libqrencode-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["WITH_TOOLS"] = False
        cmake.definitions["WITH_TESTS"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        lib = "qrencode"
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            lib += "d"
        self.cpp_info.libs = [lib]
