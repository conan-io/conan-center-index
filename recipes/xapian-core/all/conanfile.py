from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path, unix_path_package_info_legacy
import os
import textwrap

required_conan_version = ">=1.57.0"


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

    package_type = "library"
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
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os != "Windows":
            self.requires("util-linux-libuuid/2.39")

    def validate(self):
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "shared builds are unavailable due to libtool's inability to create shared libraries"
            )

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
            "--disable-documentation",
        ])
        env = tc.environment()
        if is_msvc(self):
            msvc_cl_sh = unix_path(self, os.path.join(self.source_folder, "msvc_cl.sh"))
            env.define("AR", "lib")
            env.define("CC", msvc_cl_sh)
            env.define("CXX", msvc_cl_sh)
            env.define("LD", msvc_cl_sh)
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        tc.generate(env)

        if is_msvc(self):
            # Custom AutotoolsDeps for cl like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            includedirs = []
            defines = []
            libs = []
            libdirs = []
            linkflags = []
            cxxflags = []
            cflags = []
            for dependency in self.dependencies.values():
                deps_cpp_info = dependency.cpp_info.aggregated_components()
                includedirs.extend(deps_cpp_info.includedirs)
                defines.extend(deps_cpp_info.defines)
                libs.extend(deps_cpp_info.libs + deps_cpp_info.system_libs)
                libdirs.extend(deps_cpp_info.libdirs)
                linkflags.extend(deps_cpp_info.sharedlinkflags + deps_cpp_info.exelinkflags)
                cxxflags.extend(deps_cpp_info.cxxflags)
                cflags.extend(deps_cpp_info.cflags)

            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("LIBS", [f"-l{lib}" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        if is_msvc(self) and not self.options.shared:
            rename(self, f"{self.package_folder}/lib/libxapian.lib",
                         f"{self.package_folder}/lib/xapian.lib")

        rm(self, "xapian-config", f"{self.package_folder}/bin")
        rm(self, "*.la", f"{self.package_folder}/lib")
        rmdir(self, f"{self.package_folder}/lib/cmake")
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")
        rmdir(self, f"{self._datarootdir}/doc")
        rmdir(self, f"{self._datarootdir}/man")
        fix_apple_shared_install_name(self)

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

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xapian")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "xapian-core")
        self.cpp_info.libs = ["xapian"]
        self.cpp_info.resdirs = ["res"]
        if not self.options.shared:
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.system_libs = ["rt", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["rpcrt4", "ws2_32"]
            elif self.settings.os == "SunOS":
                self.cpp_info.system_libs = ["socket", "nsl"]

        xapian_aclocal_dir = os.path.join(self._datarootdir, "aclocal")
        self.buildenv_info.prepend_path("AUTOMAKE_CONAN_INCLUDES", xapian_aclocal_dir)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "xapian"
        self.cpp_info.names["cmake_find_package_multi"] = "xapian"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(unix_path_package_info_legacy(self, xapian_aclocal_dir))
