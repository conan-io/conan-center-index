from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conan.errors import ConanInvalidConfiguration
from io import StringIO
import os
import re
import textwrap

required_conan_version = ">=1.33.0"


class CPythonConan(ConanFile):
    name = "cpython"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.python.org"
    description = "Python is a programming language that lets you work quickly and integrate systems more effectively."
    topics = ("python", "cpython", "language", "script")
    license = ("Python-2.0",)
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "optimizations": [True, False],
        "lto": [True, False],
        "docstrings": [True, False],
        "pymalloc": [True, False],
        "with_bz2": [True, False],
        "with_gdbm": [True, False],
        "with_nis": [True, False],
        "with_sqlite3": [True, False],
        "with_tkinter": [True, False],
        "with_curses": [True, False],

        # Python 2 options
        "unicode": ["ucs2", "ucs4"],
        "with_bsddb": [True, False],
        # Python 3 options
        "with_lzma": [True, False],

        # options that don't change package id
        "env_vars": [True, False],  # set environment variables
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "optimizations": False,
        "lto": False,
        "docstrings": True,
        "pymalloc": True,
        "with_bz2": True,
        "with_gdbm": True,
        "with_nis": False,
        "with_sqlite3": True,
        "with_tkinter": True,
        "with_curses": True,

        # Python 2 options
        "unicode": "ucs2",
        "with_bsddb": False,  # True,  # FIXME: libdb package missing (#5309/#5392)
        # Python 3 options
        "with_lzma": True,

        # options that don't change package id
        "env_vars": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _version_number_only(self):
        return re.match(r"^([0-9.]+)", self.version).group(1)

    @property
    def _version_tuple(self):
        return tuple(self._version_number_only.split("."))

    @property
    def _supports_modules(self):
        return self.settings.compiler != "Visual Studio" or self.options.shared

    @property
    def _version_suffix(self):
        if self.settings.compiler == "Visual Studio":
            joiner = ""
        else:
            joiner = "."
        return joiner.join(self._version_tuple[:2])

    @property
    def _is_py3(self):
        return tools.scm.Version(self, self._version_number_only).major == "3"

    @property
    def _is_py2(self):
        return tools.scm.Version(self, self._version_number_only).major == "2"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            del self.options.lto
            del self.options.docstrings
            del self.options.pymalloc
            del self.options.with_curses
            del self.options.with_gdbm
            del self.options.with_nis
        if self._is_py2:
            # Python 2.xx does not support following options
            del self.options.with_lzma
        elif self._is_py3:
            # Python 3.xx does not support following options
            del self.options.with_bsddb
            del self.options.unicode

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self._supports_modules:
                del self.options.with_bz2
                del self.options.with_sqlite3
                del self.options.with_tkinter

                del self.options.with_bsddb
                del self.options.with_lzma
        if self.settings.compiler == "Visual Studio":
            # The msbuild generator only works with Visual Studio
            self.generators.append("MSBuildDeps")

    def validate(self):
        if self.options.shared:
            if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("cpython does not support MT(d) runtime when building a shared cpython library")
        if self.settings.compiler == "Visual Studio":
            if self.options.optimizations:
                raise ConanInvalidConfiguration("This recipe does not support optimized MSVC cpython builds (yet)")
                # FIXME: should probably throw when cross building
                # FIXME: optimizations for Visual Studio, before building the final `build_type`:
                # 1. build the MSVC PGInstrument build_type,
                # 2. run the instrumented binaries, (PGInstrument should have created a `python.bat` file in the PCbuild folder)
                # 3. build the MSVC PGUpdate build_type
            if self.settings.build_type == "Debug" and "d" not in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("Building debug cpython requires a debug runtime (Debug cpython requires _CrtReportMode symbol, which only debug runtimes define)")
            if self._is_py2:
                if self.settings.compiler.version >= tools.scm.Version(self, "14"):
                    self.output.warn("Visual Studio versions 14 and higher were never officially supported by the CPython developers")
            if str(self.settings.arch) not in self._msvc_archs:
                raise ConanInvalidConfiguration("Visual Studio does not support this architecture")

            if not self.options.shared and tools.scm.Version(self, self._version_number_only) >= "3.10":
                raise ConanInvalidConfiguration("Static msvc build disabled (>=3.10) due to \"AttributeError: module 'sys' has no attribute 'winver'\"")

        if self.options.get_safe("with_curses", False) and not self.options["ncurses"].with_widec:
            raise ConanInvalidConfiguration("cpython requires ncurses with wide character support")

    def package_id(self):
        del self.info.options.env_vars

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _with_libffi(self):
        # cpython 3.7.x on MSVC uses an ancient libffi 2.00-beta (which is not available at cci, and is API/ABI incompatible with current 3.2+)
        return self._supports_modules \
               and (self.settings.compiler != "Visual Studio" or tools.scm.Version(self, self._version_number_only) >= "3.8")

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self._supports_modules:
            self.requires("openssl/1.1.1l")
            self.requires("expat/2.4.1")
            if self._with_libffi:
                self.requires("libffi/3.2.1")
            if tools.scm.Version(self, self._version_number_only) < "3.8":
                self.requires("mpdecimal/2.4.2")
            elif tools.scm.Version(self, self._version_number_only) < "3.10":
                self.requires("mpdecimal/2.5.0")
            else:
                self.requires("mpdecimal/2.5.0")  # FIXME: no 2.5.1 to troubleshoot apple
        if self.settings.os != "Windows":
            if not tools.is_apple_os(self, self.settings.os):
                self.requires("libuuid/1.0.3")
            self.requires("libxcrypt/4.4.25")
        if self.options.get_safe("with_bz2"):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_gdbm", False):
            self.requires("gdbm/1.19")
        if self.options.get_safe("with_nis", False):
            # TODO: Add nis when available.
            raise ConanInvalidConfiguration("nis is not available on CCI (yet)")
        if self.options.get_safe("with_sqlite3"):
            self.requires("sqlite3/3.36.0")
        if self.options.get_safe("with_tkinter"):
            self.requires("tk/8.6.10")
        if self.options.get_safe("with_curses", False):
            self.requires("ncurses/6.2")
        if self.options.get_safe("with_bsddb", False):
            self.requires("libdb/5.3.28")
        if self.options.get_safe("with_lzma", False):
            self.requires("xz_utils/5.2.5")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--with-doc-strings={}".format(yes_no(self.options.docstrings)),
            "--with-pymalloc={}".format(yes_no(self.options.pymalloc)),
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-optimizations={}".format(yes_no(self.options.optimizations)),
            "--with-lto={}".format(yes_no(self.options.lto)),
            "--with-pydebug={}".format(yes_no(self.settings.build_type == "Debug")),
        ]
        if self._is_py2:
            conf_args.extend([
                "--enable-unicode={}".format(yes_no(self.options.unicode)),
            ])
        if self._is_py3:
            conf_args.extend([
                "--with-system-libmpdec",
                "--with-openssl={}".format(self.deps_cpp_info["openssl"].rootpath),
                "--enable-loadable-sqlite-extensions={}".format(yes_no(not self.options["sqlite3"].omit_load_extension)),
            ])
        if self.settings.compiler == "intel":
            conf_args.extend(["--with-icc"])
        if tools.get_env("CC") or self.settings.compiler != "gcc":
            conf_args.append("--without-gcc")
        if self.options.with_tkinter:
            tcltk_includes = []
            tcltk_libs = []
            # FIXME: collect using some conan util (https://github.com/conan-io/conan/issues/7656)
            for dep in ("tcl", "tk", "zlib"):
                tcltk_includes += ["-I{}".format(d) for d in self.deps_cpp_info[dep].include_paths]
                tcltk_libs += ["-l{}".format(lib) for lib in self.deps_cpp_info[dep].libs]
            if self.settings.os == "Linux" and not self.options["tk"].shared:
                # FIXME: use info from xorg.components (x11, xscrnsaver)
                tcltk_libs.extend(["-l{}".format(lib) for lib in ("X11", "Xss")])
            conf_args.extend([
                "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
                "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
            ])
        if self.settings.os in ("Linux", "FreeBSD"):
            # Building _testembed fails due to missing pthread/rt symbols
            self._autotools.link_flags.append("-lpthread")

        build = None
        if tools.build.cross_building(self, self) and not tools.build.cross_building(self, self, skip_x64_x86=True):
            # Building from x86_64 to x86 is not a "real" cross build, so set build == host
            build = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder, build=build)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches",{}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self._is_py3 and tools.scm.Version(self, self._version_number_only) < "3.10":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "setup.py"),
                                  ":libmpdec.so.2", "mpdec")
        if self.settings.compiler == "Visual Studio":
            runtime_library = {
                "MT": "MultiThreaded",
                "MTd": "MultiThreadedDebug",
                "MD": "MultiThreadedDLL",
                "MDd": "MultiThreadedDebugDLL",
            }[str(self.settings.compiler.runtime)]
            self.output.info("Patching runtime")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pyproject.props"),
                                  "MultiThreadedDLL", runtime_library)
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pyproject.props"),
                                  "MultiThreadedDebugDLL", runtime_library)

        # Remove vendored packages
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Modules", "_decimal", "libmpdec"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Modules", "expat"))

        if self.options.get_safe("with_curses", False):
            # FIXME: this will link to ALL libraries of ncurses. Only need to link to ncurses(w) (+ eventually tinfo)
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "setup.py"),
                                  "curses_libs = ",
                                  "curses_libs = {} #".format(repr(self.deps_cpp_info["ncurses"].libs + self.deps_cpp_info["ncurses"].system_libs)))

        # Enable static MSVC cpython
        if not self.options.shared:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pythoncore.vcxproj"),
                                  "<PreprocessorDefinitions>","<PreprocessorDefinitions>Py_NO_BUILD_SHARED;")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pythoncore.vcxproj"),
                                  "Py_ENABLE_SHARED", "Py_NO_ENABLE_SHARED")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pythoncore.vcxproj"),
                                  "DynamicLibrary", "StaticLibrary")

            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "python.vcxproj"),
                                  "<Link>", "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "python.vcxproj"),
                                  "<PreprocessorDefinitions>", "<PreprocessorDefinitions>Py_NO_ENABLE_SHARED;")

            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pythonw.vcxproj"),
                                  "<Link>", "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PCbuild", "pythonw.vcxproj"),
                                  "<ItemDefinitionGroup>", "<ItemDefinitionGroup><ClCompile><PreprocessorDefinitions>Py_NO_ENABLE_SHARED;%(PreprocessorDefinitions)</PreprocessorDefinitions></ClCompile>")

    def _upgrade_single_project_file(self, project_file):
        """
        `devenv /upgrade <project.vcxproj>` will upgrade *ALL* projects referenced by the project.
        By temporarily moving the solution project, only one project is upgraded
        This is needed for static cpython or for disabled optional dependencies (e.g. tkinter=False)
        Restore it afterwards because it is needed to build some targets.
        """
        tools.files.rename(self, os.path.join(self._source_subfolder, "PCbuild", "pcbuild.sln"),
                     os.path.join(self._source_subfolder, "PCbuild", "pcbuild.sln.bak"))
        tools.files.rename(self, os.path.join(self._source_subfolder, "PCbuild", "pcbuild.proj"),
                     os.path.join(self._source_subfolder, "PCbuild", "pcbuild.proj.bak"))
        with tools.vcvars(self.settings):
            self.run("devenv \"{}\" /upgrade".format(project_file), run_environment=True)
        tools.files.rename(self, os.path.join(self._source_subfolder, "PCbuild", "pcbuild.sln.bak"),
                     os.path.join(self._source_subfolder, "PCbuild", "pcbuild.sln"))
        tools.files.rename(self, os.path.join(self._source_subfolder, "PCbuild", "pcbuild.proj.bak"),
                     os.path.join(self._source_subfolder, "PCbuild", "pcbuild.proj"))

    @property
    def _solution_projects(self):
        if self.options.shared:
            solution_path = os.path.join(self._source_subfolder, "PCbuild", "pcbuild.sln")
            projects = set(m.group(1) for m in re.finditer("\"([^\"]+)\\.vcxproj\"", open(solution_path).read()))

            def project_build(name):
                if os.path.basename(name) in self._msvc_discarded_projects:
                    return False
                if "test" in name:
                    return False
                return True

            def sort_importance(key):
                importance = (
                    "pythoncore",   # The python library MUST be built first. All modules and executables depend on it
                    "python",       # Build the python executable next (for convenience, when debugging)
                )
                try:
                    return importance.index(key)
                except ValueError:
                    return len(importance)

            projects = sorted((p for p in projects if project_build(p)), key=sort_importance)
            return projects
        else:
            return "pythoncore", "python", "pythonw"

    @property
    def _msvc_discarded_projects(self):
        discarded = {"python_uwp", "pythonw_uwp"}
        if not self.options.with_bz2:
            discarded.add("bz2")
        if not self.options.with_sqlite3:
            discarded.add("_sqlite3")
        if not self.options.with_tkinter:
            discarded.add("_tkinter")
        if self._is_py2:
            # Python 2 Visual Studio projects NOT to build
            discarded = discarded.union({"bdist_wininst", "libeay", "ssleay", "sqlite3", "tcl", "tk", "tix"})
            if not self.options.with_bsddb:
                discarded.add("_bsddb")
        elif self._is_py3:
            discarded = discarded.union({"bdist_wininst", "liblzma", "openssl", "sqlite3", "xxlimited"})
            if not self.options.with_lzma:
                discarded.add("_lzma")
        return discarded

    @property
    def _msvc_archs(self):
        archs = {
            "x86": "Win32",
            "x86_64": "x64",
        }
        if tools.scm.Version(self, self._version_number_only) >= "3.8":
            archs.update({
                "armv7": "ARM",
                "armv8_32": "ARM",
                "armv8": "ARM64",
            })
        return archs

    def _msvc_build(self):
        msbuild = MSBuild(self)
        msbuild_properties = {
            "IncludeExternals": "true",
        }
        projects = self._solution_projects
        self.output.info("Building {} Visual Studio projects: {}".format(len(projects), projects))

        with tools.no_op():
            for project_i, project in enumerate(projects, 1):
                self.output.info("[{}/{}] Building project '{}'...".format(project_i, len(projects), project))
                project_file = os.path.join(self._source_subfolder, "PCbuild", project + ".vcxproj")
                self._upgrade_single_project_file(project_file)
                msbuild.build(project_file, upgrade_project=False, build_type="Debug" if self.settings.build_type == "Debug" else "Release",
                              platforms=self._msvc_archs, properties=msbuild_properties)

    def build(self):
        # FIXME: these checks belong in validate, but the versions of dependencies are not available there yet
        if self._supports_modules:
            if tools.scm.Version(self, self._version_number_only) < "3.8.0":
                if tools.scm.Version(self, self.deps_cpp_info["mpdecimal"].version) >= "2.5.0":
                    raise ConanInvalidConfiguration("cpython versions lesser then 3.8.0 require a mpdecimal lesser then 2.5.0")
            elif tools.scm.Version(self, self._version_number_only) >= "3.9.0":
                if tools.scm.Version(self, self.deps_cpp_info["mpdecimal"].version) < "2.5.0":
                    raise ConanInvalidConfiguration("cpython 3.9.0 (and newer) requires (at least) mpdecimal 2.5.0")

        if self._with_libffi:
            if tools.scm.Version(self, self.deps_cpp_info["libffi"].version) >= "3.3" and self.settings.compiler == "Visual Studio" and "d" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration("libffi versions >= 3.3 cause 'read access violations' when using a debug runtime (MTd/MDd)")

        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._msvc_build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _msvc_artifacts_path(self):
        build_subdir_lut = {
            "x86_64": "amd64",
            "x86": "win32",
        }
        if tools.scm.Version(self, self._version_number_only) >= "3.8":
            build_subdir_lut.update({
                "armv7": "arm32",
                "armv8_32": "arm32",
                "armv8": "arm64",
            })
        return os.path.join(self._source_subfolder, "PCbuild", build_subdir_lut[str(self.settings.arch)])

    @property
    def _msvc_install_subprefix(self):
        return "bin"

    def _copy_essential_dlls(self):
        if self.settings.compiler == "Visual Studio":
            # Until MSVC builds support cross building, copy dll's of essential (shared) dependencies to python binary location.
            # These dll's are required when running the layout tool using the newly built python executable.
            dest_path = os.path.join(self.build_folder, self._msvc_artifacts_path)
            if self._with_libffi:
                for bin_path in self.deps_cpp_info["libffi"].bin_paths:
                    self.copy("*.dll", src=bin_path, dst=dest_path)
            for bin_path in self.deps_cpp_info["expat"].bin_paths:
                self.copy("*.dll", src=bin_path, dst=dest_path)
            for bin_path in self.deps_cpp_info["zlib"].bin_paths:
                self.copy("*.dll", src=bin_path, dst=dest_path)

    def _msvc_package_layout(self):
        self._copy_essential_dlls()
        install_prefix = os.path.join(self.package_folder, self._msvc_install_subprefix)
        tools.files.mkdir(self, install_prefix)
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        # FIXME: if cross building, use a build python executable here
        python_built = os.path.join(build_path, "python{}.exe".format(infix))
        layout_args = [
            os.path.join(self._source_subfolder, "PC", "layout", "main.py"),
            "-v",
            "-s", self._source_subfolder,
            "-b", build_path,
            "--copy", install_prefix,
            "-p",
            "--include-pip",
            "--include-venv",
            "--include-dev",
        ]
        if self.options.with_tkinter:
            layout_args.append("--include-tcltk")
        if self.settings.build_type == "Debug":
            layout_args.append("-d")
        python_args = " ".join("\"{}\"".format(a) for a in layout_args)
        self.run("{} {}".format(python_built, python_args), run_environment=True)

        tools.files.rmdir(self, os.path.join(self.package_folder, "bin", "tcl"))

        for file in os.listdir(install_prefix):
            if re.match("vcruntime.*", file):
                os.unlink(os.path.join(install_prefix, file))
                continue
        os.unlink(os.path.join(install_prefix, "LICENSE.txt"))
        for file in os.listdir(os.path.join(install_prefix, "libs")):
            if not re.match("python.*", file):
                os.unlink(os.path.join(install_prefix, "libs", file))

    def _msvc_package_copy(self):
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        self.copy("*.exe", src=build_path, dst=os.path.join(self.package_folder, self._msvc_install_subprefix))
        self.copy("*.dll", src=build_path, dst=os.path.join(self.package_folder, self._msvc_install_subprefix))
        self.copy("*.pyd", src=build_path, dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "DLLs"))
        self.copy("python{}{}.lib".format(self._version_suffix, infix), src=build_path, dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "libs"))
        self.copy("*", src=os.path.join(self._source_subfolder, "Include"), dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "include"))
        self.copy("pyconfig.h", src=os.path.join(self._source_subfolder, "PC"), dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "include"))
        self.copy("*.py", src=os.path.join(self._source_subfolder, "lib"), dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "Lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, self._msvc_install_subprefix, "Lib", "test"))

        packages = {}
        get_name_version = lambda fn: fn.split(".", 2)[:2]
        whldir = os.path.join(self._source_subfolder, "Lib", "ensurepip", "_bundled")
        for fn in filter(lambda n: n.endswith(".whl"), os.listdir(whldir)):
            name, version = get_name_version(fn)
            add = True
            if name in packages:
                pname, pversion = get_name_version(packages[name])
                add = tools.scm.Version(self, version) > tools.scm.Version(self, pversion)
            if add:
                packages[name] = fn
        for fname in packages.values():
            tools.files.unzip(self, filename=os.path.join(whldir, fname), destination=os.path.join(self.package_folder, "bin", "Lib", "site-packages"))

        self.run("{} -c \"import compileall; compileall.compile_dir('{}')\"".format(os.path.join(build_path, self._cpython_interpreter_name), os.path.join(self.package_folder, self._msvc_install_subprefix, "Lib").replace("\\", "/")),
                 run_environment=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            if self._is_py2 or not self.options.shared:
                self._msvc_package_copy()
            else:
                self._msvc_package_layout()
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "vcruntime*")
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

            # Rewrite shebangs of python scripts
            for filename in os.listdir(os.path.join(self.package_folder, "bin")):
                filepath = os.path.join(self.package_folder, "bin", filename)
                if not os.path.isfile(filepath):
                    continue
                if os.path.islink(filepath):
                    continue
                with open(filepath, "rb") as fn:
                    firstline = fn.readline(1024)
                    if not(firstline.startswith(b"#!") and b"/python" in firstline and b"/bin/sh" not in firstline):
                        continue
                    text = fn.read()
                self.output.info("Rewriting shebang of {}".format(filename))
                with open(filepath, "wb") as fn:
                    fn.write(textwrap.dedent("""\
                        #!/bin/sh
                        ''':'
                        __file__="$0"
                        while [ -L "$__file__" ]; do
                            __file__="$(dirname "$__file__")/$(readlink "$__file__")"
                        done
                        exec "$(dirname "$__file__")/python{}" "$0" "$@"
                        '''
                        """.format(self._version_suffix)).encode())
                    fn.write(text)

            if not os.path.exists(self._cpython_symlink):
                os.symlink("python{}".format(self._version_suffix), self._cpython_symlink)
        self._fix_install_name()

    @property
    def _cpython_symlink(self):
        symlink = os.path.join(self.package_folder, "bin", "python")
        if self.settings.os == "Windows":
            symlink += ".exe"
        return symlink

    @property
    def _cpython_interpreter_name(self):
        if self.settings.compiler == "Visual Studio":
            suffix = ""
        else:
            suffix = self._version_suffix
        python = "python{}".format(suffix)
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                python += "_d"
        if self.settings.os == "Windows":
            python += ".exe"
        return python

    @property
    def _cpython_interpreter_path(self):
        return os.path.join(self.package_folder, "bin", self._cpython_interpreter_name)

    @property
    def _abi_suffix(self):
        res = ""
        if self._is_py3:
            if self.settings.build_type == "Debug":
                res += "d"
            if tools.scm.Version(self, self._version_number_only) < "3.8":
                if self.options.get_safe("pymalloc", False):
                    res += "m"
        return res

    @property
    def _lib_name(self):
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                lib_ext = "_d"
            else:
                lib_ext = ""
        else:
            lib_ext = self._abi_suffix + (".dll.a" if self.options.shared and self.settings.os == "Windows" else "")
        return "python{}{}".format(self._version_suffix, lib_ext)

    def _fix_install_name(self):
        if tools.is_apple_os(self, self.settings.os) and self.options.shared:
            buffer = StringIO()
            python = os.path.join(self.package_folder, "bin", "python")
            self.run('otool -L "%s"' % python, output=buffer)
            lines = buffer.getvalue().strip().split('\n')[1:]
            for line in lines:
                library = line.split()[0]
                if library.startswith(self.package_folder):
                    new = library.replace(self.package_folder, "@executable_path/..")
                    self.output.info("patching {}, replace {} with {}".format(python, library, new))
                    self.run("install_name_tool -change {} {} {}".format(library, new, python))

    def package_info(self):
        # FIXME: conan components Python::Interpreter component, need a target type
        # self.cpp_info.names["cmake_find_package"] = "Python"
        # self.cpp_info.names["cmake_find_package_multi"] = "Python"
        # FIXME: conan components need to generate multiple .pc files (python2, python-27)

        py_version = tools.scm.Version(self, self._version_number_only)
        # python component: "Build a C extension for Python"
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["python"].includedirs = [os.path.join(self._msvc_install_subprefix, "include")]
            libdir = os.path.join(self._msvc_install_subprefix, "libs")
        else:
            self.cpp_info.components["python"].includedirs.append(os.path.join("include", "python{}{}".format(self._version_suffix, self._abi_suffix)))
            libdir = "lib"
        if self.options.shared:
            self.cpp_info.components["python"].defines.append("Py_ENABLE_SHARED")
        else:
            self.cpp_info.components["python"].defines.append("Py_NO_ENABLE_SHARED")
            if self.settings.os == "Linux":
                self.cpp_info.components["python"].system_libs.extend(["dl", "m", "pthread", "util"])
            elif self.settings.os == "Windows":
                self.cpp_info.components["python"].system_libs.extend(["pathcch", "shlwapi", "version", "ws2_32"])
        self.cpp_info.components["python"].requires = ["zlib::zlib"]
        if self.settings.os != "Windows":
            self.cpp_info.components["python"].requires.append("libxcrypt::libxcrypt")
        self.cpp_info.components["python"].names["pkg_config"] = "python-{}.{}".format(py_version.major, py_version.minor)
        self.cpp_info.components["python"].libdirs = []

        self.cpp_info.components["_python_copy"].names["pkg_config"] = "python{}".format(py_version.major)
        self.cpp_info.components["_python_copy"].requires = ["python"]
        self.cpp_info.components["_python_copy"].libdirs = []

        # embed component: "Embed Python into an application"
        self.cpp_info.components["embed"].libs = [self._lib_name]
        self.cpp_info.components["embed"].libdirs = [libdir]
        self.cpp_info.components["embed"].names["pkg_config"] = "python-{}.{}-embed".format(py_version.major, py_version.minor)
        self.cpp_info.components["embed"].requires = ["python"]

        self.cpp_info.components["_embed_copy"].requires = ["embed"]
        self.cpp_info.components["_embed_copy"].names["pkg_config"] = ["python{}-embed".format(py_version.major)]
        self.cpp_info.components["_embed_copy"].libdirs = []

        if self._supports_modules:
            # hidden components: the C extensions of python are built as dynamically loaded shared libraries.
            # C extensions or applications with an embedded Python should not need to link to them..
            self.cpp_info.components["_hidden"].requires = [
                "openssl::openssl",
                "expat::expat",
                "mpdecimal::mpdecimal",
            ]
            if self._with_libffi:
                self.cpp_info.components["_hidden"].requires.append("libffi::libffi")
            if self.settings.os != "Windows":
                if not tools.is_apple_os(self, self.settings.os):
                    self.cpp_info.components["_hidden"].requires.append("libuuid::libuuid")
                self.cpp_info.components["_hidden"].requires.append("libxcrypt::libxcrypt")
            if self.options.with_bz2:
                self.cpp_info.components["_hidden"].requires.append("bzip2::bzip2")
            if self.options.get_safe("with_gdbm", False):
                self.cpp_info.components["_hidden"].requires.append("gdbm::gdbm")
            if self.options.with_sqlite3:
                self.cpp_info.components["_hidden"].requires.append("sqlite3::sqlite3")
            if self.options.get_safe("with_curses", False):
                self.cpp_info.components["_hidden"].requires.append("ncurses::ncurses")
            if self.options.get_safe("with_bsddb"):
                self.cpp_info.components["_hidden"].requires.append("libdb::libdb")
            if self.options.get_safe("with_lzma"):
                self.cpp_info.components["_hidden"].requires.append("xz_utils::xz_utils")
            if self.options.get_safe("with_tkinter"):
                self.cpp_info.components["_hidden"].requires.append("tk::tk")
            self.cpp_info.components["_hidden"].libdirs = []

        if self.options.env_vars:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)

        python = self._cpython_interpreter_path
        self.user_info.python = python
        if self.options.env_vars:
            self.output.info("Setting PYTHON environment variable: {}".format(python))
            self.env_info.PYTHON = python

        if self.settings.compiler == "Visual Studio":
            pythonhome = os.path.join(self.package_folder, "bin")
        elif tools.is_apple_os(self, self.settings.os):
            pythonhome = self.package_folder
        else:
            version = tools.scm.Version(self, self._version_number_only)
            pythonhome = os.path.join(self.package_folder, "lib", "python{}.{}".format(version.major, version.minor))
        self.user_info.pythonhome = pythonhome

        pythonhome_required = self.settings.compiler == "Visual Studio" or tools.is_apple_os(self, self.settings.os)
        self.user_info.module_requires_pythonhome = pythonhome_required

        if self.settings.compiler == "Visual Studio":
            if self.options.env_vars:
                self.output.info("Setting PYTHONHOME environment variable: {}".format(pythonhome))
                self.env_info.PYTHONHOME = pythonhome

        if self._is_py2:
            python_root = ""
        else:
            python_root = self.package_folder
            if self.options.env_vars:
                self.output.info("Setting PYTHON_ROOT environment variable: {}".format(python_root))
                self.env_info.PYTHON_ROOT = python_root
        self.user_info.python_root = python_root
