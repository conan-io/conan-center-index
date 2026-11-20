from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class QScintillaConan(ConanFile):
    name = "qscintilla"
    description = (
        "QScintilla is a port to Qt of the Scintilla source code editing widget: "
        "syntax highlighting, code folding, margins, auto-completion and call tips."
    )
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.riverbankcomputing.com/software/qscintilla/"
    topics = ("qt", "editor", "scintilla", "syntax-highlighting", "widget")
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
    implements = ["auto_shared_fpic"]

    @property
    def _qt_major(self):
        return Version(self.dependencies["qt"].ref.version).major

    @property
    def _lib_name(self):
        # Mirrors the TARGET logic of src/qscintilla.pro: only Debug on macOS ("_debug") and Windows ("d")
        # gets a suffix; release builds and Linux (any build type) use the plain name.
        name = f"qscintilla2_qt{self._qt_major}"
        if self.settings.build_type == "Debug":
            if self.settings.os == "Macos":
                name += "_debug"
            elif self.settings.os == "Windows":
                name += "d"
        return name

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=5.15 <7]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")  # qmake
        if not is_msvc(self):
            # qmake generates GNU Makefiles (MSVC uses nmake from VCVars)
            self.tool_requires("make/[*]")

    def validate(self):
        if Version(self.dependencies["qt"].ref.version).major == 5:
            check_min_cppstd(self, 11)
        else:
            check_min_cppstd(self, 17)

        if cross_building(self):
            raise ConanInvalidConfiguration(
                "Cross-building is not supported: qmake must run against a Qt prefix matching the host platform"
            )
        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration("On Windows only MSVC is supported (qmake generates nmake Makefiles)")

        qt_options = self.dependencies["qt"].options
        if not (qt_options.gui and qt_options.widgets):
            raise ConanInvalidConfiguration(f"{self.ref} requires qt:gui=True and qt:widgets=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _find_qmake(self):
        qt_folder = self.dependencies.build["qt"].package_folder
        exe = "qmake.exe" if self.settings_build.os == "Windows" else "qmake"
        for subdir in ("bin", "libexec", "lib"):
            candidate = os.path.join(qt_folder, subdir, exe)
            if os.path.isfile(candidate):
                return candidate
        raise ConanInvalidConfiguration(f"Could not find {exe} in {qt_folder}")

    def generate(self):
        VirtualBuildEnv(self).generate()
        if is_msvc(self):
            VCVars(self).generate()
        else:
            # Needed by Autotools.make(): it reads the conanbuild.conf this toolchain writes
            AutotoolsToolchain(self).generate()
        # Tell qmake where the Qt it should build against lives (the conan package is relocatable,
        # so the prefix hardcoded at Qt configure time is not valid here).
        qt_folder = self.dependencies["qt"].package_folder.replace("\\", "/")
        save(self, os.path.join(self.build_folder, "qt.conf"),
             f"[Paths]\nPrefix = {qt_folder}\nHostPrefix = {qt_folder}\n")

    def _qmake_args(self):
        args = [
            "-qtconf", os.path.join(self.build_folder, "qt.conf"),
            os.path.join(self.source_folder, "src", "qscintilla.pro"),
            "CONFIG-=debug_and_release",
            "CONFIG+=debug" if self.settings.build_type == "Debug" else "CONFIG+=release",
        ]
        if not self.options.shared:
            args.append("CONFIG+=staticlib")

        compilers = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        if compilers.get("c"):
            args.append(f"QMAKE_CC={compilers['c']}")
        if compilers.get("cpp"):
            args.extend([f"QMAKE_CXX={compilers['cpp']}",
                         f"QMAKE_LINK={compilers['cpp']}",
                         f"QMAKE_LINK_SHLIB={compilers['cpp']}"])
        if self.options.get_safe("fPIC"):
            args.append("QMAKE_CXXFLAGS+=-fPIC")

        # The .pro installs into Qt's own prefix ($$[QT_INSTALL_LIBS] etc.). Assignments after `-after` are
        # processed after the .pro file, so they override those paths and make `install` target our package.
        pkg = self.package_folder.replace("\\", "/")
        args.extend([
            "-after",
            f"target.path={pkg}/lib",
            f"header.path={pkg}/include",
            "INSTALLS-=trans qsci features",  # translations, API files and the qmake .prf are not needed
        ])
        return args

    def _make(self, target=None):
        if is_msvc(self):
            # qmake's win32-msvc spec writes NMake-format Makefiles, which GNU make cannot read
            self.run(f"nmake {target or ''}".strip(), cwd=self.build_folder)
        else:
            # GNU make from the make tool_requires, honouring tools.build:jobs
            Autotools(self).make(target=target)

    def build(self):
        self.run(" ".join([f'"{self._find_qmake()}"'] + [f'"{a}"' if " " in a else a for a in self._qmake_args()]),
                 cwd=self.build_folder)
        self._make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Install paths were redirected to the package folder in _qmake_args()
        self._make("install")
        if self.settings.os == "Windows":
            # qmake puts the DLL next to the import library
            copy(self, "*.dll", src=os.path.join(self.package_folder, "lib"),
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            rm(self, "*.dll", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QScintilla")
        self.cpp_info.set_property("cmake_target_name", "QScintilla::QScintilla")
        self.cpp_info.libs = [self._lib_name]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui", "qt::qtWidgets", "qt::qtPrintSupport"]
        if self.settings.os == "Macos" and self._qt_major == 5:
            self.cpp_info.requires.append("qt::qtMacExtras")
        if self.options.shared:
            self.cpp_info.defines.append("QSCINTILLA_DLL")
