from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException, ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibwebsocketsConan(ConanFile):
    name = "libwebsockets"
    description = "Canonical libwebsockets.org websocket library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/warmcat/libwebsockets"
    license = "MIT"
    topics = ("libwebsockets", "websocket")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libuv": [True, False],
        "with_libevent": [False, "libevent", "libev"],
        "with_zlib": [False, "zlib", "miniz", "bundled"],
        "with_ssl": [False, "openssl", "mbedtls", "wolfssl"],
        "with_sqlite3": [True, False],
        "with_libmount": [True, False],
        "with_hubbub": [True, False],
        "ssl_client_use_os_ca_certs": [True, False],                            # SSL support should make use of the OS-installed CA root certs
        "ssl_server_with_ecdh_cert": [True, False],                             # Include SSL server use ECDH certificate

        "enable_network": [True, False],                                        # Compile with network-related code
        "role_h1": [True, False],                                               # Compile with support for http/1 (needed for ws)
        "role_ws": [True, False],                                               # Compile with support for websockets
        "role_mqtt": [True, False],                                             # Build with support for MQTT client
        "role_dbus": [True, False],                                             # Compile with support for DBUS
        "role_raw_proxy": [True, False],                                        # Raw packet proxy
        "role_raw_file": [True, False],                                         # Compile with support for raw files
        "enable_http2": [True, False],                                          # Compile with server support for HTTP/2
        "enable_lwsws": [True, False],                                          # Libwebsockets Webserver
        "enable_cgi": [True, False],                                            # Include CGI (spawn process with network-connected stdin/out/err) APIs
        "enable_ipv6": [True, False],                                           # Compile with support for ipv6
        "enable_unix_sock": [True, False],                                      # Compile with support for UNIX domain socket
        "enable_plugins": [True, False],                                        # Support plugins for protocols and extensions
        "enable_http_proxy": [True, False],                                     # Support for active HTTP proxying
        "enable_zip_fops": [True, False],                                       # Support serving pre-zipped files
        "enable_socks5": [True, False],                                         # Allow use of SOCKS5 proxy on client connections
        "enable_generic_sessions": [True, False],                               # With the Generic Sessions plugin
        "enable_peer_limits": [True, False],                                    # Track peers and restrict resources a single peer can allocate
        "enable_access_log": [True, False],                                     # Support generating Apache-compatible access logs
        "enable_ranges": [True, False],                                         # Support http ranges (RFC7233)
        "enable_server_status": [True, False],                                  # Support json + jscript server monitoring
        "enable_threadpool": [True, False],                                     # Managed worker thread pool support (relies on pthreads)
        "enable_http_stream_compression": [True, False],                        # Support HTTP stream compression
        "enable_http_brotli": [True, False],                                    # Also offer brotli http stream compression (requires LWS_WITH_HTTP_STREAM_COMPRESSION)
        "enable_acme": [True, False],                                           # Enable support for ACME automatic cert acquisition + maintenance (letsencrypt etc)
        "enable_fts": [True, False],                                            # Full Text Search support
        "enable_sys_async_dns": [True, False],                                  # Nonblocking internal IPv4 + IPv6 DNS resolver
        "enable_sys_ntpclient": [True, False],                                  # Build in tiny ntpclient good for tls date validation and run via lws_system
        "enable_sys_dhcp_client": [True, False],                                # Build in tiny DHCP client
        "enable_http_basic_auth": [True, False],                                # Support Basic Auth
        "enable_http_uncommon_headers": [True, False],                          # Include less common http header support
        "enable_secure_streams": [True, False],                                 # Secure Streams protocol-agnostic API
        "enable_secure_streams_proxy_api": [True, False],                       # Secure Streams support to work across processes
        "enable_secure_streams_sys_auth_api_amazon_com": [True, False],         # Auth support for api.amazon.com
        "enable_secure_streams_static_policy_only": [True, False],

        "without_client": [True, False],                                        # Don't build the client part of the library
        "without_server": [True, False],                                        # Don't build the server part of the library

        "enable_extensions": [True, False],                                     # Compile with extensions
        "enable_builtin_getifaddrs": [True, False],                             # Use the BSD getifaddrs implementation from libwebsockets if it is missing (this will result in a compilation error) ... The default is to assume that your libc provides it. On some systems such as uclibc it doesn't exist.
        "enable_fallback_gethostbyname": [True, False],                         # Also try to do dns resolution using gethostbyname if getaddrinfo fails
        "enable_builtin_sha1": [True, False],                                   # Build the lws sha-1 (eg, because openssl will provide it
        "enable_daemonize": [True, False],                                      # Build the daemonization api
        "enable_lejp": [True, False],                                           # With the Lightweight JSON Parser
        "enable_struct_json": [True, False],                                    # Generic struct serialization to and from JSON
        "enable_struct_sqlite3": [True, False],                                 # Generic struct serialization to and from SQLITE3

        "disable_logs": [True, False],                                          # Disable all logging other than _err and _user from being compiled in
        "logs_timestamp": [True, False],                                        # Timestamp at start of logs
        "avoid_sigpipe_ign": [True, False],                                     # Android 7+ reportedly needs this
        "enable_stats": [True, False],                                          # Keep statistics of lws internal operations
        "enable_jose": [True, False],                                           # JSON Web Signature / Encryption / Keys (RFC7515/6/) API
        "enable_gencrypto": [True, False],                                      # Enable support for Generic Crypto apis independent of TLS backend
        "enable_selftests": [True, False],                                      # Selftests run at context creation
        "enable_gcov": [True, False],                                           # Build with gcc gcov coverage instrumentation
        "enable_lwsac": [True, False],                                          # lwsac Chunk Allocation api
        "enable_custom_headers": [True, False],                                 # Store and allow querying custom HTTP headers (H1 only)
        "enable_diskcache": [True, False],                                      # Hashed cache directory with lazy LRU deletion to size limit
        "enable_dir": [True, False],                                            # Directory scanning api support
        "enable_lejp_conf": [True, False],                                      # With LEJP configuration parser as used by lwsws
        "enable_deprecated_lws_dll": [True, False],                             # Migrate to lws_dll2 instead ASAP
        "enable_sequencer": [True, False],                                      # lws_seq_t support
        "enable_external_poll": [True, False],                                  # Support external POLL integration using callback messages (not recommended)
        "enable_lws_dsh": [True, False],                                        # Support lws_dsh_t Disordered Shared Heap
        "enable_external_http_proxying": [True, False],                         # Support external http proxies for client connections
        "enable_file_ops": [True, False],                                       # Support file operations vfs
        "enable_detailed_latency": [True, False],                               # Record detailed latency stats for each read and write
        "enable_udp": [True, False],                                            # Platform supports UDP
        "enable_spawn": [True, False],                                          # Spawn subprocesses with piped stdin/out/stderr
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libuv": False,
        "with_libevent": False,
        "with_zlib": False,
        "with_ssl": "openssl",
        "with_sqlite3": False,
        "with_libmount": False,
        "with_hubbub": False,

        "ssl_client_use_os_ca_certs": True,
        "ssl_server_with_ecdh_cert": False,

        "enable_network": True,
        "role_h1": True,
        "role_ws": True,
        "role_mqtt": False,
        "role_dbus": False,
        "role_raw_proxy": False,
        "role_raw_file": True,
        "enable_http2": True,
        "enable_lwsws": False,
        "enable_cgi": False,
        "enable_ipv6": False,
        "enable_unix_sock": True,
        "enable_plugins": False,
        "enable_http_proxy": False,
        "enable_zip_fops": False,
        "enable_socks5": False,
        "enable_generic_sessions": False,
        "enable_peer_limits": False,
        "enable_access_log": False,
        "enable_ranges": False,
        "enable_server_status": False,
        "enable_threadpool": False,
        "enable_http_stream_compression": False,
        "enable_http_brotli": False,
        "enable_acme": False,
        "enable_fts": False,
        "enable_sys_async_dns": False,
        "enable_sys_ntpclient": False,
        "enable_sys_dhcp_client": False,
        "enable_http_basic_auth": True,
        "enable_http_uncommon_headers": True,
        "enable_secure_streams": False,
        "enable_secure_streams_proxy_api": False,
        "enable_secure_streams_sys_auth_api_amazon_com": False,
        "enable_secure_streams_static_policy_only": False,

        "without_client": False,
        "without_server": False,

        "enable_extensions": False,
        "enable_builtin_getifaddrs": True,
        "enable_fallback_gethostbyname": False,
        "enable_builtin_sha1": True,
        "enable_daemonize": False,
        "enable_lejp": True,
        "enable_struct_json": False,
        "enable_struct_sqlite3": False,

        "disable_logs": False,
        "logs_timestamp": True,
        "avoid_sigpipe_ign": False,
        "enable_stats": False,
        "enable_jose": False,
        "enable_gencrypto": False,
        "enable_selftests": False,
        "enable_gcov": False,
        "enable_lwsac": True,
        "enable_custom_headers": True,
        "enable_diskcache": False,
        "enable_dir": False,
        "enable_lejp_conf": False,
        "enable_deprecated_lws_dll": False,
        "enable_sequencer": True,
        "enable_external_poll": False,
        "enable_lws_dsh": False,
        "enable_external_http_proxying": True,
        "enable_file_ops": True,
        "enable_detailed_latency": False,
        "enable_udp": True,
        "enable_spawn": False
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_libuv:
            self.requires("libuv/1.44.1")

        if self.options.with_libevent == "libevent":
            self.requires("libevent/2.1.12")
        elif self.options.with_libevent == "libev":
            self.requires("libev/4.33")

        if self.options.with_zlib == "zlib":
            self.requires("zlib/1.2.12")
        elif self.options.with_zlib == "miniz":
            self.requires("miniz/2.2.0")

        if self.options.with_libmount:
            self.requires("libmount/2.36.2")

        if self.options.with_sqlite3:
            self.requires("sqlite3/3.37.2")

        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1o")
        elif self.options.with_ssl == "mbedtls":
            self.requires("mbedtls/2.25.0")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/4.8.1")

    def validate(self):
        if self.options.shared and self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            # https://github.com/conan-io/conan-center-index/pull/5321#issuecomment-826367276
            raise ConanInvalidConfiguration("{}/{} shared=True with gcc<5 does not build. Please submit a PR with a fix.".format(self.name, self.version))
        if tools.Version(self.version) <= "4.0.15" and self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) >= "12":
            raise ConanInvalidConfiguration("{}/{} with apple-clang>=12 does not build. Please submit a PR with a fix.".format(self.name, self.version))
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < 16 and tools.Version(self.version) >= "4.3.2":
            raise ConanInvalidConfiguration ("{}/{} requires at least Visual Studio 2019".format(self.name, self.version))

        if self.options.with_hubbub:
            raise ConanInvalidConfiguration("Library hubbub not implemented (yet) in CCI")
            # TODO - Add hubbub package when available.

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _get_library_extension(self, dep):
        if self.options[dep].shared:
            if self.settings.os == "Windows" :
                if self._is_msvc:
                    return ".lib"
                else:
                    return ".dll.a"
            elif self.settings.os == "Macos":
                return ".dylib"
            else:
                return ".so"
        else:
            if self.settings.os == "Windows" and self._is_msvc:
                return ".lib"
            else:
                return ".a"

    @property
    def _get_library_prefix(self):
        if self.settings.os == "Windows" :
            return ""
        return "lib"

    def _cmakify_path_list(self, paths):
        return ";".join(paths).replace("\\", "/")

    def _find_library(self, libname, dep):
        for path in self.deps_cpp_info[dep].lib_paths:
            lib_fullpath = os.path.join(path, self._get_library_prefix + libname + self._get_library_extension(dep))

            print("Test : " + str(lib_fullpath))
            if os.path.isfile(lib_fullpath):
                return lib_fullpath
        raise ConanException("Library {} not found".format(lib_fullpath))

    def _find_libraries(self, dep):
        return [self._find_library(lib, dep) for lib in self.deps_cpp_info[dep].libs]

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["LWS_WITHOUT_TESTAPPS"] = True
        self._cmake.definitions["LWS_WITHOUT_TEST_SERVER"] = True
        self._cmake.definitions["LWS_WITHOUT_TEST_SERVER_EXTPOLL"] = True
        self._cmake.definitions["LWS_WITHOUT_TEST_PING"] = True
        self._cmake.definitions["LWS_WITHOUT_TEST_CLIENT"] = True

        self._cmake.definitions["LWS_LINK_TESTAPPS_DYNAMIC"] = True
        self._cmake.definitions["LWS_WITH_SHARED"] = self.options.shared
        self._cmake.definitions["LWS_WITH_STATIC"] = not self.options.shared
        self._cmake.definitions["LWS_WITH_SSL"] = bool(self.options.with_ssl)

        if self.options.with_ssl == "openssl":
            self._cmake.definitions["LWS_OPENSSL_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("openssl"))
            self._cmake.definitions["LWS_OPENSSL_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["openssl"].include_paths)
        elif self.options.with_ssl == "mbedtls":
            self._cmake.definitions["LWS_WITH_MBEDTLS"] = True
            self._cmake.definitions["LWS_MBEDTLS_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("mbedtls"))
            self._cmake.definitions["LWS_MBEDTLS_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["mbedtls"].include_paths)
        elif self.options.with_ssl == "wolfssl":
            self._cmake.definitions["LWS_WITH_WOLFSSL"] = True
            self._cmake.definitions["LWS_WOLFSSL_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("wolfssl"))
            self._cmake.definitions["LWS_WOLFSSL_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["wolfssl"].include_paths)
        else:
            self._cmake.definitions["LWS_WITH_WOLFSSL"] = False

        self._cmake.definitions["LWS_WITH_LIBEV"] = self.options.with_libevent == "libev"
        if self.options.with_libevent == "libev":
            self._cmake.definitions["LWS_LIBEV_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("libev"))
            self._cmake.definitions["LWS_LIBEV_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["libev"].include_paths).replace("\\", "/")

        self._cmake.definitions["LWS_WITH_LIBUV"] = self.options.with_libuv
        if self.options.with_libuv:
            self._cmake.definitions["LWS_LIBUV_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("libuv"))
            self._cmake.definitions["LWS_LIBUV_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["libuv"].include_paths)

        self._cmake.definitions["LWS_WITH_LIBEVENT"] = self.options.with_libevent == "libevent"
        if self.options.with_libevent == "libevent":
            self._cmake.definitions["LWS_LIBEVENT_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("libevent"))
            self._cmake.definitions["LWS_LIBEVENT_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["libevent"].include_paths)

        self._cmake.definitions["LWS_WITH_ZLIB"] = self.options.with_zlib != False
        self._cmake.definitions["LWS_WITH_MINIZ"] = self.options.with_zlib == "miniz"
        self._cmake.definitions["LWS_WITH_BUNDLED_ZLIB"] = self.options.with_zlib == "bundled"
        if self.options.with_zlib == "zlib":
            self._cmake.definitions["LWS_ZLIB_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("zlib"))
            self._cmake.definitions["LWS_ZLIB_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["zlib"].include_paths)
        elif self.options.with_zlib == "miniz":
            self._cmake.definitions["MINIZ_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("miniz"))
            self._cmake.definitions["MINIZ_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["miniz"].include_paths)

        self._cmake.definitions["LWS_WITH_SQLITE3"] = self.options.with_sqlite3
        if self.options.with_sqlite3:
            self._cmake.definitions["LWS_SQLITE3_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("sqlite3"))
            self._cmake.definitions["LWS_SQLITE3_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["sqlite3"].include_paths)

        self._cmake.definitions["LWS_WITH_FSMOUNT"] = self.options.with_libmount
        if self.options.with_libmount:
            self._cmake.definitions["LWS_LIBMOUNT_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("libmount"))
            self._cmake.definitions["LWS_LIBMOUNT_INCLUDE_DIRS"] = self._cmakify_path_list(self.deps_cpp_info["libmount"].include_paths)

        self._cmake.definitions["LWS_WITH_HUBBUB"] = self.options.with_hubbub

        self._cmake.definitions["LWS_SSL_CLIENT_USE_OS_CA_CERTS"] = self.options.ssl_client_use_os_ca_certs
        self._cmake.definitions["LWS_SSL_SERVER_WITH_ECDH_CERT"] = self.options.ssl_server_with_ecdh_cert

        self._cmake.definitions["LWS_WITH_NETWORK"] = self.options.enable_network
        self._cmake.definitions["LWS_ROLE_H1"] = self.options.role_h1
        self._cmake.definitions["LWS_ROLE_WS"] = self.options.role_ws
        self._cmake.definitions["LWS_ROLE_MQTT"] = self.options.role_mqtt
        self._cmake.definitions["LWS_ROLE_DBUS"] = self.options.role_dbus
        self._cmake.definitions["LWS_ROLE_RAW_PROXY"] = self.options.role_raw_proxy
        self._cmake.definitions["LWS_ROLE_RAW_FILE"] = self.options.role_raw_file
        self._cmake.definitions["LWS_WITH_HTTP2"] = self.options.enable_http2
        self._cmake.definitions["LWS_WITH_LWSWS"] = self.options.enable_lwsws
        self._cmake.definitions["LWS_WITH_CGI"] = self.options.enable_cgi
        self._cmake.definitions["LWS_IPV6"] = self.options.enable_ipv6
        self._cmake.definitions["LWS_UNIX_SOCK"] = self.options.enable_unix_sock
        self._cmake.definitions["LWS_WITH_PLUGINS"] = self.options.enable_plugins
        self._cmake.definitions["LWS_WITH_HTTP_PROXY"] = self.options.enable_http_proxy
        self._cmake.definitions["LWS_WITH_ZIP_FOPS"] = self.options.enable_zip_fops
        self._cmake.definitions["LWS_WITH_SOCKS5"] = self.options.enable_socks5
        self._cmake.definitions["LWS_WITH_GENERIC_SESSIONS"] = self.options.enable_generic_sessions
        self._cmake.definitions["LWS_WITH_PEER_LIMITS"] = self.options.enable_peer_limits
        self._cmake.definitions["LWS_WITH_ACCESS_LOG"] = self.options.enable_access_log
        self._cmake.definitions["LWS_WITH_RANGES"] = self.options.enable_ranges
        self._cmake.definitions["LWS_WITH_SERVER_STATUS"] = self.options.enable_server_status
        self._cmake.definitions["LWS_WITH_THREADPOOL"] = self.options.enable_threadpool
        self._cmake.definitions["LWS_WITH_HTTP_STREAM_COMPRESSION"] = self.options.enable_http_stream_compression
        self._cmake.definitions["LWS_WITH_HTTP_BROTLI"] = self.options.enable_http_brotli
        self._cmake.definitions["LWS_WITH_ACME"] = self.options.enable_acme
        self._cmake.definitions["LWS_WITH_FTS"] = self.options.enable_fts
        self._cmake.definitions["LWS_WITH_SYS_ASYNC_DNS"] = self.options.enable_sys_async_dns
        self._cmake.definitions["LWS_WITH_SYS_NTPCLIENT"] = self.options.enable_sys_ntpclient
        self._cmake.definitions["LWS_WITH_SYS_DHCP_CLIENT"] = self.options.enable_sys_dhcp_client
        self._cmake.definitions["LWS_WITH_HTTP_BASIC_AUTH"] = self.options.enable_http_basic_auth
        self._cmake.definitions["LWS_WITH_HTTP_UNCOMMON_HEADERS"] = self.options.enable_http_uncommon_headers

        self._cmake.definitions["LWS_WITHOUT_EXTENSIONS"] = not self.options.enable_extensions
        self._cmake.definitions["LWS_WITHOUT_BUILTIN_GETIFADDRS"] = not self.options.enable_builtin_getifaddrs
        self._cmake.definitions["LWS_FALLBACK_GETHOSTBYNAME"] = self.options.enable_fallback_gethostbyname
        self._cmake.definitions["LWS_WITHOUT_BUILTIN_SHA1"] = not self.options.enable_builtin_sha1
        self._cmake.definitions["LWS_WITHOUT_DAEMONIZE"] = not self.options.enable_daemonize
        self._cmake.definitions["LWS_WITH_LEJP"] = self.options.enable_lejp
        self._cmake.definitions["LWS_WITH_STRUCT_JSON"] = self.options.enable_struct_json
        self._cmake.definitions["LWS_WITH_STRUCT_SQLITE3"] = self.options.enable_struct_sqlite3

        self._cmake.definitions["LWS_WITH_NO_LOGS"] = self.options.disable_logs
        self._cmake.definitions["LWS_LOGS_TIMESTAMP"] = self.options.logs_timestamp
        self._cmake.definitions["LWS_AVOID_SIGPIPE_IGN"] = self.options.avoid_sigpipe_ign
        self._cmake.definitions["LWS_WITH_STATS"] = self.options.enable_stats
        self._cmake.definitions["LWS_WITH_JOSE"] = self.options.enable_jose
        self._cmake.definitions["LWS_WITH_GENCRYPTO"] = self.options.enable_gencrypto
        self._cmake.definitions["LWS_WITH_SELFTESTS"] = self.options.enable_selftests
        self._cmake.definitions["LWS_WITH_GCOV"] = self.options.enable_gcov
        self._cmake.definitions["LWS_WITH_LWSAC"] = self.options.enable_lwsac
        self._cmake.definitions["LWS_WITH_CUSTOM_HEADERS"] = self.options.enable_custom_headers
        self._cmake.definitions["LWS_WITH_DISKCACHE"] = self.options.enable_diskcache
        self._cmake.definitions["LWS_WITH_DIR"] = self.options.enable_dir
        self._cmake.definitions["LWS_WITH_LEJP_CONF"] = self.options.enable_lejp_conf
        self._cmake.definitions["LWS_WITH_DEPRECATED_LWS_DLL"] = self.options.enable_deprecated_lws_dll
        self._cmake.definitions["LWS_WITH_SEQUENCER"] = self.options.enable_sequencer
        self._cmake.definitions["LWS_WITH_EXTERNAL_POLL"] = self.options.enable_external_poll
        self._cmake.definitions["LWS_WITH_LWS_DSH"] = self.options.enable_lws_dsh
        self._cmake.definitions["LWS_CLIENT_HTTP_PROXYING"] = self.options.enable_external_http_proxying
        self._cmake.definitions["LWS_WITH_FILE_OPS"] = self.options.enable_file_ops
        self._cmake.definitions["LWS_WITH_DETAILED_LATENCY"] = self.options.enable_detailed_latency
        self._cmake.definitions["LWS_WITH_UDP"] = self.options.enable_udp
        self._cmake.definitions["LWS_WITH_SPAWN"] = self.options.enable_spawn

        self._cmake.definitions["LWS_WITH_ALSA"] = False
        self._cmake.definitions["LWS_WITH_GTK"] = False

        if tools.Version(self.version) >= "4.1.0":
            self._cmake.definitions["LWS_WITH_SYS_SMD"] = self.settings.os != "Windows"
            self._cmake.definitions["DISABLE_WERROR"] = True

        # Temporary override Windows 10 SDK for Visual Studio 2019, see issue #4450
        # CCI worker has 10.0.17763.0 SDK installed alongside with 10.0.20348 but only 20348 can be used with Visual Studio 2019
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) == 16:
            self._cmake.definitions["CMAKE_SYSTEM_VERSION"] = "10.0.20348"

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.files.replace_in_file(self, 
            cmakelists,
            "SET(CMAKE_INSTALL_NAME_DIR \"${CMAKE_INSTALL_PREFIX}/${LWS_INSTALL_LIB_DIR}${LIB_SUFFIX}\")",
            "",
        )
        if tools.Version(self.version) == "4.0.15" and self.options.with_ssl:
            tools.files.replace_in_file(self, 
                cmakelists,
                "list(APPEND LIB_LIST ws2_32.lib userenv.lib psapi.lib iphlpapi.lib)",
                "list(APPEND LIB_LIST ws2_32.lib userenv.lib psapi.lib iphlpapi.lib crypt32.lib)"
            )
        if tools.Version(self.version) < "4.1.0":
            tools.files.replace_in_file(self, cmakelists, "-Werror", "")
        if tools.Version(self.version) >= "4.1.4":
            tools.files.replace_in_file(self, cmakelists, "add_compile_options(/W3 /WX)", "add_compile_options(/W3)")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._cmake_target: "Libwebsockets::{}".format(self._cmake_target)}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _cmake_target(self):
        return "websockets_shared" if self.options.shared else "websockets"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Libwebsockets")
        self.cpp_info.set_property("cmake_target_name", self._cmake_target)
        pkgconfig_name = "libwebsockets" if self.options.shared else "libwebsockets_static"
        self.cpp_info.set_property("pkg_config_name", pkgconfig_name)
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_libwebsockets"].libs = tools.files.collect_libs(self, self)
        if self.settings.os == "Windows":
            self.cpp_info.components["_libwebsockets"].system_libs.extend(["ws2_32", "crypt32"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_libwebsockets"].system_libs.extend(["dl", "m"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Libwebsockets"
        self.cpp_info.names["cmake_find_package_multi"] = "Libwebsockets"
        self.cpp_info.names["pkg_config"] = pkgconfig_name
        self.cpp_info.components["_libwebsockets"].names["cmake_find_package"] = self._cmake_target
        self.cpp_info.components["_libwebsockets"].names["cmake_find_package_multi"] = self._cmake_target
        self.cpp_info.components["_libwebsockets"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["_libwebsockets"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["_libwebsockets"].builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.components["_libwebsockets"].set_property("cmake_target_name", self._cmake_target)
        self.cpp_info.components["_libwebsockets"].set_property("pkg_config_name", pkgconfig_name)
        if self.options.with_libuv:
            self.cpp_info.components["_libwebsockets"].requires.append("libuv::libuv")
        if self.options.with_libevent == "libevent":
            self.cpp_info.components["_libwebsockets"].requires.append("libevent::libevent")
        elif self.options.with_libevent == "libev":
            self.cpp_info.components["_libwebsockets"].requires.append("libev::libev")
        if self.options.with_zlib == "zlib":
            self.cpp_info.components["_libwebsockets"].requires.append("zlib::zlib")
        elif self.options.with_zlib == "miniz":
            self.cpp_info.components["_libwebsockets"].requires.append("miniz::miniz")
        if self.options.with_libmount:
            self.cpp_info.components["_libwebsockets"].requires.append("libmount::libmount")
        if self.options.with_sqlite3:
            self.cpp_info.components["_libwebsockets"].requires.append("sqlite3::sqlite3")
        if self.options.with_ssl == "openssl":
            self.cpp_info.components["_libwebsockets"].requires.append("openssl::openssl")
        elif self.options.with_ssl == "mbedtls":
            self.cpp_info.components["_libwebsockets"].requires.append("mbedtls::mbedtls")
        elif self.options.with_ssl == "wolfssl":
            self.cpp_info.components["_libwebsockets"].requires.append("wolfssl::wolfssl")
        if self.options.with_hubbub:
            # TODO - Add hubbub package when available.
            pass
