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
    generators = "visual_studio"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "optimizations": [True, False],
        "lto": [True, False],
        "docstrings": [True, False],
        "pymalloc": [True, False],
        "unicode": ["ucs2", "ucs4"],
        "with_bz2": [True, False],
        "with_bsddb": [True, False],
        "with_gdbm": [True, False],
        "with_nis": [True, False],
        "with_sqlite3": [True, False],
        "with_tkinter": [True, False],
        # "with_curses": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "optimizations": False,
        "lto": False,
        "docstrings": True,
        "pymalloc": True,
        "unicode": "ucs2",
        "with_bz2": True,
        "with_bsddb": True,
        "with_gdbm": True,
        "with_nis": True,
        "with_sqlite3": True,
        "with_tkinter": False,
        # "with_curses": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _version_major_minor(self):
        if self.settings.compiler == "Visual Studio":
            joiner = ""
        else:
            joiner = "."
        return joiner.join(self.version.split(".")[:2])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            del self.options.lto
            del self.options.docstrings
            del self.options.pymalloc
            del self.options.with_gdbm
            del self.options.with_nis
            del self.options.with_curses
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version >= tools.Version(14):
                self.output.warn("Visual Studio versions 14 and higher are not supported")
            if not self.options.shared:
                raise ConanInvalidConfiguration("MSVC does not support a static build")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Python-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("openssl/1.1.1g")
        self.requires("expat/2.2.9")
        self.requires("mpdecimal/2.4.2")
        self.requires("zlib/1.2.11")
        if self.settings.compiler != "Visual Studio":
            self.requires("libffi/3.3")
        if self.settings.os != "Windows":
            self.requires("libuuid/1.0.3")
            self.requires("libxcrypt/4.4.16")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_bsddb:
            self.requires("libdb/5.3.28")
        if self.options.get_safe("with_gdbm"):
            self.requires("gdbm/1.18.1")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.31.1")
        if self.options.with_tkinter:
            raise ConanInvalidConfiguration("tk is not available on CCI (yet)")
            self.requires("tk/8.6.9.1@bincrafters/stable", private=self._is_installer)
        if self.options.get_safe("with_curses"):
            self.requires("ncurses/6.2")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        conf_args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-unicode={}".format(self.options.unicode),
            "--with-doc-strings" if self.options.docstrings else "--without-doc-strings",
            "--with-pymalloc" if self.options.pymalloc else "--without-pymalloc",
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-optimizations" if self.options.optimizations else "--disable-optimizations",
            "--with-lto" if self.options.lto else "--without-lto",
            "--with-pydebug" if self.settings.build_type == "Debug" else "--without-pydebug",
        ]
        if self.settings.compiler == "intel":
            conf_args.extend(["--with-icc", "--without-gcc"])
        if tools.get_env("CC"):
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

    def _build_msvc(self):
        msbuild = MSBuild(self)
        msvc_archs = {
            "x86": "Win32",
            "x86_64": "x64",
        }
        msvc_properties = {
            "IncludeExternals": "true",
        }
        solution_path = os.path.join(self._source_subfolder, "PCBuild", "pcbuild.sln")
        project_set = set(m.group(1) for m in re.finditer("\"([^\"]+)\\.vcxproj\"", open(solution_path).read()))
        projects = dict((os.path.basename(p), p) for p in project_set)

        for project in {"bdist_wininst", "libeay", "ssleay", "sqlite3", "tcl", "tk", "tix"}:
            projects.pop(project)
        if not self.options.with_bsddb:
            projects.pop("_bsddb")
        if not self.options.with_bz2:
            projects.pop("bz2")
        if not self.options.with_sqlite3:
            projects.pop("_sqlite3")
        if not self.options.with_tkinter:
            projects.pop("_tkinter")

        self.output.info("Building Visual Studio projects: {}".format(set(projects.keys())))

        upgraded = False
        for project in projects.values():
            project_file = os.path.join(self._source_subfolder, "PCBuild", project + ".vcxproj")
            msbuild.build(project_file, upgrade_project=not upgraded, build_type="Debug" if self.settings.build_type == "Debug" else "Release", arch=msvc_archs, properties=msvc_properties)
            upgraded = True

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _msvc_artifacts_path(self):
        build_subdir = {
            "x86_64": "amd64",
            "x86": "Win32",
        }[str(self.settings.arch)]
        return os.path.join(self._source_subfolder, "PCBuild", build_subdir)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            build_subdir = {
                "x86_64": "amd64",
                "x86": "Win32",
            }[str(self.settings.arch)]
            build_path = os.path.join(self._source_subfolder, "PCBuild", build_subdir)
            infix = "_d" if self.settings.build_type == "Debug" else ""
            self.copy("*.exe", src=build_path, dst=os.path.join(self.package_folder, "bin"))
            self.copy("*.dll", src=build_path, dst=os.path.join(self.package_folder, "bin"))
            self.copy("*.pyd", src=build_path, dst=os.path.join(self.package_folder, "bin", "DLLs"))
            self.copy("python{}{}.lib".format(self._version_major_minor, infix), src=build_path, dst=os.path.join(self.package_folder, "lib"))
            self.copy("*", src=os.path.join(self._source_subfolder, "Include"), dst=os.path.join(self.package_folder, "include", "python{}".format(self._version_major_minor)))
            self.copy("pyconfig.h", src=os.path.join(self._source_subfolder, "PC"), dst=os.path.join(self.package_folder, "include", "python{}".format(self._version_major_minor)))
            self.copy("*.py", src=os.path.join(self._source_subfolder, "lib"), dst=os.path.join(self.package_folder, "bin", "Lib"))
            tools.rmdir(os.path.join(self.package_folder, "bin", "lib", "test"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

            for script_name in ("2to3", "idle", "pydoc", "python{}-config".format(self._version_major_minor), "smtpd.py"):
                script = os.path.join(self.package_folder, "bin", script_name)
                with open(script, "r") as fn:
                    fn.readline()
                    text = fn.read()
                with open(script, "w") as fn:
                    fn.write("#!/usr/bin/env python{}\n".format(self._version_major_minor))
                    fn.write(text)

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

    def package_info(self):
        # FIXME: conan components Python::Interpreter component, need a target type
        # self.cpp_info.names["cmake_find_package"] = "Python"
        # self.cpp_info.names["cmake_find_package_multi"] = "Python"
        # FIXME: conan components need to generate multiple .pc files (python2, python-27)
        self.cpp_info.names["pkg_config"] = "python2"
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                lib_ext = "_d"
            else:
                lib_ext = ""
        else:
            lib_ext = ".dll.a" if self.options.shared and self.settings.os == "Windows" else ""
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

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        if self.settings.compiler == "Visual Studio":
            pythonhome = os.path.join(self.package_folder, "bin")
            self.output.info("Setting PYTHONHOME environment variable: {}".format(pythonhome))
            self.env_info.PYTHONHOME = pythonhome
