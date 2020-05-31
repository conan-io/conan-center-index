import os
import re
from conans import ConanFile, AutoToolsBuildEnvironment, RunEnvironment, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibcurlConan(ConanFile):
    name = "libcurl"

    description = "command line tool and library for transferring data with URLs"
    topics = ("conan", "curl", "libcurl", "data-transfer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://curl.haxx.se"
    license = "MIT"
    exports_sources = ["lib_Makefile_add.am", "CMakeLists.txt"]
    generators = "cmake", "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_openssl": [True, False],
               "with_winssl": [True, False],
               "with_ldap": [True, False],
               "darwin_ssl": [True, False],
               "with_libssh2": [True, False],
               "with_libidn": [True, False],
               "with_librtmp": [True, False],
               "with_libmetalink": [True, False],
               "with_libpsl": [True, False],
               "with_largemaxwritesize": [True, False],
               "with_nghttp2": [True, False],
               "with_brotli": [True, False]
               }
    default_options = {'shared': False,
                       'fPIC': True,
                       'with_openssl': True,
                       'with_winssl': False,
                       'with_ldap': False,
                       'darwin_ssl': True,
                       'with_libssh2': False,
                       'with_libidn': False,
                       'with_librtmp': False,
                       'with_libmetalink': False,
                       'with_libpsl': False,
                       'with_largemaxwritesize': False,
                       'with_nghttp2': False,
                       'with_brotli': False
                       }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _autotools = False

    _cmake = None

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler != "Visual Studio"

    @property
    def _is_win_x_android(self):
        return self.settings.os == "Android" and tools.os_info.is_windows


    def imports(self):
        # Copy shared libraries for dependencies to fix DYLD_LIBRARY_PATH problems
        #
        # Configure script creates conftest that cannot execute without shared openssl binaries.
        # Ways to solve the problem:
        # 1. set *LD_LIBRARY_PATH (works with Linux with RunEnvironment
        #     but does not work on OS X 10.11 with SIP)
        # 2. copying dylib's to the build directory (fortunately works on OS X)

        if self.settings.os == "Macos":
            self.copy("*.dylib*", dst=self._source_subfolder, keep_path=False)

    def config_options(self):
        if not tools.is_apple_os(self.settings.os):
            del self.options.darwin_ssl

        if self.settings.os != "Windows":
            del self.options.with_winssl

        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        # be careful with those flags:
        # - with_openssl AND darwin_ssl uses darwin_ssl (to maintain recipe compatibilty)
        # - with_openssl AND NOT darwin_ssl uses openssl
        # - with_openssl AND with_winssl raises to error
        # - with_openssl AND NOT with_winssl uses openssl
        # Moreover darwin_ssl is set by default and with_winssl is not

        if self.settings.os == "Windows" and self.options.with_winssl and self.options.with_openssl:
            raise ConanInvalidConfiguration('Specify only with_winssl or with_openssl')

        if self.options.with_openssl:
            # enforce shared linking due to openssl dependency
            if not tools.is_apple_os(self.settings.os) or not self.options.darwin_ssl:
                self.options["openssl"].shared = self.options.shared
        if self.options.with_libssh2:
            if self.settings.compiler != "Visual Studio":
                self.options["libssh2"].shared = self.options.shared

    def system_requirements(self):
        # TODO: Declare tools needed to compile. The idea is Conan checking that they are
        #   installed and providing a meaningful message before starting the compilation. It
        #   would be much better than installed them (sudo required).
        pass

    def build_requirements(self):
        if self._is_mingw and "CONAN_BASH_PATH" not in os.environ and \
           tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        elif self._is_win_x_android:
            self.build_requires("ninja/1.9.0")
        elif self.settings.os == "Linux":
            self.build_requires("libtool/2.4.6")

    def requirements(self):
        if self.options.with_openssl:
            if tools.is_apple_os(self.settings.os) and self.options.darwin_ssl:
                pass
            elif self.settings.os == "Windows" and self.options.with_winssl:
                pass
            else:
                self.requires("openssl/1.1.1g")
        if self.options.with_libssh2:
            if self.settings.compiler != "Visual Studio":
                self.requires("libssh2/1.9.0")
        if self.options.with_nghttp2:
            self.requires("libnghttp2/1.40.0")

        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("curl-%s" % self.version, self._source_subfolder)
        tools.download("https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=True)

    def build(self):
        self._patch_misc_files()
        if self.settings.compiler == "Visual Studio" or self._is_win_x_android:
            self._build_with_cmake()
        else:
            self._build_with_autotools()


    def _patch_misc_files(self):
        if self.options.with_largemaxwritesize:
            tools.replace_in_file(os.path.join(self._source_subfolder, 'include', 'curl', 'curl.h'),
                                  "define CURL_MAX_WRITE_SIZE 16384",
                                  "define CURL_MAX_WRITE_SIZE 10485760")

        # https://github.com/curl/curl/issues/2835
        # for additional info, see this comment https://github.com/conan-io/conan-center-index/pull/1008#discussion_r386122685
        if self.settings.compiler == 'apple-clang' and self.settings.compiler.version == '9.1':
            if self.options.darwin_ssl:
                tools.replace_in_file(os.path.join(self._source_subfolder, 'lib', 'vtls', 'sectransp.c'),
                                      '#define CURL_BUILD_MAC_10_13 MAC_OS_X_VERSION_MAX_ALLOWED >= 101300',
                                      '#define CURL_BUILD_MAC_10_13 0')

    def _get_configure_command_args(self):
        params = []
        params.append("--without-libidn2" if not self.options.with_libidn else "--with-libidn2")
        params.append("--without-librtmp" if not self.options.with_librtmp else "--with-librtmp")
        params.append("--without-libmetalink" if not self.options.with_libmetalink else "--with-libmetalink")
        params.append("--without-libpsl" if not self.options.with_libpsl else "--with-libpsl")
        params.append("--without-brotli" if not self.options.with_brotli else "--with-brotli")

        if tools.is_apple_os(self.settings.os) and self.options.darwin_ssl:
            params.append("--with-darwinssl")
            params.append("--without-ssl")
        elif self.settings.os == "Windows" and self.options.with_winssl:
            params.append("--with-winssl")
            params.append("--without-ssl")
        elif self.options.with_openssl:
            openssl_path = self.deps_cpp_info["openssl"].rootpath.replace('\\', '/')
            params.append("--with-ssl=%s" % openssl_path)
        else:
            params.append("--without-ssl")

        if self.options.with_libssh2:
            params.append("--with-libssh2=%s" % self.deps_cpp_info["libssh2"].lib_paths[0].replace('\\', '/'))
        else:
            params.append("--without-libssh2")

        if self.options.with_nghttp2:
            params.append("--with-nghttp2=%s" % self.deps_cpp_info["libnghttp2"].rootpath.replace('\\', '/'))
        else:
            params.append("--without-nghttp2")

        params.append("--with-zlib=%s" % self.deps_cpp_info["zlib"].lib_paths[0].replace('\\', '/'))

        if not self.options.shared:
            params.append("--disable-shared")
            params.append("--enable-static")
        else:
            params.append("--enable-shared")
            params.append("--disable-static")

        if not self.options.with_ldap:
            params.append("--disable-ldap")

        # Cross building flags
        if tools.cross_building(self.settings):
            if self.settings.os == "Linux" and "arm" in self.settings.arch:
                params.append('--host=%s' % self._get_linux_arm_host())
            elif self.settings.os == "iOS":
                params.append("--enable-threaded-resolver")
                params.append("--disable-verbose")
            elif self.settings.os == "Android":
                pass # this just works, conan is great!

        return params


    def _get_linux_arm_host(self):
        arch = None
        if self.settings.os == 'Linux':
            arch = 'arm-linux-gnu'
            # aarch64 could be added by user
            if 'aarch64' in self.settings.arch:
                arch = 'aarch64-linux-gnu'
            elif 'arm' in self.settings.arch and 'hf' in self.settings.arch:
                arch = 'arm-linux-gnueabihf'
            elif 'arm' in self.settings.arch and self._arm_version(str(self.settings.arch)) > 4:
                arch = 'arm-linux-gnueabi'
        return arch

    # TODO, this should be a inner fuction of _get_linux_arm_host since it is only used from there
    # it should not polute the class namespace, since there are iOS and Android arm aritectures also
    def _arm_version(self, arch):
        version = None
        match = re.match(r"arm\w*(\d)", arch)
        if match:
            version = int(match.group(1))
        return version

    def _patch_mingw_files(self):
        if not self._is_mingw:
            return
        # patch autotools files
        # for mingw builds - do not compile curl tool, just library
        # linking errors are much harder to fix than to exclude curl tool
        tools.replace_in_file("Makefile.am",
                              'SUBDIRS = lib src',
                              'SUBDIRS = lib')

        tools.replace_in_file("Makefile.am",
                              'include src/Makefile.inc',
                              '')

        # patch for zlib naming in mingw
        # when cross-building, the name is correct
        if not tools.cross_building(self.settings):
            tools.replace_in_file("configure.ac",
                                  '-lz ',
                                  '-lzlib ')

        # patch for openssl extras in mingw
        if self.options.with_openssl:
            tools.replace_in_file("configure",
                                  '-lcrypto ',
                                  '-lcrypto -lcrypt32 ')

        if self.options.shared:
            # patch for shared mingw build
            tools.replace_in_file(os.path.join('lib', 'Makefile.am'),
                                  'noinst_LTLIBRARIES = libcurlu.la',
                                  '')
            tools.replace_in_file(os.path.join('lib', 'Makefile.am'),
                                  'noinst_LTLIBRARIES =',
                                  '')
            tools.replace_in_file(os.path.join('lib', 'Makefile.am'),
                                  'lib_LTLIBRARIES = libcurl.la',
                                  'noinst_LTLIBRARIES = libcurl.la')
            # add directives to build dll
            # used only for native mingw-make
            if not tools.cross_building(self.settings):
                added_content = tools.load(os.path.join(self.source_folder, 'lib_Makefile_add.am'))
                tools.save(os.path.join('lib', 'Makefile.am'), added_content, append=True)

    def _build_with_autotools(self):
        with tools.chdir(self._source_subfolder):
            use_win_bash = self._is_mingw and not tools.cross_building(self.settings)

            # autoreconf
            self.run('./buildconf', win_bash=use_win_bash, run_environment=True)

            # fix generated autotools files on alle to have relocateable binaries
            if tools.is_apple_os(self.settings.os):
                tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name ")

            self.run("chmod +x configure")

            env_run = RunEnvironment(self)
            # run configure with *LD_LIBRARY_PATH env vars it allows to pick up shared openssl
            self.output.info("Run vars: " + repr(env_run.vars))
            with tools.environment_append(env_run.vars):
                autotools, autotools_vars = self._configure_autotools()
                autotools.make(vars=autotools_vars)

    def _configure_autotools_vars(self):
        autotools_vars = self._autotools.vars
        # tweaks for mingw
        if self._is_mingw:
            autotools_vars['RCFLAGS'] = '-O COFF'
            if self.settings.arch == "x86":
                autotools_vars['RCFLAGS'] += ' --target=pe-i386'
            else:
                autotools_vars['RCFLAGS'] += ' --target=pe-x86-64'

            del autotools_vars['LIBS']
            self.output.info("Autotools env vars: " + repr(autotools_vars))

        if tools.cross_building(self.settings):
            if self.settings.os == "iOS":
                iphoneos = tools.apple_sdk_name(self.settings)
                ios_dev_target = str(self.settings.os.version).split(".")[0]
                if self.settings.arch in ["x86", "x86_64"]:
                    autotools_vars['CPPFLAGS'] = "-D__IPHONE_OS_VERSION_MIN_REQUIRED={}0000".format(ios_dev_target)
                elif self.settings.arch in ["armv7", "armv7s", "armv8"]:
                    autotools_vars['CPPFLAGS'] = ""
                else:
                    raise ConanInvalidConfiguration("Unsuported iOS arch {}".format(self.settings.arch))

                cc = tools.XCRun(self.settings, iphoneos).cc
                sysroot = "-isysroot {}".format(tools.XCRun(self.settings, iphoneos).sdk_path)

                if self.settings.arch == "armv8":
                    configure_arch = "arm64"
                    configure_host = "arm" #unused, autodetected
                else:
                    configure_arch = self.settings.arch
                    configure_host = self.settings.arch #unused, autodetected


                arch_flag = "-arch {}".format(configure_arch)
                ios_min_version = tools.apple_deployment_target_flag(self.settings.os, self.settings.os.version)
                extra_flag = "-Werror=partial-availability"
                extra_def = " -DHAVE_SOCKET -DHAVE_FCNTL_O_NONBLOCK"
                # if we debug, maybe add a -gdwarf-2 , but why would we want that?

                autotools_vars['CC'] = cc
                autotools_vars['IPHONEOS_DEPLOYMENT_TARGET'] = ios_dev_target
                autotools_vars['CFLAGS'] = "{} {} {} {}".format(
                    sysroot, arch_flag, ios_min_version, extra_flag
                )

                if self.options.with_openssl:
                    openssl_path = self.deps_cpp_info["openssl"].rootpath
                    openssl_libdir = self.deps_cpp_info["openssl"].libdirs[0]
                    autotools_vars['LDFLAGS'] = "{} {} -L{}/{}".format(arch_flag, sysroot, openssl_path, openssl_libdir)
                else:
                    autotools_vars['LDFLAGS'] = "{} {}".format(arch_flag, sysroot)

                autotools_vars['CPPFLAGS'] += extra_def

            elif self.settings.os == "Android":
                # nothing do to at the moment, this seems to just work
                pass

        return autotools_vars

    def _configure_autotools(self):

        if not self._autotools:
            use_win_bash = self._is_mingw and not tools.cross_building(self.settings)
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=use_win_bash)

            if self.settings.os != "Windows":
                self._autotools.fpic = self.options.fPIC

            autotools_vars = self._configure_autotools_vars()

            # tweaks for mingw
            if self._is_mingw:
                # patch autotools files
                self._patch_mingw_files()

                self._autotools.defines.append('_AMD64_')

            configure_args = self._get_configure_command_args()

            if self.settings.os == "iOS" and self.settings.arch == "x86_64":
                # please do not autodetect --build for the iOS simulator, thanks!
                self._autotools.configure(vars=autotools_vars, args=configure_args, build=False)
            else:
                self._autotools.configure(vars=autotools_vars, args=configure_args)


        return self._autotools, self._configure_autotools_vars()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        if self._is_win_x_android:
            self._cmake = CMake(self, generator="Ninja")
        else:
            self._cmake = CMake(self)
        self._cmake.definitions['BUILD_TESTING'] = False
        self._cmake.definitions['BUILD_CURL_EXE'] = False
        self._cmake.definitions['CURL_DISABLE_LDAP'] = not self.options.with_ldap
        self._cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        self._cmake.definitions['CURL_STATICLIB'] = not self.options.shared
        self._cmake.definitions['CMAKE_DEBUG_POSTFIX'] = ''
        self._cmake.definitions['CMAKE_USE_LIBSSH2'] = self.options.with_libssh2

        # all these options are exclusive. set just one of them
        # mac builds do not use cmake so don't even bother about darwin_ssl
        self._cmake.definitions['CMAKE_USE_WINSSL'] = 'with_winssl' in self.options and self.options.with_winssl
        self._cmake.definitions['CMAKE_USE_OPENSSL'] = 'with_openssl' in self.options and self.options.with_openssl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _build_with_cmake(self):
        # patch cmake files
        with tools.chdir(self._source_subfolder):
            tools.replace_in_file("CMakeLists.txt",
                                  "include(CurlSymbolHiding)",
                                  "")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

        # Execute install
        if self.settings.compiler == "Visual Studio" or self._is_win_x_android:
            cmake = self._configure_cmake()
            cmake.install()
        else:
            env_run = RunEnvironment(self)
            with tools.environment_append(env_run.vars):
                with tools.chdir(self._source_subfolder):
                    autotools, autotools_vars = self._configure_autotools()
                    autotools.install(vars=autotools_vars)
        if self._is_mingw:
            # Handle only mingw libs
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*dll.a", dst="lib", keep_path=False)
            self.copy(pattern="*.def", dst="lib", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)

        self.copy("cacert.pem", dst="res")

        # no need to distribute share folder (docs/man pages)
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        # no need for pc files
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # no need for cmake files
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        # Remove libtool files (*.la)
        if os.path.isfile(os.path.join(self.package_folder, 'lib', 'libcurl.la')):
            os.remove(os.path.join(self.package_folder, 'lib', 'libcurl.la'))

    def package_info(self):
        self.cpp_info.names['cmake_find_package'] = 'CURL'
        self.cpp_info.names['cmake_find_package_multi'] = 'CURL'

        if self.settings.compiler != "Visual Studio":
            self.cpp_info.libs = ['curl']
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.extend(["rt", "pthread"])
                if self.options.with_libssh2:
                    self.cpp_info.libs.extend(["ssh2"])
                if self.options.with_libidn:
                    self.cpp_info.libs.extend(["idn"])
                if self.options.with_librtmp:
                    self.cpp_info.libs.extend(["rtmp"])
                if self.options.with_brotli:
                    self.cpp_info.libs.extend(["brotlidec"])
            if self.settings.os == "Macos":
                if self.options.with_ldap:
                    self.cpp_info.system_libs.extend(["ldap"])
                if self.options.darwin_ssl:
                    self.cpp_info.frameworks.extend(["Cocoa", "Security"])
        else:
            self.cpp_info.libs = ['libcurl_imp'] if self.options.shared else ['libcurl']

        if self.settings.os == "Windows":
            # used on Windows for VS build, native and cross mingw build
            self.cpp_info.system_libs.append('ws2_32')
            if self.options.with_ldap:
                self.cpp_info.system_libs.append("wldap32")
            if self.options.with_winssl:
                self.cpp_info.system_libs.append("Crypt32")

        if self._is_mingw:
            # provide pthread for dependent packages
            self.cpp_info.cflags.append("-pthread")
            self.cpp_info.exelinkflags.append("-pthread")
            self.cpp_info.sharedlinkflags.append("-pthread")

        if not self.options.shared:
            self.cpp_info.defines.append("CURL_STATICLIB=1")
