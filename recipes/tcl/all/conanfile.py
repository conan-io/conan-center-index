from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag, NMakeToolchain, NMakeDeps
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class TclConan(ConanFile):
    name = "tcl"
    description = "Tcl is a very powerful but easy to learn dynamic programming language."
    license = "TCL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tcl.tk"
    topics = ("scripting", "programming")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")
        # source folder must be a sub-directory of the build folder
        self.folders.build = "."

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()

            deps = NMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            def yes_no(v): return "yes" if v else "no"
            tc.configure_args.extend([
                "--enable-threads",
                "--enable-symbols={}".format(yes_no(self.settings.build_type == "Debug")),
                "--enable-64bit={}".format(yes_no(self.settings.arch == "x86_64")),
            ])
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        if is_apple_os(self) and self.settings.arch not in ("x86", "x86_64"):
            macos_configure = os.path.join(self.source_folder, "macosx", "configure")
            replace_in_file(self, macos_configure, "#define HAVE_CPUID 1", "#undef HAVE_CPUID")

        unix_config_dir = os.path.join(self.source_folder, "unix")
        # When disabling 64-bit support (in 32-bit), this test must be 0 in order to use "long long" for 64-bit ints
        # (${tcl_type_64bit} can be either "__int64" or "long long")
        replace_in_file(self, os.path.join(unix_config_dir, "configure"),
                        "(sizeof(${tcl_type_64bit})==sizeof(long))",
                        "(sizeof(${tcl_type_64bit})!=sizeof(long))")

        unix_makefile_in = os.path.join(unix_config_dir, "Makefile.in")
        # Avoid building internal libraries as shared libraries
        replace_in_file(self, unix_makefile_in, "--enable-shared --enable-threads", "--enable-threads")
        # Avoid clearing CFLAGS and LDFLAGS in the makefile
        replace_in_file(self, unix_makefile_in, "\nCFLAGS\t", "\n#CFLAGS\t")
        replace_in_file(self, unix_makefile_in, "\nLDFLAGS\t", "\n#LDFLAGS\t")
        # Use CFLAGS and CPPFLAGS as argument to CC
        replace_in_file(self, unix_makefile_in, "${CFLAGS}", "${CFLAGS} ${CPPFLAGS}")

        win_config_dir = os.path.join(self.source_folder, "win")

        # Fix install for MinGW
        win_makefile_in = os.path.join(win_config_dir, "Makefile.in")
        replace_in_file(self, win_makefile_in, "INSTALL_ROOT	=", "INSTALL_ROOT	= $(DESTDIR)")
        # No link to static libgcc for MinGW
        win_tcl_m4 = os.path.join(win_config_dir, "tcl.m4")
        replace_in_file(self, win_tcl_m4, "-static-libgcc", "")

        # nmake creates a temporary file with mixed forward/backward slashes
        # force the filename to avoid cryptic error messages
        win_makefile_vc = os.path.join(win_config_dir, "makefile.vc")
        replace_in_file(self, win_makefile_vc, "@type << >$@", "type <<temp.tmp >$@")

        win_rules_vc = os.path.join(self.source_folder, "win", "rules.vc")
        # do not treat nmake build warnings as errors
        replace_in_file(self, win_rules_vc, "cwarn = $(cwarn) -WX", "")
        # disable whole program optimization to be portable across different MSVC versions.
        # See conan-io/conan-center-index#4811 conan-io/conan-center-index#4094
        replace_in_file(self,
                        win_rules_vc,
                        "OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL",
                        "")

    def _build_nmake(self, targets):
        opts = []
        # https://core.tcl.tk/tips/doc/trunk/tip/477.md
        if not self.options.shared:
            opts.append("static")
        if self.settings.build_type == "Debug":
            opts.append("symbols")
        if is_msvc_static_runtime(self):
            opts.append("nomsvcrt")
        else:
            opts.append("msvcrt")
        if "d" not in msvc_runtime_flag(self):
            opts.append("unchecked")

        win_config_dir = os.path.join(self.source_folder, "win")
        with chdir(self, win_config_dir):
            self.run('nmake -nologo -f "{cfgdir}/makefile.vc" INSTALLDIR="{pkgdir}" OPTS={opts} {targets}'.format(
                cfgdir=win_config_dir,
                pkgdir=self.package_folder,
                opts=",".join(opts),
                targets=" ".join(targets),
            ))

    def _get_configure_subdir(self):
        return {
            "Macos": "macosx",
            "Linux": "unix",
            "FreeBSD": "unix",
            "Windows": "win",
        }[str(self.settings.os)]

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_nmake(["release"])
        else:
            autotools = Autotools(self)
            autotools.configure(build_script_folder=self._get_configure_subdir())
            # https://core.tcl.tk/tcl/tktview/840660e5a1
            for root, _, list_of_files in os.walk(self.build_folder):
                if "Makefile" in list_of_files:
                    replace_in_file(self, os.path.join(root, "Makefile"), "-Dstrtod=fixstrtod", "", strict=False)
            # For some reason this target "binaries" may not be built before others
            # on Windows while it's a dependency of many other targets
            autotools.make(target="binaries")
            autotools.make()

    def package(self):
        copy(self, "license.terms", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            self._build_nmake(["install-binaries", "install-libraries"])
        else:
            autotools = Autotools(self)
            autotools.install()
            autotools.install(target="install-private-headers")

            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "man"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            fix_apple_shared_install_name(self)

        # Relocatable tclConfig.sh
        tclConfigShPath = os.path.join(self.package_folder, "lib", "tclConfig.sh")
        ## Comment out references to build folder
        replace_in_file(self, tclConfigShPath, "\nTCL_BUILD_", "\n#TCL_BUILD_")
        replace_in_file(self, tclConfigShPath, "\nTCL_SRC_DIR", "\n#TCL_SRC_DIR")
        ## Replace references to package folder by TCL_ROOT env var supposed to be defined by VirtualRunEnv
        if is_msvc(self):
            replace_in_file(self, tclConfigShPath, self.package_folder, "${TCL_ROOT}")
        else:
            replace_in_file(self, tclConfigShPath, "TCL_PREFIX='/'", "TCL_PREFIX='${TCL_ROOT}'")
            replace_in_file(self, tclConfigShPath, "TCL_EXEC_PREFIX='/'", "TCL_EXEC_PREFIX='${TCL_ROOT}'")
            for to_replace in ["//", "/"]:
                replace_in_file(self, tclConfigShPath, f"-L{to_replace}lib", "-L${TCL_ROOT}/lib", strict=False)
                replace_in_file(self, tclConfigShPath, f"{{{to_replace}lib}}", "{${TCL_ROOT}/lib}", strict=False)
                replace_in_file(self, tclConfigShPath, f"='{to_replace}lib", "='${TCL_ROOT}/lib", strict=False)
                replace_in_file(self, tclConfigShPath, f"-I{to_replace}include", "-I${TCL_ROOT}/include", strict=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TCL")

        # There are other libs in subfolders, but they are only used
        # for TCL extensions and should not be linked against.
        self.cpp_info.libs = collect_libs(self, os.path.join(self.package_folder, "lib"))

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "netapi32", "userenv"])
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("STATIC_BUILD")

        tcl_version = Version(self.version)
        tcl_library = os.path.join(self.package_folder, "lib", f"tcl{tcl_version.major}.{tcl_version.minor}")
        self.runenv_info.define_path("TCL_LIBRARY", tcl_library)

        tcl_root = self.package_folder
        self.runenv_info.define_path("TCL_ROOT", tcl_root)

        tclsh_list = list(filter(lambda fn: fn.startswith("tclsh"), os.listdir(os.path.join(self.package_folder, "bin"))))
        tclsh = os.path.join(self.package_folder, "bin", tclsh_list[0])
        self.runenv_info.define_path("TCLSH", tclsh)

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "TCL"
        self.cpp_info.names["cmake_find_package_multi"] = "TCL"
        self.env_info.TCL_LIBRARY = tcl_library
        self.env_info.TCL_ROOT = tcl_root
        self.env_info.TCLSH = tclsh
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
