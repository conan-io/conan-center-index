from conans import AutoToolsBuildEnvironment, ConanFile, tools
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
        "http_transport": ["libcurl", "socket", None],
    }
    default_options = {
        "fPIC": True,
        "http_transport": None,
    }
    exports_sources = "patches/*"

    _autotools = None

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

    def requirements(self):
        # FIXME: use mini_chromium conan package instead of embedded package
        self.requires("linux-syscall-support/cci.20200813")
        self.requires("libcurl/7.75.0")

    def validate(self):
        if not self.options["libcurl"].shared:
            # FIXME: is this true?
            self.output.warn("crashpad needs a shared libcurl library")

    def source(self):
        tools.get(self.conan_data["sources"][self.version]["url"]["crashpad"], destination=self._source_subfolder)
        tools.get(self.conan_data["sources"][self.version]["url"]["mini_chromium"],
                  destination=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium"))

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

        if self.settings.compiler == "gcc":
            # Remove gcc-incompatible compiler arguments
            for comp_arg in ("-Werror", "-Wheader-hygiene", "-Wnewline-eof", "-Wstring-conversion", "-Wexit-time-destructors", "-fobjc-call-cxx-cdtors"):
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
            "extra_cflags=\\\"{}\\\"".format(" ".join(extra_cflags)),
            "extra_cflags_c=\\\"{}\\\"".format(" ".join(extra_cflags_c)),
            "extra_cflags_cc=\\\"{}\\\"".format(" ".join(extra_cflags_cc)),
            "extra_ldflags=\\\"{}\\\"".format(" ".join(extra_ldflags)),
        ]
        with tools.chdir(self._source_subfolder):
            with self._build_context():
                self.run("gn gen out/Default --args=\"{}\"".format(" ".join(gn_args)), run_environment=True)
                for target in ("client", "minidump", "crashpad_handler"):
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
        self.cpp_info.libs = ["minidump", "snapshot", "client", "util", "compat", "common", "base"]
