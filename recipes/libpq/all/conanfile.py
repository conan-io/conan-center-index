from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibpqConan(ConanFile):
    name = "libpq"
    description = "The library used by all the standard PostgreSQL tools."
    topics = ("conan", "libpq", "postgresql", "database", "db")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.postgresql.org/docs/current/static/libpq.html"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "PostgreSQL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False],
        "disable_rpath": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'with_zlib': True, 'with_openssl': False, 'disable_rpath': False}
    generators = "cmake"
    _autotools = None

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("strawberryperl/5.30.0.1")
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_clang8_x86(self):
        return self.settings.os == "Linux" and \
               self.settings.compiler == "clang" and \
               self.settings.compiler.version == "8" and \
               self.settings.arch == "x86"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11")
        if self.options.with_openssl:
            self.requires.add("openssl/1.0.2s")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "postgresql-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            args = ['--without-readline']
            args.append('--with-zlib' if self.options.with_zlib else '--without-zlib')
            args.append('--with-openssl' if self.options.with_openssl else '--without-openssl')
            if self.options.disable_rpath:
                args.append('--disable-rpath')
            if self._is_clang8_x86:
                self._autotools.flags.append("-msse2")
            with tools.chdir(self._source_subfolder):
                self._autotools.configure(args=args)
        return self._autotools

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_OPENSSL"] = self.options.with_openssl
        cmake.definitions["USE_ZLIB"] = self.options.with_zlib
        cmake.configure()
        return cmake

    def build(self):
        if self.settings.compiler == "Visual Studio":
            # https://www.postgresql.org/docs/8.3/install-win32-libpq.html
            # https://github.com/postgres/postgres/blob/master/src/tools/msvc/README
            if not self.options.shared:
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "tools", "msvc", "MKvcbuild.pm"),
                                      "$libpq = $solution->AddProject('libpq', 'dll', 'interfaces',",
                                      "$libpq = $solution->AddProject('libpq', 'lib', 'interfaces',")
            with tools.vcvars(self.settings):
                config = "DEBUG" if self.settings.build_type == "Debug" else "RELEASE"
                with tools.environment_append({"CONFIG": config}):
                    with tools.chdir(os.path.join(self._source_subfolder, "src", "tools", "msvc")):
                        self.run("perl build.pl libpq")
        else:
            autotools = self._configure_autotools()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "backend")):
                autotools.make(target="generated-headers")
            with tools.chdir(os.path.join(self._source_subfolder, "src", "common")):
                autotools.make()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "include")):
                autotools.make()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
                autotools.make()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "bin", "pg_config")):
                autotools.make()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("*postgres_ext.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*pg_config.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*pg_config_ext.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*libpq-fe.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*libpq-events.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*.h", src=os.path.join(self._source_subfolder, "src", "include", "libpq"), dst=os.path.join("include", "libpq"), keep_path=False)
            self.copy("*genbki.h", src=self._source_subfolder, dst=os.path.join("include", "catalog"), keep_path=False)
            self.copy("*pg_type.h", src=self._source_subfolder, dst=os.path.join("include", "catalog"), keep_path=False)
            self.copy("*.lib", src=self._source_subfolder, dst="lib", keep_path=False)
            if self.options.shared:
                self.copy("*.dll", src=self._source_subfolder, dst="bin", keep_path=False)
        else:
            autotools = self._configure_autotools()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "common")):
                autotools.install()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "include")):
                autotools.install()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
                autotools.install()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "bin", "pg_config")):
                autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "include", "postgresql", "server"))
            self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self._source_subfolder, "src", "include", "catalog"))
        self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self._source_subfolder, "src", "backend", "catalog"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.env_info.PostgreSQL_ROOT = self.package_folder
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(["ws2_32", "secur32", "advapi32", "shell32", "crypt32", "wldap32"])
