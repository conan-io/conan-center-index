import os
import re
import textwrap
from io import StringIO

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rm, rmdir, unzip
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuildDeps, MSBuildToolchain, MSBuild, is_msvc, is_msvc_static_runtime, msvc_runtime_flag
from conan.tools.scm import Version

required_conan_version = ">=1.58.0"


class CPythonConan(ConanFile):
    name = "cpython"
    description = "Python is a programming language that lets you work quickly and integrate systems more effectively."
    license = "Python-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.python.org"
    topics = ("python", "cpython", "language", "script")

    package_type = "library"
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
    def _version_suffix(self):
        v = Version(self.version)
        joiner = "" if is_msvc(self) else "."
        return f"{v.major}{joiner}{v.minor}"

    @property
    def _is_py3(self):
        return Version(self.version).major == 3

    @property
    def _is_py2(self):
        return Version(self.version).major == 2

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
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
            self.options.rm_safe("fPIC")
        if not self._supports_modules:
            self.options.rm_safe("with_bz2")
            self.options.rm_safe("with_sqlite3")
            self.options.rm_safe("with_tkinter")

            self.options.rm_safe("with_bsddb")
            self.options.rm_safe("with_lzma")

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _with_libffi(self):
        # cpython 3.7.x on MSVC uses an ancient libffi 2.00-beta (which is not available at cci, and is API/ABI incompatible with current 3.2+)
        return self._supports_modules and (not is_msvc(self) or Version(self.version) >= "3.8")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]", force=True)
        if self._supports_modules:
            self.requires("openssl/[>=1.1 <4]")
            self.requires("expat/2.5.0")
            if self._with_libffi:
                self.requires("libffi/3.4.4")
            if Version(self.version) < "3.8":
                self.requires("mpdecimal/2.4.2")
            elif Version(self.version) < "3.10":
                self.requires("mpdecimal/2.5.0")
            else:
                self.requires("mpdecimal/2.5.0")  # FIXME: no 2.5.1 to troubleshoot apple
        if self.settings.os != "Windows":
            if not is_apple_os(self):
                self.requires("util-linux-libuuid/2.39")
            self.requires("libxcrypt/4.4.35")
        if self.options.get_safe("with_bz2"):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_gdbm", False):
            self.requires("gdbm/1.23")
        if self.options.get_safe("with_nis", False):
            # TODO: Add nis when available.
            raise ConanInvalidConfiguration("nis is not available on CCI (yet)")
        if self.options.get_safe("with_sqlite3"):
            self.requires("sqlite3/3.43.1")
        if self.options.get_safe("with_tkinter"):
            self.requires("tk/8.6.10")
        if self.options.get_safe("with_curses", False):
            # Used in a public header
            # https://github.com/python/cpython/blob/v3.10.13/Include/py_curses.h#L34
            self.requires("ncurses/6.4", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_bsddb", False):
            self.requires("libdb/5.3.28")
        if self.options.get_safe("with_lzma", False):
            self.requires("xz_utils/5.4.4")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.options.env_vars

    def validate(self):
        if self.options.shared:
            if is_msvc_static_runtime(self):
                raise ConanInvalidConfiguration(
                    "cpython does not support MT(d) runtime when building a shared cpython library"
                )
        if is_msvc(self):
            if self.options.optimizations:
                raise ConanInvalidConfiguration(
                    "This recipe does not support optimized MSVC cpython builds (yet)"
                )
                # FIXME: should probably throw when cross building
                # FIXME: optimizations for Visual Studio, before building the final `build_type`:
                # 1. build the MSVC PGInstrument build_type,
                # 2. run the instrumented binaries, (PGInstrument should have created a `python.bat` file in the PCbuild folder)
                # 3. build the MSVC PGUpdate build_type
            if self.settings.build_type == "Debug" and "d" not in msvc_runtime_flag(self):
                raise ConanInvalidConfiguration(
                    "Building debug cpython requires a debug runtime (Debug cpython requires _CrtReportMode"
                    " symbol, which only debug runtimes define)"
                )
            if str(self.settings.arch) not in self._msvc_archs:
                raise ConanInvalidConfiguration("Visual Studio does not support this architecture")
            if not self.options.shared and Version(self.version) >= "3.10":
                raise ConanInvalidConfiguration("Static msvc build disabled (>=3.10) due to \"AttributeError: module 'sys' has no attribute 'winver'\"")

        if self.options.get_safe("with_curses", False) and not self.dependencies["ncurses"].options.with_widec:
            raise ConanInvalidConfiguration("cpython requires ncurses with wide character support")

        if self._supports_modules:
            if Version(self.version) < "3.8.0":
                if self.dependencies["mpdecimal"].ref.version >= "2.5.0":
                    raise ConanInvalidConfiguration("cpython versions lesser then 3.8.0 require a mpdecimal lesser then 2.5.0")
            elif Version(self.version) >= "3.9.0":
                if self.dependencies["mpdecimal"].ref.version < "2.5.0":
                    raise ConanInvalidConfiguration("cpython 3.9.0 (and newer) requires (at least) mpdecimal 2.5.0")

        if self._with_libffi:
            if self.dependencies["libffi"].ref.version >= "3.3" and is_msvc(self) and "d" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration("libffi versions >= 3.3 cause 'read access violations' when using a debug runtime (MTd/MDd)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _generate_autotools(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--with-doc-strings={}".format(yes_no(self.options.docstrings)),
            "--with-pymalloc={}".format(yes_no(self.options.pymalloc)),
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-optimizations={}".format(yes_no(self.options.optimizations)),
            "--with-lto={}".format(yes_no(self.options.lto)),
            "--with-pydebug={}".format(yes_no(self.settings.build_type == "Debug")),
        ]
        if self._is_py2:
            tc.configure_args += ["--enable-unicode={}".format(yes_no(self.options.unicode))]
        if self._is_py3:
            tc.configure_args += [
                "--with-system-libmpdec",
                "--with-openssl={}".format(self.dependencies["openssl"].package_folder),
                "--enable-loadable-sqlite-extensions={}".format(
                    yes_no(not self.dependencies["sqlite3"].options.omit_load_extension)
                ),
            ]
        if self.settings.compiler == "intel-cc":
            tc.configure_args.append("--with-icc")
        if os.environ.get("CC") or self.settings.compiler != "gcc":
            tc.configure_args.append("--without-gcc")
        if self.options.with_tkinter:
            tcltk_includes = []
            tcltk_libs = []
            # FIXME: collect using some conan util (https://github.com/conan-io/conan/issues/7656)
            for dep in ("tcl", "tk", "zlib"):
                cpp_info = self.dependencies[dep].cpp_info.aggregated_components()
                tcltk_includes += [f"-I{d}" for d in cpp_info.includedirs]
                tcltk_libs += [f"-L{lib}" for lib in cpp_info.libdirs]
                tcltk_libs += [f"-l{lib}" for lib in cpp_info.libs]
            if self.settings.os in ["Linux", "FreeBSD"] and not self.dependencies["tk"].options.shared:
                # FIXME: use info from xorg.components (x11, xscrnsaver)
                tcltk_libs.extend([f"-l{lib}" for lib in ("X11", "Xss")])
            tc.configure_args += [
                "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
                "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
            ]
        if self.settings.os in ("Linux", "FreeBSD"):
            # Building _testembed fails due to missing pthread/rt symbols
            tc.ldflags.append("-lpthread")

        tc.make_args += ["DESTDIR=", "prefix=", "exec_prefix="]

        build = None
        if cross_building(self) and not cross_building(self, skip_x64_x86=True):
            # Building from x86_64 to x86 is not a "real" cross build, so set build == host
            build = get_gnu_triplet(
                self, str(self.settings.os), str(self.settings.arch), str(self.settings.compiler)
            )
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()


    def generate(self):
        if is_msvc(self):
            # The msbuild generator only works with Visual Studio
            deps = MSBuildDeps(self)
            deps.generate()
            # The toolchain.props is not injected yet, but it also generates VCVars
            toolchain = MSBuildToolchain(self)
            toolchain.generate()
        else:
            self._generate_autotools()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self._is_py3 and Version(self.version) < "3.10":
            replace_in_file(self, os.path.join(self.source_folder, "setup.py"), ":libmpdec.so.2", "mpdec")
        if is_msvc(self):
            runtime_library = {
                "MT": "MultiThreaded",
                "MTd": "MultiThreadedDebug",
                "MD": "MultiThreadedDLL",
                "MDd": "MultiThreadedDebugDLL",
            }[msvc_runtime_flag(self)]
            self.output.info("Patching runtime")
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pyproject.props"),
                            "MultiThreadedDLL", runtime_library)
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pyproject.props"),
                            "MultiThreadedDebugDLL", runtime_library)

        # Remove vendored packages
        rmdir(self, os.path.join(self.source_folder, "Modules", "_decimal", "libmpdec"))
        rmdir(self, os.path.join(self.source_folder, "Modules", "expat"))

        if self.options.get_safe("with_curses", False):
            # FIXME: this will link to ALL libraries of ncurses. Only need to link to ncurses(w) (+ eventually tinfo)
            ncurses_info = self.dependencies["ncurses"].cpp_info.aggregated_components()
            replace_in_file(self, os.path.join(self.source_folder, "setup.py"),
                "curses_libs = ",
                "curses_libs = {} #".format(repr(ncurses_info.libs + ncurses_info.system_libs)))

        # Enable static MSVC cpython
        if not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pythoncore.vcxproj"),
                "<PreprocessorDefinitions>",
                "<PreprocessorDefinitions>Py_NO_BUILD_SHARED;")
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pythoncore.vcxproj"),
                "Py_ENABLE_SHARED",
                "Py_NO_ENABLE_SHARED")
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pythoncore.vcxproj"),
                "DynamicLibrary",
                "StaticLibrary")

            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "python.vcxproj"),
                "<Link>",
                "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "python.vcxproj"),
                "<PreprocessorDefinitions>",
                "<PreprocessorDefinitions>Py_NO_ENABLE_SHARED;")

            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pythonw.vcxproj"),
                "<Link>",
                "<Link><AdditionalDependencies>shlwapi.lib;ws2_32.lib;pathcch.lib;version.lib;%(AdditionalDependencies)</AdditionalDependencies>")
            replace_in_file(self, os.path.join(self.source_folder, "PCbuild", "pythonw.vcxproj"),
                "<ItemDefinitionGroup>",
                "<ItemDefinitionGroup><ClCompile><PreprocessorDefinitions>Py_NO_ENABLE_SHARED;%(PreprocessorDefinitions)</PreprocessorDefinitions></ClCompile>")

    def _upgrade_single_project_file(self, project_file):
        """
        `devenv /upgrade <project.vcxproj>` will upgrade *ALL* projects referenced by the project.
        By temporarily moving the solution project, only one project is upgraded
        This is needed for static cpython or for disabled optional dependencies (e.g. tkinter=False)
        Restore it afterwards because it is needed to build some targets.
        """
        rename(self,os.path.join(self.source_folder, "PCbuild", "pcbuild.sln"),
               os.path.join(self.source_folder, "PCbuild", "pcbuild.sln.bak"))
        rename(self, os.path.join(self.source_folder, "PCbuild", "pcbuild.proj"),
               os.path.join(self.source_folder, "PCbuild", "pcbuild.proj.bak"))
        self.run(f'devenv "{project_file}" /upgrade')
        rename(self, os.path.join(self.source_folder, "PCbuild", "pcbuild.sln.bak"),
               os.path.join(self.source_folder, "PCbuild", "pcbuild.sln"))
        rename(self, os.path.join(self.source_folder, "PCbuild", "pcbuild.proj.bak"),
               os.path.join(self.source_folder, "PCbuild", "pcbuild.proj"))

    @property
    def _solution_projects(self):
        if self.options.shared:
            solution_path = os.path.join(self.source_folder, "PCbuild", "pcbuild.sln")
            projects = set(m.group(1) for m in re.finditer('"([^"]+)\\.vcxproj"', open(solution_path).read()))

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
        discarded = {
            "python_uwp",
            "pythonw_uwp",
        }
        if not self.options.with_bz2:
            discarded.add("bz2")
        if not self.options.with_sqlite3:
            discarded.add("_sqlite3")
        if not self.options.with_tkinter:
            discarded.add("_tkinter")
        if self._is_py2:
            # Python 2 Visual Studio projects NOT to build
            discarded = discarded.union({
                "bdist_wininst",
                "libeay",
                "ssleay",
                "sqlite3",
                "tcl",
                "tk",
                "tix",
            })
            if not self.options.with_bsddb:
                discarded.add("_bsddb")
        elif self._is_py3:
            discarded = discarded.union({
                "bdist_wininst",
                "liblzma",
                "openssl",
                "sqlite3",
                "xxlimited",
            })
            if not self.options.with_lzma:
                discarded.add("_lzma")
        return discarded

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

    def _msvc_build(self):
        msbuild = MSBuild(self)
        msbuild.platform = self._msvc_archs[str(self.settings.arch)]
        # TODO
        msbuild_properties = {
            "IncludeExternals": "true",
        }

        projects = self._solution_projects
        self.output.info(f"Building {len(projects)} Visual Studio projects: {projects}")

        for project_i, project in enumerate(projects, 1):
            self.output.info(f"[{project_i}/{len(projects)}] Building project '{project}'...")
            project_file = os.path.join(self.source_folder, "PCbuild", project + ".vcxproj")
            self._upgrade_single_project_file(project_file)
            msbuild.build(project_file)

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._msvc_build()
        else:
            autotools = Autotools(self)
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
        return os.path.join(self.source_folder, "PCbuild", build_subdir_lut[str(self.settings.arch)])

    @property
    def _msvc_install_subprefix(self):
        return "bin"

    def _copy_essential_dlls(self):
        if is_msvc(self):
            # Until MSVC builds support cross building, copy dll's of essential (shared) dependencies to python binary location.
            # These dll's are required when running the layout tool using the newly built python executable.
            dest_path = os.path.join(self.build_folder, self._msvc_artifacts_path)
            if self._with_libffi:
                for bin_path in self.dependencies["libffi"].cpp_info.bindirs:
                    copy(self, "*.dll", src=bin_path, dst=dest_path)
            for bin_path in self.dependencies["expat"].cpp_info.bindirs:
                copy(self, "*.dll", src=bin_path, dst=dest_path)
            for bin_path in self.dependencies["zlib"].cpp_info.bindirs:
                copy(self, "*.dll", src=bin_path, dst=dest_path)

    def _msvc_package_layout(self):
        self._copy_essential_dlls()
        install_prefix = os.path.join(self.package_folder, self._msvc_install_subprefix)
        mkdir(self, install_prefix)
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        # FIXME: if cross building, use a build python executable here
        python_built = os.path.join(build_path, f"python{infix}.exe")
        layout_args = [
            os.path.join(self.source_folder, "PC", "layout", "main.py"),
            "-v",
            "-s", self.source_folder,
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
        python_args = " ".join(f'"{a}"' for a in layout_args)
        self.run(f"{python_built} {python_args}")

        rmdir(self, os.path.join(self.package_folder, "bin", "tcl"))

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
        copy(self, "*.exe",
             src=build_path,
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix))
        copy(self, "*.dll",
             src=build_path,
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix))
        copy(self, "*.pyd",
             src=build_path,
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "DLLs"))
        copy(self, f"python{self._version_suffix}{infix}.lib",
             src=build_path,
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "libs"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "Include"),
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "include"))
        copy(self, "pyconfig.h",
             src=os.path.join(self.source_folder, "PC"),
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "include"))
        copy(self, "*.py",
             src=os.path.join(self.source_folder, "lib"),
             dst=os.path.join(self.package_folder, self._msvc_install_subprefix, "Lib"))
        rmdir(self, os.path.join(self.package_folder, self._msvc_install_subprefix, "Lib", "test"))

        packages = {}
        get_name_version = lambda fn: fn.split(".", 2)[:2]
        whldir = os.path.join(self.source_folder, "Lib", "ensurepip", "_bundled")
        for fn in filter(lambda n: n.endswith(".whl"), os.listdir(whldir)):
            name, version = get_name_version(fn)
            add = True
            if name in packages:
                pname, pversion = get_name_version(packages[name])
                add = Version(version) > Version(pversion)
            if add:
                packages[name] = fn
        for fname in packages.values():
            unzip(self, filename=os.path.join(whldir, fname),
                  destination=os.path.join(self.package_folder, "bin", "Lib", "site-packages"))

        interpreter_path = os.path.join(build_path, self._cpython_interpreter_name)
        lib_dir_path = os.path.join(self.package_folder, self._msvc_install_subprefix, "Lib").replace("\\", "/")
        self.run(f"{interpreter_path} -c \"import compileall; compileall.compile_dir('{lib_dir_path}')\"")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            if self._is_py2 or not self.options.shared:
                self._msvc_package_copy()
            else:
                self._msvc_package_layout()
            rm(self, "vcruntime*", os.path.join(self.package_folder, "bin"), recursive=True)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

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
                self.output.info(f"Rewriting shebang of {filename}")
                with open(filepath, "wb") as fn:
                    fn.write(textwrap.dedent(f"""\
                        #!/bin/sh
                        ''':'
                        __file__="$0"
                        while [ -L "$__file__" ]; do
                            __file__="$(dirname "$__file__")/$(readlink "$__file__")"
                        done
                        exec "$(dirname "$__file__")/python{self._version_suffix}" "$0" "$@"
                        '''
                        """).encode())
                    fn.write(text)

            if not os.path.exists(self._cpython_symlink):
                os.symlink(f"python{self._version_suffix}", self._cpython_symlink)
        self._fix_install_name()

    @property
    def _cpython_symlink(self):
        symlink = os.path.join(self.package_folder, "bin", "python")
        if self.settings.os == "Windows":
            symlink += ".exe"
        return symlink

    @property
    def _cpython_interpreter_name(self):
        python = "python"
        if is_msvc(self):
            if self.settings.build_type == "Debug":
                python += "_d"
        else:
            python += self._version_suffix
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
            lib_ext = self._abi_suffix + (
                ".dll.a" if self.options.shared and self.settings.os == "Windows" else ""
            )
        return f"python{self._version_suffix}{lib_ext}"

    def _fix_install_name(self):
        if is_apple_os(self) and self.options.shared:
            buffer = StringIO()
            python = os.path.join(self.package_folder, "bin", "python")
            self.run(f'otool -L "{python}"', buffer)
            lines = buffer.getvalue().strip().split("\n")[1:]
            for line in lines:
                library = line.split()[0]
                if library.startswith(self.package_folder):
                    new = library.replace(self.package_folder, "@executable_path/..")
                    self.output.info(f"patching {python}, replace {library} with {new}")
                    self.run(f"install_name_tool -change {library} {new} {python}")

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
            self.cpp_info.components["python"].includedirs.append(
                os.path.join("include", f"python{self._version_suffix}{self._abi_suffix}")
            )
            libdir = "lib"
        if self.options.shared:
            self.cpp_info.components["python"].defines.append("Py_ENABLE_SHARED")
        else:
            self.cpp_info.components["python"].defines.append("Py_NO_ENABLE_SHARED")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["python"].system_libs.extend(["dl", "m", "pthread", "util"])
            elif self.settings.os == "Windows":
                self.cpp_info.components["python"].system_libs.extend(
                    ["pathcch", "shlwapi", "version", "ws2_32"]
                )
        self.cpp_info.components["python"].requires = ["zlib::zlib"]
        if self.settings.os != "Windows":
            self.cpp_info.components["python"].requires.append("libxcrypt::libxcrypt")
        self.cpp_info.components["python"].set_property(
            "pkg_config_name", f"python-{py_version.major}.{py_version.minor}"
        )
        self.cpp_info.components["python"].libdirs = []

        self.cpp_info.components["_python_copy"].set_property("pkg_config_name", f"python{py_version.major}")
        self.cpp_info.components["_python_copy"].requires = ["python"]
        self.cpp_info.components["_python_copy"].libdirs = []

        # embed component: "Embed Python into an application"
        self.cpp_info.components["embed"].libs = [self._lib_name]
        self.cpp_info.components["embed"].libdirs = [libdir]
        self.cpp_info.components["embed"].set_property(
            "pkg_config_name", f"python-{py_version.major}.{py_version.minor}-embed"
        )
        self.cpp_info.components["embed"].requires = ["python"]

        self.cpp_info.components["_embed_copy"].requires = ["embed"]
        self.cpp_info.components["_embed_copy"].set_property(
            "pkg_config_name", f"python{py_version.major}-embed"
        )
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
                if not is_apple_os(self):
                    self.cpp_info.components["_hidden"].requires.append("util-linux-libuuid::util-linux-libuuid")
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
            self.output.info(f"Appending PATH environment variable: {bindir}")
            self.env_info.PATH.append(bindir)

        python = self._cpython_interpreter_path
        self.conf_info.define("user.cpython:python", python)
        self.user_info.python = python
        if self.options.env_vars:
            self.env_info.PYTHON = python

        if is_msvc(self):
            pythonhome = os.path.join(self.package_folder, "bin")
        elif is_apple_os(self):
            pythonhome = self.package_folder
        else:
            version = Version(self.version)
            pythonhome = os.path.join(
                self.package_folder, "lib", f"python{version.major}.{version.minor}"
            )
        self.conf_info.define("user.cpython:pythonhome", pythonhome)
        self.user_info.pythonhome = pythonhome

        pythonhome_required = is_msvc(self) or is_apple_os(self)
        self.conf_info.define("user.cpython:module_requires_pythonhome", pythonhome_required)
        self.user_info.module_requires_pythonhome = pythonhome_required

        if is_msvc(self):
            if self.options.env_vars:
                self.output.info(f"Setting PYTHONHOME environment variable: {pythonhome}")
                self.env_info.PYTHONHOME = pythonhome

        if self._is_py2:
            python_root = ""
        else:
            python_root = self.package_folder
            if self.options.env_vars:
                self.output.info(f"Setting PYTHON_ROOT environment variable: {python_root}")
                self.env_info.PYTHON_ROOT = python_root
        self.conf_info.define("user.cpython:python_root", python_root)
        self.user_info.python_root = python_root
