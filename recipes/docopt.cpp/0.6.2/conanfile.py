from conans import ConanFile, CMake, tools
import os


class DocoptCppConan(ConanFile):
    name = "docopt.cpp"
    version = "0.6.2"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/docopt/docopt.cpp"
    settings = "os", "compiler", "build_type", "arch"
    description = "C++11 port of docopt"
    options = {"shared": [True, False], "fPIC": [True, False], "boost_regex": [True, False]}
    default_options = {"shared": False, "fPIC": True, "boost_regex": False}
    topics = ("CLI", "getopt", "options", "argparser")
    generators = 'cmake'
    exports_sources = ['patches/**', 'CMakeLists.txt']
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.boost_regex:
            self.requires("boost/1.71.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_BOOST_REGEX"] = self.options.boost_regex
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["docopt"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.defines = ["DOCOPT_DLL"]
