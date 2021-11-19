import os
from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment

requires_conan_version = ">=1.33.0"


class I2cConan(ConanFile):
    name = "i2c-tools"
    license = "LGPL 2.1"
    url = "https://mirrors.edge.kernel.org/pub/software/utils/i2c-tools/"
    description = "I2C tools for the linux kernel as well as an I2C library."
    topics = ("i2c")
    os = "linux"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("i2c-tools only support Linux")

    @property
    def _source_subfolder(self):
        return "i2c-tools"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "i2c-tools-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        self.run("make", cwd=self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder, keep_path=False)
        self.copy("*.h", dst="include/i2c", src=self._source_subfolder, keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.so.0", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["i2c"]
