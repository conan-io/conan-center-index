from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

class QbsConan(ConanFile):
    name = "qbs"
    description = "The Qbs build system"
    topics = ("conan", "qbs", "build", "automation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://qbs.io"
    license = "LGPL-2.1-only", "LGPL-3.0-only", "Nokia-Qt-exception-1.1"
    settings = "arch", "build_type", "compiler", "os"
    no_copy_source=True
    exports = ["patches/*.patch"]
    build_policy = "missing"

    build_requires = "qt/5.15.2"

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom/1.1.3")

    def configure(self):
        if self.settings.os not in ["Windows", "Linux", "Macos"]:
            raise ConanInvalidConfiguration("The OS ({}) is not supported by {}.".format(self.settings.os, self.name))
        if self.settings.arch not in ["x86_64"]:
            raise ConanInvalidConfiguration("The arch ({}) is not supported by {}.".format(self.settings.arch, self.name))

        self.options["qt"].gui = False
        self.options["qt"].openssl = False
        self.options["qt"].qtscript = True
        self.options["qt"].shared = False
        self.options["qt"].widgets = False
        self.options["qt"].with_odbc = False
        self.options["qt"].with_pq = False
        self.options["qt"].with_sqlite3 = False
        self.options["qt"].with_zstd = False
        for dep, options in self._data["options"].items():
            for key, value in options.items():
                setattr(self.options[dep], key, value)

        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "5.0",
            "clang": "6.0",
            "apple-clang": "11",
            "Visual Studio": "16",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warn(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))


    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch, base_path="qbs-src-%s" % self.version)

    def build(self):
        qmake = os.path.join(self.deps_cpp_info["qt"].bin_paths[0], "qmake")
        source_dirpath = os.path.join(self.source_folder, "qbs-src-%s" % self.version)
        project_filepath = os.path.join(source_dirpath, "qbs.pro")
        args = [
            "-r", project_filepath,
            "QT-=gui",
            "CONFIG+=release",
            "CONFIG-=debug",
            "CONFIG-=debug_and_release",
            "CONFIG+=nomake_tests",
            "CONFIG+=qbs_no_dev_install",
            "CONFIG+=qbs_no_man_install",
            "QBS_INSTALL_PREFIX=/"
        ]
        ncores = tools.cpu_count()

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            self.run("%s %s" % (qmake, " ".join(args)), run_environment=True)
            self.run("%s -j%s" % (self._data["build_tool"], ncores), run_environment=True)

    def package(self):
        install_root = os.path.join(self.package_folder, "bin")
        self.run("%s install INSTALL_ROOT=%s" % (self._data["build_tool"], install_root))
        # This recipe builds Qbs statically, the libs are not needed.
        tools.rmdir(os.path.join(install_root, "lib"))
        tools.rmdir(os.path.join(install_root, "share", "qbs", "examples"))
        self.copy(src="qbs-src-%s" % self.version, dst="licenses", pattern="LICENSE*")
        self.copy(src="qbs-src-%s" % self.version, dst="licenses", pattern="LGPL*")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        binpath = os.path.join(self.package_folder, 'bin/bin')
        self.env_info.PATH.append(binpath)

    @property
    def _data(self):
        data = {
            'Linux': {
                "build_tool": "make",
                'options': {}
            },
            'Macos': {
                "build_tool": "make",
                'options': {}
            },
            'Windows': {
                "build_tool": "jom" if self.settings.compiler == "Visual Studio" else "mingw32-make",
                'options': {}
            }
        }
        return data[str(self.settings.os)]
