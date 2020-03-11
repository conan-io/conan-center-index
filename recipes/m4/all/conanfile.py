from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import glob
import os


class M4Conan(ConanFile):
    name = "m4"
    description = "GNU M4 is an implementation of the traditional Unix macro processor"
    topics = ("conan", "m4", "macro", "macro processor")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/m4/"
    license = "GPL-3.0-only"
    exports_sources = ["patches/*.patch"]
    settings = "os_build", "arch_build", "compiler"

    _autotools = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_clang(self):
        return str(self.settings.compiler).endswith("clang")

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("m4-" + self.version, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        args = []
        if self._is_msvc:
            args.extend(['CC={}/build-aux/compile cl -nologo'.format(tools.unix_path(self._source_subfolder)),
                         'CXX={}/build-aux/compile cl -nologo'.format(tools.unix_path(self._source_subfolder)),
                         'LD=link',
                         'NM=dumpbin -symbols',
                         'STRIP=:',
                         'AR={}/build-aux/ar-lib lib'.format(tools.unix_path(self._source_subfolder)),
                         'RANLIB=:'])
        elif self._is_clang:
            args.extend(['CFLAGS=-rtlib=compiler-rt'])

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    @contextmanager
    def _build_context(self):
        if self._is_msvc:
            with tools.vcvars(self.settings):
                yield
        else:
            yield

    def build(self):
        # 0001-fflush-adjust-to-glibc-2.28-libio.h-removal.patch
        # 0002-fflush-be-more-paranoid-about-libio.h-change.patch
        # these two patches are from https://git.busybox.net/buildroot/commit/?id=c48f8a64626c60bd1b46804b7cf1a699ff53cdf3
        # to fix compiler error on certain systems:
        # freadahead.c:92:3: error: #error "Please port gnulib freadahead.c to your platform! Look at the definition of fflush, fread, ungetc on your system, then report this to bug-gnulib."
        # 0003-secure_snprintf.patch
        # patch taken from https://github.com/macports/macports-ports/blob/master/devel/m4/files/secure_snprintf.patch
        # to fix invalid instruction error on OSX when running m4
        for patchargs in self.conan_data["patches"][self.version]:
            self.output.info('applying patch "{}"'.format(patchargs["patch_file"]))
            tools.patch(**patchargs)

        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            if bool(os.environ.get("CONAN_RUN_TESTS", "")):
                self.output.info("Running m4 checks...")
                with tools.chdir("checks"):
                    autotools.make(target="check-local")

    def package(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler
        self.info.include_build_settings()

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        m4 = "m4.exe" if self.settings.os_build == "Windows" else "m4"
        self.env_info.M4 = os.path.join(self.package_folder, "bin", m4).replace("\\", "/")
