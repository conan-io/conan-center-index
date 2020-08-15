import os

from conans import ConanFile, CMake, tools

class R8brainFreeSrcConan(ConanFile):
    name = "r8brain-free-src"
    version = "4.6"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/avaneev/r8brain-free-srcn"
    description = "https://github.com/avaneev/r8brain-free-src"
    topics = ("Audio", "Sample Rate", "Conversion")
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "r8brain-free-src-version-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["r8brain"]

