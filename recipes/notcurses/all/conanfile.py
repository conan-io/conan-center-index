from conans import ConanFile, CMake, tools


class NotcursesConan(ConanFile):
    name = "notcurses"
    version = "2.1.2"
    description = "a blingful TUI/character graphics library"
    topics = ("graphics", "curses", "tui", "console", "ncurses")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nick-black.com/dankwiki/index.php/Notcurses"
    license = "Apache-2.0"
    author = "nick black dank@qemfd.net"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_doctest": [True, False]}
    default_options = {"shared": True,
                       "with_doctest": True}
    generators = "cmake"

    def source(self):
        self.run("git clone https://github.com/dankamongmen/notcurses.git")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="notcurses")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/notcurses %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="notcurses")
        self.copy("*notcurses.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["notcurses"]

