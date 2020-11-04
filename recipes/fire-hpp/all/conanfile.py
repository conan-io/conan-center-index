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
    exports_sources = ["bsl_1_0"]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        tar_name = url[url.rfind("/")+1:url.find(".tar.gz")]
        extracted_dir = "{}-{}".format(self.name, tar_name)
        os.rename("bsl_1_0", "LICENSE")
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FIRE_EXAMPLES"] = False
        self._cmake.definitions["FIRE_UNIT_TESTS"] = False
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()
