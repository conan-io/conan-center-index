import glob
import os
import re
from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LibcurlConan(ConanFile):
    name = "libcurl"

    description = "command line tool and library for transferring data with URLs"
    topics = ("conan", "curl", "libcurl", "data-transfer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://curl.haxx.se"
    license = "MIT"
    exports_sources = ["lib_Makefile_add.am", "CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package_multi", "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, "openssl", "wolfssl", "schannel", "darwinssl"],
        "with_openssl": [True, False, "deprecated"],
        "with_wolfssl": [True, False, "deprecated"],
        "with_winssl": [True, False, "deprecated"],
        "darwin_ssl": [True, False, "deprecated"],
        "with_ldap": [True, False],
        "with_libssh2": [True, False],
        "with_libidn": [True, False],
        "with_librtmp": [True, False],
        "with_libmetalink": [True, False],
        "with_libpsl": [True, False],
        "with_largemaxwritesize": [True, False],
        "with_nghttp2": [True, False],
        "with_zlib": [True, False],
        "with_brotli": [True, False],
        "with_zstd": [True, False],
        "with_c_ares": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
        "with_openssl": "deprecated",
        "with_wolfssl": "deprecated",
        "with_winssl": "deprecated",
        "darwin_ssl": "deprecated",
        "with_ldap": False,
        "with_libssh2": False,
        "with_libidn": False,
        "with_librtmp": False,
        "with_libmetalink": False,
        "with_libpsl": False,
        "with_largemaxwritesize": False,
        "with_nghttp2": False,
        "with_zlib": True,
        "with_brotli": False,
        "with_zstd": False,
        "with_c_ares": False,
    }

    _autotools = None
    _autotools_vars = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler != "Visual Studio"

    @property
    def _is_win_x_android(self):
        return self.settings.os == "Android" and tools.os_info.is_windows

    @property
    def _is_using_cmake_build(self):
        return self.settings.compiler == "Visual Studio" or self._is_win_x_android

    @property
    def _has_zstd_option(self):
        return tools.Version(self.version) >= "7.72.0"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_zstd_option:
            del self.options.with_zstd
        # Default options
        self.options.with_ssl = "darwinssl" if tools.is_apple_os(self.settings.os) else "openssl"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        # Deprecated options
        # ===============================
        if (any(deprecated_option != "deprecated" for deprecated_option in [self.options.with_openssl, self.options.with_wolfssl, self.options.with_winssl, self.options.darwin_ssl])):
            self.output.warn("with_openssl, with_winssl, darwin_ssl and with_wolfssl options are deprecated. Use with_ssl option instead.")
            if tools.is_apple_os(self.settings.os) and self.options.with_ssl == "darwinssl":
                if self.options.darwin_ssl == True:
                    self.options.with_ssl = "darwinssl"
                elif self.options.with_openssl == True:
                    self.options.with_ssl = "openssl"
                elif self.options.with_wolfssl == True:
                    self.options.with_ssl = "wolfssl"
                else:
                    self.options.with_ssl = False
            if not tools.is_apple_os(self.settings.os) and self.options.with_ssl == "openssl":
                if self.settings.os == "Windows" and self.options.with_winssl == True:
                    self.options.with_ssl = "schannel"
                elif self.options.with_openssl == True:
                    self.options.with_ssl = "openssl"
                elif self.options.with_wolfssl == True:
                    self.options.with_ssl = "wolfssl"
                else:
                    self.options.with_ssl = False
        # ===============================

        if self.options.with_ssl == "schannel" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("schannel only suppported on Windows.")
        if self.options.with_ssl == "darwinssl" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("darwinssl only suppported on Apple like OS (Macos, iOS, watchOS or tvOS).")
        if self.options.with_ssl == "wolfssl" and self._is_using_cmake_build and tools.Version(self.version) < "7.70.0":
            raise ConanInvalidConfiguration("Before 7.70.0, libcurl has no wolfssl support for Visual Studio or \"Windows to Android cross compilation\"")

        # These options are not used in CMake build yet
        if self._is_using_cmake_build:
            del self.options.with_libidn
            del self.options.with_librtmp
            del self.options.with_libmetalink
            del self.options.with_libpsl

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1k")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/4.6.0")
        if self.options.with_nghttp2:
            self.requires("libnghttp2/1.43.0")
        if self.options.with_libssh2:
            self.requires("libssh2/1.9.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.4.9")
        if self.options.with_c_ares:
            self.requires("c-ares/1.17.1")

    def package_id(self):
        # Deprecated options
        del self.info.options.with_openssl
        del self.info.options.with_winssl
        del self.info.options.darwin_ssl
        del self.info.options.with_wolfssl

    def build_requirements(self):
        if self._is_using_cmake_build:
            if self._is_win_x_android:
                self.build_requires("ninja/1.10.2")
        else:
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.3")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        tools.download("https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=True)

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

    def build(self):
        self._patch_sources()
        if self._is_using_cmake_build:
            self._build_with_cmake()
        else:
            self._build_with_autotools()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        self._patch_misc_files()
        self._patch_mingw_files()
        self._patch_cmake()

    def _patch_misc_files(self):
        if self.options.with_largemaxwritesize:
            tools.replace_in_file(os.path.join(self._source_subfolder, "include", "curl", "curl.h"),
                                  "define CURL_MAX_WRITE_SIZE 16384",
                                  "define CURL_MAX_WRITE_SIZE 10485760")

        # https://github.com/curl/curl/issues/2835
        # for additional info, see this comment https://github.com/conan-io/conan-center-index/pull/1008#discussion_r386122685
        if self.settings.compiler == "apple-clang" and self.settings.compiler.version == "9.1":
            if self.options.with_ssl == "darwinssl":
                tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "vtls", "sectransp.c"),
                                      "#define CURL_BUILD_MAC_10_13 MAC_OS_X_VERSION_MAX_ALLOWED >= 101300",
                                      "#define CURL_BUILD_MAC_10_13 0")

    def _patch_mingw_files(self):
        if not self._is_mingw:
            return
        # patch for zlib naming in mingw
        if self.options.with_zlib:
            configure_ac = os.path.join(self._source_subfolder, "configure.ac")
            zlib_name = self.deps_cpp_info["zlib"].libs[0]
            tools.replace_in_file(configure_ac,
                                  "AC_CHECK_LIB(z,",
                                  "AC_CHECK_LIB({},".format(zlib_name))
            tools.replace_in_file(configure_ac,
                                  "-lz ",
                                  "-l{} ".format(zlib_name))

        if self.options.shared:
            # for mingw builds - do not compile curl tool, just library
            # linking errors are much harder to fix than to exclude curl tool
            top_makefile = os.path.join(self._source_subfolder, "Makefile.am")
            tools.replace_in_file(top_makefile, "SUBDIRS = lib src", "SUBDIRS = lib")
            tools.replace_in_file(top_makefile, "include src/Makefile.inc", "")
            # patch for shared mingw build
            lib_makefile = os.path.join(self._source_subfolder, "lib", "Makefile.am")
            tools.replace_in_file(lib_makefile,
                                  "noinst_LTLIBRARIES = libcurlu.la",
                                  "")
            tools.replace_in_file(lib_makefile,
                                  "noinst_LTLIBRARIES =",
                                  "")
            tools.replace_in_file(lib_makefile,
                                  "lib_LTLIBRARIES = libcurl.la",
                                  "noinst_LTLIBRARIES = libcurl.la")
            # add directives to build dll
            # used only for native mingw-make
            if not tools.cross_building(self.settings):
                added_content = tools.load("lib_Makefile_add.am")
                tools.save(lib_makefile, added_content, append=True)

    def _patch_cmake(self):
        if not self._is_using_cmake_build:
            return
        # Custom findZstd.cmake file relies on pkg-config file, make sure that it's consumed on all platforms
        if self._has_zstd_option:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMake", "FindZstd.cmake"),
                                  "if(UNIX)", "if(TRUE)")
        # TODO: check this patch, it's suspicious
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "include(CurlSymbolHiding)", "")

    def _get_configure_command_args(self):
        yes_no = lambda v: "yes" if v else "no"
        params = [
            "--with-libidn2={}".format(yes_no(self.options.with_libidn)),
            "--with-librtmp={}".format(yes_no(self.options.with_librtmp)),
            "--with-libmetalink={}".format(yes_no(self.options.with_libmetalink)),
            "--with-libpsl={}".format(yes_no(self.options.with_libpsl)),
            "--with-schannel={}".format(yes_no(self.options.with_ssl == "schannel")),
            "--with-secure-transport={}".format(yes_no(self.options.with_ssl == "darwinssl")),
            "--with-brotli={}".format(yes_no(self.options.with_brotli)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-ldap={}".format(yes_no(self.options.with_ldap)),
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-ares={}".format(yes_no(self.options.with_c_ares)),
            "--enable-threaded-resolver={}".format(yes_no(self.options.with_c_ares)),
        ]
        if self.options.with_ssl == "openssl":
            params.append("--with-ssl={}".format(tools.unix_path(self.deps_cpp_info["openssl"].rootpath)))
        else:
            params.append("--without-ssl")
        if self.options.with_ssl == "wolfssl":
            params.append("--with-wolfssl={}".format(tools.unix_path(self.deps_cpp_info["wolfssl"].rootpath)))
        else:
            params.append("--without-wolfssl")

        if self.options.with_libssh2:
            params.append("--with-libssh2={}".format(tools.unix_path(self.deps_cpp_info["libssh2"].rootpath)))
        else:
            params.append("--without-libssh2")

        if self.options.with_nghttp2:
            params.append("--with-nghttp2={}".format(tools.unix_path(self.deps_cpp_info["libnghttp2"].rootpath)))
        else:
            params.append("--without-nghttp2")

        if self.options.with_zlib:
            params.append("--with-zlib={}".format(tools.unix_path(self.deps_cpp_info["zlib"].rootpath)))
        else:
            params.append("--without-zlib")

        if self._has_zstd_option:
            params.append("--with-zstd={}".format(yes_no(self.options.with_zstd)))

        # Cross building flags
        if tools.cross_building(self.settings):
            if self.settings.os == "Linux" and "arm" in self.settings.arch:
                params.append("--host=%s" % self._get_linux_arm_host())
            elif self.settings.os == "iOS":
                params.append("--enable-threaded-resolver")
                params.append("--disable-verbose")
            elif self.settings.os == "Android":
                pass # this just works, conan is great!

        return params

    def _get_linux_arm_host(self):
        arch = None
        if self.settings.os == "Linux":
            arch = "arm-linux-gnu"
            # aarch64 could be added by user
            if "aarch64" in self.settings.arch:
                arch = "aarch64-linux-gnu"
            elif "arm" in self.settings.arch and "hf" in self.settings.arch:
                arch = "arm-linux-gnueabihf"
            elif "arm" in self.settings.arch and self._arm_version(str(self.settings.arch)) > 4:
                arch = "arm-linux-gnueabi"
        return arch

    # TODO, this should be a inner fuction of _get_linux_arm_host since it is only used from there
    # it should not polute the class namespace, since there are iOS and Android arm aritectures also
    def _arm_version(self, arch):
        version = None
        match = re.match(r"arm\w*(\d)", arch)
        if match:
            version = int(match.group(1))
        return version

    def _build_with_autotools(self):
        with tools.chdir(self._source_subfolder):
            # autoreconf
            self.run("{} -fiv".format(tools.get_env("AUTORECONF") or "autoreconf"), win_bash=tools.os_info.is_windows, run_environment=True)

            # fix generated autotools files on alle to have relocateable binaries
            if tools.is_apple_os(self.settings.os):
                tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name ")

            self.run("chmod +x configure")

            # run configure with *LD_LIBRARY_PATH env vars it allows to pick up shared openssl
            with tools.run_environment(self):
                autotools, autotools_vars = self._configure_autotools()
                autotools.make(vars=autotools_vars)

    def _configure_autotools_vars(self):
        autotools_vars = self._autotools.vars
        # tweaks for mingw
        if self._is_mingw:
            autotools_vars["RCFLAGS"] = "-O COFF"
            if self.settings.arch == "x86":
                autotools_vars["RCFLAGS"] += " --target=pe-i386"
            else:
                autotools_vars["RCFLAGS"] += " --target=pe-x86-64"
        return autotools_vars

    def _configure_autotools(self):
        if self._autotools and self._autotools_vars:
            return self._autotools, self._autotools_vars

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        if self.settings.os != "Windows":
            self._autotools.fpic = self.options.get_safe("fPIC", True)

        self._autotools_vars = self._configure_autotools_vars()

        # tweaks for mingw
        if self._is_mingw:
            self._autotools.defines.append("_AMD64_")

        if tools.cross_building(self) and tools.is_apple_os(self.settings.os):
            self._autotools.defines.extend(['HAVE_SOCKET', 'HAVE_FCNTL_O_NONBLOCK'])

        configure_args = self._get_configure_command_args()

        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            # please do not autodetect --build for the iOS simulator, thanks!
            self._autotools.configure(vars=self._autotools_vars, args=configure_args, build=False)
        else:
            self._autotools.configure(vars=self._autotools_vars, args=configure_args)

        return self._autotools, self._autotools_vars

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        if self._is_win_x_android:
            self._cmake = CMake(self, generator="Ninja")
        else:
            self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_CURL_EXE"] = False
        self._cmake.definitions["CURL_DISABLE_LDAP"] = not self.options.with_ldap
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["CURL_STATICLIB"] = not self.options.shared
        self._cmake.definitions["CMAKE_DEBUG_POSTFIX"] = ""
        if tools.Version(self.version) >= "7.72.0":
            self._cmake.definitions["CMAKE_USE_SCHANNEL"] = self.options.with_ssl == "schannel"
        else:
            self._cmake.definitions["CMAKE_USE_WINSSL"] = self.options.with_ssl == "schannel"
        self._cmake.definitions["CMAKE_USE_OPENSSL"] = self.options.with_ssl == "openssl"
        if tools.Version(self.version) >= "7.70.0":
            self._cmake.definitions["CMAKE_USE_WOLFSSL"] = self.options.with_ssl == "wolfssl"
        self._cmake.definitions["USE_NGHTTP2"] = self.options.with_nghttp2
        self._cmake.definitions["CURL_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["CURL_BROTLI"] = self.options.with_brotli
        if self._has_zstd_option:
            self._cmake.definitions["CURL_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["CMAKE_USE_LIBSSH2"] = self.options.with_libssh2
        self._cmake.definitions["ENABLE_ARES"] = self.options.with_c_ares

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _build_with_cmake(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("cacert.pem", dst="res")
        if self._is_using_cmake_build:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        else:
            with tools.run_environment(self):
                with tools.chdir(self._source_subfolder):
                    autotools, autotools_vars = self._configure_autotools()
                    autotools.install(vars=autotools_vars)
            tools.rmdir(os.path.join(self.package_folder, "share"))
            for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(la_file)
            if self._is_mingw and self.options.shared:
                # Handle only mingw libs
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
                self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                self.copy(pattern="*.lib", dst="lib", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CURL"
        self.cpp_info.names["cmake_find_package_multi"] = "CURL"
        self.cpp_info.names["pkg_config"] = "libcurl"
        self.cpp_info.components["curl"].names["cmake_find_package"] = "libcurl"
        self.cpp_info.components["curl"].names["cmake_find_package_multi"] = "libcurl"
        self.cpp_info.components["curl"].names["pkg_config"] = "libcurl"

        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["curl"].libs = ["libcurl_imp"] if self.options.shared else ["libcurl"]
        else:
            self.cpp_info.components["curl"].libs = ["curl"]
            if self.settings.os == "Linux":
                if self.options.with_libidn:
                    self.cpp_info.components["curl"].libs.append("idn")
                if self.options.with_librtmp:
                    self.cpp_info.components["curl"].libs.append("rtmp")

        if self.settings.os == "Linux":
            self.cpp_info.components["curl"].system_libs = ["rt", "pthread"]
        elif self.settings.os == "Windows":
            # used on Windows for VS build, native and cross mingw build
            self.cpp_info.components["curl"].system_libs = ["ws2_32"]
            if self.options.with_ldap:
                self.cpp_info.components["curl"].system_libs.append("wldap32")
            if self.options.with_ssl == "schannel":
                self.cpp_info.components["curl"].system_libs.append("crypt32")
        elif tools.is_apple_os(self.settings.os):
            if tools.Version(self.version) >= "7.77.0":
                self.cpp_info.components["curl"].frameworks.append("SystemConfiguration")
            if self.options.with_ldap:
                self.cpp_info.components["curl"].system_libs.append("ldap")
            if self.options.with_ssl == "darwinssl":
                self.cpp_info.components["curl"].frameworks.extend(["CoreFoundation", "Security"])

        if self._is_mingw:
            # provide pthread for dependent packages
            self.cpp_info.components["curl"].cflags.append("-pthread")
            self.cpp_info.components["curl"].exelinkflags.append("-pthread")
            self.cpp_info.components["curl"].sharedlinkflags.append("-pthread")

        if not self.options.shared:
            self.cpp_info.components["curl"].defines.append("CURL_STATICLIB=1")

        if self.options.with_ssl == "openssl":
            self.cpp_info.components["curl"].requires.append("openssl::openssl")
        if self.options.with_ssl == "wolfssl":
            self.cpp_info.components["curl"].requires.append("wolfssl::wolfssl")
        if self.options.with_nghttp2:
            self.cpp_info.components["curl"].requires.append("libnghttp2::libnghttp2")
        if self.options.with_libssh2:
            self.cpp_info.components["curl"].requires.append("libssh2::libssh2")
        if self.options.with_zlib:
            self.cpp_info.components["curl"].requires.append("zlib::zlib")
        if self.options.with_brotli:
            self.cpp_info.components["curl"].requires.append("brotli::brotli")
        if self.options.get_safe("with_zstd"):
            self.cpp_info.components["curl"].requires.append("zstd::zstd")
        if self.options.with_c_ares:
            self.cpp_info.components["curl"].requires.append("c-ares::c-ares")
