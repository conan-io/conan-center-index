from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class CrashpadConan(ConanFile):
    name = "crashpad"
    description = "Crashpad is a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "crashpad", "crash", "error", "stacktrace", "collecting", "reporting")
    license = "Apache-2.0"
    homepage = "https://chromium.googlesource.com/crashpad/crashpad/+/master/README.md"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "http_transport": ["libcurl", "socket", "boringssl", None],
        "with_tls": ["openssl", False],
    }
    default_options = {
        "fPIC": True,
        "http_transport": None,
        "with_tls": "openssl",
    }
    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ("Linux", "FreeBSD"):
            self.options.http_transport = "libcurl"
        elif self.settings.os == "Android":
            self.options.http_transport = "socket"

    def build_requirements(self):
        self.build_requires("gn/cci.20210429")
        # FIXME: needs python 2.x support on Windows (uses print without parentheses + _winreg module)

    def requirements(self):
        # FIXME: use mini_chromium conan package instead of embedded package
        self.requires("zlib/1.2.11")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.requires("linux-syscall-support/cci.20200813")
        if self.options.http_transport != "socket":
            del self.options.with_tls
        if self.options.http_transport == "libcurl":
            self.requires("libcurl/7.75.0")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/1.1.1k")

    def validate(self):
        if self.options.http_transport == "libcurl":
            if not self.options["libcurl"].shared:
                # FIXME: is this true?
                self.output.warn("crashpad needs a shared libcurl library")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not (yet) supported by this recipe because the build system requires python 2.x which is not (yet) available on CCI.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version]["url"]["crashpad"], destination=self._source_subfolder, strip_root=True)
        tools.get(**self.conan_data["sources"][self.version]["url"]["mini_chromium"],
                  destination=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium"), strip_root=True)

    @property
    def _gn_os(self):
        if tools.is_apple_os(self.settings.os):
            return "mac"
        return {
            "Windows": "win",
        }.get(str(self.settings.os), str(self.settings.os).lower())

    @property
    def _gn_arch(self):
        return {
            "x86_64": "x64",
            "armv8": "aarch64",
            "x86": "x86",
        }.get(str(self.settings.arch), str(self.settings.arch))

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                yield
        else:
            env_defaults = {}
            if self.settings.compiler == "gcc":
                env_defaults.update({
                    "CC": "gcc",
                    "CXX": "g++",
                    "LD": "g++",
                })
            elif self.settings.compiler in ("clang", "apple-clang"):
                env_defaults.update({
                    "CC": "clang",
                    "CXX": "clang++",
                    "LD": "clang++",
                })
            env = {}
            for key, value in env_defaults.items():
                if not tools.get_env(key):
                    env[key] = value
            with tools.environment_append(env):
                yield

    @property
    def _http_transport_impl(self):
        if str(self.options.http_transport) == "None":
            return ""
        else:
            return str(self.options.http_transport)

    def build(self):
        # Order of ssl and crypto is wrong (first ssl, then crypto)
        tools.replace_in_file(os.path.join(self._source_subfolder, "util", "BUILD.gn"), "\"crypto\"", "SSL_LABEL")
        tools.replace_in_file(os.path.join(self._source_subfolder, "util", "BUILD.gn"), "\"ssl\"", "\"crypto\"")
        tools.replace_in_file(os.path.join(self._source_subfolder, "util", "BUILD.gn"), "SSL_LABEL", "\"ssl\"")

        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "zlib", "BUILD.gn"), "zlib_source = \"embedded\"", "zlib_source = \"system\"")
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "common.gypi"), "-fPIC", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party","mini_chromium", "mini_chromium", "build", "config", "BUILD.gn"),   "-fPIC", "")

        # Allow compiling crashpad with gcc (fetch compiler from environment variables)
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn"),
                              "\"clang\"", "getenv(\"CC\")")
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn"),
                              "\"clang++\"", "getenv(\"CXX\")")
        toolchain_path = os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn")

        # Use conan linux-syscall-support package
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "lss", "lss.h"),
                              "include \"third_party/lss/linux_syscall_support.h\"",
                              "include <linux_syscall_support.h>")
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "lss", "lss.h"),
                              "include \"third_party/lss/lss/linux_syscall_support.h\"",
                              "include <linux_syscall_support.h>")

        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn"),
                              "assert(false, \"Unsupported architecture\")",
                              "print(\"Unknown architecture -> assume conan knows how to handle it\")")

        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "win_helper.py"),
                              "print line", "print(line)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "win_helper.py"),
                              "print result", "print(result)")

        if self.settings.compiler == "gcc":
            # Remove gcc-incompatible compiler arguments
            for comp_arg in ("-Werror", "-Wheader-hygiene", "-Wnewline-eof", "-Wstring-conversion", "-Wexit-time-destructors", "-fobjc-call-cxx-cdtors", "-Wextra-semi", "-Wimplicit-fallthrough"):
                tools.replace_in_file(toolchain_path,
                                      "\"{}\"".format(comp_arg), "\"\"")


        autotools = AutoToolsBuildEnvironment(self)
        extra_cflags = autotools.flags + ["-D{}".format(d) for d in autotools.defines]
        extra_cflags_c = []
        extra_cflags_cc = autotools.cxx_flags
        extra_ldflags = autotools.link_flags
        if self.options.get_safe("fPIC"):
            extra_cflags.append("-fPIC")
        extra_cflags.extend("-I'{}'".format(inc) for inc in autotools.include_paths)
        extra_ldflags.extend("-L'{}'".format(libdir) for libdir in autotools.library_paths)
        if self.settings.compiler == "clang":
            if self.settings.compiler.get_safe("libcxx"):
                stdlib = {
                    "libstdc++11": "libstdc++",
                }.get(str(self.settings.compiler.libcxx), str(self.settings.compiler.libcxx))
                extra_cflags_cc.append("-stdlib={}".format(stdlib))
                extra_ldflags.append("-stdlib={}".format(stdlib))
        gn_args = [
            "host_os=\\\"{}\\\"".format(self._gn_os),
            "host_cpu=\\\"{}\\\"".format(self._gn_arch),
            "is_debug={}".format(str(self.settings.build_type == "Debug").lower()),
            "crashpad_http_transport_impl=\\\"{}\\\"".format(self._http_transport_impl),
            "crashpad_use_boringssl_for_http_transport_socket={}".format(str(self.options.get_safe("with_tls", False) != False).lower()),
            "extra_cflags=\\\"{}\\\"".format(" ".join(extra_cflags)),
            "extra_cflags_c=\\\"{}\\\"".format(" ".join(extra_cflags_c)),
            "extra_cflags_cc=\\\"{}\\\"".format(" ".join(extra_cflags_cc)),
            "extra_ldflags=\\\"{}\\\"".format(" ".join(extra_ldflags)),
        ]
        with tools.chdir(self._source_subfolder):
            with self._build_context():
                self.run("gn gen out/Default --args=\"{}\"".format(" ".join(gn_args)), run_environment=True)
                for target in ("client", "minidump", "crashpad_handler", "snapshot"):
                    # FIXME: Remove verbose once everything is working hunky dory
                    self.run("ninja -v -C out/Default {target} -j{parallel}".format(
                        target=target,
                        parallel=tools.cpu_count()), run_environment=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        self.copy("*.h", src=os.path.join(self._source_subfolder, "client"), dst=os.path.join("include", "client"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "util"), dst=os.path.join("include", "util"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "base"), dst=os.path.join("include", "base"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build"), dst=os.path.join("include", "build"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "out", "Default", "gen", "build"), dst=os.path.join("include", "build"))

        self.copy("*.a", src=os.path.join(self._source_subfolder, "out", "Default"), dst="lib", keep_path=False)
        self.copy("crashpad_handler", src=os.path.join(self._source_subfolder, "out", "Default"), dst="bin", keep_path=False)
        self.copy("crashpad_handler.exe", src=os.path.join(self._source_subfolder, "out", "Default"), dst="bin", keep_path=False)

    def package_info(self):
        minichromium_libs = ["base"]
        util_libs = ["util"]
        if tools.is_apple_os(self.settings.os):
            util_libs.append("mig_output")
        if self.settings.os in ("Linux", "FreeBSD"):
            util_libs.append("compat")
        client_libs = ["client", "common"]
        snapshot_libs = ["snapshot", "context"]
        minidump_libs = ["minidump", "format"]
        handler_libs = ["handler"]

        self.output.info("DEBUG: contents of /lib: {}".format(os.listdir(os.path.join(self.package_folder, "lib"))))
        self.cpp_info.libs = handler_libs + minidump_libs + snapshot_libs + client_libs + util_libs + minichromium_libs
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["rpcrt4", "dbghelp"]
        # FIXME: what frameworks are missing?
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks = ["CoreFoundation"]
            # self.cpp_info.frameworks = ["ApplicationServices", "CoreFoundation", "Foundation", "IOKit", "Security"]
