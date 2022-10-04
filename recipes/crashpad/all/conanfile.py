from conans import AutoToolsBuildEnvironment
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, copy, rename, save, rm, chdir, replace_in_file
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc, check_min_vs, VCVars
from conan.tools.build import check_min_cppstd, build_jobs, cross_building
from conan.tools.layout import basic_layout
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
import os
import sys
import textwrap


required_conan_version = ">=1.52.0"


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
    _autotools_flags = {}

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _minimum_compiler(self):
        return {
            "apple-clang": "10",
            "gcc": "5",
            "clang": "3.9",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ("Linux", "FreeBSD"):
            self.options.http_transport = "libcurl"
        elif self.settings.os == "Android":
            self.options.http_transport = "socket"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # FIXME: use mini_chromium conan package instead of embedded package (if possible)
        self.requires("zlib/1.2.12")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.requires("linux-syscall-support/cci.20200813")
        if self.options.http_transport != "socket":
            del self.options.with_tls
        if self.options.http_transport == "libcurl":
            self.requires("libcurl/7.84.0")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        if is_msvc(self):
            check_min_vs(1911)
            if self.info.options.http_transport in ("libcurl", "socket"):
                raise ConanInvalidConfiguration(f"http_transport={self.info.options.http_transport} is not valid when building with Visual Studio")
        else:
            minimum_version = self._minimum_compiler.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")
        if self.info.options.http_transport == "libcurl":
            if not self.options["libcurl"].shared:
                # FIXME: is this true?
                self.output.warn("crashpad needs a shared libcurl library")

    def build_requirements(self):
        self.tool_requires("ninja/1.10.2")
        self.tool_requires("gn/cci.20210429")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["crashpad"], destination=self.source_folder, strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["mini_chromium"],
                        destination=os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium"), strip_root=True)

    @property
    def _gn_os(self):
        if is_apple_os(self):
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

    def generate(self):
        if is_msvc(self):
            tc = VCVars(self)
            tc.generate()
        else:
            env = Environment()
            if self.settings.compiler == "gcc":
                env.define("CC", "gcc")
                env.define("CXX", "g++")
                env.define("LD", "g++")
            elif self.settings.compiler in ("clang", "apple-clang"):
                env.define("CC", "clang")
                env.define("CXX", "clang++")
                env.define("LD", "clang++")
            envvars = env.vars(self)
            envvars.save_script("compiler_defines")

        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def _patch_source(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "third_party", "zlib", "BUILD.gn"),
                                  "libs = [ \"z\" ]",
                                  "libs = [ {} ]".format(", ".join("\"{}.lib\"".format(l) for l in self.deps_cpp_info["zlib"].libs)))
        if self.settings.compiler == "gcc":
            toolchain_path = os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn")
            # Remove gcc-incompatible compiler arguments
            for comp_arg in ("-Wheader-hygiene", "-Wnewline-eof", "-Wstring-conversion", "-Wexit-time-destructors", "-fobjc-call-cxx-cdtors", "-Wextra-semi", "-Wimplicit-fallthrough"):
                replace_in_file(self, toolchain_path,
                                      "\"{}\"".format(comp_arg), "\"\"")

    def build(self):
        self._patch_source()
        # TODO: Use AutotoolsToolchain to capture compiler flags
        autotools = AutoToolsBuildEnvironment(self)
        extra_cflags = autotools.flags + ["-D{}".format(d) for d in autotools.defines]
        extra_cflags_c = []
        extra_cflags_cc = autotools.cxx_flags
        extra_ldflags = autotools.link_flags
        if self.options.get_safe("fPIC"):
            extra_cflags.append("-fPIC")
        extra_cflags.extend("-I {}".format(inc) for inc in autotools.include_paths)
        extra_ldflags.extend("-{}{}".format("LIBPATH:" if is_msvc(self) else "L ", libdir) for libdir in autotools.library_paths)
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
        with chdir(self, self.source_folder):
            parsed_gn_args = " ".join(gn_args)
            self.run(f'gn gen out/Default --args="{parsed_gn_args}" --script-executable="{sys.executable}"', env="conanbuild")
            targets = ["client", "minidump", "crashpad_handler", "snapshot"]
            if self.settings.os == "Windows":
                targets.append("crashpad_handler_com")
            self.run("ninja -C out/Default {targets} -j{parallel}".format(
                targets=" ".join(targets),
                parallel=build_jobs(self)), env="conanbuild")

    def package(self):
        def lib_filename(name):
            prefix, suffix = ("", ".lib")  if is_msvc(self) else ("lib", ".a")
            return f"{prefix}{name}{suffix}"

        rename(self, os.path.join(self.source_folder, "out", "Default", "obj", "client", lib_filename("common")),
                     os.path.join(self.source_folder, "out", "Default", "obj", "client", lib_filename("client_common")))
        rename(self, os.path.join(self.source_folder, "out", "Default", "obj", "handler", lib_filename("common")),
                     os.path.join(self.source_folder, "out", "Default", "obj", "handler", lib_filename("handler_common")))

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        copy(self, "*.h", src=os.path.join(self.source_folder, "client"), dst=os.path.join(self.package_folder, "include", "client"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "util"), dst=os.path.join(self.package_folder, "include", "util"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium", "base"), dst=os.path.join(self.package_folder, "include", "base"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium", "build"), dst=os.path.join(self.package_folder, "include", "build"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "out", "Default", "gen", "build"), dst=os.path.join(self.package_folder, "include", "build"))

        copy(self, "*.a", src=os.path.join(self.source_folder, "out", "Default"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        copy(self, "*.lib", src=os.path.join(self.source_folder, "out", "Default"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "crashpad_handler", src=os.path.join(self.source_folder, "out", "Default"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "crashpad_handler.exe", src=os.path.join(self.source_folder, "out", "Default"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "crashpad_handler_com.com", src=os.path.join(self.source_folder, "out", "Default"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        if self.settings.os == "Windows":
            rename(self, os.path.join(self.package_folder, "bin", "crashpad_handler_com.com"),
                         os.path.join(self.package_folder, "bin", "crashpad_handler.com"))

        # Remove accidentally copied libraries. These are used by the executables, not by the libraries.
        rm(self, "*getopt*", os.path.join(self.package_folder, "lib"))

        save(self, os.path.join(self.package_folder, "lib", "cmake", "crashpad-cxx.cmake"),
                   textwrap.dedent("""\
                    if(TARGET crashpad::mini_chromium_base)
                        target_compile_features(crashpad::mini_chromium_base INTERFACE cxx_std_14)
                    endif()
                   """))

    def package_info(self):
        self.cpp_info.components["mini_chromium_base"].libs = ["base"]
        self.cpp_info.components["mini_chromium_base"].build_modules = [os.path.join(self.package_folder, "lib", "cmake", "crashpad-cxx.cmake")]
        self.cpp_info.components["mini_chromium_base"].builddirs = [os.path.join("lib", "cmake")]
        if is_apple_os(self):
            if self.settings.os == "Macos":
                self.cpp_info.components["mini_chromium_base"].frameworks = ["ApplicationServices", "CoreFoundation", "Foundation", "IOKit", "Security"]
            else:  # iOS
                self.cpp_info.components["mini_chromium_base"].frameworks = ["CoreFoundation", "CoreGraphics", "CoreText", "Foundation", "Security"]

        self.cpp_info.components["util"].libs = ["util"]
        self.cpp_info.components["util"].requires = ["mini_chromium_base", "zlib::zlib"]
        if is_apple_os(self):
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
        if is_apple_os(self):
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
