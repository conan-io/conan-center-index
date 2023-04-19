from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, download, export_conandata_patches, get, load, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

import os
import re

required_conan_version = ">=1.54.0"


class LibcurlConan(ConanFile):
    name = "libcurl"
    description = "command line tool and library for transferring data with URLs"
    license = "curl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://curl.se"
    topics = ("curl", "data-transfer",
            "ftp", "gopher", "http", "imap", "ldap", "mqtt", "pop3", "rtmp", "rtsp",
            "scp", "sftp", "smb", "smtp", "telnet", "tftp")
    package_type = "library"
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
        "with_libgsasl": [True, False],
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
        "with_ca_bundle": [False, "auto", "ANY"],
        "with_ca_path": [False, "auto", "ANY"],
        "with_ca_fallback": [True, False],
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
        "with_libgsasl": False,
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
        "with_ca_bundle": "auto",
        "with_ca_path": "auto",
        "with_ca_fallback": False,
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
    def _has_metalink_option(self):
        # Support for metalink was removed in version 7.78.0 https://github.com/curl/curl/pull/7176
        return Version(self.version) < "7.78.0" and not self._is_using_cmake_build

    @property
    def _has_with_libpsl_option(self):
        return not (self._is_using_cmake_build and Version(self.version) < "7.84.0")

    def export_sources(self):
        copy(self, "lib_Makefile_add.am", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_metalink_option:
            del self.options.with_libmetalink
        if not self._has_with_libpsl_option:
            del self.options.with_libpsl
        if self._is_using_cmake_build:
            del self.options.with_libgsasl

        # Before 7.86.0, enabling unix sockets configure option would fail on windows
        # It was fixed with this PR: https://github.com/curl/curl/pull/9688
        if self._is_mingw and Version(self.version) < "7.86.0":
            del self.options.with_unix_sockets

        # Default options
        self.options.with_ssl = "darwinssl" if is_apple_os(self) else "openssl"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        if self._is_using_cmake_build:
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/3.1.0")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/5.5.1")
        if self.options.with_nghttp2:
            self.requires("libnghttp2/1.51.0")
        if self.options.with_libssh2:
            self.requires("libssh2/1.10.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_c_ares:
            self.requires("c-ares/1.19.0")
        if self.options.get_safe("with_libpsl"):
            self.requires("libpsl/0.21.1")

    def validate(self):
        if self.options.with_ssl == "schannel" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("schannel only suppported on Windows.")
        if self.options.with_ssl == "darwinssl" and not is_apple_os(self):
            raise ConanInvalidConfiguration("darwinssl only suppported on Apple like OS (Macos, iOS, watchOS or tvOS).")
        if self.options.with_ssl == "openssl":
            openssl = self.dependencies["openssl"]
            if self.options.with_ntlm and openssl.options.no_des:
                raise ConanInvalidConfiguration("option with_ntlm=True requires openssl:no_des=False")

    def build_requirements(self):
        if self._is_using_cmake_build:
            if self._is_win_x_android:
                self.tool_requires("ninja/1.11.1")
        else:
            self.tool_requires("libtool/2.4.7")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")
            if self.settings.os in [ "tvOS", "watchOS" ]:
                self.tool_requires("gnu-config/cci.20210814")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        download(self, "https://curl.se/ca/cacert-2023-01-10.pem", "cacert.pem", verify=True, sha256="fb1ecd641d0a02c01bc9036d513cb658bbda62a75e246bedbc01764560a639f0")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if self._is_using_cmake_build:
            self._generate_with_cmake()
        else:
            self._generate_with_autotools()

    def build(self):
        self._patch_sources()
        if self._is_using_cmake_build:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            # autoreconf is caalled with "--force" which regenerate all files.
            # Because we want to use a patched config.sub for tvOS/watchOS, we
            # need to call this patch after autoreconf.
            self._patch_autoreconf()
            autotools.configure()
            autotools.make()

    def _patch_autoreconf(self):
        # Fix config.sub for tvOS/watchOS
        if self.settings.os in [ "tvOS", "watchOS" ]:
            for gnu_config in [
                    self.conf.get("user.gnu-config:config_guess", check_type=str),
                    self.conf.get("user.gnu-config:config_sub", check_type=str),
            ]:
                if gnu_config:
                    copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)

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

        # zlib naming is not always very consistent
        if self.options.with_zlib:
            configure_ac = os.path.join(self.source_folder, "configure.ac")
            zlib_name = self.dependencies["zlib"].cpp_info.aggregated_components().libs[0]
            replace_in_file(self, configure_ac,
                                  "AC_CHECK_LIB(z,",
                                  f"AC_CHECK_LIB({zlib_name},")
            replace_in_file(self, configure_ac,
                                  "-lz ",
                                  f"-l{zlib_name} ")

        if self._is_mingw and self.options.shared:
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
                # The patch file is located in the base src folder
                added_content = load(self, os.path.join(self.folders.base_source, "lib_Makefile_add.am"))
                save(self, lib_makefile, added_content, append=True)

    def _patch_cmake(self):
        if not self._is_using_cmake_build:
            return
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # TODO: check this patch, it's suspicious
        replace_in_file(self, cmakelists,
                              "include(CurlSymbolHiding)", "")

        # brotli
        replace_in_file(self, cmakelists, "find_package(Brotli QUIET)", "find_package(brotli REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "if(BROTLI_FOUND)", "if(brotli_FOUND)")
        replace_in_file(self, cmakelists, "${BROTLI_LIBRARIES}", "brotli::brotli")
        replace_in_file(self, cmakelists, "${BROTLI_INCLUDE_DIRS}", "${brotli_INCLUDE_DIRS}")

        # zstd
        # Use upstream FindZstd.cmake because check_symbol_exists() is called
        # afterwards and it would fail with zstd_LIBRARIES generated by CMakeDeps
        replace_in_file(self, cmakelists, "find_package(Zstd REQUIRED)", "find_package(Zstd REQUIRED MODULE)")
        replace_in_file(self, os.path.join(self.source_folder, "CMake", "FindZstd.cmake"), "if(UNIX)", "if(0)")

        # c-ares
        replace_in_file(self, cmakelists, "find_package(CARES REQUIRED)", "find_package(c-ares REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "${CARES_LIBRARY}", "c-ares::cares")

        # libpsl
        if self._has_with_libpsl_option:
            replace_in_file(self, cmakelists, "find_package(LibPSL)", "find_package(libpsl REQUIRED CONFIG)")
            replace_in_file(self, cmakelists, "if(LIBPSL_FOUND)", "if(libpsl_FOUND)")
            replace_in_file(self, cmakelists, "${LIBPSL_LIBRARY}", "libpsl::libpsl")
            replace_in_file(self, cmakelists, "${LIBPSL_INCLUDE_DIR}", "${libpsl_INCLUDE_DIRS}")

        # libssh2
        replace_in_file(self, cmakelists, "find_package(LibSSH2)", "find_package(Libssh2 REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "if(LIBSSH2_FOUND)", "if(Libssh2_FOUND)")
        replace_in_file(self, cmakelists, "${LIBSSH2_LIBRARY}", "Libssh2::libssh2")
        replace_in_file(self, cmakelists, "${LIBSSH2_INCLUDE_DIR}", "${Libssh2_INCLUDE_DIRS}")

        # libnghttp2
        replace_in_file(self, cmakelists, "find_package(NGHTTP2 REQUIRED)", "find_package(libnghttp2 REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "${NGHTTP2_INCLUDE_DIRS}", "${libnghttp2_INCLUDE_DIRS}")
        replace_in_file(self, cmakelists, "${NGHTTP2_LIBRARIES}", "libnghttp2::nghttp2")

        # wolfssl
        replace_in_file(self, cmakelists, "find_package(WolfSSL REQUIRED)", "find_package(wolfssl REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "${WolfSSL_LIBRARIES}", "${wolfssl_LIBRARIES}")
        replace_in_file(self, cmakelists, "${WolfSSL_INCLUDE_DIRS}", "${wolfssl_INCLUDE_DIRS}")

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
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--with-libidn2={self._yes_no(self.options.with_libidn)}",
            f"--with-librtmp={self._yes_no(self.options.with_librtmp)}",
            f"--with-libpsl={self._yes_no(self.options.with_libpsl)}",
            f"--with-libgsasl={self._yes_no(self.options.with_libgsasl)}",
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
            f"--enable-unix-sockets={self._yes_no(self.options.get_safe('with_unix_sockets'))}",
            f"--with-zstd={self._yes_no(self.options.with_zstd)}",
        ])

        # Since 7.77.0, disabling TLS must be explicitly requested otherwise it fails
        if Version(self.version) >= "7.77.0" and not self.options.with_ssl:
            tc.configure_args.append("--without-ssl")

        openssl_option = "ssl" if Version(self.version) < "7.77.0" else "openssl"
        if self.options.with_ssl == "openssl":
            path = unix_path(self, self.dependencies["openssl"].package_folder)
            tc.configure_args.append(f"--with-{openssl_option}={path}")
        else:
            tc.configure_args.append(f"--without-{openssl_option}")

        if self.options.with_ssl == "wolfssl":
            path = unix_path(self, self.dependencies["wolfssl"].package_folder)
            tc.configure_args.append(f"--with-wolfssl={path}")
        else:
            tc.configure_args.append("--without-wolfssl")

        if self.options.with_libssh2:
            path = unix_path(self, self.dependencies["libssh2"].package_folder)
            tc.configure_args.append(f"--with-libssh2={path}")
        else:
            tc.configure_args.append("--without-libssh2")

        if self.options.with_nghttp2:
            path = unix_path(self, self.dependencies["libnghttp2"].package_folder)
            tc.configure_args.append(f"--with-nghttp2={path}")
        else:
            tc.configure_args.append("--without-nghttp2")

        if self.options.with_zlib:
            path = unix_path(self, self.dependencies["zlib"].package_folder)
            tc.configure_args.append(f"--with-zlib={path}")
        else:
            tc.configure_args.append("--without-zlib")

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

        if not self.options.with_ca_bundle:
            tc.configure_args.append("--without-ca-bundle")
        elif self.options.with_ca_bundle != "auto":
            tc.configure_args.append(f"--with-ca-bundle={str(self.options.with_ca_bundle)}")

        if not self.options.with_ca_path:
            tc.configure_args.append("--without-ca-path")
        elif self.options.with_ca_path != "auto":
            tc.configure_args.append(f"--with-ca-path={str(self.options.with_ca_path)}")

        tc.configure_args.append(f"--with-ca-fallback={self._yes_no(self.options.with_ca_fallback)}")

        # Cross building flags
        if cross_building(self):
            if self.settings.os == "Linux" and "arm" in self.settings.arch:
                tc.configure_args.append(f"--host={self._get_linux_arm_host()}")
            elif self.settings.os == "iOS":
                tc.configure_args.append("--enable-threaded-resolver")
                tc.configure_args.append("--disable-verbose")
            elif self.settings.os == "Android":
                pass # this just works, conan is great!

        env = tc.environment()

        # tweaks for mingw
        if self._is_mingw:
            rcflags = "-O COFF"
            if self.settings.arch == "x86":
                rcflags += " --target=pe-i386"
            elif self.settings.arch == "x86_64":
                rcflags += " --target=pe-x86-64"
                tc.extra_defines.append("_AMD64_")
            env.define("RCFLAGS", rcflags)

        if self.settings.os != "Windows":
            tc.fpic = self.options.get_safe("fPIC", True)


        if cross_building(self) and is_apple_os(self):
            tc.extra_defines.extend(['HAVE_SOCKET', 'HAVE_FCNTL_O_NONBLOCK'])

        tc.generate(env)
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
        tc.variables["ENABLE_UNICODE"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_CURL_EXE"] = False
        tc.variables["CURL_DISABLE_LDAP"] = not self.options.with_ldap
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["CURL_STATICLIB"] = not self.options.shared
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_SCHANNEL"] = self.options.with_ssl == "schannel"
        else:
            tc.variables["CMAKE_USE_SCHANNEL"] = self.options.with_ssl == "schannel"
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_OPENSSL"] = self.options.with_ssl == "openssl"
        else:
            tc.variables["CMAKE_USE_OPENSSL"] = self.options.with_ssl == "openssl"
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_WOLFSSL"] = self.options.with_ssl == "wolfssl"
        else:
            tc.variables["CMAKE_USE_WOLFSSL"] = self.options.with_ssl == "wolfssl"
        tc.variables["USE_NGHTTP2"] = self.options.with_nghttp2
        tc.variables["CURL_ZLIB"] = self.options.with_zlib
        tc.variables["CURL_BROTLI"] = self.options.with_brotli
        tc.variables["CURL_ZSTD"] = self.options.with_zstd
        if self._has_with_libpsl_option:
            tc.variables["CURL_USE_LIBPSL"] = self.options.with_libpsl
        if Version(self.version) >= "7.81.0":
            tc.variables["CURL_USE_LIBSSH2"] = self.options.with_libssh2
        else:
            tc.variables["CMAKE_USE_LIBSSH2"] = self.options.with_libssh2
        tc.variables["ENABLE_ARES"] = self.options.with_c_ares
        if not self.options.with_c_ares:
            tc.variables["ENABLE_THREADED_RESOLVER"] = self.options.with_threaded_resolver
        tc.variables["CURL_DISABLE_PROXY"] = not self.options.with_proxy
        tc.variables["USE_LIBRTMP"] = self.options.with_librtmp
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

        if self.options.with_ca_bundle:
            tc.cache_variables["CURL_CA_BUNDLE"] = str(self.options.with_ca_bundle)
        else:
            tc.cache_variables["CURL_CA_BUNDLE"] = "none"

        if self.options.with_ca_path:
            tc.cache_variables["CURL_CA_PATH"] = str(self.options.with_ca_path)
        else:
            tc.cache_variables["CURL_CA_PATH"] = "none"

        tc.cache_variables["CURL_CA_FALLBACK"] = self.options.with_ca_fallback

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "cacert.pem", src=self.source_folder, dst=os.path.join(self.package_folder, "res"))
        if self._is_using_cmake_build:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            if self._is_mingw and self.options.shared:
                # Handle only mingw libs
                copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
                copy(self, pattern="*.dll.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
                copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CURL")
        self.cpp_info.set_property("cmake_target_name", "CURL::libcurl")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "libcurl")

        self.cpp_info.components["curl"].resdirs = ["res"]
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
            if Version(self.version) >= "7.78.0" or self.options.with_ssl == "darwinssl":
                self.cpp_info.components["curl"].frameworks.append("CoreFoundation")
            if Version(self.version) >= "7.77.0":
                self.cpp_info.components["curl"].frameworks.append("SystemConfiguration")
            if self.options.with_ldap:
                self.cpp_info.components["curl"].system_libs.append("ldap")
            if self.options.with_ssl == "darwinssl":
                self.cpp_info.components["curl"].frameworks.append("Security")

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
        if self.options.with_zstd:
            self.cpp_info.components["curl"].requires.append("zstd::zstd")
        if self.options.with_c_ares:
            self.cpp_info.components["curl"].requires.append("c-ares::c-ares")
        if self.options.get_safe("with_libpsl"):
            self.cpp_info.components["curl"].requires.append("libpsl::libpsl")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CURL"
        self.cpp_info.names["cmake_find_package_multi"] = "CURL"
        self.cpp_info.components["curl"].names["cmake_find_package"] = "libcurl"
        self.cpp_info.components["curl"].names["cmake_find_package_multi"] = "libcurl"
        self.cpp_info.components["curl"].set_property("cmake_target_name", "CURL::libcurl")
        self.cpp_info.components["curl"].set_property("pkg_config_name", "libcurl")
