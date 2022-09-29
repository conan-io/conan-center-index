import os
import textwrap

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, get, mkdir, rename, rmdir, save, rm
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
from conans import CMake

required_conan_version = ">=1.51.3"


class DbusConan(ConanFile):
    name = "dbus"
    license = ("AFL-2.1", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/dbus"
    description = "D-Bus is a simple system for interprocess communication and coordination."
    topics = ("dbus")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "system_socket": "ANY",
        "system_pid_file": "ANY",
        "with_x11": [True, False],
        "with_glib": [True, False],
        "with_selinux": [True, False],
        "session_socket_dir": "ANY",
    }
    default_options = {
        "system_socket": "",
        "system_pid_file": "",
        "with_x11": False,
        "with_glib": False,
        "with_selinux": False,
        "session_socket_dir": "/tmp",
    }

    generators = "cmake", "cmake_find_package", "VirtualBuildEnv", "VirtualRunEnv"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            del self.options.with_x11

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("expat/2.4.9")
        if self.options.with_glib:
            self.requires("glib/2.73.3")
        if self.options.with_selinux:
            self.requires("selinux/3.3")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")

    def validate(self):
        if Version(self.version) >= "1.14.0":
            if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < 7:
                raise ConanInvalidConfiguration("dbus requires at least gcc 7.")
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("dbus 1.14.0 does not support windows. contributions are welcome")

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, self._source_subfolder))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)

            self._cmake.definitions["DBUS_BUILD_TESTS"] = False
            self._cmake.definitions["DBUS_ENABLE_DOXYGEN_DOCS"] = False
            self._cmake.definitions["DBUS_ENABLE_XML_DOCS"] = False

            self._cmake.definitions["DBUS_BUILD_X11"] = self.options.get_safe("with_x11", False)
            self._cmake.definitions["DBUS_WITH_GLIB"] = self.options.with_glib
            self._cmake.definitions["DBUS_DISABLE_ASSERT"] = is_apple_os(self)
            self._cmake.definitions["DBUS_DISABLE_CHECKS"] = False

            # Conan does not provide an EXPAT_LIBRARIES CMake variable for the Expat library.
            # Define EXPAT_LIBRARIES to be the expat::expat target provided by Conan to fix linking.
            self._cmake.definitions["EXPAT_LIBRARIES"] = "expat::expat"

            # https://github.com/freedesktop/dbus/commit/e827309976cab94c806fda20013915f1db2d4f5a
            self._cmake.definitions["DBUS_SESSION_SOCKET_DIR"] = self.options.session_socket_dir

            self._cmake.configure(source_folder=self._source_subfolder,
                                  build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        mkdir(self, os.path.join(self.package_folder, "res"))
        for i in ["var", "share", "etc"]:
            rename(self, os.path.join(self.package_folder, i), os.path.join(self.package_folder, "res", i))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "systemd"))
        rm(self, "*.la", self.package_folder)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"dbus-1": "dbus-1::dbus-1"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "DBus1")
        self.cpp_info.set_property("cmake_target_name", "dbus-1")
        self.cpp_info.set_property("pkg_config_name", "dbus-1")
        self.cpp_info.includedirs.extend([
            os.path.join("include", "dbus-1.0"),
            os.path.join("lib", "dbus-1.0", "include"),
        ])
        self.cpp_info.libs = ["dbus-1"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("rt")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["iphlpapi", "ws2_32"])
        else:
            self.cpp_info.system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "DBus1"
        self.cpp_info.filenames["cmake_find_package_multi"] = "DBus1"
        self.cpp_info.names["cmake_find_package"] = "dbus-1"
        self.cpp_info.names["cmake_find_package_multi"] = "dbus-1"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "dbus-1"
