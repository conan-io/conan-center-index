import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.45.0"


class GperftoolsConan(ConanFile):
    name = "gperftools"

    description = "Google Performance Tools"
    topics = ("conan", "gperftools", "tcmalloc", "cpu/heap profiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gperftools/gperftools"
    license = ["BSD-3-Clause License"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "gperftools is not supported by Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            # libtool:   error: can't build i686-pc-mingw32 shared library unless -no-undefined is specified
            raise ConanInvalidConfiguration(
                "gperftools can't be built as shared on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        if self.settings.os == "Windows" and not os.environ.get("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=self.settings.os == "Windows")
        args = []
        if self.options.shared:
            args.extend(['--disable-static', '--enable-shared'])
        else:
            args.extend(['--disable-shared', '--enable-static'])
        self._autotools.configure(
            configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        os.unlink(os.path.join(self.package_folder, "lib", "libprofiler.la"))
        os.unlink(os.path.join(self.package_folder, "lib", "libtcmalloc.la"))
        os.unlink(os.path.join(self.package_folder,
                  "lib", "libtcmalloc_and_profiler.la"))
        os.unlink(os.path.join(self.package_folder,
                  "lib", "libtcmalloc_debug.la"))
        os.unlink(os.path.join(self.package_folder,
                  "lib", "libtcmalloc_minimal.la"))
        os.unlink(os.path.join(self.package_folder,
                  "lib", "libtcmalloc_minimal_debug.la"))

    def package_info(self):
        self.cpp_info.libs = ["tcmalloc_and_profiler"]
