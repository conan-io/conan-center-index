from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class PixmanConan(ConanFile):
    name = "pixman"
    description = "Pixman is a low-level software library for pixel manipulation"
    topics = ("conan", "pixman", "graphics", "compositing", "rasterization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    _autotools = None

    @property
    def _includedir(self):
        return os.path.join("include", "pixman-1")

    @property
    def _folder(self):
        return "{}-{}".format(self.name, self.version)

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20190524")

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("pixman can only built as static library for Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        if self.settings.os == 'Macos':
            # https://lists.freedesktop.org/archives/pixman/2014-November/003461.html
            test_makefile = os.path.join(self._folder, 'test', 'Makefile.in')
            tools.replace_in_file(test_makefile,
                                  'region_test_OBJECTS = region-test.$(OBJEXT)',
                                  'region_test_OBJECTS = region-test.$(OBJEXT) utils.$(OBJEXT)')
            tools.replace_in_file(test_makefile,
                                  'scaling_helpers_test_OBJECTS = scaling-helpers-test.$(OBJEXT)',
                                  'scaling_helpers_test_OBJECTS = scaling-helpers-test.$(OBJEXT) utils.$(OBJEXT)')

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--disable-libpng", "--disable-gtk"]
            if self.options.shared:
                args.extend(["--enable-shared", "--disable-static"])
            else:
                args.extend(["--enable-static", "--disable-shared"])
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.configure(configure_dir=self._folder, args=args)
        return self._autotools

    def build(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                make_vars = {
                    "MMX": "on" if self.settings.arch == "x86" else "off",
                    "SSE2": "on",
                    "SSSE3": "on",
                    "CFG": str(self.settings.build_type).lower(),
                }
                tools.replace_in_file(os.path.join(self._folder, 'Makefile.win32.common'),
                                        '-MDd ', '-%s ' % str(self.settings.compiler.runtime))
                tools.replace_in_file(os.path.join(self._folder, 'Makefile.win32.common'),
                                        '-MD ', '-%s ' % str(self.settings.compiler.runtime))
                var_args = " ".join("{}={}".format(k, v) for k, v in make_vars.items())
                self.run("make -C {}/pixman -f Makefile.win32 {}".format(self._folder, var_args),
                            win_bash=True)
        else:
            autotools = self._configure_autotools()
            autotools.make(target="pixman")

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            self.copy(pattern="*{}pixman.h".format(os.sep), dst=self._includedir, keep_path=False)
            self.copy(pattern="*{}pixman-version.h".format(os.sep), dst=self._includedir, keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
        la = os.path.join(self.package_folder, "lib", "libpixman-1.la")
        if os.path.isfile(la):
            os.unlink(la)
        self.copy(os.path.join(self._folder, 'COPYING'), dst='licenses')
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [self._includedir]
        self.cpp_info.names['pkg_config'] = 'pixman-1'
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m"]
