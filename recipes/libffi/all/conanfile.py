from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.51.3"


class PackageConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceware.org/libffi/"
    topics = ("libffi", "runtime", "foreign-function-interface", "runtime-library")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False
        ,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    @property
    def win_bash(self):
        return self._settings_build.os == "Windows"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

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
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")
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
            "--datarootdir=${prefix}/res",
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
            tc.configure_args.append(f"--build={build}")
            tc.configure_args.append(f"--host={host}")

        if is_msvc(self):
            msvcc = unix_path(self, str(self.source_path.joinpath("msvcc.sh")))
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
                tc.extra_defines.append("d")

        if self.options.shared:
            tc.extra_defines.append("FFI_BUILDING_DLL")
        else:
            tc.extra_defines.append("FFI_BUILDING")

        if self.settings.build_type == "Debug":
            tc.extra_defines.append("FFI_DEBUG")

        env = tc.environment()
        if is_msvc(self):
            env.define("LD", "link")
            env.define_path("CXX", msvcc)
            env.define_path("CC", msvcc)
            env.define("CXXCPP", "cl -nologo -EP")
            env.define("CPP", "cl -nologo -EP")
            # env.define("AR", f"{unix_path(self, self.conf.get('tools.automake:ar-lib'))} lib") FIXME: Use the conf once https://github.com/conan-io/conan-center-index/pull/12898 is merged
            env.define("AR", f"{unix_path(self, self.deps_user_info['automake'].ar_lib)} lib")
            env.define("LD", "link")
            env.define("LIBTOOL", unix_path(self, str(self.source_path.joinpath("ltmain.sh"))))
            env.define("INSTALL", unix_path(self, str(self.source_path.joinpath("install-sh"))))
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
                sysv_s_src = self.source_path.joinpath("src", "arm", "sysv.S")
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

        if is_apple_os(self):
            fix_apple_shared_install_name(self)

        copy(self, pattern="*.dll", dst=self.package_path.joinpath("bin"), src=self.package_path.joinpath("lib"))
        copy(self, pattern="LICENSE", dst=self.package_path.joinpath("licenses"), src=self.source_folder)

        rm(self, "*.la", self.package_path.joinpath("lib"), recursive=True)
        rmdir(self, self.package_path.joinpath("lib", "pkgconfig"))
        rmdir(self, self.package_path.joinpath("share"))

    def package_info(self):
        self.cpp_info.libs = ["{}ffi".format("lib" if is_msvc(self) else "")]
        self.cpp_info.set_property("pkg_config_name", "libffi")
        if not self.options.shared:
            self.cpp_info.defines = ["FFI_BUILDING"]
