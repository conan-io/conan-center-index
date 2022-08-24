import os
from conan import ConanFile, tools
from conans import CMake


class IrrXMLConan(ConanFile):
    name = "irrxml"
    license = "ZLIB"
    homepage = "http://www.ambiera.com/irrxml"
    url = "https://github.com/conan-io/conan-center-index"
    description = "irrXML is a simple and fast open source xml parser for C++"
    topics = ("xml", "xml-parser", "parser", "xml-reader")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _extract_license(self):
        header = tools.files.load(self, os.path.join(self.package_folder, "include", "irrXML.h"))
        license_contents = header[header.find(r"\section license License")+25:header.find(r"\section history", 1)]
        tools.save("LICENSE", license_contents)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
