from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os

class LibpropertiesConan(ConanFile):
    name = "libproperties"
    license = "Apache-2.0"
    homepage = "https://github.com/tinyhubs/libproperties"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libproperties is a library to parse the Java .properties files. It was writen in pure C. And fully compatible with the Java .properties file format."
    topics = ("properties", "java", "pure-c")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], }
    default_options = {"shared": False, "fPIC": True, }
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_package_tag(self):
        return "{}-{}".format(self.name, self.version)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        source_dir = "{}-{}".format(self.name, self.version)
        os.rename(source_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBPROPERTIES_INSTALL"] = True
        self._cmake.definitions["LIBPROPERTIES_TEST"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines = ["LIBPROPERTIES_STATIC"]
        self.cpp_info.libs = ["properties"]
