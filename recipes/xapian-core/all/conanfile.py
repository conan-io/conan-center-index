from conan.tools.files import rename
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import textwrap

required_conan_version = ">=1.43.0"


class XapianCoreConan(ConanFile):
    name = "xapian-core"
    description = (
        "Xapian is a highly adaptable toolkit which allows developers to easily "
        "add advanced indexing and search facilities to their own applications."
    )
    topics = ("xapian", "search", "engine", "indexing", "query")
    license = "GPL-2.0-or-later"
    homepage = "https://xapian.org/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("shared builds are unavailable due to libtool's inability to create shared libraries")

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("libuuid/1.0.3")
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _build_context(self):
        if self._is_msvc:
            with tools.vcvars(self.settings):
                msvc_cl_sh =  os.path.join(self.build_folder, "msvc_cl.sh").replace("\\", "/")
                env = {
                    "AR": "lib",
                    "CC": msvc_cl_sh,
                    "CXX": msvc_cl_sh,
                    "LD": msvc_cl_sh,
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        self._autotools.link_flags.extend(["-L{}".format(l.replace("\\", "/")) for l in self._autotools.library_paths])
        self._autotools.library_paths = []
        if self._is_msvc:
            self._autotools.cxx_flags.extend(["-EHsc", "-FS"])
        conf_args = [
            "--datarootdir={}".format(self._datarootdir.replace("\\", "/")),
            "--disable-documentation",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Relocatable shared lib on macOS
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                              "-install_name \\$rpath/",
                              "-install_name @rpath/")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        if self._is_msvc and not self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "libxapian.lib"),
                         os.path.join(self.package_folder, "lib", "xapian.lib"))

        os.unlink(os.path.join(os.path.join(self.package_folder, "bin", "xapian-config")))
        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libxapian.la")))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self._datarootdir, "doc"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            set(XAPIAN_FOUND TRUE)
            set(XAPIAN_INCLUDE_DIR ${xapian_INCLUDE_DIR}
                                   ${xapian_INCLUDE_DIR_RELEASE}
                                   ${xapian_INCLUDE_DIR_RELWITHDEBINFO}
                                   ${xapian_INCLUDE_DIR_MINSIZEREL}
                                   ${xapian_INCLUDE_DIR_DEBUG})
            set(XAPIAN_LIBRARIES ${xapian_LIBRARIES}
                                 ${xapian_LIBRARIES_RELEASE}
                                 ${xapian_LIBRARIES_RELWITHDEBINFO}
                                 ${xapian_LIBRARIES_MINSIZEREL}
                                 ${xapian_LIBRARIES_DEBUG})
        """)
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xapian")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "xapian-core")

        self.cpp_info.libs = ["xapian"]
        if not self.options.shared:
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.system_libs = ["rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["rpcrt4", "ws2_32"]
            elif self.settings.os == "SunOS":
                self.cpp_info.system_libs = ["socket", "nsl"]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(binpath))
        self.env_info.PATH.append(binpath)

        xapian_aclocal = tools.unix_path(os.path.join(self._datarootdir, "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(xapian_aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(tools.unix_path(xapian_aclocal))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "xapian"
        self.cpp_info.names["cmake_find_package_multi"] = "xapian"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
