from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.52.0"


class DbusConan(ConanFile):
    name = "dbus"
    license = ("AFL-2.1", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/dbus"
    description = "D-Bus is a simple system for interprocess communication and coordination."
    topics = ("dbus")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "system_socket": ["ANY"],
        "system_pid_file": ["ANY"],
        "with_x11": [True, False],
        "with_glib": [True, False],
        "with_selinux": [True, False],
        "session_socket_dir": ["ANY"],
    }
    default_options = {
        "system_socket": "",
        "system_pid_file": "",
        "with_x11": False,
        "with_glib": False,
        "with_selinux": False,
        "session_socket_dir": "/tmp",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            del self.options.with_x11

    def configure(self):
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/2.4.9")
        if self.options.with_glib:
            self.requires("glib/2.74.0")
        if self.options.with_selinux:
            self.requires("selinux/3.3")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")

    def validate(self):
        if Version(self.version) >= "1.14.0":
            if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < 7:
                raise ConanInvalidConfiguration(f"{self.ref} requires at least gcc 7.")
            if self.info.settings.os == "Windows":
                raise ConanInvalidConfiguration(f"{self.ref} does not support windows. contributions are welcome")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DBUS_BUILD_TESTS"] = False
        tc.variables["DBUS_ENABLE_DOXYGEN_DOCS"] = False
        tc.variables["DBUS_ENABLE_XML_DOCS"] = False
        tc.variables["DBUS_BUILD_X11"] = self.options.get_safe("with_x11", False)
        tc.variables["DBUS_WITH_GLIB"] = self.options.with_glib
        tc.variables["DBUS_DISABLE_ASSERT"] = is_apple_os(self)
        tc.variables["DBUS_DISABLE_CHECKS"] = False
        # https://github.com/freedesktop/dbus/commit/e827309976cab94c806fda20013915f1db2d4f5a
        tc.variables["DBUS_SESSION_SOCKET_DIR"] = self.options.session_socket_dir
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Unfortunately, there is currently no other way to force disable
        # CMAKE_FIND_PACKAGE_PREFER_CONFIG ON in CMake conan_toolchain.
        replace_in_file(
            self,
            os.path.join(self.generators_folder, "conan_toolchain.cmake"),
            "set(CMAKE_FIND_PACKAGE_PREFER_CONFIG ON)",
            "",
            strict=False,
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        if Version(self.version) < "1.14.0":
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "cmake"))
        else:
            cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        mkdir(self, os.path.join(self.package_folder, "res"))
        for i in ["var", "share", "etc"]:
            rename(self, os.path.join(self.package_folder, i), os.path.join(self.package_folder, "res", i))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "systemd"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"dbus-1": "dbus-1::dbus-1"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
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
        self.cpp_info.resdirs = ["res"]
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
