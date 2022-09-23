from conan import ConanFile
from conan.tools.files import rename, apply_conandata_patches, replace_in_file, rmdir, save, rm, get
from conan.tools.microsoft import is_msvc
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment, tools
from contextlib import contextmanager
import functools
import textwrap

required_conan_version = ">=1.51.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.settings.os != "Windows":
            self.requires("libuuid/1.0.3")

    def validate(self):
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("shared builds are unavailable due to libtool's inability to create shared libraries")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _build_context(self):
        if is_msvc(self):
            with tools.vcvars(self.settings):
                msvc_cl_sh =  f"{self.build_folder}/msvc_cl.sh".replace("\\", "/")
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
        return f"{self.package_folder}/bin/share"

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        autotools.link_flags.extend(["-L{}".format(l.replace("\\", "/")) for l in autotools.library_paths])
        autotools.library_paths = []
        if is_msvc(self):
            autotools.cxx_flags.append("-EHsc")
            if self.settings.compiler == "Visual Studio":
                vs_ide_version = self.settings.compiler.version
            else:
                vs_ide_version = msvc_version_to_vs_ide_version(self.settings.compiler.version)
            if Version(vs_ide_version) >= "12":
                autotools.flags.append("-FS")
        conf_args = [
            "--datarootdir={}".format(self._datarootdir.replace("\\", "/")),
            "--disable-documentation",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return autotools

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Relocatable shared lib on macOS
        replace_in_file(self, f"{self._source_subfolder}/configure",
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

        if is_msvc(self) and not self.options.shared:
            rename(self, f"{self.package_folder}/lib/libxapian.lib",
                         f"{self.package_folder}/lib/xapian.lib")

        rm(self, "xapian-config", f"{self.package_folder}/bin")
        rm(self, "libxapian.la", f"{self.package_folder}/lib")
        rmdir(self, f"{self.package_folder}/lib/cmake")
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")
        rmdir(self, f"{self._datarootdir}/doc")
        rmdir(self, f"{self._datarootdir}/man")
        self._create_cmake_module_variables(
            f"{self.package_folder}/{self._module_file_rel_path}"
        )

    def _create_cmake_module_variables(self, module_file):
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
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return f"lib/cmake/conan-official-{self.name}-variables.cmake"

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

        binpath = f"{self.package_folder}/bin"
        self.output.info(f"Appending PATH environment variable: {binpath}")
        self.env_info.PATH.append(binpath)

        xapian_aclocal = tools.unix_path(f"{self._datarootdir}/aclocal")
        self.output.info(f"Appending AUTOMAKE_CONAN_INCLUDES environment variable: {xapian_aclocal}")
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(tools.unix_path(xapian_aclocal))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "xapian"
        self.cpp_info.names["cmake_find_package_multi"] = "xapian"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
