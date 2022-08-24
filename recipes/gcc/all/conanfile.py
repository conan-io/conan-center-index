from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException, ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class GccConan(ConanFile):
    name = "gcc"
    description = "The GNU Compiler Collection includes front ends for C, " \
                  "C++, Objective-C, Fortran, Ada, Go, and D, as well as " \
                  "libraries for these languages (libstdc++,...). "
    topics = ("gcc", "gnu", "compiler", "c", "c++")
    homepage = "https://gcc.gnu.org"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-only"
    settings = "os", "compiler", "arch", "build_type"
    _autotools = None

    def build_requirements(self):
        self.build_requires("flex/2.6.4")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        pkgversion = 'conan GCC %s' % self.version
        bugurl = self.url + '/issues'
        libdir = "%s/lib/gcc/%s" % (self.package_folder, self.version)
        args = [
            "--enable-languages=c,c++",
            "--disable-nls",
            "--disable-multilib",
            "--disable-bootstrap",
            "--with-system-zlib",
            "--with-gmp=%s" % self.deps_cpp_info['gmp'].rootpath,
            '--with-mpc=%s' % self.deps_cpp_info["mpc"].rootpath,
            "--with-mpfr=%s" % self.deps_cpp_info["mpfr"].rootpath,
            "--without-isl",
            "--libdir=%s" % libdir,
            '--with-pkgversion=%s' % pkgversion,
            "--program-suffix=-%s" % self.version,
            "--with-bugurl=%s" % bugurl
        ]
        if self.settings.os == "Macos":
            xcrun = tools.XCRun(self.settings)
            args.extend([
                '--with-native-system-header-dir=/usr/include',
                "--with-sysroot={}".format(xcrun.sdk_path)
            ])
        self._autotools.libs = []  # otherwise causes config.log to fail finding -lmpc
        if self.settings.compiler in ["clang", "apple-clang"]:
            # xgcc: error: unrecognized command-line option -stdlib=libc++
            if self.settings.compiler.libcxx == "libc++":
                self._autotools.cxx_flags.remove("-stdlib=libc++")
            elif self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"]:
                self._autotools.cxx_flags.remove("-stdlib=libstdc++")
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("mpc/1.2.0")
        self.requires("mpfr/4.1.0")
        self.requires("gmp/6.2.0")
        self.requires("zlib/1.2.11")

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows builds aren't supported (yet), sorry")
        if tools.cross_building(self.settings):
            raise ConanInvalidConfiguration("no cross-building support (yet), sorry")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "gcc-%s" % self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _make_args(self):
        if self.settings.os == "Macos":
            return ["BOOT_LDFLAGS=-Wl,-headerpad_max_install_names"]
        return []

    def build(self):
        # If building on x86_64, change the default directory name for 64-bit libraries to "lib":
        libdir = "%s/lib/gcc/%s" % (self.package_folder, self.version)
        tools.replace_in_file(os.path.join(self.source_folder,
                                           self._source_subfolder, "gcc", "config", "i386", "t-linux64"),
                              "m64=../lib64", "m64=../lib", strict=False)
        # Ensure correct install names when linking against libgcc_s;
        # see discussion in https://github.com/Homebrew/legacy-homebrew/pull/34303
        tools.replace_in_file(os.path.join(self.source_folder,
                                           self._source_subfolder, "libgcc", "config", "t-slibgcc-darwin"),
                              "@shlib_slibdir@", libdir, strict=False)
        autotools = self._configure_autotools()
        autotools.make(args=self._make_args)

    def package_id(self):
        del self.info.settings.compiler

    def package(self):
        autotools = self._configure_autotools()
        if self.settings.build_type == "Debug":
            autotools.install(args=self._make_args)
        else:
            autotools.make(args=["install-strip"] + self._make_args)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.la")
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : " + bindir)
        self.env_info.PATH.append(bindir)

        cc = os.path.join(bindir, "gcc-%s" % self.version)
        self.output.info("Creating CC env var with : " + cc)
        self.env_info.CC = cc

        cxx = os.path.join(bindir, "g++-%s" % self.version)
        self.output.info("Creating CXX env var with : " + cxx)
        self.env_info.CXX = cxx
