from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

requires_conan_version = ">=1.33.0"


class I2cConan(ConanFile):
    name = "i2c-tools"
    license = "GPL-2.0-or-later", "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://i2c.wiki.kernel.org/index.php/I2C_Tools"
    description = "I2C tools for the linux kernel as well as an I2C library."
    topics = ("i2c")
    os = "linux"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

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

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.flags += [f"-I{path}" for path in autotools.include_paths]
        with tools.chdir(self._source_subfolder):
            autotools.make(target="lib/libi2c.so" if self.options.shared else "lib/libi2c.a")

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING.LGPL", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include", keep_path=False)
        self.copy("*.h", src=self._source_subfolder, dst="include/i2c", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["i2c"]
