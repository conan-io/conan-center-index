from conan import ConanFile
from conan.tools import files
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class QxmppConan(ConanFile):
    name = "qxmpp"
    license = "LGPL-2.1"
    homepage = "https://github.com/qxmpp-project/qxmpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform C++ XMPP client and server library. It is written in C++ and uses Qt framework."
    topics = "qt", "qt6", "xmpp", "xmpp-library", "xmpp-server", "xmpp-client"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gstreamer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gstreamer": False,
    }

    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("qt/6.2.4")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.19.2")
            self.requires("glib/2.70.1")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["WITH_GSTREAMER"] = self.options.with_gstreamer
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.LGPL", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared and self.settings.os == "Windows":
            files.mkdir(self, os.path.join(self.package_folder, "bin"))
            files.rename(self, os.path.join(self.package_folder, "lib", "qxmpp.dll"),
                         os.path.join(self.package_folder, "bin", "qxmpp.dll"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QXmpp")
        self.cpp_info.set_property("cmake_target_name", "QXmpp::QXmpp")
        self.cpp_info.set_property("pkg_config_name", "qxmpp")
        self.cpp_info.libs = ["qxmpp"]
        self.cpp_info.includedirs.append(os.path.join("include", "qxmpp"))
        self.cpp_info.requires = ["qt::qtCore", "qt::qtNetwork", "qt::qtXml"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "QXmpp"
        self.cpp_info.names["cmake_find_package_multi"] = "QXmpp"
