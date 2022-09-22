import os
import re
import textwrap
import sys

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, load, replace_in_file, rmdir, mkdir, apply_conandata_patches, rm, unzip, \
    copy, save
from conan.tools.gnu import AutotoolsToolchain, PkgConfigDeps, AutotoolsDeps, Autotools
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.microsoft import MSBuild, is_msvc, msvc_runtime_flag, MSBuildDeps, MSBuildToolchain, VCVars
from conan.tools.microsoft.visual import msvc_version_to_toolset_version
from conan.tools.scm import Version
from conans.tools import get_gnu_triplet
from jinja2 import Template

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
    short_paths = True  # Due to the long path names on Windows for the site-packages

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
    def _ms_toolset_version(self):
        if self.settings.get_safe("compiler") == "Visual Studio":
            return msvc_version_to_toolset_version({"17": "193",
                                                    "16": "192",
                                                    "15": "191",
                                                    "14": "190",
                                                    "12": "180",
                                                    "11": "170"}[self.settings.get_safe("compiler.version")])
        elif self.settings.get_safe("compiler") == "msvc":
            return msvc_version_to_toolset_version(self.settings.compiler.version)
        return None

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
            if Version(self.deps_cpp_info["libffi"].version) >= "3.3" and is_msvc(self) and "d" in msvc_runtime_flag(self):
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
            tc.configure_args = [
                f"--prefix={self._install_path}",
                f"--enable-shared={yes_no(self.options.get_safe('shared', False))}",
                f"--with-doc-strings={yes_no(self.options.get_safe('docstrings', False))}",
                f"--with-pymalloc={yes_no(self.options.get_safe('pymalloc', False))}",
                "--with-system-expat",
                "--with-system-ffi",
                f"--enable-optimizations={yes_no(self.options.get_safe('optimizations', False))}",
                f"--with-lto={yes_no(self.options.get_safe('lto', False))}",
                f"--with-pydebug={yes_no(self.settings.build_type == 'Debug')}",
            ]

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

            # FIXME: use MSBuildtoolchain.properties once Conan 1.53 is available https://github.com/conan-io/conan/pull/12147
            replace_in_file(self, self.source_path.joinpath("PCbuild", "Directory.Build.props"), "</Project>",
                            textwrap.dedent(f"""  <PropertyGroup>
                                                    <IncludeExternals>true</IncludeExternals>
                                                    <PlatformToolset>{self._ms_toolset_version}</PlatformToolset>
                                                  </PropertyGroup>
                                                </Project>"""), runtime_library)

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
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythoncore.vcxproj"), "<PreprocessorDefinitions>","<PreprocessorDefinitions>Py_NO_BUILD_SHARED;")
            replace_in_file(self,self.source_path.joinpath("PCbuild", "pythoncore.vcxproj"), "Py_ENABLE_SHARED", "Py_NO_ENABLE_SHARED")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythoncore.vcxproj"), "DynamicLibrary", "StaticLibrary")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "python.vcxproj"),
                                  "<Link>", "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "python.vcxproj"), "<PreprocessorDefinitions>", "<PreprocessorDefinitions>Py_NO_ENABLE_SHARED;")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythonw.vcxproj"),
                                  "<Link>", "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            replace_in_file(self, self.source_path.joinpath("PCbuild", "pythonw.vcxproj"),
                                  "<ItemDefinitionGroup>", "<ItemDefinitionGroup><ClCompile><PreprocessorDefinitions>Py_NO_ENABLE_SHARED;%(PreprocessorDefinitions)</PreprocessorDefinitions></ClCompile>")

    def build(self):
        self._validate_final()
        self._patch_sources()
        if is_msvc(self):
            projects = self._solution_projects
            self.output.info(f"Building {len(projects)} Visual Studio projects: {projects}")

            for project_i, project in enumerate(projects, 1):
                self.output.info(f"[{project_i}/{len(projects)}] Building project '{project}'...")
                project_file = self.source_path.joinpath("PCbuild", project + ".vcxproj")
                msbuild = MSBuild(self)
                msbuild.build(sln=project_file)
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    @property
    def _msvc_arch_path(self):
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
        return build_subdir_lut[str(self.settings.arch)]

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
        return self.source_path.joinpath("PCbuild", self._msvc_arch_path)

    @property
    def _install_path(self):
        return self.package_path.joinpath("bin") if is_msvc(self) else self.package_path

    @property
    def _lib_path(self):
        return self._install_path.joinpath("libs") if is_msvc(self) else self._install_path.joinpath("lib")

    @property
    def _include_path(self):
        return self._install_path.joinpath("include") if is_msvc(self) else self._install_path.joinpath("include", f"python{self._version_suffix}{self._abi_suffix}")

    @property
    def _modules_path(self):
        return self._install_path.joinpath("Lib") if is_msvc(self) else self._install_path.joinpath("lib")

    @property
    def _site_packages_path(self):
        return self._modules_path.joinpath("site-packages")

    @property
    def _cpython_symlink(self):
        ext = ".exe" if self.settings.os == "Windows" else ""
        symlink = self._install_path.joinpath(f"python{ext}")
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

    @property
    def _cmake_build_module_path(self):
        return self.package_path.joinpath("res", "cmake", "python_variables.cmake")

    def _copy_essential_dlls(self):
            # Until MSVC builds support cross building, copy dll's of essential (shared) dependencies to python binary location.
            # These dll's are required when running the layout tool using the newly built python executable.
        if self._with_libffi:
            for bin_path in self.deps_cpp_info["libffi"].bin_paths:
                copy(self, "*.dll", src=bin_path, dst=self._msvc_artifacts_path)
        for bin_path in self.deps_cpp_info["expat"].bin_paths:
            copy(self, "*.dll", src=bin_path, dst=self._msvc_artifacts_path)
        for bin_path in self.deps_cpp_info["zlib"].bin_paths:
            copy(self, "*.dll", src=bin_path, dst=self._msvc_artifacts_path)

    def _msvc_package_layout(self):
        self._copy_essential_dlls()
        mkdir(self, self._install_path)
        python_built = self._msvc_artifacts_path.joinpath(self._cpython_interpreter_name) if not cross_building(self) else sys.executable
        layout_args = [
            self.source_path.joinpath("PC", "layout", "main.py"),
            "-v",
            "-s", self.source_path,
            "-b", self._msvc_artifacts_path,
            "--copy", self._install_path,
            "-p",
            "--include-pip",
            "--include-venv",
            "--include-dev",
            "--include-stable"
        ]
        if self.options.get_safe("with_tkinter", False):
            layout_args.append("--include-tcltk")
        if self.settings.build_type == "Debug":
            layout_args.append("-d")
        python_args = " ".join(f"\"{a}\"" for a in layout_args)
        self.run(f"{python_built} {python_args}", run_environment=True, env="conanrun")

        rmdir(self, self._install_path.joinpath("tcl"))
        rm(self, "python.*", self._lib_path, recursive=True)
        rm(self, "LICENSE.txt", self._install_path, recursive=True)
        rm(self, "vcruntime*", self._install_path, recursive=True)

    def _msvc_package_copy(self):
        py_version = Version(self.version)
        infix = "_d" if self.settings.build_type == "Debug" else ""
        copy(self, "*.exe", src=self._msvc_artifacts_path, dst=self._install_path)
        copy(self, "*.dll", src=self._msvc_artifacts_path, dst=self._install_path)
        copy(self, "*.pyd", src=self._msvc_artifacts_path, dst=self._install_path.joinpath("DLLs"))
        copy(self, f"python{self._version_suffix}{infix}.dll", src=self._msvc_artifacts_path, dst=self._install_path)
        copy(self, f"python{py_version.major}{infix}.dll", src=self._msvc_artifacts_path, dst=self._install_path)  # Limited Python ABI
        copy(self, f"python{self._version_suffix}{infix}.lib", src=self._msvc_artifacts_path, dst=self._lib_path)
        copy(self, f"python{py_version.major}{infix}.lib", src=self._msvc_artifacts_path, dst=self._lib_path)  # Limited Python ABI
        copy(self, "*", src=self.source_path.joinpath("Include"), dst=self._include_path)
        copy(self, "pyconfig.h", src=self.source_path.joinpath("PC"), dst=self._include_path)
        copy(self, "*.py", src=self.source_path.joinpath("lib"), dst=self._modules_path)
        rmdir(self, self._modules_path.joinpath("test"))

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
            unzip(self, filename=fname, destination=self._site_packages_path)

        self.run(f"{self._msvc_artifacts_path.joinpath(self._cpython_interpreter_name)} -c \"import compileall; compileall.compile_dir('{self._modules_path}')\"",
                 run_environment=True)

    @property
    def _cmake_variables(self):
        content = Template("""{% for k, v in kwargs.items()  %}set({{ k }} {{ v }})\n{% endfor %}""")
        py_version = Version(self.version)

        suffix = "{}{}{}".format(
            "d" if self.settings.build_type == "Debug" else "",
            "m" if self.options.get_safe("pymalloc", False) else "",
            "u" if self.options.get_safe("unicode", False) else "",
        )
        cmake_arg = ";".join("ON" if a else "OFF" for a in (self.settings.build_type == "Debug", self.options.get_safe("pymalloc", False), self.options.get_safe("unicode", False)))
        return content.render(kwargs={"BUILD_MODULE": "ON" if self._supports_modules else "OFF",
                                        "PY_VERSION_MAJOR": py_version.major,
                                        "PY_VERSION_MAJOR_MINOR": f"{py_version.major}.{py_version.minor}",
                                        "PY_FULL_VERSION": self.version,
                                        "PY_VERSION_SUFFIX": suffix,
                                        "PYTHON_EXECUTABLE": str(self._cpython_interpreter_path),
                                        f"Python{py_version.major}_EXECUTABLE": str(self._cpython_interpreter_path),
                                        "Python_EXECUTABLE": str(self._cpython_interpreter_path),
                                        f"Python{py_version.major}_ROOT_DIR": str(self.package_folder),
                                        "Python_ROOT_DIR": str(self.package_folder),
                                        f"Python{py_version.major}_USE_STATIC_LIBS": "OFF" if self.options.shared else "ON",
                                        "Python_USE_STATIC_LIBS": "OFF" if self.options.shared else "ON",
                                        f"Python{py_version.major}_FIND_FRAMEWORK": "NEVER",
                                        "Python_FIND_FRAMEWORK": "NEVER",
                                        f"Python{py_version.major}_FIND_REGISTRY": "NEVER",
                                        "Python_FIND_REGISTRY": "NEVER",
                                        f"Python{py_version.major}_FIND_IMPLEMENTATIONS": "CPython",
                                        "Python_FIND_IMPLEMENTATIONS": "CPython",
                                        f"Python{py_version.major}_FIND_STRATEGY": "LOCATION",
                                        "Python_FIND_STRATEGY": "LOCATION",
                                        f"Python{py_version.major}_FIND_ABI": cmake_arg,
                                        "Python_FIND_ABI": cmake_arg,
                                        f"Python{py_version.major}_LIBRARY": str(self._lib_path),
                                        "Python_LIBRARY": str(self._lib_path),
                                        f"Python{py_version.major}_INCLUDE_DIR": str(self._include_path),
                                        "Python_INCLUDE_DIR": str(self._include_path),
                                        })

    def package(self):
        copy(self, "LICENSE*", src=self.source_path, dst=self.package_path.joinpath("licenses"))
        save(self, self._cmake_build_module_path, self._cmake_variables)

        if is_msvc(self):
            if self._is_py2 or not self.options.shared:
                self._msvc_package_copy()
            else:
                self._msvc_package_layout()
        else:
            autotools = Autotools(self)
            autotools.install(args=[])
            rmdir(self, self._lib_path.joinpath("pkgconfig"))
            rmdir(self, self._install_path.joinpath("share"))

            # Rewrite shebangs of python scripts
            for file in self.package_path.joinpath("bin").glob("**/*"):
                if not file.is_file() or file.is_symlink():
                    continue
                try:
                    text = load(self, file)
                except UnicodeDecodeError:
                    continue
                firstline = text.splitlines()[0]
                if not (firstline.startswith("#!") and "/python" in firstline and "/bin/sh" not in firstline):
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

    def package_info(self):
        py_version = Version(self.version)

        self.cpp_info.set_property("cmake_file_name", "Python")

        self.cpp_info.components["python"].includedirs = [str(self._include_path)]
        self.cpp_info.components["python"].libdirs = [str(self._lib_path)]
        self.cpp_info.components["python"].libs = [self._lib_name]
        self.cpp_info.components["python"].builddirs = [str(self._cmake_build_module_path.parent)]

        self.cpp_info.components["python"].set_property("cmake_target_aliases", ["Python::Python"])
        self.cpp_info.components["python"].set_property("cmake_build_modules", [str(self._cmake_build_module_path)])
        self.cpp_info.components["python"].names["cmake_build_modules"] = [str(self._cmake_build_module_path)]

        self.cpp_info.components["python"].set_property("pkg_config", f"python-{py_version.major}.{py_version.minor}")
        self.cpp_info.components["python"].names["pkg_config"] = f"python-{py_version.major}.{py_version.minor}"

        if self.options.shared:
            self.cpp_info.components["python"].defines.append("Py_ENABLE_SHARED")
        else:
            self.cpp_info.components["python"].defines.append("Py_NO_ENABLE_SHARED")
            if self.settings.os == "Linux":
                self.cpp_info.components["python"].system_libs.extend(["dl", "m", "pthread", "util", "nsl"])
            elif self.settings.os == "Windows":
                self.cpp_info.components["python"].system_libs.extend(["pathcch", "shlwapi", "version", "ws2_32"])
        self.cpp_info.components["python"].requires = ["zlib::zlib"]
        if self.settings.os != "Windows":
            self.cpp_info.components["python"].requires.append("libxcrypt::libxcrypt")

        self.cpp_info.components["_python_copy"].set_property("pkg_config", f"python{py_version.major}")
        self.cpp_info.components["_python_copy"].names["pkg_config"] = f"python{py_version.major}"
        self.cpp_info.components["_python_copy"].requires = ["python"]
        self.cpp_info.components["_python_copy"].libdirs = []
        self.cpp_info.components["_python_copy"].includedirs = []

        # embed component: "Embed Python into an application"
        self.cpp_info.components["embed"].libs = [self._lib_name]
        self.cpp_info.components["embed"].libdirs = [str(self._lib_path)]
        self.cpp_info.components["embed"].includedirs = []
        self.cpp_info.components["embed"].set_property("pkg_config", f"python-{py_version.major}.{py_version.minor}-embed")
        self.cpp_info.components["embed"].names["pkg_config"] = f"python-{py_version.major}.{py_version.minor}-embed"
        self.cpp_info.components["embed"].requires = ["python"]

        self.cpp_info.components["_embed_copy"].requires = ["embed"]
        self.cpp_info.components["_embed_copy"].set_property("pkg_config", f"python{py_version.major}-embed")
        self.cpp_info.components["_embed_copy"].names["pkg_config"] = f"python{py_version.major}-embed"
        self.cpp_info.components["_embed_copy"].libdirs = []
        self.cpp_info.components["_embed_copy"].includedirs = []

        if self._supports_modules:
            # hidden components: the C extensions of python are built as dynamically loaded shared libraries.
            # C extensions or applications with an embedded Python should not need to link to them...
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
            if self.options.get_safe("with_sqlite3", False):
                self.cpp_info.components["_hidden"].requires.append("sqlite3::sqlite3")
            if self.options.get_safe("with_curses", False):
                self.cpp_info.components["_hidden"].requires.append("ncurses::ncurses")
            if self.options.get_safe("with_bsddb", False):
                self.cpp_info.components["_hidden"].requires.append("libdb::libdb")
            if self.options.get_safe("with_lzma", False):
                self.cpp_info.components["_hidden"].requires.append("xz_utils::xz_utils")
            if self.options.get_safe("with_tkinter", False):
                self.cpp_info.components["_hidden"].requires.append("tk::tk")
            self.cpp_info.components["_hidden"].libdirs = []
            self.cpp_info.components["_hidden"].includedirs = []

        if self.options.env_vars:
            self.output.info(f"Appending PATH environment variable: {self._install_path}")
            self.env_info.PATH.append(str(self._install_path))

        self.output.info(f"Setting userinfo: `python` to: {self._cpython_interpreter_path}")
        self.user_info.python = str(self._cpython_interpreter_path)
        self.output.info(f"Setting conf: `tools.cpython:python` to: {self._cpython_interpreter_path}")
        self.conf_info.define("tools.cpython:python", str(self._cpython_interpreter_path))
        if self.options.env_vars:
            self.output.info(f"Setting PYTHON environment variable: {self._cpython_interpreter_path}")
            self.env_info.PYTHON = str(self._cpython_interpreter_path)
            self.buildenv_info.define_path("PYTHON", str(self._cpython_interpreter_path))
            self.runenv_info.define_path("PYTHON", str(self._cpython_interpreter_path))

        if is_msvc(self):
            pythonhome = self._install_path
        elif is_apple_os(self):
            pythonhome = self.package_path
        else:
            version = Version(self.version)
            pythonhome = self._lib_path.joinpath(f"python{version.major}.{version.minor}")
        self.output.info(f"Setting userinfo: `pythonhome` to: {pythonhome}")
        self.user_info.pythonhome = str(pythonhome)
        self.output.info(f"Setting conf: `tools.cpython:pythonhome` to: {pythonhome}")
        self.conf_info.define("tools.cpython:pythonhome", str(pythonhome))

        if is_msvc(self) and self.options.env_vars:
            self.output.info(f"Setting PYTHONHOME environment variable: {pythonhome}")
            self.env_info.PYTHONHOME = str(pythonhome)
            self.buildenv_info.define_path("PYTHONHOME", str(pythonhome))
            self.runenv_info.define_path("PYTHONHOME", str(pythonhome))

        pythonhome_required = is_msvc(self) or is_apple_os(self)
        self.output.info(f"Setting userinfo: `module_requires_pythonhome` to: {pythonhome_required}")
        self.user_info.module_requires_pythonhome = pythonhome_required
        self.output.info(f"Setting conf: `tools.cpython:module_requires_pythonhome` to: {pythonhome_required}")
        self.conf_info.define("tools.cpython:module_requires_pythonhome", pythonhome_required)

        python_root = "" if self._is_py2 else self.package_folder
        self.output.info(f"Setting userinfo: `python_root` to: {python_root}")
        self.user_info.python_root = python_root
        self.output.info(f"Setting conf: `tools.cpython:python_root` to: {python_root}")
        self.conf_info.define("tools.cpython:python_root", python_root)

        if self.options.env_vars:
            self.output.info(f"Setting PYTHON_ROOT environment variable: {python_root}")
            self.env_info.PYTHON_ROOT = python_root
            self.buildenv_info.define_path("PYTHON_ROOT", python_root)
            self.runenv_info.define_path("PYTHON_ROOT", python_root)
