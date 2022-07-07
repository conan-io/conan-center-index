from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.45.0"

class MoldConan(ConanFile):
    name = "mold"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rui314/mold/"
    license = "Zlib"
    description = ("mold is a faster drop-in replacement for existing Unix linkers. It is several times faster than the LLVM lld linker")
    topics = ("mold", "ld", "linkage", "compilation")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "make"

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration('{} can\'t be built on {}.'.format(self.name, self.settings.os))
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "8":
            raise ConanInvalidConfiguration('Use Gcc compiler version higher than 8')

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        #self._patch_sources()
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="mold")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("mold", src=self._source_subfolder, dst="bin", keep_path=False)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)
        self.env_info.LD = "mold"
        self.buildenv_info.prepend_path("MOLD_ROOT", self.package_folder)
        self.env_info.MOLD_ROOT = self.package_folder
        self.cpp_info.includedirs = []

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m"])
