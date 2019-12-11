import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class Nghttp2Conan(ConanFile):
    name = "libnghttp2"
    description = "HTTP/2 C Library and tools"
    topics = ("conan", "http")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nghttp2.org"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_app": [True, False],
               "with_hpack": [True, False],
               "with_asio": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_app": True,
                       "with_hpack": True,
                       "with_asio": False}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_asio and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Build with asio and MSVC is not supported yet, see upstream bug #589")
        if self.settings.compiler == "gcc":
            v = tools.Version(str(self.settings.compiler.version))
            if v < "6.0":
                raise ConanInvalidConfiguration("gcc >= 6.0 required")

    def requirements(self):
        self.requires.add("zlib/1.2.11")
        if self.options.with_app:
            self.requires.add("openssl/1.1.1d")
            self.requires.add("c-ares/1.15.0")
            self.requires.add("libev/4.27")
            self.requires.add("libxml2/2.9.9")
        if self.options.with_hpack:
            self.requires.add("jansson/2.12")
        if self.options.with_asio:
            self.requires.add("boost/1.71.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "nghttp2-{0}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["ENABLE_SHARED_LIB"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["ENABLE_STATIC_LIB"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["ENABLE_HPACK_TOOLS"] = "ON" if self.options.with_hpack else "OFF"
        cmake.definitions["ENABLE_APP"] = "ON" if self.options.with_app else "OFF"
        cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        cmake.definitions["ENABLE_PYTHON_BINDINGS"] = "OFF"
        cmake.definitions["ENABLE_FAILMALLOC"] = "OFF"
        # disable unneeded auto-picked dependencies
        cmake.definitions["WITH_LIBXML2"] = "OFF"
        cmake.definitions["WITH_JEMALLOC"] = "OFF"
        cmake.definitions["WITH_SPDYLAY"] = "OFF"

        cmake.definitions["ENABLE_ASIO_LIB"] = "ON" if self.options.with_asio else "OFF"

        if self.options.with_app:
            cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['openssl'].rootpath
        if self.options.with_asio:
            cmake.definitions['BOOST_ROOT'] = self.deps_cpp_info['boost'].rootpath
        cmake.definitions['ZLIB_ROOT'] = self.deps_cpp_info['zlib'].rootpath

        cmake.configure()
        return cmake

    def _build_with_autotools(self):
        prefix = os.path.abspath(self.package_folder)
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            if self.settings.os == 'Windows':
                prefix = tools.unix_path(prefix)
            args = []
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            if self.options.with_hpack:
                args.append('--enable-hpack-tools')
            else:
                args.append('--disable-hpack-tools')

            if self.options.with_app:
                args.append('--enable-app')
            else:
                args.append('--disable-app')

            args.append('--disable-examples')
            args.append('--disable-python-bindings')
            # disable unneeded auto-picked dependencies
            args.append('--without-jemalloc')
            args.append('--without-systemd')
            args.append('--without-libxml2')

            if self.options.with_asio:
                args.append('--enable-asio-lib')
                args.append('--with-boost=' + self.deps_cpp_info['boost'].rootpath)
            else:
                args.append('--without-boost')

            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            self._build_with_autotools()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.install()
            cmake.patch_config_paths()

        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

        for la_name in ('libnghttp2.la', 'libnghttp2_asio.la'):
            la_file = os.path.join(self.package_folder, "lib", la_name)
            if os.path.isfile(la_file):
                os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == 'Visual Studio':
            if not self.options.shared:
                self.cpp_info.defines.append('NGHTTP2_STATICLIB')
