import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    description = "Flex and Bison for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lexxmark/winflexbison"
    topics = ("conan", "winflexbison", "flex", "bison")

    generators = "cmake"
    license = "GPLv3"
    exports_sources = ["CMakeLists.txt"]

    settings = "os_build", "build_type", "arch", "compiler"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("winflexbison is only supported on Windows.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="data/*", dst="bin", src="{}/bison".format(self._source_subfolder), keep_path=True)
        self.copy(pattern="FlexLexer.h", dst="include", src=os.path.join(self._source_subfolder, "flex", "src"), keep_path=False)
        self.copy(pattern="COPYING", dst="licenses", src=os.path.join(self._source_subfolder, "bison", "src"), keep_path=False)
        actual_build_path = "{}/bin/{}".format(self._source_subfolder, self.settings.build_type)
        self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)