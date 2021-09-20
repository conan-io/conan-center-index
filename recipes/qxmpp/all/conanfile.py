from conans import ConanFile, CMake, tools
import os


class QxmppConan(ConanFile):
    name = "qxmpp"
    license = "LGPL-2.1"
    homepage = "https://github.com/qxmpp-project/qxmpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform C++ XMPP client and server library. It is written in C++ and uses Qt framework."
    topics = "qt", "qt6", "xmpp", "xmpp-library", "xmpp-server", "xmpp-client"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["patches/*", "CMakeLists.txt"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_gstreamer": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_gstreamer": False}
    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        self._cmake.definitions["BUILD_TESTS"] = "OFF"
        self._cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        self._cmake.definitions["WITH_GSTREAMER"] = self.options.with_gstreamer
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.LGPL", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["qxmpp"]
        self.cpp_info.includedirs.append(os.path.join("include", "qxmpp"))
        self.cpp_info.filenames["cmake_find_package"] = "QXmpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "QXmpp"
        self.cpp_info.names["cmake_find_package"] = "QXmpp"
        self.cpp_info.names["cmake_find_package_multi"] = "QXmpp"
        self.cpp_info.names["pkg_config"] = "qxmpp"
        self.cpp_info.requires = ["qt::qtCore", "qt::qtNetwork", "qt::qtXml"]

