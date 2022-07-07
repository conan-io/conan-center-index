from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from os import path

required_conan_version = ">=1.33.0"


class QbsConan(ConanFile):
    name = "qbs"
    description = "The Qbs build system"
    topics = ("qbs", "build", "tool")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://qbs.io"
    license = "LGPL-2.1-only", "LGPL-3.0-only", "Nokia-Qt-exception-1.1"

    short_paths = True
    settings = "os", "arch", "compiler", "build_type"
    exports = ["patches/*.patch"]

    def validate(self):
        if self.settings.os not in ["Linux", "Windows", "Macos"]:
            raise ConanInvalidConfiguration(
                "qbs supports Linux/Windows/macOS only.")

        if self.settings.build_type not in ["Debug", "Release"]:
            raise ConanInvalidConfiguration(
                "qbs can be builed only as debug or release.")

    def build_requirements(self):
        self.tool_requires("qt/5.15.5")
        if self.settings.compiler == "Visual Studio":
            self.tool_requires("jom/1.1.3")

    def configure(self):
        self.options["qt"].gui = False
        self.options["qt"].openssl = False
        self.options["qt"].qtscript = True
        self.options["qt"].shared = True
        self.options["qt"].widgets = False
        self.options["qt"].with_odbc = False
        self.options["qt"].with_pcre2 = False
        self.options["qt"].with_pq = False
        self.options["qt"].with_sqlite3 = False
        self.options["qt"].with_zstd = False

        if self.settings.compiler not in ["gcc", "clang"] or tools.Version(self.settings.compiler.version) >= "5.3":
            self.options["qt"].with_mysql = False

        if self.settings.os == "Linux":
            self.options["qt"].with_icu = False

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
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @property
    def _data(self):
        data = {
            'Linux': {
                "build_tool": "make",
                "frameworks": [],
                "system_libs": ["m"],
            },
            'Macos': {
                "build_tool": "make",
                "frameworks": ["SystemConfiguration", "DiskArbitration", "CoreFoundation",
                               "CFNetwork", "Foundation", "CoreServices", "IOKit", "Security",
                               "ApplicationServices", "AppKit"],
                "system_libs": [],
            },
            'Windows': {
                "build_tool": "jom" if self.settings.compiler == "Visual Studio" else "mingw32-make",
                "frameworks": [],
                "system_libs": ["mpr", "psapi", "winmm", "winmm", "dnsapi",
                                "iphlpapi", "netapi32", "userenv", "ws2_32", "ws2_32", "version"],
            }
        }

        return data[str(self.settings.os)]

    def build(self):
        project_filepath = path.join(self.source_folder, "qbs.pro")
        args = [
            "-r", project_filepath,
            "QT-=gui",
            "CONFIG-=release",
            "CONFIG-=debug",
            "CONFIG-=debug_and_release",
            "CONFIG+=%s" % str(self.settings.build_type).lower(),
            "CONFIG+=nomake_tests",
            "CONFIG+=qbs_no_dev_install",
            "CONFIG+=qbs_no_man_install",
            "CONFIG+=qbs_enable_bundled_qt",
            "CONFIG+=no_qt_rpath",
            "QBS_INSTALL_PREFIX=/"
        ]
        ncores = tools.cpu_count()

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            self.run("qmake  %s" % ' '.join(args), run_environment=True)
            self.run("%s -j%s" %
                     (self._data['build_tool'], ncores), run_environment=True)

    def package(self):
        self.run("%s install INSTALL_ROOT=%s" %
                 (self._data["build_tool"], self.package_folder))
        # This recipe builds Qbs statically, the libs are not needed.
        tools.rmdir(path.join(self.package_folder, "share", "qbs", "examples"))
        self.copy(dst="licenses", pattern="LICENSE*")
        self.copy(dst="licenses", pattern="LGPL*")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        binpath = path.join(self.package_folder, 'bin')
        self.env_info.PATH.append(binpath)

        self.cpp_info.includedirs = []

        self.cpp_info.system_libs = self._data["system_libs"]
        self.cpp_info.system_libs = self._data["frameworks"]
