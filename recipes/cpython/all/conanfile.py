from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import os
import re


class CPythonConan(ConanFile):
    name = "cpython"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.python.org"
    description = "Python is a programming language that lets you work quickly and integrate systems more effectively."
    topics = ("conan", "python", "cpython", "language", "script")
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

    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "optimizations": False,
        "lto": False,
        "docstrings": True,
        "pymalloc": True,
        "with_bz2": True,
        "with_gdbm": True,
        "with_nis": False,
        "with_sqlite3": True,
        "with_tkinter": False,  # FIXME: enable by default
        "with_curses": False,   # FIXME: enable by default

        # Python 2 options
        "unicode": "ucs2",
        "with_bsddb": True,
        # Python 3 options
        "with_lzma": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _version_tuple(self):
        return tuple(self.version.split("."))

    @property
    def _version_major_minor(self):
        if self.settings.compiler == "Visual Studio":
            joiner = ""
        else:
            joiner = "."
        return joiner.join(self._version_tuple[:2])

    @property
    def _is_py3(self):
        return tools.Version(self.version).major == "3"

    @property
    def _is_py2(self):
        return tools.Version(self.version).major == "2"

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
        if tools.is_apple_os(self.settings.os):
            if self._is_py2:
                # FIXME: python2 does not build on Macos due to a missing uuid_string_t type
                raise ConanInvalidConfiguration("This recipe (currently) does not support building python2 for apple products.")
        if self.settings.compiler == "Visual Studio":
            # The msbuild generator only works with Visual Studio
            self.generators.append("msbuild")
            if not self.options.shared:
                raise ConanInvalidConfiguration("MSVC does not support a static build")
            if self._is_py2:
                if self.settings.compiler.version >= tools.Version("14"):
                    self.output.warn("Visual Studio versions 14 and higher are not supported")
            if str(self.settings.arch) not in self._msvc_archs:
                raise ConanInvalidConfiguration("Visual Studio does not support this architecure")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Python-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("openssl/1.1.1g")
        if not (self.settings.compiler == "Visual Studio" and tools.Version(self.version) >= tools.Version("3.8")):
            self.requires("expat/2.2.9")
        self.requires("mpdecimal/2.4.2")
        self.requires("zlib/1.2.11")
        if self.settings.compiler != "Visual Studio" or tools.Version(self.version) >= "3.8":
            self.requires("libffi/3.3")
        if self.settings.os != "Windows":
            self.requires("libuuid/1.0.3")
            self.requires("libxcrypt/4.4.16")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_gdbm", False):
            self.requires("gdbm/1.18.1")
        if self.options.get_safe("with_nis", False):
            # TODO: Add nis when available.
            raise ConanInvalidConfiguration("nis is not available on CCI (yet)")
            self.requires("nis/x.y.z")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.31.1")
        if self.options.with_tkinter:
          # TODO: Add tk when available
            raise ConanInvalidConfiguration("tk is not available on CCI (yet)")
            self.requires("tk/8.6.9.1@bincrafters/stable", private=self._is_installer)
        if self.options.get_safe("with_curses", False):
            raise ConanInvalidConfiguration("ncurses is not available on CCI (yet)")
            self.requires("ncurses/6.2")
        if self._is_py2:
            if self.options.with_bsddb:
                self.requires("libdb/5.3.28")
        else:
            if self.options.with_lzma:
                self.requires("xz_utils/5.2.4")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        conf_args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--with-doc-strings" if self.options.docstrings else "--without-doc-strings",
            "--with-pymalloc" if self.options.pymalloc else "--without-pymalloc",
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-optimizations" if self.options.optimizations else "--disable-optimizations",
            "--with-lto" if self.options.lto else "--without-lto",
            "--with-pydebug" if self.settings.build_type == "Debug" else "--without-pydebug",
        ]
        if self._is_py2:
            conf_args.extend([
                "--enable-unicode={}".format(self.options.unicode),
            ])
        if self._is_py3:
            conf_args.extend([
                "--with-system-libmpdec",
                "--with-openssl={}".format(self.deps_cpp_info["openssl"].rootpath),
                "--disable-loadable-sqlite-extensions" if self.options["sqlite3"].omit_load_extension else "--enable-loadable-sqlite-extensions",
            ])
        if self.settings.compiler == "intel":
            conf_args.extend(["--with-icc"])
        if tools.get_env("CC") or self.settings.compiler != "gcc":
            conf_args.append("--without-gcc")
        if self.options.with_tkinter:
            tcltk_includes = []
            tcltk_libs = []
            for dep in ("tcl", "tk", "zlib"):
                tcltk_includes += ["-I{}".format(d) for d in self.deps_cpp_info[dep].include_paths]
                tcltk_libs += ["-l{}".format(lib) for lib in self.deps_cpp_info[dep].libs]
            conf_args.extend([
                "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
                "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
            ])

        build = None
        if tools.cross_building(self.settings) and not tools.cross_building(self.settings, skip_x64_x86=True):
            # Building from x86_64 to x86 is not a "real" cross build, so set build == host
            build = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder, build=build)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches",{}).get(self.version, []):
            tools.patch(**patch)
        if self._is_py3:
            tools.replace_in_file(os.path.join(self._source_subfolder, "setup.py"),
                                  ":libmpdec.so.2", "mpdec")
        if self.settings.compiler == "Visual Studio":
            runtime_library = {
                "MT": "MultiThreaded",
                "MTd": "MultiThreadedDebug",
                "MD": "MultiThreadedDLL",
                "MDd": "MultiThreadedDebugDLL",
            }[str(self.settings.compiler.runtime)]
            self.output.info("Patching runtime")
            tools.replace_in_file(os.path.join(self._source_subfolder, "PCbuild", "pyproject.props"),
                                  "MultiThreadedDLL", runtime_library)
            tools.replace_in_file(os.path.join(self._source_subfolder, "PCbuild", "pyproject.props"),
                                  "MultiThreadedDebugDLL", runtime_library)

    @property
    def _solution_projects(self):
        solution_path = os.path.join(self._source_subfolder, "PCBuild", "pcbuild.sln")
        project_set = set(m.group(1) for m in re.finditer("\"([^\"]+)\\.vcxproj\"", open(solution_path).read()))
        discarded = self._msvc_discarded_projects
        projects = set(filter(lambda p: os.path.basename(p) not in discarded, project_set))
        return projects

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
        if tools.Version(self.version) >= "3.8":
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

        upgraded = False
        for project_i, project in enumerate(projects):
            self.output.info(" [{}/{}] Building project '{}'...".format(project_i, len(projects), project))
            project_file = os.path.join(self._source_subfolder, "PCBuild", project + ".vcxproj")
            msbuild.build(project_file, upgrade_project=not upgraded, build_type="Debug" if self.settings.build_type == "Debug" else "Release",
                          platforms=self._msvc_archs, properties=msbuild_properties)
            upgraded = True

    def build(self):
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
        if tools.Version(self.version) >= "3.8":
            build_subdir_lut.update({
                "armv7": "arm32",
                "armv8_32": "arm32",
                "armv8": "arm64",
            })
        return os.path.join(self._source_subfolder, "PCBuild", build_subdir_lut[str(self.settings.arch)])

    def _msvc_package_layout(self):
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        python_built = os.path.join(build_path, "python{}.exe".format(infix))
        layout_args = [
            os.path.join(self._source_subfolder, "PC", "layout", "main.py"),
            "-v",
            "-s", self._source_subfolder,
            "-b", build_path,
            "--copy", self.package_folder,
            "-p",
            "--include-pip",
            "--include-venv",
            "--include-dev",
        ]
        if self.settings.build_type == "Debug":
            layout_args.append("-d")
        python_args = " ".join("\"{}\"".format(a) for a in layout_args)
        self.run("{} {}".format(python_built, python_args), run_environment=True)

        os.mkdir(os.path.join(self.package_folder, "bin"))
        for file in os.listdir(self.package_folder):
            if re.match("vcruntime.*", file):
                os.unlink(os.path.join(self.package_folder, file))
                continue
            if re.match(".*\\.(exe|dll)", file):
                os.rename(os.path.join(self.package_folder, file),
                          os.path.join(self.package_folder, "bin", file))
        os.unlink(os.path.join(self.package_folder, "LICENSE.txt"))
        os.rename(os.path.join(self.package_folder, "Lib"),
                  os.path.join(self.package_folder, "bin", "Lib"))
        os.rename(os.path.join(self.package_folder, "DLLs"),
                  os.path.join(self.package_folder, "bin", "DLLs"))
        os.rename(os.path.join(self.package_folder, "libs"),
                  os.path.join(self.package_folder, "lib"))
        for file in os.listdir(os.path.join(self.package_folder, "lib")):
            if not re.match("python.*", file):
                os.unlink(os.path.join(self.package_folder, "lib", file))

    def _msvc_package_copy(self):
        build_path = self._msvc_artifacts_path
        infix = "_d" if self.settings.build_type == "Debug" else ""
        self.copy("*.exe", src=build_path, dst=os.path.join(self.package_folder, "bin"))
        self.copy("*.dll", src=build_path, dst=os.path.join(self.package_folder, "bin"))
        self.copy("*.pyd", src=build_path, dst=os.path.join(self.package_folder, "bin", "DLLs"))
        self.copy("python{}{}.lib".format(self._version_major_minor, infix), src=build_path, dst=os.path.join(self.package_folder, "lib"))
        self.copy("*", src=os.path.join(self._source_subfolder, "Include"), dst=os.path.join(self.package_folder, "include", "python{}".format(self._version_major_minor)))
        self.copy("pyconfig.h", src=os.path.join(self._source_subfolder, "PC"), dst=os.path.join(self.package_folder, "include", "python{}".format(self._version_major_minor)))
        self.copy("*.py", src=os.path.join(self._source_subfolder, "lib"), dst=os.path.join(self.package_folder, "bin", "Lib"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "lib", "test"))

        self.run("{} -c \"import compileall; compileall.compile_dir('{}')\"".format(os.path.join(build_path, self._cpython_interpreter_name), os.path.join(self.package_folder, "bin", "Lib").replace("\\", "/")),
                 run_environment=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            if self._is_py2:
                self._msvc_package_copy()
            else:
                self._msvc_package_layout()
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

            if self._is_py2:
                scripts = ("2to3", "idle", "pydoc", "python{}-config".format(self._version_major_minor), "smtpd.py")
            else:
                script_prefixes = ("2to3-", "easy_install-", "idle", "pydoc", "pyvenv-", "pip")
                scripts = tuple(os.path.join(self.package_folder, "bin", sp + self._version_major_minor) for sp in script_prefixes)

            for script_name in scripts:
                script = os.path.join(self.package_folder, "bin", script_name)
                if not os.path.isfile(script):
                    continue
                with open(script, "r") as fn:
                    fn.readline()
                    text = fn.read()
                with open(script, "w") as fn:
                    fn.write("#!/usr/bin/env python{}\n".format(self._version_major_minor))
                    fn.write(text)

            if not os.path.exists(self._cpython_symlink):
                os.symlink("python{}".format(self._version_major_minor), self._cpython_symlink)

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
            suffix = self._version_major_minor
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
            if tools.Version(self.version) < tools.Version("3.8"):
                if self.options.get_safe("pymalloc", False):
                    res += "m"
        return res

    def package_info(self):
        # FIXME: conan components Python::Interpreter component, need a target type
        # self.cpp_info.names["cmake_find_package"] = "Python"
        # self.cpp_info.names["cmake_find_package_multi"] = "Python"
        # FIXME: conan components need to generate multiple .pc files (python2, python-27)
        self.cpp_info.names["pkg_config"] = "python{}".format(self.version.split(".")[0])
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                lib_ext = "_d"
            else:
                lib_ext = ""
        else:
            if self._is_py3:
                self.cpp_info.includedirs.append(
                    os.path.join("include", "python{}{}".format(self._version_major_minor, self._abi_suffix)))
            lib_ext = self._abi_suffix + (".dll.a" if self.options.shared and self.settings.os == "Windows" else "")
        self.cpp_info.includedirs.append(os.path.join("include", "python{}".format(self._version_major_minor)))
        self.cpp_info.libs = ["python{}{}".format(self._version_major_minor, lib_ext)]
        if self.options.shared:
            self.cpp_info.defines.append("Py_ENABLE_SHARED")
        else:
            self.cpp_info.defines.append("Py_NO_ENABLE_SHARED")
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.extend(["dl", "m", "pthread", "util"])
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["shlwapi", "version", "ws2_32"])

        python = self._cpython_interpreter_path
        self.output.info("Setting PYTHON environment variable: {}".format(python))
        self.env_info.PYTHON = python

        if self.settings.compiler == "Visual Studio":
            pythonhome = os.path.join(self.package_folder, "bin")
        else:
            pythonhome = os.path.join(self.package_folder)
        self.output.info("Setting PYTHONHOME environment variable: {}".format(pythonhome))
        self.env_info.PYTHONHOME = pythonhome

        if self._is_py2:
            if self.settings.compiler == "Visual Studio":
                pass
        else:
            python_root = tools.unix_path(self.package_folder)
            self.output.info("Setting PYTHON_ROOT environment variable: {}".format(python_root))
            self.env_info.PYTHON_ROOT = python_root

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
