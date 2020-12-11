from conans import ConanFile, CMake, tools

import os


class SemverCConan(ConanFile):
    name = "semver.c"
    version = "1.0.0"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/h2non/semver.c"
    description = "Semantic versioning for c"
    topics = ("versioning")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        cmake = CMake(self)

        if self.options.shared:
            cmake.definitions['CONAN_STATIC'] = False
        else:
            cmake.definitions['CONAN_STATIC'] = True

        cmake.configure(source_folder=".")
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("*semver.c.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["semver.c"]
