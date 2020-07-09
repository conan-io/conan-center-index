import os
from conans import CMake, ConanFile, tools


class DbusConan(ConanFile):
    name = "dbus"
    license = "AFL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/dbus"
    description = "D-Bus is a simple system for interprocess communication and coordination."
    topics = ("conan", "dbus")
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "with_x11": [True, False],
        "with_glib": [True, False],
        "enable_assert": [True, False],
        "enable_checks": [True, False],
        "install_system_libs": [True, False],
        "use_output_debug_string": [True, False]}

    default_options = {
        "with_x11": False,
        "with_glib": False,
        "enable_assert": True,
        "enable_checks": True,
        "install_system_libs": False,
        "use_output_debug_string": False}

    generators = "cmake_find_package", "cmake_paths", "cmake"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    requires = (
        "expat/2.2.9"
    )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)


    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.65.0")

        if self.options.with_x11:
            self.requires("xorg/system")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)

            self._cmake.definitions["DBUS_BUILD_TESTS"] = False
            self._cmake.definitions["DBUS_ENABLE_DOXYGEN_DOCS"] = False
            self._cmake.definitions["DBUS_ENABLE_XML_DOCS"] = False

            self._cmake.definitions["DBUS_BUILD_X11"] = self.options.with_x11
            self._cmake.definitions["DBUS_WITH_GLIB"] = self.options.with_glib
            self._cmake.definitions["DBUS_DISABLE_ASSERT"] = self.options.enable_assert
            self._cmake.definitions["DBUS_DISABLE_CHECKS"] = self.options.enable_checks
            self._cmake.definitions["DBUS_INSTALL_SYSTEM_LIBS"] = self.options.install_system_libs
            self._cmake.definitions["DBUS_USE_OUTPUT_DEBUG_STRING"] = self.options.use_output_debug_string

            path_to_cmake_lists = os.path.join(self._source_subfolder, "cmake")

            self._cmake.configure(source_folder=path_to_cmake_lists,
                                  build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        dbus_cmake = tools.os.path.join(
            self._source_subfolder, "cmake", "CMakeLists.txt")

        if self.options.with_glib:
            tools.replace_in_file(dbus_cmake, "GLib2", "glib")
            tools.replace_in_file(dbus_cmake, "GLIB2", "GLIB")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "DBus1"
        self.cpp_info.names["cmake_find_package_multi"] = "DBus1"
        self.cpp_info.names["pkg_config"] = "dbus-1"
        self.cpp_info.libs = tools.collect_libs(self)
