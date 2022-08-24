from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import textwrap

required_conan_version = ">=1.33.0"


class CrashpadConan(ConanFile):
    name = "crashpad"
    description = "Crashpad is a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "crashpad", "crash", "error", "stacktrace", "collecting", "reporting")
    license = "Apache-2.0"
    homepage = "https://chromium.googlesource.com/crashpad/crashpad/+/master/README.md"
    provides = "crashpad", "mini_chromium"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "http_transport": ["libcurl", "socket", None],
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

    def _minimum_compiler_cxx14(self):
        return {
            "apple-clang": 10,
            "gcc": 5,
            "clang": "3.9",
            "Visual Studio": 14,
        }.get(str(self.settings.compiler))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ("Linux", "FreeBSD"):
            self.options.http_transport = "libcurl"
        elif self.settings.os == "Android":
            self.options.http_transport = "socket"

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")
        self.build_requires("gn/cci.20210429")

    def requirements(self):
        # FIXME: use mini_chromium conan package instead of embedded package (if possible)
        self.requires("zlib/1.2.12")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.requires("linux-syscall-support/cci.20200813")
        if self.options.http_transport != "socket":
            del self.options.with_tls
        if self.options.http_transport == "libcurl":
            self.requires("libcurl/7.82.0")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/1.1.1o")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.http_transport in ("libcurl", "socket"):
                raise ConanInvalidConfiguration("http_transport={} is not valid when building with Visual Studio".format(self.options.http_transport))
        if self.options.http_transport == "libcurl":
            if not self.options["libcurl"].shared:
                # FIXME: is this true?
                self.output.warn("crashpad needs a shared libcurl library")
        min_compiler_version = self._minimum_compiler_cxx14()
        if min_compiler_version:
            if tools.scm.Version(self.settings.compiler.version) < min_compiler_version:
                raise ConanInvalidConfiguration("crashpad needs a c++14 capable compiler, version >= {}".format(min_compiler_version))
        else:
            self.output.warn("This recipe does not know about the current compiler and assumes it has sufficient c++14 supports.")
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 14)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version]["crashpad"], destination=self._source_subfolder, strip_root=True)
        tools.files.get(self, **self.conan_data["sources"][self.version]["mini_chromium"],
                  destination=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium"), strip_root=True)

    @property
    def _gn_os(self):
        if tools.apple.is_apple_os(self):
            if self.settings.os == "Macos":
                return "mac"
            else:
                return "ios"
        return {
            "Windows": "win",
        }.get(str(self.settings.os), str(self.settings.os).lower())

    @property
    def _gn_arch(self):
        return {
            "x86_64": "x64",
            "armv8": "arm64",
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

    def _version_greater_equal_to_cci_20220219(self):
        return self.version >= "cci.20220219"

    def _has_separate_util_net_lib(self):
        return self._version_greater_equal_to_cci_20220219()

    def _needs_to_link_tool_support(self):
        return self._version_greater_equal_to_cci_20220219()

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if self.settings.compiler == "Visual Studio":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "third_party", "zlib", "BUILD.gn"),
                                  "libs = [ \"z\" ]",
                                  "libs = [ {} ]".format(", ".join("\"{}.lib\"".format(l) for l in self.deps_cpp_info["zlib"].libs)))

        if self.settings.compiler == "gcc":
            toolchain_path = os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn")
            # Remove gcc-incompatible compiler arguments
            for comp_arg in ("-Wheader-hygiene", "-Wnewline-eof", "-Wstring-conversion", "-Wexit-time-destructors", "-fobjc-call-cxx-cdtors", "-Wextra-semi", "-Wimplicit-fallthrough"):
                tools.files.replace_in_file(self, toolchain_path,
                                      "\"{}\"".format(comp_arg), "\"\"")

        autotools = AutoToolsBuildEnvironment(self)
        extra_cflags = autotools.flags + ["-D{}".format(d) for d in autotools.defines]
        extra_cflags_c = []
        extra_cflags_cc = autotools.cxx_flags
        extra_ldflags = autotools.link_flags
        if self.options.get_safe("fPIC"):
            extra_cflags.append("-fPIC")
        extra_cflags.extend("-I {}".format(inc) for inc in autotools.include_paths)
        extra_ldflags.extend("-{}{}".format("LIBPATH:" if self.settings.compiler == "Visual Studio" else "L ", libdir) for libdir in autotools.library_paths)
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
        with tools.files.chdir(self, self._source_subfolder):
            with self._build_context():
                self.run("gn gen out/Default --args=\"{}\"".format(" ".join(gn_args)), run_environment=True)
                targets = ["client", "minidump", "crashpad_handler", "snapshot"]
                if self.settings.os == "Windows":
                    targets.append("crashpad_handler_com")
                self.run("ninja -C out/Default {targets} -j{parallel}".format(
                    targets=" ".join(targets),
                    parallel=tools.cpu_count(self, )), run_environment=True)

        def lib_filename(name):
            prefix, suffix = ("", ".lib")  if self.settings.compiler == "Visual Studio" else ("lib", ".a")
            return "{}{}{}".format(prefix, name, suffix)
        tools.files.rename(self, os.path.join(self._source_subfolder, "out", "Default", "obj", "client", lib_filename("common")),
                     os.path.join(self._source_subfolder, "out", "Default", "obj", "client", lib_filename("client_common")))
        tools.files.rename(self, os.path.join(self._source_subfolder, "out", "Default", "obj", "handler", lib_filename("common")),
                     os.path.join(self._source_subfolder, "out", "Default", "obj", "handler", lib_filename("handler_common")))

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        self.copy("*.h", src=os.path.join(self._source_subfolder, "client"), dst=os.path.join("include", "client"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "util"), dst=os.path.join("include", "util"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "base"), dst=os.path.join("include", "base"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium", "build"), dst=os.path.join("include", "build"))
        self.copy("*.h", src=os.path.join(self._source_subfolder, "out", "Default", "gen", "build"), dst=os.path.join("include", "build"))

        self.copy("*.a", src=os.path.join(self._source_subfolder, "out", "Default"), dst="lib", keep_path=False)

        self.copy("*.lib", src=os.path.join(self._source_subfolder, "out", "Default"), dst="lib", keep_path=False)
        self.copy("crashpad_handler", src=os.path.join(self._source_subfolder, "out", "Default"), dst="bin", keep_path=False)
        self.copy("crashpad_handler.exe", src=os.path.join(self._source_subfolder, "out", "Default"), dst="bin", keep_path=False)
        self.copy("crashpad_handler_com.com", src=os.path.join(self._source_subfolder, "out", "Default"), dst="bin", keep_path=False)
        if self.settings.os == "Windows":
            tools.files.rename(self, os.path.join(self.package_folder, "bin", "crashpad_handler_com.com"),
                         os.path.join(self.package_folder, "bin", "crashpad_handler.com"))

        # Remove accidentally copied libraries. These are used by the executables, not by the libraries.
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*getopt*")

        tools.files.save(self, os.path.join(self.package_folder, "lib", "cmake", "crashpad-cxx.cmake"),
                   textwrap.dedent("""\
                    if(TARGET crashpad::mini_chromium_base)
                        target_compile_features(crashpad::mini_chromium_base INTERFACE cxx_std_14)
                    endif()
                   """))

    def package_info(self):
        self.cpp_info.components["mini_chromium_base"].libs = ["base"]
        self.cpp_info.components["mini_chromium_base"].build_modules = [os.path.join(self.package_folder, "lib", "cmake", "crashpad-cxx.cmake")]
        self.cpp_info.components["mini_chromium_base"].builddirs = [os.path.join("lib", "cmake")]
        if tools.apple.is_apple_os(self):
            if self.settings.os == "Macos":
                self.cpp_info.components["mini_chromium_base"].frameworks = ["ApplicationServices", "CoreFoundation", "Foundation", "IOKit", "Security"]
            else:  # iOS
                self.cpp_info.components["mini_chromium_base"].frameworks = ["CoreFoundation", "CoreGraphics", "CoreText", "Foundation", "Security"]

        self.cpp_info.components["util"].libs = ["util"]
        self.cpp_info.components["util"].requires = ["mini_chromium_base", "zlib::zlib"]
        if tools.apple.is_apple_os(self):
            self.cpp_info.components["util"].libs.append("mig_output")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["util"].libs.append("compat")
            self.cpp_info.components["util"].requires.append("linux-syscall-support::linux-syscall-support")
        if self.settings.os == "Windows":
            self.cpp_info.components["util"].system_libs.extend(["dbghelp", "rpcrt4"])
        if self.options.http_transport == "libcurl":
            self.cpp_info.components["util"].requires.append("libcurl::libcurl")
        elif self.options.get_safe("with_tls") == "openssl":
            self.cpp_info.components["util"].requires.append("openssl::openssl")
        if self.settings.os == "Macos":
            self.cpp_info.components["util"].frameworks.extend(["CoreFoundation", "Foundation", "IOKit"])
            self.cpp_info.components["util"].system_libs.append("bsm")

        self.cpp_info.components["client_common"].libs = ["client_common"]
        self.cpp_info.components["client_common"].requires = ["util", "mini_chromium_base"]

        self.cpp_info.components["client"].libs = ["client"]
        self.cpp_info.components["client"].requires = ["util", "mini_chromium_base", "client_common"]
        if self.settings.os == "Windows":
            self.cpp_info.components["client"].system_libs.append("rpcrt4")

        self.cpp_info.components["context"].libs = ["context"]
        self.cpp_info.components["context"].requires = ["util"]

        self.cpp_info.components["snapshot"].libs = ["snapshot"]
        self.cpp_info.components["snapshot"].requires = ["context", "client_common", "mini_chromium_base", "util"]
        if tools.apple.is_apple_os(self):
            self.cpp_info.components["snapshot"].frameworks.extend(["OpenCL"])

        self.cpp_info.components["format"].libs = ["format"]
        self.cpp_info.components["format"].requires = ["snapshot", "mini_chromium_base", "util"]

        self.cpp_info.components["minidump"].libs = ["minidump"]
        self.cpp_info.components["minidump"].requires = ["snapshot", "mini_chromium_base", "util"]

        extra_handler_common_req = []
        if self._has_separate_util_net_lib():
            self.cpp_info.components["net"].libs = ["net"]
            extra_handler_common_req = ["net"]

        extra_handler_req = []
        if self._needs_to_link_tool_support():
            self.cpp_info.components["tool_support"].libs = ["tool_support"]
            extra_handler_req = ["tool_support"]

        self.cpp_info.components["handler_common"].libs = ["handler_common"]
        self.cpp_info.components["handler_common"].requires = ["client_common", "snapshot", "util"] + extra_handler_common_req

        self.cpp_info.components["handler"].libs = ["handler"]
        self.cpp_info.components["handler"].requires = ["client", "util", "handler_common", "minidump", "snapshot"] + extra_handler_req

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
