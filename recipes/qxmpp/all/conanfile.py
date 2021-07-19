from conans import ConanFile, CMake, tools
from os import path


class QxmppConan(ConanFile):
    name = "qxmpp"
    license = "LGPL-2.1"
    url = "https://github.com/qxmpp-project/qxmpp"
    description = "Cross-platform C++ XMPP client and server library. It is written in C++ and uses Qt framework."
    topics = ("qt", "qt6", "xmpp", "xmpp-library", "xmpp-server", "xmpp-client")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["patches/*"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "withGstreamer": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "withGstreamer": False}
    generators = "cmake"

    def requirements(self):
        self.requires("qt/6.1.2")
        if self.options.withGstreamer:
            self.requires("gstreamer/1.19.1")
            self.requires("glib/2.68.3")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        gitTag: str = self.conan_data["sources"][self.version]["gitTag"]

        self.run("git clone https://github.com/qxmpp-project/qxmpp.git")
        self.run(f"cd qxmpp && git checkout tags/{gitTag} -b {gitTag} && cd ..")
        tools.patch("qxmpp", self.conan_data["patches"][self.version]["default"])

        if self.options.withGstreamer:
            tools.patch("qxmpp", self.conan_data["patches"][self.version]["gstreamer"])

    def __get_option_str(self, b: bool) -> str:
        if b:
            return "ON"
        else:
            return "OFF"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["WITH_GSTREAMER"] = self.__get_option_str(self.options.withGstreamer)
        cmake.configure(source_folder="qxmpp")
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include/base", src="qxmpp/base")
        self.copy("*.h", dst="include/client", src="qxmpp/client")
        self.copy("*.h", dst="include/server", src="qxmpp/server")
        self.copy("*qxmpp.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["qxmpp"]

