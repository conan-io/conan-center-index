from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, download, get, load, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
# TODO: Migrate
from conans.tools import get_env

import os
import re

required_conan_version = ">=1.51.3"


class LibcurlConan(ConanFile):
    name = "libcurl"
    description = "command line tool and library for transferring data with URLs"
    license = "curl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://curl.se"
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
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_win_x_android(self):
        return self.settings.os == "Android" and self._settings_build.os == "Windows"

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
        if Version(self.version) < "7.10.4":
            self.license = "MIT"
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_zstd_option:
            del self.options.with_zstd
        if not self._has_metalink_option:
            del self.options.with_libmetalink
        # Default options
        self.options.with_ssl = "darwinssl" if is_apple_os(self) else "openssl"

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
            self.requires("wolfssl/5.4.0")
        if self.options.with_nghttp2:
            self.requires("libnghttp2/1.48.0")
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
        if self.options.with_ssl == "darwinssl" and not is_apple_os(self):
            raise ConanInvalidConfiguration("darwinssl only suppported on Apple like OS (Macos, iOS, watchOS or tvOS).")
        if self.options.with_ssl == "wolfssl" and self._is_using_cmake_build and Version(self.version) < "7.70.0":
            raise ConanInvalidConfiguration("Before 7.70.0, libcurl has no wolfssl support for Visual Studio or \"Windows to Android cross compilation\"")
        if self.options.with_ssl == "openssl":
            if self.options.with_ntlm and self.options["openssl"].no_des:
                raise ConanInvalidConfiguration("option with_ntlm=True requires openssl:no_des=False")

    def build_requirements(self):
        if self._is_using_cmake_build:
            if self._is_win_x_android:
                self.tool_requires("ninja/1.11.0")
        else:
            self.tool_requires("libtool/2.4.6")
            self.tool_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not get_env("CONAN_BASH_PATH") and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        download(self, "https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=True, sha256="6ed95025fba2aef0ce7b647607225745624497f876d74ef6ec22b26e73e9de77")

    def generate(self):
        if self._is_using_cmake_build:
            self._generate_with_cmake()
        else:
            self._generate_with_autotools()
        ms = VirtualBuildEnv(self)
        ms.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

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
            copy(self, "*.dylib*", src=self.build_folder, dst=self.source_folder, keep_path=False)

    def build(self):
        self._patch_sources()
        if self._is_using_cmake_build:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def _patch_sources(self):
        apply_conandata_patches(self)
        self._patch_misc_files()
        self._patch_autotools()
        self._patch_cmake()

    def _patch_misc_files(self):
        if self.options.with_largemaxwritesize:
            replace_in_file(self, os.path.join(self.source_folder, "include", "curl", "curl.h"),
                                  "define CURL_MAX_WRITE_SIZE 16384",
                                  "define CURL_MAX_WRITE_SIZE 10485760")

        # https://github.com/curl/curl/issues/2835
        # for additional info, see this comment https://github.com/conan-io/conan-center-index/pull/1008#discussion_r386122685
        if self.settings.compiler == "apple-clang" and self.settings.compiler.version == "9.1":
            if self.options.with_ssl == "darwinssl":
                replace_in_file(self, os.path.join(self.source_folder, "lib", "vtls", "sectransp.c"),
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
                                      f"AC_CHECK_LIB({zlib_name}")
                replace_in_file(self, configure_ac,
                                      "-lz ",
                                      f"-l{zlib_name}")

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

    def _yes_no(self, value):
        return "yes" if value else "no"

    def _generate_with_autotools(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--with-libidn2={self._yes_no(self.options.with_libidn)}",
            f"--with-librtmp={self._yes_no(self.options.with_librtmp)}",
            f"--with-libpsl={self._yes_no(self.options.with_libpsl)}",
            f"--with-schannel={self._yes_no(self.options.with_ssl == 'schannel')}",
            f"--with-secure-transport={self._yes_no(self.options.with_ssl == 'darwinssl')}",
            f"--with-brotli={self._yes_no(self.options.with_brotli)}",
            f"--enable-shared={self._yes_no(self.options.shared)}",
            f"--enable-static={self._yes_no(not self.options.shared)}",
            f"--enable-dict={self._yes_no(self.options.with_dict)}",
            f"--enable-file={self._yes_no(self.options.with_file)}",
            f"--enable-ftp={self._yes_no(self.options.with_ftp)}",
            f"--enable-gopher={self._yes_no(self.options.with_gopher)}",
            f"--enable-http={self._yes_no(self.options.with_http)}",
            f"--enable-imap={self._yes_no(self.options.with_imap)}",
            f"--enable-ldap={self._yes_no(self.options.with_ldap)}",
            f"--enable-mqtt={self._yes_no(self.options.with_mqtt)}",
            f"--enable-pop3={self._yes_no(self.options.with_pop3)}",
            f"--enable-rtsp={self._yes_no(self.options.with_rtsp)}",
            f"--enable-smb={self._yes_no(self.options.with_smb)}",
            f"--enable-smtp={self._yes_no(self.options.with_smtp)}",
            f"--enable-telnet={self._yes_no(self.options.with_telnet)}",
            f"--enable-tftp={self._yes_no(self.options.with_tftp)}",
            f"--enable-debug={self._yes_no(self.settings.build_type == 'Debug')}",
            f"--enable-ares={self._yes_no(self.options.with_c_ares)}",
            f"--enable-threaded-resolver={self._yes_no(self.options.with_threaded_resolver)}",
            f"--enable-cookies={self._yes_no(self.options.with_cookies)}",
            f"--enable-ipv6={self._yes_no(self.options.with_ipv6)}",
            f"--enable-manual={self._yes_no(self.options.with_docs)}",
            f"--enable-verbose={self._yes_no(self.options.with_verbose_debug)}",
            f"--enable-symbol-hiding={self._yes_no(self.options.with_symbol_hiding)}",
            f"--enable-unix-sockets={self._yes_no(self.options.with_unix_sockets)}",
        ])
        if self.options.with_ssl == "openssl":
            path = unix_path(self, self.deps_cpp_info["openssl"].rootpath)
            tc.configure_args.append(f"--with-ssl={path}")
        else:
            tc.configure_args.append("--without-ssl")
        if self.options.with_ssl == "wolfssl":
            path = unix_path(self, self.deps_cpp_info["wolfssl"].rootpath)
            tc.configure_args.append(f"--with-wolfssl={path}")
        else:
            tc.configure_args.append("--without-wolfssl")

        if self.options.with_libssh2:
            path = unix_path(self, self.deps_cpp_info["libssh2"].rootpath)
            tc.configure_args.append(f"--with-libssh2={path}")
        else:
            tc.configure_args.append("--without-libssh2")

        if self.options.with_nghttp2:
            path = unix_path(self, self.deps_cpp_info["libnghttp2"].rootpath)
            tc.configure_args.append(f"--with-nghttp2={path}")
        else:
            tc.configure_args.append("--without-nghttp2")

        if self.options.with_zlib:
            path = unix_path(self, self.deps_cpp_info["zlib"].rootpath)
            tc.configure_args.append(f"--with-zlib={path}")
        else:
            tc.configure_args.append("--without-zlib")

        if self._has_zstd_option:
            tc.configure_args.append(f"--with-zstd={self._yes_no(self.options.with_zstd)}")

        if self._has_metalink_option:
            tc.configure_args.append(f"--with-libmetalink={self._yes_no(self.options.with_libmetalink)}")

        if not self.options.with_proxy:
            tc.configure_args.append("--disable-proxy")

        if not self.options.with_rtsp:
            tc.configure_args.append("--disable-rtsp")

        if not self.options.with_crypto_auth:
            tc.configure_args.append("--disable-crypto-auth") # also disables NTLM in versions of curl prior to 7.78.0

        # ntlm will default to enabled if any SSL options are enabled
        if not self.options.with_ntlm:
            if Version(self.version) <= "7.77.0":
                tc.configure_args.append("--disable-crypto-auth")
            else:
                tc.configure_args.append("--disable-ntlm")

        if not self.options.with_ntlm_wb:
            tc.configure_args.append("--disable-ntlm-wb")

        if self.options.with_ca_bundle is False:
            tc.configure_args.append("--without-ca-bundle")
        elif self.options.with_ca_bundle:
            tc.configure_args.append("--with-ca-bundle=" + str(self.options.with_ca_bundle))

        if self.options.with_ca_path is False:
            tc.configure_args.append('--without-ca-path')
        elif self.options.with_ca_path:
            tc.configure_args.append("--with-ca-path=" + str(self.options.with_ca_path))

        # Cross building flags
        if cross_building(self):
            if self.settings.os == "Linux" and "arm" in self.settings.arch:
                tc.configure_args.append(f"--host={self._get_linux_arm_host()}")
            elif self.settings.os == "iOS":
                tc.configure_args.append("--enable-threaded-resolver")
                tc.configure_args.append("--disable-verbose")
            elif self.settings.os == "Android":
                pass # this just works, conan is great!

        # tweaks for mingw
        if self._is_mingw:
            rcflags = "-O COFF"
            if self.settings.arch == "x86":
                rcflags += " --target=pe-i386"
            else:
                rcflags += " --target=pe-x86-64"
            env = tc.environment()
            env.define("RCFLAGS", rcflags)

            tc.extra_defines.append("_AMD64_")

        if self.settings.os != "Windows":
            tc.fpic = self.options.get_safe("fPIC", True)


        if cross_building(self) and is_apple_os(self):
            tc.extra_defines.extend(['HAVE_SOCKET', 'HAVE_FCNTL_O_NONBLOCK'])

        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()


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

    def _generate_with_cmake(self):
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

        if self.options.with_ca_bundle is False:
            tc.variables['CURL_CA_BUNDLE'] = 'none'
        elif self.options.with_ca_bundle:
            tc.variables['CURL_CA_BUNDLE'] = self.options.with_ca_bundle

        if self.options.with_ca_path is False:
            tc.variables['CURL_CA_PATH'] = 'none'
        elif self.options.with_ca_path:
            tc.variables['CURL_CA_PATH'] = self.options.with_ca_path

        tc.generate()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="cacert.pem", src=self.build_folder, dst="res")
        if self._is_using_cmake_build:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            autotools = Autotools(self)
            autotools.install()
            fix_apple_shared_install_name(self)
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            if self._is_mingw and self.options.shared:
                # Handle only mingw libs
                copy(self, pattern="*.dll", src=self.build_folder, dst="bin", keep_path=False)
                copy(self, pattern="*.dll.a", src=self.build_folder, dst="lib", keep_path=False)
                copy(self, pattern="*.lib", src=self.build_folder, dst="lib", keep_path=False)
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
        elif is_apple_os(self):
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
