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

    generators = "make"

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f'{self.name} can not be built on {self.settings.os}.')
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) <= "10":
            raise ConanInvalidConfiguration("GCC version 10 or higher required")
        if (self.settings.compiler == "clang" or self.settings.compiler == "apple-clang") and tools.Version(self.settings.compiler.version) <= "11":
            raise ConanInvalidConfiguration("Clang version 11 or higher required")
        if self.settings.compiler == "apple-clang" and "arm" in self.settings.arch :
            raise ConanInvalidConfiguration('Use apple-clang does not work on ARM with this recipe')

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _get_include_path(self, dependency):
        include_path = self.deps_cpp_info[dependency].rootpath
        include_path = os.path.join(include_path, "include")
        return include_path

    def _patch_sources(self):
        tools.replace_in_file("source_subfolder/Makefile", "-Ithird-party/xxhash ", "-I{} -I{} -I{}".format(
        self._get_include_path("zlib"),
        self._get_include_path("openssl"),
        self._get_include_path("xxhash")))

        tools.replace_in_file("source_subfolder/Makefile", "-Ithird-party/mimalloc/include", "-I{}".format(
        self._get_include_path("mimalloc")))

        tools.replace_in_file("source_subfolder/Makefile", "-Ithird-party/tbb/include", "-I{}".format(
        self._get_include_path("onetbb")))

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("openssl/1.1.1q")
        self.requires("xxhash/0.8.1")
        self.requires("onetbb/2021.3.0")
        self.requires("mimalloc/2.0.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="mold")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("mold", src=self._source_subfolder, dst="bin", keep_path=False)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        mold_location = os.path.join(bindir, "bindir")

        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)
        self.env_info.LD = mold_location
        self.buildenv_info.prepend_path("MOLD_ROOT", bindir)
        self.cpp_info.includedirs = []

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl", "z"])
