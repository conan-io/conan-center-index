from conans import ConanFile, CMake, tools
import os


class DocoptCppConan(ConanFile):
    name = "docopt.cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/docopt/docopt.cpp"
    settings = "os", "compiler", "build_type", "arch"
    description = "C++11 port of docopt"
    options = {"shared": [True, False], "fPIC": [True, False], "boost_regex": [True, False]}
    default_options = {"shared": False, "fPIC": True, "boost_regex": False}
    topics = ("CLI", "getopt", "options", "argparser")
    generators = "cmake", "cmake_find_package"
    exports_sources = ["patches/**", "CMakeLists.txt"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        if self.options.boost_regex:
            self.requires("boost/1.74.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_BOOST_REGEX"] = self.options.boost_regex
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # TODO: imported CMake target shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "docopt"
        self.cpp_info.names["cmake_find_package_multi"] = "docopt"
        self.cpp_info.names["pkg_config"] = "docopt"
        cmake_target = "docopt" if self.options.shared else "docopt_s"
        self.cpp_info.components["docopt"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["docopt"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["docopt"].libs = ["docopt"]
        if self.settings.os == "Linux":
            self.cpp_info.components["docopt"].system_libs = ["m"]
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.components["docopt"].defines = ["DOCOPT_DLL"]
        if self.options.boost_regex:
            self.cpp_info.components["docopt"].requires.append("boost::boost")
