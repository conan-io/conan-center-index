from conans import ConanFile, CMake, tools
import os
import json


class SignalrQtConan(ConanFile):
    name = "signalr-qt"
    url = "https://github.com/trassir/conan-center-index"
    homepage = "https://github.com/p3root/signalr-qt"
    topics = ("signalr-qt", "conan")
    license = "signalr-qt"
    description = "C++ implementation of Microsofts ASP.Net SignalR"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": True
    }
    generators = "json"

    current_dir = os.path.abspath(os.path.dirname(__file__))
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        sha256 = self.conan_data["sources"][self.version]["sha256"]
        url = self.conan_data["sources"][self.version]["url"]
        tools.get(url, sha256=sha256)
        os.rename("signalr-qt-%s" % self.version, self._source_subfolder)

    def requirements(self):
        self.requires.add("qt/5.14.1")

    def _find_qmake(self):
        buildinfo = json.load("conanbuildinfo.json")
        for dep in buildinfo["dependencies"]:
            if dep["name"] != "qt":
                continue
            for bin in dep["bin_paths"]:
                return(os.path.join(bin, "qmake"))
        return "qmake"

    def _build_with_qmake(self):
        qmake = self._find_qmake()
        with tools.chdir(self._source_subfolder):
            self.output.info("Building with qmake")

            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                args = [self._source_subfolder, "DESTDIR=bin"]

                def _getenvpath(var):
                    val = os.getenv(var)
                    if val and tools.os_info.is_windows:
                        val = val.replace("\\", "/")
                        os.environ[var] = val
                    return val

                value = _getenvpath('CC')
                if value:
                    args += ['QMAKE_CC=' + value,
                             'QMAKE_LINK_C=' + value,
                             'QMAKE_LINK_C_SHLIB=' + value]

                value = _getenvpath('CXX')
                if value:
                    args += ['QMAKE_CXX=' + value,
                             'QMAKE_LINK=' + value,
                             'QMAKE_LINK_SHLIB=' + value]

                self.run("%s %s" % (qmake, " ".join(args)), run_environment=True)

    def _build_with_make(self):
        with tools.chdir(self._source_subfolder):
            self.output.info("Building with make")
            if tools.os_info.is_windows:
                if self.settings.compiler == "Visual Studio":
                    make = "jom"
                else:
                    make = "mingw32-make"
            else:
                make = "make"
            self.run(make, run_environment=True)

    def _install_with_make(self):
        with tools.chdir(self._source_subfolder):
            self.output.info("Installing with make")
            if tools.os_info.is_windows:
                if self.settings.compiler == "Visual Studio":
                    make = "jom"
                else:
                    make = "mingw32-make"
            else:
                make = "make"
            self.run("%s install" % make)

    def build(self):
        self._build_with_qmake()
        self._build_with_make()
        self._install_with_make()

    def package(self):
        self._install_with_make()
        self.copy("README.md", src=self._source_subfolder, dst=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["signalr-qt"]
