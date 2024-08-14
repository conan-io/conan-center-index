from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime, msvc_runtime_flag, unix_path
from conan.tools.scm import Version
import glob
import os
import shutil

required_conan_version = ">=1.57.0"


class LibffiConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceware.org/libffi/"
    topics = ("runtime", "foreign-function-interface", "runtime-library")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
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
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def validate(self):
        if is_apple_os(self) and self.settings.arch == "armv8" and Version(self.version) < "3.4.0":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Apple ARM CPUs")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            "--enable-builddir=no",
            "--enable-docs=no",
        ])

        if self._settings_build.compiler == "apple-clang":
            tc.configure_args.append("--disable-multi-os-directory")

        if self.options.shared:
            tc.extra_defines.append("FFI_BUILDING_DLL")
        if Version(self.version) < "3.4.6":
            tc.extra_defines.append("FFI_BUILDING")
        elif not self.options.shared:
            tc.extra_defines.append("FFI_STATIC_BUILD")

        env = tc.environment()
        if self._settings_build.os == "Windows" and (is_msvc(self) or self.settings.compiler == "clang"):
            build = "{}-{}-{}".format(
                "x86_64" if self._settings_build.arch == "x86_64" else "i686",
                "pc" if self._settings_build.arch == "x86" else "win64",
                "mingw64")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "win64",
                "mingw64")
            tc.update_configure_args({
                "--build": build,
                "--host": host
                })

            if is_msvc(self) and check_min_vs(self, "180", raise_invalid=False):
                # https://github.com/conan-io/conan/issues/6514
                tc.extra_cflags.append("-FS")

            if is_msvc_static_runtime(self):
                tc.extra_defines.append("USE_STATIC_RTL")
            if "d" in msvc_runtime_flag(self):
                tc.extra_defines.append("USE_DEBUG_RTL")

            architecture_flag = ""
            if is_msvc(self):
                if self.settings.arch == "x86_64":
                    architecture_flag = "-m64"
                elif self.settings.arch == "x86":
                    architecture_flag = "-m32"
            elif self.settings.compiler == "clang":
                architecture_flag = "-clang-cl"

            compile_wrapper = unix_path(self, os.path.join(self.source_folder, "msvcc.sh"))
            if architecture_flag:
                compile_wrapper = f"{compile_wrapper} {architecture_flag}"

            ar_wrapper = unix_path(self, self.dependencies.build["automake"].conf_info.get("user.automake:lib-wrapper"))
            env.define("CC", f"{compile_wrapper}")
            env.define("CXX", f"{compile_wrapper}")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.define("CXXCPP", "cl -nologo -EP")
            env.define("CPP", "cl -nologo -EP")
            env.define("LIBTOOL", unix_path(self, os.path.join(self.source_folder, "ltmain.sh")))
            env.define("INSTALL", unix_path(self, os.path.join(self.source_folder, "install-sh")))
        tc.generate(env=env)

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem
        fix_apple_shared_install_name(self)
        mkdir(self, os.path.join(self.package_folder, "bin"))
        for dll in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            shutil.move(dll, os.path.join(self.package_folder, "bin"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["{}ffi".format("lib" if is_msvc(self) else "")]
        self.cpp_info.set_property("pkg_config_name", "libffi")
        if not self.options.shared:
            static_define = "FFI_STATIC_BUILD" if Version(self.version) >= "3.4.6" else "FFI_BUILDING"
            self.cpp_info.defines = [static_define]
