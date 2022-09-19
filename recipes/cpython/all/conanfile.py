import os
import re
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, load, replace_in_file, rmdir, rename, mkdir, apply_conandata_patches, rm, unzip, \
    copy, save
from conan.tools.gnu import AutotoolsToolchain, PkgConfigDeps, AutotoolsDeps, Autotools
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.microsoft import MSBuild, is_msvc, msvc_runtime_flag, MSBuildDeps, MSBuildToolchain, VCVars
from conan.tools.scm import Version
from conans.tools import get_gnu_triplet

required_conan_version = ">=1.51.3"


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

    @property
    def _supports_modules(self):
        return not is_msvc(self) or self.options.shared

    @property
    def _is_py3(self):
        return Version(self.version).major == "3"

    @property
    def _is_py2(self):
        return Version(self.version).major == "2"

    @property
    def _version_suffix(self):
        version = Version(self.version)
        joiner = "" if is_msvc(self) else "."
        return f"{version.major}{joiner}{version.minor}"

    @property
    def _msvc_archs(self):
        archs = {
            "x86": "Win32",
            "x86_64": "x64",
        }
        if Version(self.version) >= "3.8":
            archs.update({
                "armv7": "ARM",
                "armv8_32": "ARM",
                "armv8": "ARM64",
            })
        return archs

    @property
    def _with_libffi(self):
        # cpython 3.7.x on MSVC uses an ancient libffi 2.00-beta (which is not available at cci, and is API/ABI incompatible with current 3.2+)
        return self._supports_modules and (is_msvc(self) or Version(self.version) >= "3.8")

    @property
    def _msvc_discarded_projects(self):
        discarded = {"python_uwp", "pythonw_uwp"}
        if not self.options.get_safe("with_bz2", False):
            discarded.add("bz2")
        if not self.options.get_safe("with_sqlite3", False):
            discarded.add("_sqlite3")
        if not self.options.get_safe("with_tkinter", False):
            discarded.add("_tkinter")
        if self._is_py2:
            # Python 2 Visual Studio projects NOT to build
            discarded = discarded.union({"bdist_wininst", "libeay", "ssleay", "sqlite3", "tcl", "tk", "tix"})
            if not self.options.get_safe("with_bsddb", False):
                discarded.add("_bsddb")
        elif self._is_py3:
            discarded = discarded.union({"bdist_wininst", "liblzma", "openssl", "sqlite3", "xxlimited"})
            if not self.options.get_safe("with_lzma", False):
                discarded.add("_lzma")
        return discarded

    @property
    def _solution_projects(self):
        if self.options.shared:
            solution_path = self.source_path.joinpath("PCbuild", "pcbuild.sln")
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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_gdbm
        if is_msvc(self):
            del self.options.lto
            del self.options.docstrings
            del self.options.pymalloc
            del self.options.with_curses
            del self.options.with_nis
        if self._is_py2:
            # Python 2.xx does not support following options
            del self.options.with_lzma
        elif self._is_py3:
            # Python 3.xx does not support following options
            del self.options.with_bsddb
            del self.options.unicode

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC  # once removed by config_options, need try..except for a second del
            except ValueError:
                pass
        if not self._supports_modules:
            del self.options.with_bz2
            del self.options.with_sqlite3
            del self.options.with_tkinter
            try:
                del self.options.with_bsddb
            except ValueError:
                pass
            try:
                del self.options.with_lzma
            except ValueError:
                pass
        try:
            del self.settings.compiler.libcxx
        except ValueError:
            pass
        try:
            del self.settings.compiler.cppstd
        except ValueError:
            pass

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
            self.folders.generators = "PCbuild"
        else:
            basic_layout(self, src_folder="cpython")  # src_folder must use the same source folder name the project

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self._supports_modules:
            self.requires("openssl/1.1.1q")
            self.requires("expat/2.4.8")
            if self._with_libffi:
                self.requires("libffi/3.4.2")
            if Version(self.version) < "3.8":
                self.requires("mpdecimal/2.4.2")
            elif Version(self.version) < "3.10":
                self.requires("mpdecimal/2.5.0")
            else:
                self.requires("mpdecimal/2.5.0")  # FIXME: no 2.5.1 to troubleshoot apple
        if self.settings.os != "Windows":
            self.requires("libxcrypt/4.4.28")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")
        if self.options.get_safe("with_bz2", False):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_gdbm", False):
            self.requires("gdbm/1.19")
        if self.options.get_safe("with_nis", False):
            # TODO: Add nis when available.
            raise ConanInvalidConfiguration("nis is not available on CCI (yet)")
        if self.options.get_safe("with_sqlite3", False):
            self.requires("sqlite3/3.39.2")
        if self.options.get_safe("with_tkinter", False):
            self.requires("tk/8.6.10")
        if self.options.get_safe("with_curses", False):
            self.requires("ncurses/6.3")
        if self.options.get_safe("with_bsddb", False):
            self.requires("libdb/5.3.28")
        if self.options.get_safe("with_lzma", False):
            self.requires("xz_utils/5.2.5")

    def package_id(self):
        del self.info.options.env_vars

    def validate(self):
        if is_msvc(self):
            if self.options.shared and "MT" in msvc_runtime_flag(self):
                raise ConanInvalidConfiguration("cpython does not support MT(d) runtime when building a shared cpython library")
            if self.options.optimizations:
                raise ConanInvalidConfiguration("This recipe does not support optimized MSVC cpython builds (yet)")
                # FIXME: should probably throw when cross building
                # FIXME: optimizations for Visual Studio, before building the final `build_type`:
                # 1. build the MSVC PGInstrument build_type,
                # 2. run the instrumented binaries, (PGInstrument should have created a `python.bat` file in the PCbuild folder)
                # 3. build the MSVC PGUpdate build_type
            if self.settings.build_type == "Debug" and "d" not in msvc_runtime_flag(self):
                raise ConanInvalidConfiguration("Building debug cpython requires a debug runtime (Debug cpython requires _CrtReportMode symbol, which only debug runtimes define)")
            if self._is_py2:
                if self.settings.compiler.version >= Version("14"):
                    self.output.warn("Visual Studio versions 14 and higher were never officially supported by the CPython developers")
            if str(self.settings.arch) not in self._msvc_archs:
                raise ConanInvalidConfiguration("Visual Studio does not support this architecture")

            if not self.options.shared and Version(self.version) >= "3.10":
                raise ConanInvalidConfiguration("Static msvc build disabled (>=3.10) due to \"AttributeError: module 'sys' has no attribute 'winver'\"")

        if self.options.get_safe("with_curses", False) and not self.options["ncurses"].with_widec:
            raise ConanInvalidConfiguration("cpython requires ncurses with wide character support")

    def _validate_final(self):
        # FIXME: these checks belong in validate, but the versions of dependencies are not available there yet
        if self._supports_modules:
            if Version(self.version) < "3.8.0":
                if Version(self.deps_cpp_info["mpdecimal"].version) >= "2.5.0":
                    raise ConanInvalidConfiguration("cpython versions lesser then 3.8.0 require a mpdecimal lesser then 2.5.0")
            elif Version(self.version) >= "3.9.0":
                if Version(self.deps_cpp_info["mpdecimal"].version) < "2.5.0":
                    raise ConanInvalidConfiguration("cpython 3.9.0 (and newer) requires (at least) mpdecimal 2.5.0")

        if self._with_libffi:
            if Version(self.deps_cpp_info["libffi"].version) >= "3.3" and self.settings.compiler == "Visual Studio" and "d" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration("libffi versions >= 3.3 cause 'read access violations' when using a debug runtime (MTd/MDd)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            deps = MSBuildDeps(self)
            deps.generate()

            tc = MSBuildToolchain(self)
            tc.generate()

            vc = VCVars(self)
            vc.generate(scope="build")
        else:
            # autotools usually uses 'yes' and 'no' to enable/disable options
            yes_no = lambda v: "yes" if v else "no"
            # --fpic is automatically managed when 'fPIC'option is declared
            # --enable/disable-shared is automatically managed when 'shared' option is declared
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-shared={yes_no(self.options.get_safe('shared', False))}",
                f"--with-doc-strings={yes_no(self.options.get_safe('docstrings', False))}",
                f"--with-pymalloc={yes_no(self.options.get_safe('pymalloc', False))}",
                "--with-system-expat",
                "--with-system-ffi",
                f"--enable-optimizations={yes_no(self.options.get_safe('optimizations', False))}",
                f"--with-lto={yes_no(self.options.get_safe('lto', False))}",
                f"--with-pydebug={yes_no(self.settings.build_type == 'Debug')}",
            ])

            if self._is_py2:
                tc.configure_args.extend([
                    f"--enable-unicode={yes_no(self.options.get_safe('unicode', False))}",
                ])
            if self._is_py3:
                tc.configure_args.extend([
                    "--with-system-libmpdec",
                    f"--with-openssl={self.deps_cpp_info['openssl'].rootpath}",
                    f"--enable-loadable-sqlite-extensions={yes_no(not self.options['sqlite3'].omit_load_extension)}",
                ])
            if self.settings.compiler == "intel":
                tc.configure_args.append("--with-icc")
            if self.settings.compiler != "gcc":
                tc.configure_args.append("--without-gcc")

            if self.options.get_safe("with_tkinter", False):
                tcltk_includes = []
                tcltk_libs = []
                # FIXME: collect using some conan util (https://github.com/conan-io/conan/issues/7656)
                for dep in ("tcl", "tk", "zlib"):
                    tcltk_includes += ["-I{}".format(d) for d in self.deps_cpp_info[dep].include_paths]
                    tcltk_libs += ["-l{}".format(lib) for lib in self.deps_cpp_info[dep].libs]
                if self.settings.os == "Linux" and not self.options["tk"].shared:
                    # FIXME: use info from xorg.components (x11, xscrnsaver)
                    tcltk_libs.extend(["-l{}".format(lib) for lib in ("X11", "Xss")])
                tc.configure_args.extend([
                    "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
                    "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
                ])
            if self.settings.os in ("Linux", "FreeBSD"):
                # Building _testembed fails due to missing pthread/rt symbols
                tc.extra_ldflags.append("-lpthread")

            if cross_building(self) and not cross_building(self, skip_x64_x86=True):
                # Building from x86_64 to x86 is not a "real" cross build, so set build == host
                tc.configure_args.extend([
                    f"--build={get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))}",
                    ])

            tc.generate()
            # generate dependencies for pkg-config
            tc = PkgConfigDeps(self)
            tc.generate()
            # generate dependencies for autotools
            tc = AutotoolsDeps(self)
            tc.generate()

        # inject tools_require env vars in build context
        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

        if self._is_py3 and Version(self.version) < "3.10":
            replace_in_file(self, self.source_path.joinpath("setup.py"), ":libmpdec.so.2", "mpdec")
        if is_msvc(self):
            runtime_library = {
                "MT": "MultiThreaded",
                "MTd": "MultiThreadedDebug",
                "MD": "MultiThreadedDLL",
                "MDd": "MultiThreadedDebugDLL",
            }[str(msvc_runtime_flag(self))]
            self.output.info("Patching runtime")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pyproject.props"), "MultiThreadedDLL", runtime_library)
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pyproject.props"), "MultiThreadedDebugDLL", runtime_library)
            replace_in_file(self, self.source_path.joinpath("PCbuild", "Directory.Build.props"), "</Project>", "  <PropertyGroup>\n    <IncludeExternals>true</IncludeExternals>\n  </PropertyGroup>\n</Project>", runtime_library)

        # Remove vendored packages
        rmdir(self, self.source_path.joinpath("Modules", "_decimal", "libmpdec"))
        rmdir(self, self.source_path.joinpath("Modules", "expat"))

        if self.options.get_safe("with_curses", False):
            # FIXME: this will link to ALL libraries of ncurses. Only need to link to ncurses(w) (+ eventually tinfo)
            replace_in_file(self, self.source_path.joinpath("setup.py"),
                                  "curses_libs = ",
                                  f"curses_libs = {repr(self.deps_cpp_info['ncurses'].libs + self.deps_cpp_info['ncurses'].system_libs)} #")

        # Enable static MSVC cpython
        if not self.options.shared:
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythoncore.vcxproj"),
                                  "<PreprocessorDefinitions>","<PreprocessorDefinitions>Py_NO_BUILD_SHARED;")
            replace_in_file(self,self.source_path.joinpath("PCbuild", "pythoncore.vcxproj"),
                                  "Py_ENABLE_SHARED", "Py_NO_ENABLE_SHARED")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythoncore.vcxproj"),
                                  "DynamicLibrary", "StaticLibrary")

            replace_in_file(self, self.source_path.joinpath("PCbuild", "python.vcxproj"),
                                  "<Link>", "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "python.vcxproj"),
                                  "<PreprocessorDefinitions>", "<PreprocessorDefinitions>Py_NO_ENABLE_SHARED;")

            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythonw.vcxproj"),
                                  "<Link>", "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythonw.vcxproj"),
                                  "<ItemDefinitionGroup>", "<ItemDefinitionGroup><ClCompile><PreprocessorDefinitions>Py_NO_ENABLE_SHARED;%(PreprocessorDefinitions)</PreprocessorDefinitions></ClCompile>")

    def _upgrade_single_project_file(self, project_file):
        """
        `devenv /upgrade <project.vcxproj>` will upgrade *ALL* projects referenced by the project.
        By temporarily moving the solution project, only one project is upgraded
        This is needed for static cpython or for disabled optional dependencies (e.g. tkinter=False)
        Restore it afterwards because it is needed to build some targets.
        """
        rename(self, self.source_path.joinpath("PCbuild", "pcbuild.sln"),
                     self.source_path.joinpath("PCbuild", "pcbuild.sln.bak"))
        rename(self, self.source_path.joinpath("PCbuild", "pcbuild.proj"),
                     self.source_path.joinpath("PCbuild", "pcbuild.proj.bak"))
        self.run(f'devenv "{project_file}" /upgrade', run_environment=True)
        rename(self, self.source_path.joinpath("PCbuild", "pcbuild.sln.bak"),
                     self.source_path.joinpath("PCbuild", "pcbuild.sln"))
        rename(self, self.source_path.joinpath("PCbuild", "pcbuild.proj.bak"),
                     self.source_path.joinpath("PCbuild", "pcbuild.proj"))

    def build(self):
        self._validate_final()
        self._patch_sources()
        if is_msvc(self):
            projects = self._solution_projects
            self.output.info(f"Building {len(projects)} Visual Studio projects: {projects}")

            for project_i, project in enumerate(projects, 1):
                self.output.info(f"[{project_i}/{len(projects)}] Building project '{project}'...")
                project_file = self.source_path.joinpath("PCbuild", project + ".vcxproj")
                self._upgrade_single_project_file(project_file)
                msbuild = MSBuild(self)
                msbuild.build(sln=project_file)
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    @property
    def _msvc_artifacts_path(self):
        build_subdir_lut = {
            "x86_64": "amd64",
            "x86": "win32",
        }
        if Version(self.version) >= "3.8":
            build_subdir_lut.update({
                "armv7": "arm32",
                "armv8_32": "arm32",
                "armv8": "arm64",
            })
        return self.source_path.joinpath("PCbuild", build_subdir_lut[str(self.settings.arch)])

    @property
    def _msvc_install_subprefix(self):
        return "bin"

    def _copy_essential_dlls(self):
        if is_msvc(self):
            # Until MSVC builds support cross building, copy dll's of essential (shared) dependencies to python binary location.
            # These dll's are required when running the layout tool using the newly built python executable.
            dest_path = self.build_path.joinpath(self._msvc_artifacts_path)
            if self._with_libffi:
                for bin_path in self.deps_cpp_info["libffi"].bin_paths:
                    copy(self, "*.dll", src=bin_path, dst=dest_path)
            for bin_path in self.deps_cpp_info["expat"].bin_paths:
                copy(self, "*.dll", src=bin_path, dst=dest_path)
            for bin_path in self.deps_cpp_info["zlib"].bin_paths:
                copy(self, "*.dll", src=bin_path, dst=dest_path)

    def _msvc_package_layout(self):
        self._copy_essential_dlls()
        install_prefix = self.package_path.joinpath(self._msvc_install_subprefix)
        mkdir(self, install_prefix)
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        # FIXME: if cross building, use a build python executable here
        python_built = build_path.joinpath("python{}.exe".format(infix))
        layout_args = [
            self.source_path.joinpath("PC", "layout", "main.py"),
            "-v",
            "-s", self.source_path,
            "-b", build_path,
            "--copy", install_prefix,
            "-p",
            "--include-pip",
            "--include-venv",
            "--include-dev",
        ]
        if self.options.get_safe("with_tkinter", False):
            layout_args.append("--include-tcltk")
        if self.settings.build_type == "Debug":
            layout_args.append("-d")
        python_args = " ".join(f"\"{a}\"" for a in layout_args)
        self.run(f"{python_built} {python_args}", run_environment=True)

        rmdir(self, os.path.join(self.package_folder, "bin", "tcl"))

        for file in install_prefix.glob("**/vcruntime.*"):
            file.unlink()
        install_prefix.joinpath("LICENSE.txt").unlink(missing_ok=True)
        for file in install_prefix.joinpath("libs").glob("**/python.*"):
            file.unlink()

    def _msvc_package_copy(self):
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        copy(self, "*.exe", src=build_path, dst=self.package_path.joinpath(self._msvc_install_subprefix))
        copy(self, "*.dll", src=build_path, dst=self.package_path.joinpath(self._msvc_install_subprefix))
        copy(self, "*.pyd", src=build_path, dst=self.package_path.joinpath(self._msvc_install_subprefix, "DLLs"))
        copy(self, "python{}{}.lib".format(self._version_suffix, infix), src=build_path, dst=self.package_path.joinpath(self._msvc_install_subprefix, "libs"))
        copy(self, "*", src=self.source_path.joinpath("Include"), dst=self.package_path.joinpath(self._msvc_install_subprefix, "include"))
        copy(self, "pyconfig.h", src=self.source_path.joinpath("PC"), dst=self.package_path.joinpath(self._msvc_install_subprefix, "include"))
        copy(self, "*.py", src=self.source_path.joinpath("lib"), dst=self.package_path.joinpath(self._msvc_install_subprefix, "Lib"))
        rmdir(self, self.package_path.joinpath(self._msvc_install_subprefix, "Lib", "test"))

        packages = {}
        get_name_version = lambda fn: fn.split(".", 2)[:2]
        whldir = self.source_path.joinpath("Lib", "ensurepip", "_bundled")
        for fn in whldir.glob("**/*.whl"):
            name, version = get_name_version(fn)
            add = True
            if name in packages:
                pname, pversion = get_name_version(packages[name])
                add = Version(version) > Version(pversion)
            if add:
                packages[name] = fn
        for fname in packages.values():
            unzip(self, filename=os.path.join(whldir, fname), destination=self.package_path.joinpath("bin", "Lib", "site-packages"))

        self.run(f"{build_path.joinpath(self._cpython_interpreter_name)} -c \"import compileall; compileall.compile_dir('{self.package_path.joinpath(self._msvc_install_subprefix, 'Lib')}')\"",
                 run_environment=True)

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst="licenses")
        if is_msvc(self):
            if self._is_py2 or not self.options.shared:
                self._msvc_package_copy()
            else:
                self._msvc_package_layout()
            rm(self, "vcruntime*", os.path.join(self.package_folder, "bin"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

            # Rewrite shebangs of python scripts
            for file in self.package_path.joinpath("bin").glob("**/*"):
                if not file.is_file() or file.is_symlink():
                    continue
                text = load(self, file)
                firstline = text.splitlines()[0]
                if not (firstline.startswith(b"#!") and b"/python" in firstline and b"/bin/sh" not in firstline):
                    continue
                self.output.info("Rewriting shebang of {}".format(file))
                content = textwrap.dedent(f"""\
                        #!/bin/sh
                        ''':'
                        __file__="$0"
                        while [ -L "$__file__" ]; do
                            __file__="$(dirname "$__file__")/$(readlink "$__file__")"
                        done
                        exec "$(dirname "$__file__")/python{self._version_suffix}" "$0" "$@"
                        '''
                        """)
                save(self, file, content)

            if not self._cpython_symlink.exists():
                self._cpython_symlink.symlink_to(self._cpython_interpreter_path)
        if is_apple_os(self):
            fix_apple_shared_install_name(self)

    @property
    def _cpython_symlink(self):
        ext = ".exe" if self.settings.os == "Windows" else ""
        symlink = self.package_path.joinpath("bin", f"python{ext}")
        return symlink

    @property
    def _cpython_interpreter_name(self):
        if is_msvc(self):
            suffix = ""
        else:
            suffix = self._version_suffix
        python = "python{}".format(suffix)
        if is_msvc(self):
            if self.settings.build_type == "Debug":
                python += "_d"
        if self.settings.os == "Windows":
            python += ".exe"
        return python

    @property
    def _cpython_interpreter_path(self):
        return self.package_path.joinpath("bin", self._cpython_interpreter_name)

    @property
    def _abi_suffix(self):
        res = ""
        if self._is_py3:
            if self.settings.build_type == "Debug":
                res += "d"
            if Version(self.version) < "3.8":
                if self.options.get_safe("pymalloc", False):
                    res += "m"
        return res

    @property
    def _lib_name(self):
        if is_msvc(self):
            if self.settings.build_type == "Debug":
                lib_ext = "_d"
            else:
                lib_ext = ""
        else:
            lib_ext = self._abi_suffix + (".dll.a" if self.options.shared and self.settings.os == "Windows" else "")
        return f"python{self._version_suffix}{lib_ext}"

    def package_info(self):
        # FIXME: conan components Python::Interpreter component, need a target type
        # self.cpp_info.names["cmake_find_package"] = "Python"
        # self.cpp_info.names["cmake_find_package_multi"] = "Python"
        # FIXME: conan components need to generate multiple .pc files (python2, python-27)

        py_version = Version(self.version)
        # python component: "Build a C extension for Python"
        if is_msvc(self):
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
        self.cpp_info.components["_python_copy"].includedirs = []

        # embed component: "Embed Python into an application"
        self.cpp_info.components["embed"].libs = [self._lib_name]
        self.cpp_info.components["embed"].libdirs = [libdir]
        self.cpp_info.components["embed"].includedirs = []
        self.cpp_info.components["embed"].names["pkg_config"] = "python-{}.{}-embed".format(py_version.major, py_version.minor)
        self.cpp_info.components["embed"].requires = ["python"]

        self.cpp_info.components["_embed_copy"].requires = ["embed"]
        self.cpp_info.components["_embed_copy"].names["pkg_config"] = ["python{}-embed".format(py_version.major)]
        self.cpp_info.components["_embed_copy"].libdirs = []
        self.cpp_info.components["_embed_copy"].includedirs = []

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
                self.cpp_info.components["_hidden"].requires.append("libxcrypt::libxcrypt")
            if self.settings.os == "Linux":
                self.cpp_info.components["_hidden"].requires.append("libuuid::libuuid")
            if self.options.get_safe("with_bz2", False):
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
            self.cpp_info.components["_hidden"].includedirs = []

        if self.options.env_vars:
            bindir = self.package_path.join("bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)

        python = self._cpython_interpreter_path
        self.user_info.python = python
        if self.options.env_vars:
            self.output.info("Setting PYTHON environment variable: {}".format(python))
            self.env_info.PYTHON = python

        if is_msvc(self):
            pythonhome = os.path.join(self.package_folder, "bin")
        elif is_apple_os(self):
            pythonhome = self.package_folder
        else:
            version = Version(self.version)
            pythonhome = os.path.join(self.package_folder, "lib", f"python{version.major}.{version.minor}")
        self.user_info.pythonhome = pythonhome

        pythonhome_required = is_msvc(self) or is_apple_os(self)
        self.user_info.module_requires_pythonhome = pythonhome_required

        if is_msvc(self):
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
