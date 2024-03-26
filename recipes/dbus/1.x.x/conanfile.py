from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rm, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class DbusConan(ConanFile):
    name = "dbus"
    license = ("AFL-2.1", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/dbus"
    description = "D-Bus is a simple system for interprocess communication and coordination."
    topics = "bus", "interprocess", "message"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "system_socket": [None, "ANY"],
        "system_pid_file": [None, "ANY"],
        "with_x11": [True, False],
        "with_glib": [True, False],
        "with_systemd": [True, False],
        "with_selinux": [True, False],
        "session_socket_dir": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "system_socket": None,
        "system_pid_file": None,
        "with_x11": False,
        "with_glib": False,
        "with_systemd": False,
        "with_selinux": False,
        "session_socket_dir": "/tmp",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            del self.options.with_systemd
        if self.settings.os not in ("Linux", "FreeBSD"):
            del self.options.with_x11
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/2.6.0")
        if self.options.with_glib:
            self.requires("glib/2.78.3")
        if self.options.get_safe("with_systemd"):
            self.requires("libsystemd/253.6")
        if self.options.with_selinux:
            self.requires("libselinux/3.3")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < 7:
            raise ConanInvalidConfiguration(f"{self.ref} requires at least gcc 7.")

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config",check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["asserts"] = not is_apple_os(self)
        tc.project_options["checks"] = False
        tc.project_options["doxygen_docs"] = "disabled"
        tc.project_options["modular_tests"] = "disabled"
        tc.project_options["system_socket"] = str(self.options.get_safe("system_socket", ""))
        tc.project_options["system_pid_file"] = str(self.options.get_safe("system_pid_file", ""))
        tc.project_options["session_socket_dir"] = str(self.options.get_safe("session_socket_dir", ""))
        tc.project_options["selinux"] = "enabled" if self.options.get_safe("with_selinux", False) else "disabled"
        tc.project_options["systemd"] = "enabled" if self.options.get_safe("with_systemd", False) else "disabled"
        if self.options.get_safe("with_systemd", False):
            tc.project_options["systemd_system_unitdir"] = os.path.join(self.package_folder, "lib", "systemd", "system")
            tc.project_options["systemd_user_unitdir"] = os.path.join(self.package_folder, "lib", "systemd", "user")
        if is_apple_os(self):
            tc.project_options["launchd_agent_dir"] = os.path.join(self.package_folder, "res", "LaunchAgents")
        tc.project_options["x11_autolaunch"] = "enabled" if self.options.get_safe("with_x11", False) else "disabled"
        tc.project_options["xml_docs"] = "disabled"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('test')", "# subdir('test')")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        mkdir(self, os.path.join(self.package_folder, "res"))
        for i in ["var", "share", "etc"]:
            rename(self, os.path.join(self.package_folder, i), os.path.join(self.package_folder, "res", i))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "systemd"))
        fix_apple_shared_install_name(self)
        if self.settings.os == "Windows" and not self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "libdbus-1.a"), os.path.join(self.package_folder, "lib", "dbus-1.lib"))

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

        if not self.options.shared:
            self.cpp_info.defines.append("DBUS_STATIC_BUILD")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "DBus1"
        self.cpp_info.filenames["cmake_find_package_multi"] = "DBus1"
        self.cpp_info.names["cmake_find_package"] = "dbus-1"
        self.cpp_info.names["cmake_find_package_multi"] = "dbus-1"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "dbus-1"
