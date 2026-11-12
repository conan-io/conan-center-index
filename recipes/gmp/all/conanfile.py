from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.files import copy, export_conandata_patches, get, patch, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
import os
import stat

required_conan_version = ">=2"


class GmpConan(ConanFile):
    name = "gmp"
    description = (
        "GMP is a free library for arbitrary precision arithmetic, operating "
        "on signed integers, rational numbers, and floating-point numbers."
    )
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("math", "arbitrary", "precision", "integer")
    license = ("LGPL-3.0", "GPL-2.0")
    homepage = "https://gmplib.org"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_assembly": [True, False],
        "enable_fat": [True, False],
        "run_checks": [True, False],
        "enable_cxx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_assembly": True,
        "enable_fat": False,
        "run_checks": False,
        "enable_cxx": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.enable_fat

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.get_safe("enable_fat"):
            del self.options.disable_assembly
        if not self.options.enable_cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.run_checks  # run_checks doesn't affect package's ID

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} cannot be built as a shared library using Visual Studio: some error occurs at link time",
            )

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")  # Needed for lib-wrapper
            if self.settings.arch in ["x86", "x86_64"]:
                self.tool_requires("yasm/1.3.0")  # Needed for determining 32-bit word size

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f'--with-pic={yes_no(self.options.get_safe("fPIC", True))}',
            f'--enable-assembly={yes_no(not self.options.get_safe("disable_assembly", False))}',
            f'--enable-fat={yes_no(self.options.get_safe("enable_fat", False))}',
            f'--enable-cxx={yes_no(self.options.enable_cxx)}',
            f'--srcdir={"../src"}', # Use relative path to avoid issues with #include "$srcdir/gmp-h.in" on Windows
        ])
        if is_msvc(self):
            tc.configure_args.extend([
                "ac_cv_c_restrict=restrict",
                "gmp_cv_asm_label_suffix=:",
                "lt_cv_sys_global_symbol_pipe=cat",  # added to get further in shared MSVC build, but it gets stuck later
            ])
            tc.extra_cxxflags.append("-EHsc")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
        env = tc.environment() # Environment must be captured *after* setting extra_cflags, etc. to pick up changes
        if is_msvc(self):
            yasm_wrapper = unix_path(self, os.path.join(self.source_folder, "yasm_wrapper.sh"))
            yasm_machine = {
                "x86": "x86",
                "x86_64": "amd64",
            }.get(str(self.settings.arch), None)
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper"))
            dumpbin_nm = unix_path(self, os.path.join(self.source_folder, "dumpbin_nm.py"))
            env.define("CC", "cl -nologo")
            if yasm_machine:
                env.define("CCAS", f"{yasm_wrapper} -a x86 -m {yasm_machine} -p gas -r raw -f win32 -g null -X gnu")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", f"python {dumpbin_nm}")
        tc.generate(env)

    def _patch_sources(self):
        # Usage allowed after consideration with CCI maintainers
        for it in self.conan_data.get("patches", {}).get(self.version, []):
            if "patch_os" not in it or self.settings.os == it["patch_os"]:
                entry = it.copy()
                patch_file = entry.pop("patch_file")
                patch_file_path = os.path.join(self.export_sources_folder, patch_file)
                if "patch_description" not in entry:
                    entry["patch_description"] = patch_file
                patch(self, patch_file=patch_file_path, **entry)

        # Fix permission issue
        if is_apple_os(self):
            configure_file = os.path.join(self.source_folder, "configure")
            configure_stats = os.stat(configure_file)
            os.chmod(configure_file, configure_stats.st_mode | stat.S_IEXEC)

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        if self.settings.os == "Macos" and cross_building(self):
            # LD flags are not passed properly by the scripts - in particular '-arch x86_64' when crossbuilding
            # and invoking libtool to generate one of the libraries. Being conservative here, but there's a chance
            # this may need to be generalised
            replace_in_file(self, os.path.join(self.build_folder, "libtool"), r'archive_cmds="\$CC ', r'archive_cmds="\$CC $LDFLAGS ')
        autotools.make()
        # INFO: According to the gmp readme file, make check should not be omitted, but it causes timeouts on the CI server.
        if self.options.run_checks:
            autotools.make(target="check")

    def package(self):
        copy(self, "COPYINGv2", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.LESSERv3", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        # Workaround to always provide a pkgconfig file depending on all components
        self.cpp_info.set_property("pkg_config_name", "gmp-all-do-not-use")

        self.cpp_info.components["libgmp"].set_property("pkg_config_name", "gmp")
        self.cpp_info.components["libgmp"].libs = ["gmp"]
        if self.options.enable_cxx:
            self.cpp_info.components["gmpxx"].set_property("pkg_config_name", "gmpxx")
            self.cpp_info.components["gmpxx"].libs = ["gmpxx"]
            self.cpp_info.components["gmpxx"].requires = ["libgmp"]
            if self.settings.os != "Windows":
                self.cpp_info.components["gmpxx"].system_libs = ["m"]
