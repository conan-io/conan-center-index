from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, MSBuild, MSBuildToolchain
import os

required_conan_version = ">=1.54.0"


class LibsodiumConan(ConanFile):
    name = "libsodium"
    description = "A modern and easy-to-use crypto library."
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://doc.libsodium.org/"
    topics = "encryption", "signature", "hashing"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_soname": [True, False],
        "PIE": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_soname": True,
        "PIE": False,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

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

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Cannot build shared libsodium libraries with static runtime")

    def build_requirements(self):
        if not is_msvc(self):
            if self._is_mingw:
                self.tool_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = "{}{}".format(
                "Debug" if self.settings.build_type == "Debug" else "Release",
                "DLL" if self.options.shared else "LIB",
            )
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()

            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.append("--enable-soname-versions={}".format(yes_no(self.options.use_soname)))
            tc.configure_args.append("--enable-pie={}".format(yes_no(self.options.PIE)))
            if self._is_mingw:
                tc.extra_ldflags.append("-lssp")
            if self.settings.os == "Emscripten":
                # FIXME: this is an old comment/test, has not been re-tested with conan2 upgrade
                self.output.warn("os=Emscripten is not tested/supported by this recipe")
                # FIXME: ./dist-build/emscripten.sh does not respect options of this recipe
            tc.generate()

    @property
    def _msvc_sln_folder(self):
        sln_folders = {
            "Visual Studio": {
                "10": "vs2010",
                "11": "vs2012",
                "12": "vs2013",
                "14": "vs2015",
                "15": "vs2017",
                "16": "vs2019",
            },
            "msvc": {
                "170": "vs2012",
                "180": "vs2013",
                "190": "vs2015",
                "191": "vs2017",
                "192": "vs2019",
            },
        }
        default_folder = "vs2019"
        if self.version != "1.0.18":
            sln_folders["Visual Studio"]["17"] = "vs2022"
            sln_folders["msvc"]["193"] = "vs2022"
            default_folder = "vs2022"

        return sln_folders.get(str(self.settings.compiler), {}).get(str(self.settings.compiler.version), default_folder)

    def _build_msvc(self):
        msvc_sln_folder = os.path.join(self.source_folder, "builds", "msvc", self._msvc_sln_folder)

        #==============================
        # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
        if self.version == "1.0.18" and self._msvc_sln_folder == "vs2019":
            toolset = MSBuildToolchain(self).toolset
            replace_in_file(
                self, os.path.join(msvc_sln_folder, "libsodium", "libsodium.vcxproj"),
                "<PlatformToolset>v142</PlatformToolset>",
                f"<PlatformToolset>{toolset}</PlatformToolset>",
            )
        conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
        replace_in_file(
            self, os.path.join(msvc_sln_folder, "libsodium", "libsodium.vcxproj"),
            "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
        )
        #==============================

        msbuild = MSBuild(self)
        msbuild.build_type = "{}{}".format(
            "Dyn" if self.options.shared else "Static",
            "Debug" if self.settings.build_type == "Debug" else "Release",
        )
        msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
        msbuild.build(os.path.join(msvc_sln_folder, "libsodium.sln"))

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            if self._is_mingw:
                autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "*LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            output_dir = os.path.join(self.source_folder, "bin")
            copy(self, "*.lib", src=output_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=output_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            inc_src = os.path.join(self.source_folder, "src", "libsodium", "include")
            copy(self, "*.h", src=inc_src, dst=os.path.join(self.package_folder, "include"), excludes=("*/private/*"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsodium")
        self.cpp_info.libs = ["{}sodium".format("lib" if is_msvc(self) else "")]
        if not self.options.shared:
            self.cpp_info.defines = ["SODIUM_STATIC"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
        if self._is_mingw:
            self.cpp_info.system_libs.append("ssp")
