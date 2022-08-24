from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.45.0"

class MoldConan(ConanFile):
    name = "mold"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rui314/mold/"
    license = "AGPL-3.0"
    description = ("mold is a faster drop-in replacement for existing Unix linkers. It is several times faster than the LLVM lld linker")
    topics = ("mold", "ld", "linkage", "compilation")

    settings = "os", "arch", "compiler", "build_type"

    generators = "make"

    def validate(self):
        if self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration('Mold is a build tool, specify mold:build_type=Release in your build profile, see https://github.com/conan-io/conan-center-index/pull/11536#issuecomment-1195607330')
        if self.settings.compiler in ["gcc", "clang", "intel-cc"] and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration('Mold can only be built with libstdc++11; specify mold:compiler.libcxx=libstdc++11 in your build profile')
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f'{self.name} can not be built on {self.settings.os}.')
        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "11":
            raise ConanInvalidConfiguration("GCC version 11 or higher required")
        if (self.settings.compiler == "clang" or self.settings.compiler == "apple-clang") and tools.scm.Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("Clang version 12 or higher required")
        if self.settings.compiler == "apple-clang" and "armv8" == self.settings.arch :
            raise ConanInvalidConfiguration(f'{self.name} is still not supported by Mac M1.')

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
        if self.settings.compiler == "apple-clang":
            tools.files.replace_in_file(self, "source_subfolder/Makefile", "-std=c++20", "-std=c++2a")

        tools.files.replace_in_file(self, "source_subfolder/Makefile", "-Ithird-party/xxhash ", "-I{} -I{} -I{} -I{} -I{}".format(
        self._get_include_path("zlib"),
        self._get_include_path("openssl"),
        self._get_include_path("xxhash"),
        self._get_include_path("mimalloc"),
        self._get_include_path("onetbb")
        ))

        tools.files.replace_in_file(self, "source_subfolder/Makefile", "MOLD_LDFLAGS += -ltbb", "MOLD_LDFLAGS += -L{} -ltbb".format(
            self.deps_cpp_info["onetbb"].lib_paths[0]))

        tools.files.replace_in_file(self, "source_subfolder/Makefile", "MOLD_LDFLAGS += -lmimalloc", "MOLD_LDFLAGS += -L{} -lmimalloc".format(
            self.deps_cpp_info["mimalloc"].lib_paths[0]))

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("openssl/1.1.1q")
        self.requires("xxhash/0.8.1")
        self.requires("onetbb/2021.3.0")
        self.requires("mimalloc/2.0.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        with tools.files.chdir(self, self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="mold", args=['SYSTEM_TBB=1', 'SYSTEM_MIMALLOC=1'])

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("mold", src=self._source_subfolder, dst="bin", keep_path=False)

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        mold_location = os.path.join(bindir, "bindir")

        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)
        self.env_info.LD = mold_location
        self.buildenv_info.prepend_path("MOLD_ROOT", bindir)
        self.cpp_info.includedirs = []

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
