from conans import ConanFile, CMake, tools
import os


class LZOConan(ConanFile):
    name = "lzo"
    description = "lzo is a portable lossless data compression library written in ANSI C"
    license = "GPL-v2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.oberhumer.com/opensource/lzo/"
    topics = ("conan", "lzo", "compression")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "{0}-{1}".format(self.name, self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        cmake.definitions["ENABLE_SHARED"] = self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "bin", "lzo", "examples"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "lzo"))
        self.cpp_info.libs = tools.collect_libs(self)
