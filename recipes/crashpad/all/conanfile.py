import os
import shutil
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import XCRun, is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, save
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CrashpadConan(ConanFile):
    name = "crashpad"
    description = "Crashpad is a crash-reporting system."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/crashpad/crashpad/+/master/README.md"
    topics = ("crash", "error", "stacktrace", "collecting", "reporting")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "http_transport": ["libcurl", "socket", None],
        "with_tls": ["openssl", False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "http_transport": None,
        "with_tls": "openssl",
    }
    provides = ["mini_chromium"]

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "gcc": "5",
            "clang": "3.9",
            "msvc": "190",
            "Visual Studio": "14",
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.options.http_transport = "libcurl"
        elif self.settings.os == "Android":
            self.options.http_transport = "socket"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.http_transport != "socket":
            self.options.rm_safe("with_tls")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # FIXME: use mini_chromium conan package instead of embedded package (if possible)
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("linux-syscall-support/cci.20200813")
        if self.options.http_transport == "libcurl":
            self.requires("libcurl/[>=7.78 <9]")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if is_msvc(self) and self.options.http_transport in ("libcurl", "socket"):
            raise ConanInvalidConfiguration(
                f"http_transport={self.options.http_transport} is not valid when building with Visual Studio"
            )
        if self.options.http_transport == "libcurl" and not self.dependencies["libcurl"].options.shared:
            # FIXME: is this true?
            self.output.warning("crashpad needs a shared libcurl library")

    def build_requirements(self):
        self.tool_requires("ninja/1.11.1")
        self.tool_requires("gn/cci.20210429")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/x.y.z")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["crashpad"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["mini_chromium"],
            destination=os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium"),
            strip_root=True)

    @property
    def _gn_os(self):
        if self.settings.os == "Windows":
            return "win"
        elif self.settings.os == "Macos":
            return "mac"
        elif is_apple_os(self):
            return "ios"
        return str(self.settings.os).lower()

    @property
    def _gn_arch(self):
        return {
            "x86_64": "x64",
            "armv8": "arm64",
            "x86": "x86",
        }.get(str(self.settings.arch), str(self.settings.arch))

    @property
    def _http_transport_impl(self):
        if not self.options.http_transport:
            return ""
        return str(self.options.http_transport)

    def _generate_args_gn(self, gn_args):
        formatted_args = {}
        for k, v in gn_args.items():
            if isinstance(v, bool):
                formatted_args[k] = "true" if v else "false"
            elif isinstance(v, str):
                formatted_args[k] = f'"{v}"'
        save(self, os.path.join(self.build_folder, "args.gn"),
             "\n".join(f"{k} = {v}" for k, v in formatted_args.items()))

    @property
    def _cxx(self):
        compilers_by_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        cxx = compilers_by_conf.get("cpp") or VirtualBuildEnv(self).vars().get("CXX")
        if cxx:
            return cxx
        if self.settings.compiler == "apple-clang":
            return XCRun(self).cxx
        compiler_version = self.settings.compiler.version
        major = Version(compiler_version).major
        if self.settings.compiler == "gcc":
            return shutil.which(f"g++-{compiler_version}") or shutil.which(f"g++-{major}") or shutil.which("g++") or ""
        if self.settings.compiler == "clang":
            return shutil.which(f"clang++-{compiler_version}") or shutil.which(f"clang++-{major}") or shutil.which("clang++") or ""
        return ""

    def generate(self):
        VirtualBuildEnv(self).generate()
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        deps = AutotoolsDeps(self)

        def _get_flags(name):
            return " ".join(filter(None, [tc.vars().get(name), deps.vars().get(name)]))

        env = Environment()
        env.define("CXX", self._cxx)
        env.vars(self).save_script("conanbuild_gn")

        gn_args = {}
        gn_args["extra_arflags"] = _get_flags("ARFLAGS")
        gn_args["extra_cflags"] = _get_flags("CPPFLAGS")
        gn_args["extra_cflags_c"] = _get_flags("CFLAGS")
        gn_args["extra_cflags_cc"] = _get_flags("CXXFLAGS")
        gn_args["extra_ldflags"] = _get_flags("LDFLAGS") + " " + _get_flags("LIBS")
        gn_args["host_os"] = self._gn_os
        gn_args["host_cpu"] = self._gn_arch
        gn_args["is_debug"] = self.settings.build_type == "Debug"
        gn_args["crashpad_http_transport_impl"] = self._http_transport_impl
        gn_args["crashpad_use_boringssl_for_http_transport_socket"] = bool(self.options.get_safe("with_tls"))
        self._generate_args_gn(gn_args)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Replace https://github.com/chromium/crashpad/blob/main/third_party/lss/lss.h
        save(self, os.path.join(self.source_folder, "third_party", "lss", "lss.h"),
             "#ifndef CRASHPAD_THIRD_PARTY_LSS_LSS_H_\n"
             "#define CRASHPAD_THIRD_PARTY_LSS_LSS_H_\n"
             "#include <linux_syscall_support.h>\n"
             "#endif\n"
        )
        if is_msvc(self):
            zlib_libs = ", ".join(f'"{l}".lib' for l in self.dependencies["zlib"].cpp_info.libs)
            replace_in_file(self, os.path.join(self.source_folder, "third_party", "zlib", "BUILD.gn"),
                            'libs = [ "z" ]', f"libs = [ {zlib_libs} ]")
        elif self.settings.compiler == "gcc":
            toolchain_path = os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium", "build", "config", "BUILD.gn")
            # Remove gcc-incompatible compiler arguments
            for comp_arg in [
                "-Wheader-hygiene",
                "-Wnewline-eof",
                "-Wstring-conversion",
                "-Wexit-time-destructors",
                "-Wextra-semi",
                "-Wimplicit-fallthrough",
                "-fobjc-call-cxx-cdtors",
            ]:
                replace_in_file(self, toolchain_path, f'"{comp_arg}"', '""')

    def build(self):
        self._patch_sources()
        self.run(f'gn gen "{self.build_folder}"', cwd=self.source_folder)
        targets = ["client", "minidump", "crashpad_handler", "snapshot"]
        if self.settings.os == "Windows":
            targets.append("crashpad_handler_com")
        self.run(f"ninja -C {self.build_folder} {' '.join(targets)} -j{os.cpu_count()}")

        def lib_filename(name):
            prefix, suffix = ("", ".lib") if is_msvc(self) else ("lib", ".a")
            return f"{prefix}{name}{suffix}"

        rename(self, os.path.join(self.build_folder, "obj", "client", lib_filename("common")),
               os.path.join(self.build_folder, "obj", "client", lib_filename("client_common")))
        rename(self, os.path.join(self.build_folder, "obj", "handler", lib_filename("common")),
            os.path.join(self.build_folder, "obj", "handler", lib_filename("handler_common")))

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

        copy(self, "*.h",
             src=os.path.join(self.source_folder, "client"),
             dst=os.path.join(self.package_folder, "include", "client"))
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "util"),
             dst=os.path.join(self.package_folder, "include", "util"))
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium", "base"),
             dst=os.path.join(self.package_folder, "include", "base"))
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "third_party", "mini_chromium", "mini_chromium", "build"),
             dst=os.path.join(self.package_folder, "include", "build"))
        copy(self, "*.h",
             src=os.path.join(self.build_folder, "gen", "build"),
             dst=os.path.join(self.package_folder, "include", "build"))

        copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "crashpad_handler", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "crashpad_handler.exe", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "crashpad_handler_com.com", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)

        if self.settings.os == "Windows":
            rename(self, os.path.join(self.package_folder, "bin", "crashpad_handler_com.com"),
                os.path.join(self.package_folder, "bin", "crashpad_handler.com"))

        # Remove accidentally copied libraries. These are used by the executables, not by the libraries.
        rm(self, "*getopt*", os.path.join(self.package_folder, "lib"), recursive=True)

        save(self, os.path.join(self.package_folder, "lib", "cmake", "crashpad-cxx.cmake"),
            textwrap.dedent("""\
                if(TARGET crashpad::mini_chromium_base)
                    target_compile_features(crashpad::mini_chromium_base INTERFACE cxx_std_14)
                endif()
               """)
             )

    def package_info(self):
        self.cpp_info.components["mini_chromium_base"].libs = ["base"]

        cmake_module = os.path.join(self.package_folder, "lib", "cmake", "crashpad-cxx.cmake")
        self.cpp_info.set_property("cmake_build_modules", [cmake_module])
        self.cpp_info.components["mini_chromium_base"].builddirs = [os.path.join("lib", "cmake")]
        self.cpp_info.components["mini_chromium_base"].build_modules = [cmake_module]

        if is_apple_os(self):
            self.cpp_info.components["mini_chromium_base"].frameworks = ["CoreFoundation", "Foundation", "Security"]
            if self.settings.os == "Macos":
                self.cpp_info.components["mini_chromium_base"].frameworks += ["ApplicationServices", "IOKit"]
            else:  # iOS
                self.cpp_info.components["mini_chromium_base"].frameworks = ["CoreGraphics", "CoreText"]

        self.cpp_info.components["util"].libs = ["util"]
        self.cpp_info.components["util"].requires = ["mini_chromium_base", "zlib::zlib"]
        if is_apple_os(self):
            self.cpp_info.components["util"].libs.append("mig_output")
        if self.settings.os in ["Linux", "FreeBSD"]:
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

        self.cpp_info.components["net"].libs = ["net"]
        self.cpp_info.components["tool_support"].libs = ["tool_support"]
        self.cpp_info.components["handler_common"].libs = ["handler_common"]
        self.cpp_info.components["handler_common"].requires = ["client_common", "snapshot", "util", "net"]

        self.cpp_info.components["handler"].libs = ["handler"]
        self.cpp_info.components["handler"].requires = ["client", "util", "handler_common", "minidump", "snapshot", "tool_support"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
