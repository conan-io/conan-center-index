from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

requires_conan_version = ">=1.33.0"


class I2cConan(ConanFile):
    name = "i2c-tools"
    license = "GPL-2.0-or-later", "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://i2c.wiki.kernel.org/index.php/I2C_Tools"
    description = "I2C tools for the linux kernel as well as an I2C library."
    topics = ("i2c")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("linux-headers-generic/5.14.9")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("i2c-tools only support Linux")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"),
                              "SRCDIRS	:= include lib eeprom stub tools $(EXTRA)",
                              "SRCDIRS	:= include lib $(EXTRA)")

    @property
    def _make_args(self):
        return [
            "PREFIX={}".format(self.package_folder),
            "BUILD_DYNAMIC_LIB={}".format("1" if self.options.shared else "0"),
            "BUILD_STATIC_LIB={}".format("0" if self.options.shared else "1"),
            "USE_STATIC_LIB={}".format("0" if self.options.shared else "1"),
        ]

    def build(self):
        self._patch_sources()
        autotools = AutoToolsBuildEnvironment(self)
        autotools.flags += [f"-I{path}" for path in autotools.include_paths]
        with tools.chdir(self._source_subfolder):
            autotools.make(args=self._make_args)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING.LGPL", src=self._source_subfolder, dst="licenses")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.flags += [f"-I{path}" for path in autotools.include_paths]
        with tools.chdir(self._source_subfolder):
            autotools.install(args=self._make_args)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["i2c"]
