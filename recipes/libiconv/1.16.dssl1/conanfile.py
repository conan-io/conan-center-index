from conans import ConanFile, tools, AutoToolsBuildEnvironment, CMake
from contextlib import contextmanager
import os
from shutil import copyfile

class LibiconvConan(ConanFile):
    name = "libiconv"
    description = "Convert text to and from Unicode"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libiconv/"
    topics = "libiconv", "iconv", "text", "encoding", "locale", "unicode", "conversion"
    license = "LGPL-2.1"
    exports_sources = ["patches/**", "CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    version = "1.16.dssl1"
    original_version = "1.16"

    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, 'source_subfolder') 

    @property
    def _build_subfolder(self):
        return os.path.join(self.source_folder, 'build_subfolder') 

    @property
    def _use_winbash(self):
        return tools.os_info.is_windows and (self.settings.compiler == "gcc" or tools.cross_building(self.settings))


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        archive_name = "{0}-{1}".format(self.name, self.original_version)
        os.rename(archive_name, self._source_subfolder)
        self._patch_sources()
        if tools.os_info.is_windows:
            copyfile(
                os.path.join(self.source_folder, 'CMakeLists.txt'), 
                os.path.join(self._source_subfolder, 'CMakeLists.txt'))

    @contextmanager
    def _build_context(self):
        env_vars = {}

        if not tools.cross_building(self.settings):
            rc = None
            if self.settings.arch == "x86":
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                rc = "windres --target=pe-x86-64"
            if rc:
                env_vars["RC"] = rc
                env_vars["WINDRES"] = rc

        with tools.no_op():
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(env_vars):
                    yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        prefix = os.path.abspath(self.package_folder)
        host = None
        build = None
        if self._use_winbash or self._is_msvc:
            prefix = prefix.replace("\\", "/")
            build = False
            if not tools.cross_building(self.settings):
                if self.settings.arch == "x86":
                    host = "i686-w64-mingw32"
                elif self.settings.arch == "x86_64":
                    host = "x86_64-w64-mingw32"

        #
        # If you pass --build when building for iPhoneSimulator, the configure script halts.
        # So, disable passing --build by setting it to False.
        #
        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            build = False

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        configure_args = ["--prefix=%s" % prefix]
        if self.options.shared:
            configure_args.extend(["--disable-static", "--enable-shared"])
        else:
            configure_args.extend(["--enable-static", "--disable-shared"])

        self._autotools.configure(args=configure_args, host=host, build=build)
        return self._autotools

    def _patch_sources(self):
        for patchdata in self.conan_data["patches"][self.version]:
            only_win = patchdata.pop('only_win', False)
            if (tools.os_info.is_windows and only_win) or not only_win:
                tools.patch(**patchdata)

    def build(self):
        if tools.os_info.is_windows:
            cmake = CMake(self)
            cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
            cmake.build(build_dir=self._build_subfolder)
        else:
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        if tools.os_info.is_windows:
            cmake = CMake(self)
            cmake.install(build_dir=self._build_subfolder)
        else:
            self.copy("COPYING.LIB", src=self._source_subfolder, dst="licenses")
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.install()

            os.unlink(os.path.join(self.package_folder, "lib", "libcharset.la"))
            os.unlink(os.path.join(self.package_folder, "lib", "libiconv.la"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        lib = "iconv"
        if self.settings.os == "Windows" and self.options.shared:
            lib += ".dll" + ".lib" if self.settings.compiler == "Visual Studio" else ".a"
        self.cpp_info.libs = [lib]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(binpath))
        self.env_info.path.append(binpath)
