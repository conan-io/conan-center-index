from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceware.org/libffi/"
    topics = ("runtime", "foreign-function-interface", "runtime-library")
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
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except ValueError:
                pass
        try:
            del self.settings.compiler.libcxx
        except ValueError:
            pass
        try:
            del self.settings.compiler.cppstd
        except ValueError:
            pass

    def layout(self):
        basic_layout(self, src_folder="libffi")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")
            self.win_bash = True
        self.tool_requires("automake/1.16.5")
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            "--enable-builddir=no",
            "--enable-docs=no",
        ])

        if is_msvc(self):
            build = "{}-{}-{}".format(
                "x86_64" if self._settings_build.arch == "x86_64" else "i686",
                "pc" if self._settings_build.arch == "x86" else "win64",
                "mingw64")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "win64",
                "mingw64")
            tc.configure_args.extend([
                f"--build={build}",
                f"--host={host}",
            ])

        if self._settings_build.compiler == "apple-clang":
            tc.configure_args.append("--disable-multi-os-directory")

        if is_msvc(self):
            msvcc = unix_path(self, os.path.join(self.source_folder, "msvcc.sh"))
            msvcc_args = []
            if self.settings.arch == "x86_64":
                msvcc_args.append("-m64")
            elif self.settings.arch == "x86":
                msvcc_args.append("-m32")

            if msvcc_args:
                msvcc_args = " ".join(msvcc_args)
                msvcc = f"{msvcc} {msvcc_args}"

            if "MT" in msvc_runtime_flag(self):
                tc.extra_defines.append("USE_STATIC_RTL")
            if "d" in msvc_runtime_flag(self):
                tc.extra_defines.append("USE_DEBUG_RTL")

        if self.options.shared:
            tc.extra_defines.append("FFI_BUILDING_DLL")
        else:
            tc.extra_defines.append("FFI_BUILDING")

        if self.settings.build_type == "Debug":
            tc.extra_defines.append("FFI_DEBUG")

        env = tc.environment()
        if is_msvc(self):
            env.define_path("CXX", msvcc)
            env.define_path("CC", msvcc)
            env.define("CXXCPP", "cl -nologo -EP")
            env.define("CPP", "cl -nologo -EP")

            # FIXME: Use the conf once https://github.com/conan-io/conan-center-index/pull/12898 is merged
            # env.define("AR", f"{unix_path(self, self.conf.get('tools.automake:ar-lib'))}")
            [version_major, version_minor, _] = self.dependencies.direct_build['automake'].ref.version.split(".", 2)
            automake_version = f"{version_major}.{version_minor}"
            ar_lib = unix_path(self, os.path.join(self.dependencies.direct_build['automake'].cpp_info.resdirs[0], f"automake-{automake_version}", "ar-lib"))
            env.define("AR", f"{ar_lib} lib")
            env.define("LD", "link")
            env.define("LIBTOOL", unix_path(self, os.path.join(self.source_folder, "ltmain.sh")))
            env.define("INSTALL", unix_path(self, os.path.join(self.source_folder, "install-sh")))
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")

        tc.generate(env)

        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def _patch_source(self):
        apply_conandata_patches(self)

        if Version(self.version) < "3.3":
            if self.settings.compiler == "clang" and Version(str(self.settings.compiler.version)) >= 7.0:
                # https://android.googlesource.com/platform/external/libffi/+/ca22c3cb49a8cca299828c5ffad6fcfa76fdfa77
                sysv_s_src = os.path.join(self.source_folder, "src", "arm", "sysv.S")
                replace_in_file(self, sysv_s_src, "fldmiad", "vldmia")
                replace_in_file(self, sysv_s_src, "fstmiad", "vstmia")
                replace_in_file(self, sysv_s_src, "fstmfdd\tsp!,", "vpush")

                # https://android.googlesource.com/platform/external/libffi/+/7748bd0e4a8f7d7c67b2867a3afdd92420e95a9f
                replace_in_file(self, sysv_s_src, "stmeqia", "stmiaeq")

    def build(self):
        self._patch_source()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem
        fix_apple_shared_install_name(self)
        copy(self, "*.dll", os.path.join(self.package_folder, "lib"), os.path.join(self.package_folder, "bin"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["{}ffi".format("lib" if is_msvc(self) else "")]
        self.cpp_info.set_property("pkg_config_name", "libffi")
        if not self.options.shared:
            self.cpp_info.defines = ["FFI_BUILDING"]
