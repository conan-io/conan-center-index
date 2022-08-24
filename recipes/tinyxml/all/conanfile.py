import os
from conans import ConanFile, CMake, tools

class TinyXmlConan(ConanFile):
    name = "tinyxml"
    description = "TinyXML is a simple, small, C++ XML parser that can be easily integrated into other programs."
    license = "Zlib"
    topics = ("conan", "tinyxml", "xml", "parser")
    homepage = "http://www.grinninglizard.com/tinyxml/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_stl": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_stl": False,
    }

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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("tinyxml", self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TINYXML_WITH_STL"] = self.options.with_stl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self._source_subfolder, "tinyxml.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 22):
            license_content.append(content_lines[i][:-1])
        tools.save("LICENSE", "\n".join(license_content))


    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.with_stl:
            self.cpp_info.defines = ["TIXML_USE_STL"]
        self.cpp_info.names["cmake_find_package"] = "TinyXML"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyXML"
