from conans import CMake, ConanFile, tools
import os

class LMDBConan(ConanFile):
    name = "lmdb"
    description = "Lightning Memory-mapped Database"
    license = "OpenLDAP Public License"
    homepage = "https://symas.com/lmdb/"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        versionname = os.path.basename(self.conan_data["sources"][self.version]["url"]).split(".tar.gz")[0]
        extracted_folder = "{0}-{1}".format(self.name, versionname)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["lmdb"]
