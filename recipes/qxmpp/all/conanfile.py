from conans import ConanFile, CMake, tools
from os import rename
from os.path import join


class QxmppConan(ConanFile):
    name = "qxmpp"
    license = "LGPL-2.1"
    homepage = "https://github.com/qxmpp-project/qxmpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform C++ XMPP client and server library. It is written in C++ and uses Qt framework."
    topics = ("qt", "qt6", "xmpp", "xmpp-library", "xmpp-server", "xmpp-client")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["patches/*"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_gstreamer": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_gstreamer": False}
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires("qt/6.1.2")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.19.1")
            self.requires("glib/2.68.3")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            
    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self.name)

    def __get_option_str(self, b: bool) -> str:
        if b:
            return "ON"
        else:
            return "OFF"

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = CMake(self)
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["WITH_GSTREAMER"] = self.__get_option_str(self.options.with_gstreamer)
        cmake.configure(source_folder="qxmpp")
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=join(self.name, "LICENSE.LGPL"))
        self.copy("*.h", dst="include/base", src=join(self.name, "base"))
        self.copy("*.h", dst="include/client", src=join(self.name, "client"))
        self.copy("*.h", dst="include/server", src=join(self.name, "server"))
        self.copy("*qxmpp.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["qxmpp"]

