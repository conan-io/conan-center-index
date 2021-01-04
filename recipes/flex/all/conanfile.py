from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class FlexConan(ConanFile):
    name = "flex"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/westes/flex"
    description = "Flex, the fast lexical analyzer generator"
    topics = ("conan", "flex", "lex", "lexer", "lexical analyzer generator")
    license = "BSD-2-Clause"    

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    requires = ("m4/1.4.18",)

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Flex package is not compatible with Windows. Consider using winflexbison instead.")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        configure_args = ["--disable-nls", "HELP2MAN=/bin/true", "M4=m4"]
        if self.options.shared:
            configure_args.extend(["--enable-shared", "--disable-static"])
        else:
            configure_args.extend(["--disable-shared", "--enable-static"])

        if self.settings.os == "Linux":
            # https://github.com/westes/flex/issues/247
            configure_args.extend(["ac_cv_func_malloc_0_nonnull=yes", "ac_cv_func_realloc_0_nonnull=yes"])
            # https://github.com/easybuilders/easybuild-easyconfigs/pull/5792
            configure_args.append("ac_cv_func_reallocarray=no")

        # stage1flex must be built on native arch: https://github.com/westes/flex/issues/78
        # This requires flex to depend on itself.
        # conan does not support this (currently), so cross build of flex is not possible atm

        self._autotools.configure(args=configure_args)
        return self._autotools


    def build(self):
        if tools.cross_building(self.settings, skip_x64_x86=True):
            raise ConanInvalidConfiguration("This recipe does not support cross building atm (missing conan support)")
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        os.unlink(os.path.join(self.package_folder, "lib", "libfl.la"))

    def package_info(self):
        self.cpp_info.libs = ["fl"]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
