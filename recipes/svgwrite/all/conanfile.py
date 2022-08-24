import os
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration


class SvgwriteConan(ConanFile):
    name = "svgwrite"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/dvd0101/svgwrite"
    description = "SVGWrite - a streaming svg library"
    topics = ("svg", "stream", "vector", "image")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ("CMakeLists.txt", "patches/*")
    requires = "span-lite/0.7.0", "fmt/6.1.2"
    generators = "cmake", "cmake_find_package"
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
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6",
            "apple-clang": "10.0"
        }

        if compiler not in minimal_version:
            self.output.warn("{} recipe lacks information about the {} compiler"
                             " standard version support".format(self.name, compiler))
        elif compiler_version < minimal_version.get(compiler):
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++17. %s %s is not"
                                            " supported." % (self.name, compiler, compiler_version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-v" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["svgwrite"]
