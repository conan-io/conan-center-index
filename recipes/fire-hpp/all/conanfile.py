from conans import ConanFile, CMake, tools
import os

class FireHppConan(ConanFile):
    name = "fire-hpp"
    homepage = "https://github.com/kongaskristjan/fire-hpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Fire for C++: Create fully functional CLIs using function signatures"
    topics = ("command-line", "argument", "parser")
    license = "BSL-1.0"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FIRE_EXAMPLES"] = False
        self._cmake.definitions["FIRE_UNIT_TESTS"] = False
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENCE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()
