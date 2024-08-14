from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path, NMakeDeps, NMakeToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class LibxsltConan(ConanFile):
    name = "libxslt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxslt is a software library implementing XSLT processor, based on libxml2"
    topics = ("xslt", "processor")
    homepage = "https://xmlsoft.org"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "debugger": [True, False],
        "crypto": [True, False],
        "profiler": [True, False],
        "plugins": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debugger": False,
        "crypto": False,
        "profiler": False,
        "plugins": False,
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
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "1.1.39":
            # see https://github.com/conan-io/conan-center-index/pull/16205#discussion_r1149570846
            self.requires("libxml2/[>=2.12.5 <3]", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("libxml2/2.11.6", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.options.plugins and not self.options.shared:
            raise ConanInvalidConfiguration("plugins require shared")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            deps = NMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                "--with-python=no",
                f"--with-libxml-src={unix_path(self, self.dependencies['libxml2'].package_folder)}",
                f"--with-debugger={yes_no(self.options.debugger)}",
                f"--with-crypto={yes_no(self.options.crypto)}",
                f"--with-profiler={yes_no(self.options.profiler)}",
                f"--with-plugins={yes_no(self.options.plugins)}",
            ])
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()

    def _build_msvc(self):
        # Configure step to generate Makefile.msvc
        deps_includedirs = []
        deps_libdirs = []
        for deps in self.dependencies.values():
            deps_cpp_info = deps.cpp_info.aggregated_components()
            deps_includedirs.extend(deps_cpp_info.includedirs)
            deps_libdirs.extend(deps_cpp_info.libdirs)

        yes_no = lambda v: "yes" if v else "no"
        args = [
            "compiler=msvc",
            f"prefix={self.package_folder}",
            f"cruntime=/{msvc_runtime_flag(self)}",
            f"debug={yes_no(self.settings.build_type == 'Debug')}",
            f"static={yes_no(not self.options.shared)}",
            "include=\"{}\"".format(";".join(deps_includedirs)),
            "lib=\"{}\"".format(";".join(deps_libdirs)),
            "iconv=no",
            "xslt_debug=no",
            f"debugger={yes_no(self.options.debugger)}",
            f"crypto={yes_no(self.options.crypto)}",
            f"profiler={yes_no(self.options.profiler)}",
            f"modules={yes_no(self.options.plugins)}",
        ]

        with chdir(self, os.path.join(self.source_folder, "win32")):
            self.run(f"cscript configure.js {' '.join(args)}")

        # Fix library names in generated Makefile.msvc
        def format_libs(package):
            libs = []
            dep_cpp_info = self.dependencies[package].cpp_info.aggregated_components()
            for lib in dep_cpp_info.libs + dep_cpp_info.system_libs:
                libname = lib
                if not libname.endswith(".lib"):
                    libname += ".lib"
                libs.append(libname)
            return " ".join(libs)

        makefile_msvc = os.path.join(self.source_folder, "win32", "Makefile.msvc")
        replace_in_file(self, makefile_msvc, "libxml2.lib", format_libs("libxml2"))
        replace_in_file(self, makefile_msvc, "libxml2_a.lib", format_libs("libxml2"))
        if self.dependencies["libxml2"].options.get_safe("icu"):
            replace_in_file(self, makefile_msvc, "LIBS = wsock32.lib", f"LIBS = {format_libs('icu')}")

        # Avoid to indirectly build both static & shared when we build utils
        lib_suffix = "" if self.options.shared else "a"
        replace_in_file(
            self, makefile_msvc,
            "$(UTILS) : $(UTILS_INTDIR) $(BINDIR) libxslt libxslta libexslt libexslta",
            f"$(UTILS) : $(UTILS_INTDIR) $(BINDIR) libxslt{lib_suffix} libexslt{lib_suffix}",
        )

        # Build with NMake
        with chdir(self, os.path.join(self.source_folder, "win32")):
            targets = f"libxslt{lib_suffix} libexslt{lib_suffix} utils"
            self.run(f"nmake -f Makefile.msvc {targets}")

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "*.h", src=os.path.join(self.source_folder, "libxslt"),
                              dst=os.path.join(self.package_folder, "include", "libxslt"))
            copy(self, "*.h", src=os.path.join(self.source_folder, "libexslt"),
                              dst=os.path.join(self.package_folder, "include", "libexslt"))
            build_dir = os.path.join(self.source_folder, "win32", "bin.msvc")
            copy(self, "*.exe", src=build_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            if self.options.shared:
                copy(self, "*xslt.lib", src=build_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
                copy(self, "*xslt.dll", src=build_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            else:
                copy(self, "*xslt_a.lib", src=build_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            os.remove(os.path.join(self.package_folder, "bin", "xslt-config"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rm(self, "*.sh", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibXslt")
        self.cpp_info.set_property("pkg_config_name", "libxslt_full_package") # unofficial, avoid conflicts in conan generators

        prefix = "lib" if is_msvc(self) else ""
        suffix = "_a" if is_msvc(self) and not self.options.shared else ""

        # xslt
        self.cpp_info.components["xslt"].set_property("cmake_target_name", "LibXslt::LibXslt")
        self.cpp_info.components["xslt"].set_property("pkg_config_name", "libxslt")
        self.cpp_info.components["xslt"].libs = [f"{prefix}xslt{suffix}"]
        if not self.options.shared:
            self.cpp_info.components["xslt"].defines = ["LIBXSLT_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.components["xslt"].system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.components["xslt"].system_libs.append("ws2_32")
        self.cpp_info.components["xslt"].requires = ["libxml2::libxml2"]

        # exslt
        self.cpp_info.components["exslt"].set_property("cmake_target_name", "LibXslt::LibExslt")
        self.cpp_info.components["exslt"].set_property("pkg_config_name", "libexslt")
        self.cpp_info.components["exslt"].libs = [f"{prefix}exslt{suffix}"]
        self.cpp_info.components["exslt"].requires = ["xslt"]
        if not self.options.shared:
            self.cpp_info.components["exslt"].defines = ["LIBEXSLT_STATIC"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "LibXslt"
        self.cpp_info.names["cmake_find_package_multi"] = "LibXslt"
        self.cpp_info.names["pkg_config"] = "libxslt_full_package"
        self.cpp_info.components["xslt"].names["cmake_find_package"] = "LibXslt"
        self.cpp_info.components["xslt"].names["cmake_find_package_multi"] = "LibXslt"
        self.cpp_info.components["xslt"].names["pkg_config"] = "libxslt"
        self.cpp_info.components["exslt"].names["cmake_find_package"] = "LibExslt"
        self.cpp_info.components["exslt"].names["cmake_find_package_multi"] = "LibExslt"
        self.cpp_info.components["exslt"].names["pkg_config"] = "libexslt"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
