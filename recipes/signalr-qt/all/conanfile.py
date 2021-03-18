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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        url = self.conan_data["sources"][self.version]["url"]
        signalr_hash = self.conan_data["sources"][self.version]["signalr_hash"]
        qthttpserver_hash = self.conan_data["sources"][self.version]["qthttpserver_hash"]
        qtwebsockets_hash = self.conan_data["sources"][self.version]["qtwebsockets_hash"]

        self.run("git clone --recursive %s %s" % (url, self._source_subfolder))
        self.run("cd %s && git checkout %s" % (self._source_subfolder, signalr_hash))
        self.run("cd %s/ThirdParty/QtWebSockets && git checkout %s" % (self._source_subfolder, qtwebsockets_hash))
        self.run("cd %s/ThirdParty/QHttpServer && git checkout %s" % (self._source_subfolder, qthttpserver_hash))

    def requirements(self):
        self.requires.add("qt/5.14.1")

    def _find_qmake(self):
        buildinfo = json.load(open("conanbuildinfo.json"))
        for dep in buildinfo["dependencies"]:
            if dep["name"] != "qt":
                continue
            for bin in dep["bin_paths"]:
                return os.path.join(bin, "qmake")
        return "qmake"

    def _build_with_qmake(self):
        qmake = self._find_qmake()
        with tools.chdir(self.source_folder):
            self.output.info("Building with qmake")

            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                args = [os.path.join(self.build_folder, self._source_subfolder)]

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
        with tools.chdir(self.source_folder):
            self.output.info("Building with make")
            if tools.os_info.is_windows:
                if self.settings.compiler == "Visual Studio":
                    make = "jom"
                else:
                    make = "mingw32-make"
            else:
                make = "make"
            self.run(make, run_environment=True)

    def build(self):
        self._build_with_qmake()
        self._build_with_make()

    def package(self):
        self.copy("README.md", src=self._source_subfolder, dst=".", keep_path=False)
        self.copy("*.h",
                  src=os.path.join(self._source_subfolder, "SignalRLibraries/SignalRClient"),
                  dst="include", 
                  keep_path=True)
        if self.settings.os == "Windows":
            self.copy("*.lib", src="", dst="lib", keep_path=False, symlinks=True)
            self.copy("*.dll", src="", dst="bin", keep_path=False, symlinks=True)
        else:
            self.copy("*.so*", src="", dst="lib", keep_path=False, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = ["signalr-qt"]
