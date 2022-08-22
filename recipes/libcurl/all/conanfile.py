import glob
import os
import re
import functools
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, chdir, copy, download, get, load, replace_in_file, rmdir, save
from conan.tools.scm import Version
from conans import AutoToolsBuildEnvironment
# TODO: Update to conan.tools.apple after 1.51.3
from conans.tools import is_apple_os, get_env, os_info, run_environment, unix_path

required_conan_version = ">=1.50.0"


class LibcurlConan(ConanFile):
    name = "libcurl"
    description = "command line tool and library for transferring data with URLs"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://curl.haxx.se"
    topics = ("curl", "data-transfer",
            "ftp", "gopher", "http", "imap", "ldap", "mqtt", "pop3", "rtmp", "rtsp",
            "scp", "sftp", "smb", "smtp", "telnet", "tftp")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, "openssl", "wolfssl", "schannel", "darwinssl"],
        "with_file": [True, False],
        "with_ftp": [True, False],
        "with_http": [True, False],
        "with_ldap": [True, False],
        "with_rtsp": [True, False],
        "with_dict": [True, False],
        "with_telnet": [True, False],
        "with_tftp": [True, False],
        "with_pop3": [True, False],
        "with_imap": [True, False],
        "with_smb": [True, False],
        "with_smtp": [True, False],
        "with_gopher": [True, False],
        "with_mqtt": [True, False],
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
        "with_threaded_resolver": [True, False],
        "with_proxy": [True, False],
        "with_crypto_auth": [True, False],
        "with_ntlm": [True, False],
        "with_ntlm_wb": [True, False],
        "with_cookies": [True, False],
        "with_ipv6": [True, False],
        "with_docs": [True, False],
        "with_verbose_debug": [True, False],
        "with_symbol_hiding": [True, False],
        "with_unix_sockets": [True, False],
        "with_verbose_strings": [True, False],
        "with_ca_bundle": "ANY",
        "with_ca_path": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
        "with_dict": True,
        "with_file": True,
        "with_ftp": True,
        "with_gopher": True,
        "with_http": True,
        "with_imap": True,
        "with_ldap": False,
        "with_mqtt": True,
        "with_pop3": True,
        "with_rtsp": True,
        "with_smb": True,
        "with_smtp": True,
        "with_telnet": True,
        "with_tftp": True,
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
        "with_threaded_resolver": True,
        "with_proxy": True,
        "with_crypto_auth": True,
        "with_ntlm": True,
        "with_ntlm_wb": True,
        "with_cookies": True,
        "with_ipv6": True,
        "with_docs": False,
        "with_verbose_debug": True,
        "with_symbol_hiding": False,
        "with_unix_sockets": True,
        "with_verbose_strings": True,
        "with_ca_bundle": None,
        "with_ca_path": None,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _is_win_x_android(self):
        return self.settings.os == "Android" and os_info.is_windows

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_using_cmake_build(self):
        return is_msvc(self) or self._is_win_x_android

    @property
    def _has_zstd_option(self):
        return Version(self.version) >= "7.72.0"

    @property
    def _has_metalink_option(self):
        # Support for metalink was removed in version 7.78.0 https://github.com/curl/curl/pull/7176
        return Version(self.version) < "7.78.0" and not self._is_using_cmake_build

    def export_sources(self):
        copy(self, "lib_Makefile_add.am", self.recipe_folder, self.export_sources_folder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_zstd_option:
            del self.options.with_zstd
        if not self._has_metalink_option:
            del self.options.with_libmetalink
        # Default options
        self.options.with_ssl = "darwinssl" if is_apple_os(self.settings.os) else "openssl"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        # These options are not used in CMake build yet
        if self._is_using_cmake_build:
            if Version(self.version) < "7.75.0":
                del self.options.with_libidn
            del self.options.with_libpsl

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/5.3.0")
        if self.options.with_nghttp2:
            self.requires("libnghttp2/1.47.0")
        if self.options.with_libssh2:
            self.requires("libssh2/1.10.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.5.2")
        if self.options.with_c_ares:
            self.requires("c-ares/1.18.1")

    def validate(self):
        if self.options.with_ssl == "schannel" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("schannel only suppported on Windows.")
        if self.options.with_ssl == "darwinssl" and not is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("darwinssl only suppported on Apple like OS (Macos, iOS, watchOS or tvOS).")
        if self.options.with_ssl == "wolfssl" and self._is_using_cmake_build and Version(self.version) < "7.70.0":
            raise ConanInvalidConfiguration("Before 7.70.0, libcurl has no wolfssl support for Visual Studio or \"Windows to Android cross compilation\"")
        if self.options.with_ssl == "openssl":
            if self.options.with_ntlm and self.options["openssl"].no_des:
                raise ConanInvalidConfiguration("option with_ntlm=True requires openssl:no_des=False")

    def build_requirements(self):
        if self._is_using_cmake_build:
            if self._is_win_x_android:
                self.build_requires("ninja/1.11.0")
        else:
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        download(self, "https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=True)

    # TODO: remove imports once rpath of shared libs of libcurl dependencies fixed on macOS
    def imports(self):
        # Copy shared libraries for dependencies to fix DYLD_LIBRARY_PATH problems
        #
        # Configure script creates conftest that cannot execute without shared openssl binaries.
        # Ways to solve the problem:
        # 1. set *LD_LIBRARY_PATH (works with Linux with RunEnvironment
        #     but does not work on OS X 10.11 with SIP)
        # 2. copying dylib's to the build directory (fortunately works on OS X)
        if self.settings.os == "Macos":
            self.copy("*.dylib*", dst=self.source_folder, keep_path=False)

    def build(self):
        self._patch_sources()
        if self._is_using_cmake_build:
            self._build_with_cmake()
        else:
            self._build_with_autotools()

    def _patch_sources(self):
        apply_conandata_patches(self)
        self._patch_misc_files()
        self._patch_autotools()
        self._patch_cmake()

    def _patch_misc_files(self):
        if self.options.with_largemaxwritesize:
            replace_in_file(self, os.path.join(self.source_folder,
                "include", "curl", "curl.h"),
                "define CURL_MAX_WRITE_SIZE 16384",
                "define CURL_MAX_WRITE_SIZE 10485760")

        # https://github.com/curl/curl/issues/2835
        # for additional info, see this comment https://github.com/conan-io/conan-center-index/pull/1008#discussion_r386122685
        if self.settings.compiler == "apple-clang" and self.settings.compiler.version == "9.1":
            if self.options.with_ssl == "darwinssl":
                replace_in_file(self, os.path.join(self.source_folder,
                    "lib", "vtls", "sectransp.c"),
                    "#define CURL_BUILD_MAC_10_13 MAC_OS_X_VERSION_MAX_ALLOWED >= 101300",
                    "#define CURL_BUILD_MAC_10_13 0")

    def _patch_autotools(self):
        if self._is_using_cmake_build:
            return

        # Disable curl tool for these reasons:
        # - link errors if mingw shared or iOS/tvOS/watchOS
        # - it makes recipe consistent with CMake build where we don't build curl tool
        top_makefile = os.path.join(self.source_folder, "Makefile.am")
        replace_in_file(self, top_makefile, "SUBDIRS = lib src", "SUBDIRS = lib")
        replace_in_file(self, top_makefile, "include src/Makefile.inc", "")

        if self._is_mingw:
            # patch for zlib naming in mingw
            if self.options.with_zlib:
                configure_ac = os.path.join(self.source_folder, "configure.ac")
                zlib_name = self.deps_cpp_info["zlib"].libs[0]
                replace_in_file(self, configure_ac,
                                      "AC_CHECK_LIB(z,",
                                      "AC_CHECK_LIB({},".format(zlib_name))
                replace_in_file(self, configure_ac,
                                      "-lz ",
                                      "-l{} ".format(zlib_name))

            if self.options.shared:
                # patch for shared mingw build
                lib_makefile = os.path.join(self.source_folder, "lib", "Makefile.am")
                replace_in_file(self, lib_makefile,
                                      "noinst_LTLIBRARIES = libcurlu.la",
                                      "")
                replace_in_file(self, lib_makefile,
                                      "noinst_LTLIBRARIES =",
                                      "")
                replace_in_file(self, lib_makefile,
                                      "lib_LTLIBRARIES = libcurl.la",
                                      "noinst_LTLIBRARIES = libcurl.la")
                # add directives to build dll
                # used only for native mingw-make
                if not cross_building(self):
                    added_content = load(self, "lib_Makefile_add.am")
                    save(self, lib_makefile, added_content, append=True)

    def _patch_cmake(self):
        if not self._is_using_cmake_build:
            return
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Custom findZstd.cmake file relies on pkg-config file, make sure that it's consumed on all platforms
        if self._has_zstd_option:
            replace_in_file(self, os.path.join(self.source_folder, "CMake", "FindZstd.cmake"),
                                  "if(UNIX)", "if(TRUE)")
        # TODO: check this patch, it's suspicious
        replace_in_file(self, cmakelists,
                              "include(CurlSymbolHiding)", "")

        # libnghttp2
        replace_in_file(self,
            cmakelists,
            "find_package(NGHTTP2 REQUIRED)",
            "find_package(libnghttp2 REQUIRED)",
        )
        replace_in_file(self,
            cmakelists,
            "include_directories(${NGHTTP2_INCLUDE_DIRS})",
            "",
        )
        replace_in_file(self,
            cmakelists,
            "list(APPEND CURL_LIBS ${NGHTTP2_LIBRARIES})",
            "list(APPEND CURL_LIBS libnghttp2::nghttp2)",
        )

        # INTERFACE_LIBRARY (generated by the cmake_find_package generator) targets doesn't have the LOCATION property.
        # So skipp the LOCATION check in the CMakeLists.txt
        if Version(self.version) >= "7.80.0":
            replace_in_file(self,
                cmakelists,
                'get_target_property(_lib "${_libname}" LOCATION)',
                """get_target_property(_type "${_libname}" TYPE)
    if(${_type} STREQUAL "INTERFACE_LIBRARY")
      # Reading the INTERFACE_LIBRARY property on non-imported target will error out.
      continue()
    endif()
    get_target_property(_lib "${_libname}" LOCATION)""",
            )

    def _get_configure_command_args(self):
        yes_no = lambda v: "yes" if v else "no"
        params = [
            "--with-libidn2={}".format(yes_no(self.options.with_libidn)),
            "--with-librtmp={}".format(yes_no(self.options.with_librtmp)),
            "--with-libpsl={}".format(yes_no(self.options.with_libpsl)),
            "--with-schannel={}".format(yes_no(self.options.with_ssl == "schannel")),
            "--with-secure-transport={}".format(yes_no(self.options.with_ssl == "darwinssl")),
            "--with-brotli={}".format(yes_no(self.options.with_brotli)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-dict={}".format(yes_no(self.options.with_dict)),
            "--enable-file={}".format(yes_no(self.options.with_file)),
            "--enable-ftp={}".format(yes_no(self.options.with_ftp)),
            "--enable-gopher={}".format(yes_no(self.options.with_gopher)),
            "--enable-http={}".format(yes_no(self.options.with_http)),
            "--enable-imap={}".format(yes_no(self.options.with_imap)),
            "--enable-ldap={}".format(yes_no(self.options.with_ldap)),
            "--enable-mqtt={}".format(yes_no(self.options.with_mqtt)),
            "--enable-pop3={}".format(yes_no(self.options.with_pop3)),
            "--enable-rtsp={}".format(yes_no(self.options.with_rtsp)),
            "--enable-smb={}".format(yes_no(self.options.with_smb)),
            "--enable-smtp={}".format(yes_no(self.options.with_smtp)),
            "--enable-telnet={}".format(yes_no(self.options.with_telnet)),
            "--enable-tftp={}".format(yes_no(self.options.with_tftp)),
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-ares={}".format(yes_no(self.options.with_c_ares)),
            "--enable-threaded-resolver={}".format(yes_no(self.options.with_threaded_resolver)),
            "--enable-cookies={}".format(yes_no(self.options.with_cookies)),
            "--enable-ipv6={}".format(yes_no(self.options.with_ipv6)),
            "--enable-manual={}".format(yes_no(self.options.with_docs)),
            "--enable-verbose={}".format(yes_no(self.options.with_verbose_debug)),
            "--enable-symbol-hiding={}".format(yes_no(self.options.with_symbol_hiding)),
            "--enable-unix-sockets={}".format(yes_no(self.options.with_unix_sockets)),
        ]
        if self.options.with_ssl == "openssl":
            params.append("--with-ssl={}".format(unix_path(self.deps_cpp_info["openssl"].rootpath)))
        else:
            params.append("--without-ssl")
        if self.options.with_ssl == "wolfssl":
            params.append("--with-wolfssl={}".format(unix_path(self.deps_cpp_info["wolfssl"].rootpath)))
        else:
            params.append("--without-wolfssl")

        if self.options.with_libssh2:
            params.append("--with-libssh2={}".format(unix_path(self.deps_cpp_info["libssh2"].rootpath)))
        else:
            params.append("--without-libssh2")

        if self.options.with_nghttp2:
            params.append("--with-nghttp2={}".format(unix_path(self.deps_cpp_info["libnghttp2"].rootpath)))
        else:
            params.append("--without-nghttp2")

        if self.options.with_zlib:
            params.append("--with-zlib={}".format(unix_path(self.deps_cpp_info["zlib"].rootpath)))
        else:
            params.append("--without-zlib")

        if self._has_zstd_option:
            params.append("--with-zstd={}".format(yes_no(self.options.with_zstd)))

        if self._has_metalink_option:
            params.append("--with-libmetalink={}".format(yes_no(self.options.with_libmetalink)))

        if not self.options.with_proxy:
            params.append("--disable-proxy")

        if not self.options.with_rtsp:
            params.append("--disable-rtsp")

        if not self.options.with_crypto_auth:
            params.append("--disable-crypto-auth") # also disables NTLM in versions of curl prior to 7.78.0

        # ntlm will default to enabled if any SSL options are enabled
        if not self.options.with_ntlm:
            if Version(self.version) <= "7.77.0":
                params.append("--disable-crypto-auth")
            else:
                params.append("--disable-ntlm")

        if not self.options.with_ntlm_wb:
            params.append("--disable-ntlm-wb")

        if self.options.with_ca_bundle == False:
            params.append("--without-ca-bundle")
        elif self.options.with_ca_bundle:
            params.append("--with-ca-bundle=" + str(self.options.with_ca_bundle))

        if self.options.with_ca_path == False:
            params.append('--without-ca-path')
        elif self.options.with_ca_path:
            params.append("--with-ca-path=" + str(self.options.with_ca_path))

        # Cross building flags
        if cross_building(self):
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
        with chdir(self, self.source_folder):
            # autoreconf
            self.run("{} -fiv".format(get_env("AUTORECONF") or "autoreconf"), win_bash=os_info.is_windows, run_environment=True)

            # fix generated autotools files to have relocatable binaries
            if is_apple_os(self.settings.os):
                replace_in_file(self, "configure", "-install_name \\$rpath/", "-install_name @rpath/")

            self.run("chmod +x configure")

            # run configure with *LD_LIBRARY_PATH env vars it allows to pick up shared openssl
            with run_environment(self):
                autotools, autotools_vars = self._configure_autotools()
                autotools.make(vars=autotools_vars)

    def _configure_autotools_vars(self):
        autotools_vars = {}
        # tweaks for mingw
        if self._is_mingw:
            autotools_vars["RCFLAGS"] = "-O COFF"
            if self.settings.arch == "x86":
                autotools_vars["RCFLAGS"] += " --target=pe-i386"
            else:
                autotools_vars["RCFLAGS"] += " --target=pe-x86-64"
        return autotools_vars

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=os_info.is_windows)

        if self.settings.os != "Windows":
            autotools.fpic = self.options.get_safe("fPIC", True)

        autotools_vars = self._configure_autotools_vars()

        # tweaks for mingw
        if self._is_mingw:
            autotools.defines.append("_AMD64_")

        if cross_building(self) and is_apple_os(self.settings.os):
            autotools.defines.extend(['HAVE_SOCKET', 'HAVE_FCNTL_O_NONBLOCK'])

        configure_args = self._get_configure_command_args()

        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            # please do not autodetect --build for the iOS simulator, thanks!
            autotools.configure(vars=autotools_vars, args=configure_args, build=False)
        else:
            autotools.configure(vars=autotools_vars, args=configure_args)

        return autotools, autotools_vars

    def generate(self):
        if self._is_win_x_android:
            tc = CMakeToolchain(self, generator="Ninja")
        else:
            tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_CURL_EXE"] = False
        tc.variables["CURL_DISABLE_LDAP"] = not self.options.with_ldap
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["CURL_STATICLIB"] = not self.options.shared
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_SCHANNEL"] = self.options.with_ssl == "schannel"
        elif Version(self.version) >= "7.72.0":
            tc.variables["CMAKE_USE_SCHANNEL"] = self.options.with_ssl == "schannel"
        else:
            tc.variables["CMAKE_USE_WINSSL"] = self.options.with_ssl == "schannel"
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_OPENSSL"] = self.options.with_ssl == "openssl"
        else:
            tc.variables["CMAKE_USE_OPENSSL"] = self.options.with_ssl == "openssl"
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_WOLFSSL"] = self.options.with_ssl == "wolfssl"
        elif Version(self.version) >= "7.70.0":
            tc.variables["CMAKE_USE_WOLFSSL"] = self.options.with_ssl == "wolfssl"
        tc.variables["USE_NGHTTP2"] = self.options.with_nghttp2
        tc.variables["CURL_ZLIB"] = self.options.with_zlib
        tc.variables["CURL_BROTLI"] = self.options.with_brotli
        if self._has_zstd_option:
            tc.variables["CURL_ZSTD"] = self.options.with_zstd
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_LIBSSH2"] = self.options.with_libssh2
        else:
            tc.variables["CMAKE_USE_LIBSSH2"] = self.options.with_libssh2
        tc.variables["ENABLE_ARES"] = self.options.with_c_ares
        if not self.options.with_c_ares:
            tc.variables["ENABLE_THREADED_RESOLVER"] = self.options.with_threaded_resolver
        tc.variables["CURL_DISABLE_PROXY"] = not self.options.with_proxy
        tc.variables["USE_LIBRTMP"] = self.options.with_librtmp
        if Version(self.version) >= "7.75.0":
            tc.variables["USE_LIBIDN2"] = self.options.with_libidn
        tc.variables["CURL_DISABLE_RTSP"] = not self.options.with_rtsp
        tc.variables["CURL_DISABLE_CRYPTO_AUTH"] = not self.options.with_crypto_auth
        tc.variables["CURL_DISABLE_VERBOSE_STRINGS"] = not self.options.with_verbose_strings

        # Also disables NTLM_WB if set to false
        if not self.options.with_ntlm:
            if Version(self.version) <= "7.77.0":
                tc.variables["CURL_DISABLE_CRYPTO_AUTH"] = True
            else:
                tc.variables["CURL_DISABLE_NTLM"] = True
        tc.variables["NTLM_WB_ENABLED"] = self.options.with_ntlm_wb

        if self.options.with_ca_bundle == False:
            tc.variables['CURL_CA_BUNDLE'] = 'none'
        elif self.options.with_ca_bundle:
            tc.variables['CURL_CA_BUNDLE'] = self.options.with_ca_bundle

        if self.options.with_ca_path == False:
            tc.variables['CURL_CA_PATH'] = 'none'
        elif self.options.with_ca_path:
            tc.variables['CURL_CA_PATH'] = self.options.with_ca_path

        tc.generate()

    def _build_with_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        self.copy("cacert.pem", dst="res")
        if self._is_using_cmake_build:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            with run_environment(self):
                with chdir(self, self.source_folder):
                    autotools, autotools_vars = self._configure_autotools()
                    autotools.install(vars=autotools_vars)
            rmdir(self, os.path.join(self.package_folder, "share"))
            for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(la_file)
            if self._is_mingw and self.options.shared:
                # Handle only mingw libs
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
                self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                self.copy(pattern="*.lib", dst="lib", keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CURL")
        self.cpp_info.set_property("cmake_target_name", "CURL::libcurl")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "libcurl")

        if is_msvc(self):
            self.cpp_info.components["curl"].libs = ["libcurl_imp"] if self.options.shared else ["libcurl"]
        else:
            self.cpp_info.components["curl"].libs = ["curl"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                if self.options.with_libidn:
                    self.cpp_info.components["curl"].libs.append("idn")
                if self.options.with_librtmp:
                    self.cpp_info.components["curl"].libs.append("rtmp")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["curl"].system_libs = ["rt", "pthread"]
        elif self.settings.os == "Windows":
            # used on Windows for VS build, native and cross mingw build
            self.cpp_info.components["curl"].system_libs = ["ws2_32"]
            if self.options.with_ldap:
                self.cpp_info.components["curl"].system_libs.append("wldap32")
            if self.options.with_ssl == "schannel":
                self.cpp_info.components["curl"].system_libs.append("crypt32")
        elif is_apple_os(self.settings.os):
            if Version(self.version) >= "7.77.0":
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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CURL"
        self.cpp_info.names["cmake_find_package_multi"] = "CURL"
        self.cpp_info.components["curl"].names["cmake_find_package"] = "libcurl"
        self.cpp_info.components["curl"].names["cmake_find_package_multi"] = "libcurl"
        self.cpp_info.components["curl"].set_property("cmake_target_name", "CURL::libcurl")
        self.cpp_info.components["curl"].set_property("pkg_config_name", "libcurl")
