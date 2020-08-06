from conans import ConanFile, tools, CMake
import os

class Graphviz(ConanFile):
    name = "graphviz"
    description = "Conan installer for Graphviz"
    topics = ("conan", "graphviz", "dot", "doxygen", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://graphviz.org/"
    license = "Eclipse Public License - v 1.0"
    generators = "virtualrunenv", "cmake_find_package"
    settings = "os", "arch", "compiler"

    _cmake = None
    _source_subfolder = "source_subfolder"
    short_paths = True

    def build_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            self.build_requires("bison/3.5.3")
            self.build_requires("flex/2.6.4")
            self.build_requires("fontconfig/2.13.91")

        if tools.os_info.is_windows and self.settings.os == "Windows":
            if not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/20200517")
            self.build_requires("strawberryperl/5.30.0.1")
            self.build_requires("winflexbison/2.5.22")

        self.build_requires("freetype/2.10.2")
        self.build_requires("expat/2.2.9")
        self.build_requires("libpng/1.6.37")
        self.build_requires("libtool/2.4.6")
        self.build_requires("pixman/0.40.0")
        self.build_requires("zlib/1.2.11")

    def export_sources(self):
        if tools.os_info.is_windows and self.settings.os == "Windows":
            self.copy("rxspencer.tar.gz")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "%s-%s" % (self.name, self.version)
        os.rename(folder_name, self._source_subfolder)
        if tools.os_info.is_windows and self.settings.os == "Windows":
            tools.untargz("rxspencer.tar.gz", destination=os.path.join(self._source_subfolder, "windows", "dependencies", "libraries")) #TODO create rxspencer conan pkg

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(source_folder=self._source_subfolder)
            if tools.os_info.is_windows and self.settings.os == "Windows":
                self._cmake.definitions["CMAKE_LIBRARY_PATH"]=os.path.join(self.build_folder, self._source_subfolder,
                    "windows", "dependencies", "libraries", "x64", "lib")
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.mkdir("licences")
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # We need to configure dot before use
        if tools.os_info.is_linux and self.settings.os == "Linux":
            os.environ['LD_LIBRARY_PATH'] = os.path.join(self.package_folder, "lib")
        self.run(os.path.join(self.package_folder, "bin", "dot -c"))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if tools.os_info.is_linux and self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH = os.path.join(self.package_folder, "lib")
