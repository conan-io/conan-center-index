from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException, ConanInvalidConfiguration, ConanExceptionInUserConanfileMethod
import os

required_conan_version = ">=1.33.0"

class TkConan(ConanFile):
    name = "tk"
    description = "Tk is a graphical user interface toolkit that takes developing desktop applications to a higher level than conventional approaches."
    topics = ("conan", "tk", "gui", "tcl", "scripting", "programming")
    homepage = "https://tcl.tk"
    license = "TCL"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("tcl/{}".format(self.version))
        if self.settings.os == "Linux":
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.options["tcl"].shared != self.options.shared:
            raise ConanInvalidConfiguration("The shared option of tcl and tk must have the same value")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for build_system in ("unix", "win", ):
            config_dir = self._get_configure_folder(build_system)

            if build_system != "win":
                # When disabling 64-bit support (in 32-bit), this test must be 0 in order to use "long long" for 64-bit ints
                # (${tcl_type_64bit} can be either "__int64" or "long long")
                tools.replace_in_file(os.path.join(config_dir, "configure"),
                                      "(sizeof(${tcl_type_64bit})==sizeof(long))",
                                      "(sizeof(${tcl_type_64bit})!=sizeof(long))")

            makefile_in = os.path.join(config_dir, "Makefile.in")
            # Avoid clearing CFLAGS and LDFLAGS in the makefile
            # tools.replace_in_file(makefile_in, "\nCFLAGS{}".format(" " if (build_system == "win" and name == "tcl") else "\t"), "\n#CFLAGS\t")
            tools.replace_in_file(makefile_in, "\nLDFLAGS\t", "\n#LDFLAGS\t")
            tools.replace_in_file(makefile_in, "${CFLAGS}", "${CFLAGS} ${CPPFLAGS}")

        rules_ext_vc = os.path.join(self.source_folder, self._source_subfolder, "win", "rules-ext.vc")
        tools.replace_in_file(rules_ext_vc,
                              "\n_RULESDIR = ",
                              "\n_RULESDIR = .\n#_RULESDIR = ")
        rules_vc = os.path.join(self.source_folder, self._source_subfolder, "win", "rules.vc")
        tools.replace_in_file(rules_vc,
                              r"$(_TCLDIR)\generic",
                              r"$(_TCLDIR)\include")
        tools.replace_in_file(rules_vc,
                              "\nTCLSTUBLIB",
                              "\n#TCLSTUBLIB")
        tools.replace_in_file(rules_vc,
                              "\nTCLIMPLIB",
                              "\n#TCLIMPLIB")

        win_makefile_in = os.path.join(self._get_configure_folder("win"), "Makefile.in")
        tools.replace_in_file(win_makefile_in, "\nTCL_GENERIC_DIR", "\n#TCL_GENERIC_DIR")

        win_rules_vc = os.path.join(self._source_subfolder, "win", "rules.vc")
        tools.replace_in_file(win_rules_vc,
                              "\ncwarn = $(cwarn) -WX",
                              "\n# cwarn = $(cwarn) -WX")
        # disable whole program optimization to be portable across different MSVC versions.
        # See conan-io/conan-center-index#4811 conan-io/conan-center-index#4094
        tools.replace_in_file(
            win_rules_vc,
            "OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL",
            "# OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL")

    def _get_default_build_system(self):
        if tools.is_apple_os(self.settings.os):
            return "macosx"
        elif self.settings.os in ("Linux", "FreeBSD"):
            return "unix"
        elif self.settings.os == "Windows":
            return "win"
        else:
            raise ValueError("tk recipe does not recognize os")

    def _get_configure_folder(self, build_system=None):
        if build_system is None:
            build_system = self._get_default_build_system()
        if build_system not in ["win", "unix", "macosx"]:
            raise ConanExceptionInUserConanfileMethod("Invalid build system: {}".format(build_system))
        return os.path.join(self.source_folder, self._source_subfolder, build_system)

    def _build_nmake(self, target="release"):
        # https://core.tcl.tk/tips/doc/trunk/tip/477.md
        opts = []
        if not self.options.shared:
            opts.append("static")
        if self.settings.build_type == "Debug":
            opts.append("symbols")
        if "MD" in str(self.settings.compiler.runtime):
            opts.append("msvcrt")
        else:
            opts.append("nomsvcrt")
        if "d" not in str(self.settings.compiler.runtime):
            opts.append("unchecked")
        # https://core.tcl.tk/tk/tktview?name=3d34589aa0
        # https://wiki.tcl-lang.org/page/Building+with+Visual+Studio+2017
        tcl_lib_path = os.path.join(self.deps_cpp_info["tcl"].rootpath, "lib")
        tclimplib, tclstublib = None, None
        for lib in os.listdir(tcl_lib_path):
            if not lib.endswith(".lib"):
                continue
            if lib.startswith("tcl{}".format("".join(self.version.split(".")[:2]))):
                tclimplib = os.path.join(tcl_lib_path, lib)
            elif lib.startswith("tclstub{}".format("".join(self.version.split(".")[:2]))):
                tclstublib = os.path.join(tcl_lib_path, lib)

        if tclimplib is None or tclstublib is None:
            raise ConanException("tcl dependency misses tcl and/or tclstub library")
        with tools.vcvars(self.settings):
            tcldir = self.deps_cpp_info["tcl"].rootpath.replace("/", "\\\\")
            self.run(
                """nmake -nologo -f "{cfgdir}/makefile.vc" INSTALLDIR="{pkgdir}" OPTS={opts} TCLDIR="{tcldir}" TCL_LIBRARY="{tcl_library}" TCLIMPLIB="{tclimplib}" TCLSTUBLIB="{tclstublib}" {target}""".format(
                    cfgdir=self._get_configure_folder("win"),
                    pkgdir=self.package_folder,
                    opts=",".join(opts),
                    tcldir=tcldir,
                    tclstublib=tclstublib,
                    tclimplib=tclimplib,
                    tcl_library=self.deps_env_info['tcl'].TCL_LIBRARY.replace("\\", "/"),
                    target=target,
                ), cwd=self._get_configure_folder("win"),
            )

    def _configure_autotools(self):
        tcl_root = self.deps_cpp_info["tcl"].rootpath
        make_args = ["TCL_GENERIC_DIR={}".format(os.path.join(tcl_root, "include")).replace("\\", "/")]
        if self._autotools:
            return self._autotools, make_args

        tclConfigShFolder = os.path.join(tcl_root, "lib").replace("\\", "/")

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--with-tcl={}".format(tools.unix_path(tclConfigShFolder)),
            "--enable-threads",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-symbols={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-64bit={}".format(yes_no(self.settings.arch == "x86_64")),
            "--with-x={}".format(yes_no(self.settings.os == "Linux")),
            "--enable-aqua={}".format(yes_no(tools.is_apple_os(self.settings.os))),
        ]

        if self.settings.os == "Windows":
            self._autotools.defines.extend(["UNICODE", "_UNICODE", "_ATL_XP_TARGETING", ])
        self._autotools.libs = []
        self._autotools.configure(configure_dir=self._get_configure_folder(), args=conf_args)
        return self._autotools, make_args

    def build(self):
        self._patch_sources()

        if self.settings.compiler == "Visual Studio":
            self._build_nmake()
        else:
            autotools, make_args = self._configure_autotools()
            autotools.make(args=make_args)

    def package(self):
        self.copy(pattern="license.terms", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            self._build_nmake("install")
        else:
            with tools.chdir(self.build_folder):
                autotools, make_args = self._configure_autotools()
                autotools.install(args=make_args)
                autotools.make(target="install-private-headers", args=make_args)
                tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "man"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # FIXME: move to patch
        tkConfigShPath = os.path.join(self.package_folder, "lib", "tkConfig.sh")
        if os.path.exists(tkConfigShPath):
            pkg_path = os.path.join(self.package_folder).replace('\\', '/')
            tools.replace_in_file(tkConfigShPath,
                                  pkg_path,
                                  "${TK_ROOT}")
            tools.replace_in_file(tkConfigShPath,
                                  "\nTK_BUILD_",
                                  "\n#TK_BUILD_")
            tools.replace_in_file(tkConfigShPath,
                                  "\nTK_SRC_DIR",
                                  "\n#TK_SRC_DIR")

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            tk_version = tools.Version(self.version)
            lib_infix = "{}{}".format(tk_version.major, tk_version.minor)
            tk_suffix = "t{}{}{}".format(
                "" if self.options.shared else "s",
                "g" if self.settings.build_type == "Debug" else "",
                "x" if "MD" in str(self.settings.compiler.runtime) and not self.options.shared else "",
            )
        else:
            tk_version = tools.Version(self.version)
            lib_infix = "{}.{}".format(tk_version.major, tk_version.minor)
            tk_suffix = ""
        self.cpp_info.libs = ["tk{}{}".format(lib_infix, tk_suffix), "tkstub{}".format(lib_infix)]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Cocoa", "Carbon", "IOKit"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "netapi32", "kernel32", "user32", "advapi32", "userenv","ws2_32", "gdi32",
                "comdlg32", "imm32", "comctl32", "shell32", "uuid", "ole32", "oleaut32"
            ]

        tk_library = os.path.join(self.package_folder, "lib", "{}{}".format(self.name, ".".join(self.version.split(".")[:2]))).replace("\\", "/")
        self.output.info("Setting TK_LIBRARY environment variable: {}".format(tk_library))
        self.env_info.TK_LIBRARY = tk_library

        tcl_root = self.package_folder.replace("\\", "/")
        self.output.info("Setting TCL_ROOT environment variable: {}".format(tcl_root))
        self.env_info.TCL_ROOT = tcl_root
