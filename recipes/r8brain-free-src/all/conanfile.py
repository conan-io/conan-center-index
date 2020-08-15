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

    def source(self):
        self.run("git clone https://github.com/avaneev/r8brain-free-src")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="r8brain-free-src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["r8brain"]

