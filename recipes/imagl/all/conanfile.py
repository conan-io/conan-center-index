from conans import ConanFile, CMake, tools, errors

class ImaglConan(ConanFile):
    name = "imagl"
    license = "GPL-3"
    homepage = "https://github.com/Woazim/imaGL"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A lightweight library to load image for OpenGL application. Directly compatible with glTexImage* functions. Tested on linux, macOS and Windows with gcc, clang and msvc."
    topics = ("opengl", "texture", "image")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    requires = [("libpng/1.6.37")]

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file(self.name + "-v" + self.version + "/CMakeLists.txt", "# conan insert",
                              '''include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure(source_folder=self.name + "-v" + self.version, defs={"STATIC_LIB": "OFF" if self.options.shared else "ON"})
        cmake.build()
        cmake.install()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src=self.package_folder + "include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy(self.name + "-v" + self.version + "/LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        debug_suffix = ""
        static_suffix = ""
        if self.settings.build_type == "Debug": debug_suffix = "d"
        if not(self.options.shared): static_suffix = "s"
        self.cpp_info.libs = ["imaGL{debug}{static}".format(debug = debug_suffix, static = static_suffix)]

    def configure(self):
        if (self.settings.compiler == "clang"
                and tools.Version(self.settings.compiler.version) < "10.0.0"):
            raise errors.ConanInvalidConfiguration("Library imaGL need clang 10+")
        if (self.settings.compiler == "gcc"
                and tools.Version(self.settings.compiler.version) < "9.0.0"):
            raise errors.ConanInvalidConfiguration("Library imaGL need gcc 9+")
        if (self.settings.compiler == "apple-clang"
                and tools.Version(self.settings.compiler.version) < "11.0.3"):
            raise errors.ConanInvalidConfiguration("Library imaGL need apple-clang 11.0.3+")
        if (self.settings.compiler == "Visual Studio"
                and tools.Version(self.settings.compiler.version) < "16.5"):
            raise errors.ConanInvalidConfiguration("Library imaGL need Visual Studio 16.5+")

