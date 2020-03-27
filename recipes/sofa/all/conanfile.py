import os

from conans import ConanFile, CMake, tools

class SofaConan(ConanFile):
    name = "sofa"
    description = "IAU Standards of Fundamental Astronomy (SOFA) C Library."
    license = "SOFA Software License"
    topics = ("conan", "sofa", "iau", "astronomy")
    homepage = "http://www.iausofa.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SOFA_VERSION"] = self.version
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._get_license())
        cmake = self._configure_cmake()
        cmake.install()

    def _get_license(self):
        sofa_header = tools.load(os.path.join(self._source_subfolder, self.version, "c", "src", "sofa.h"))
        begin = sofa_header.find("/*----------------------------------------------------------------------")
        return sofa_header[begin:]

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
