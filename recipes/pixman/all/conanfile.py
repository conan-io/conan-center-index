from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PixmanConan(ConanFile):
    name = "pixman"
    description = "Pixman is a low-level software library for pixel manipulation"
    topics = ("pixman", "graphics", "compositing", "rasterization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _includedir(self):
        return os.path.join("include", "pixman-1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("pixman can only be built as a static library on Windows")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.win32.common"),
                                  "-MDd ", "-{} ".format(str(self.settings.compiler.runtime)))
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.win32.common"),
                                  "-MD ", "-{} ".format(str(self.settings.compiler.runtime)))
        if tools.is_apple_os(self, self.settings.os):
            # https://lists.freedesktop.org/archives/pixman/2014-November/003461.html
            test_makefile = os.path.join(self._source_subfolder, "test", "Makefile.in")
            tools.files.replace_in_file(self, test_makefile,
                                  "region_test_OBJECTS = region-test.$(OBJEXT)",
                                  "region_test_OBJECTS = region-test.$(OBJEXT) utils.$(OBJEXT)")
            tools.files.replace_in_file(self, test_makefile,
                                  "scaling_helpers_test_OBJECTS = scaling-helpers-test.$(OBJEXT)",
                                  "scaling_helpers_test_OBJECTS = scaling-helpers-test.$(OBJEXT) utils.$(OBJEXT)")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-libpng",
            "--disable-gtk",
        ]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                make_vars = {
                    "MMX": "on" if self.settings.arch == "x86" else "off",
                    "SSE2": "on",
                    "SSSE3": "on",
                    "CFG": str(self.settings.build_type).lower(),
                }
                var_args = " ".join("{}={}".format(k, v) for k, v in make_vars.items())
                self.run("make -C {}/pixman -f Makefile.win32 {}".format(self._source_subfolder, var_args),
                            win_bash=True)
        else:
            autotools = self._configure_autotools()
            autotools.make(target="pixman")

    def package(self):
        self.copy(os.path.join(self._source_subfolder, "COPYING"), dst="licenses")
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            self.copy(pattern="*{}pixman.h".format(os.sep), dst=self._includedir, keep_path=False)
            self.copy(pattern="*{}pixman-version.h".format(os.sep), dst=self._includedir, keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.includedirs.append(self._includedir)
        self.cpp_info.names["pkg_config"] = "pixman-1"
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
