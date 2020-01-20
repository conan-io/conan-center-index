from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import glob


class M4Conan(ConanFile):
    name = "m4"
    description = "GNU M4 is an implementation of the traditional Unix macro processor"
    topics = ("conan", "m4", "macro", "macro processor")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/m4/"
    license = "GPL-3.0-only"
    exports_sources = ["patches/*.patch"]
    settings = "os_build", "arch_build", "compiler"
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

    def build(self):
        # 0001-fflush-adjust-to-glibc-2.28-libio.h-removal.patch
        # 0002-fflush-be-more-paranoid-about-libio.h-change.patch
        # these two patches are from https://git.busybox.net/buildroot/commit/?id=c48f8a64626c60bd1b46804b7cf1a699ff53cdf3
        # to fix compiler error on certain systems:
        # freadahead.c:92:3: error: #error "Please port gnulib freadahead.c to your platform! Look at the definition of fflush, fread, ungetc on your system, then report this to bug-gnulib."
        # 0003-secure_snprintf.patch
        # patch taken from https://github.com/macports/macports-ports/blob/master/devel/m4/files/secure_snprintf.patch
        # to fix invalid instruction error on OSX when running m4
        for filename in sorted(glob.glob("patches/*.patch")):
            self.output.info('applying patch "%s"' % filename)
            tools.patch(base_path=self._source_subfolder, patch_file=filename)

        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(self._source_subfolder):
                args = []
                if self._is_msvc:
                    args.extend(['CC=$PWD/build-aux/compile cl -nologo',
                                 'CXX=$PWD/build-aux/compile cl -nologo',
                                 'LD=link',
                                 'NM=dumpbin -symbols',
                                 'STRIP=:',
                                 'AR=$PWD/build-aux/ar-lib lib',
                                 'RANLIB=:'])
                elif self._is_clang:
                    args.extend(['CFLAGS=-rtlib=compiler-rt'])

                env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                env_build.configure(args=args)
                env_build.make()
                env_build.install()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler
        self.info.include_build_settings()

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        m4 = "m4.exe" if self.settings.os_build == "Windows" else "m4"
        self.env_info.M4 = os.path.join(self.package_folder, "bin", m4).replace("\\", "/")
