import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path

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
        if self.win_bash and not os.environ.get("CONAN_BASH_PATH"):
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

        if is_msvc(self) or self.settings.compiler == "clang":
            msvcc = unix_path(self, os.path.join(self.source_folder, "msvcc.sh"))
            msvcc_args = []
            if is_msvc(self):
                if self.settings.arch == "x86_64":
                    msvcc_args.append("-m64")
                elif self.settings.arch == "x86":
                    msvcc_args.append("-m32")
            elif self.settings.compiler == "clang":
                msvcc_args.append("-clang-cl")

            if msvcc_args:
                msvcc_args = " ".join(msvcc_args)
                msvcc = f"{msvcc} {msvcc_args}"

        if is_msvc(self):
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
        if is_msvc(self) or self.settings.compiler == "clang":
            env.define("LD", "link")
            env.define_path("CXX", msvcc)
            env.define_path("CC", msvcc)
            env.define("CXXCPP", "cl -nologo -EP")
            env.define("CPP", "cl -nologo -EP")
            env.define("AR", unix_path(self, self.conf.get('tools.automake:ar-lib')))
            env.define("LD", "link")
            env.define("LIBTOOL", unix_path(self, os.path.join(self.source_folder, 'ltmain.sh')))
            env.define("INSTALL", unix_path(self, os.path.join(self.source_folder, "install-sh")))
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")

        tc.generate(env)

        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem

        copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["{}ffi".format("lib" if is_msvc(self) else "")]
        self.cpp_info.set_property("pkg_config_name", "libffi")
        if not self.options.shared:
            self.cpp_info.defines = ["FFI_BUILDING"]
