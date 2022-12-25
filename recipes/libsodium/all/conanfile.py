from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, rmdir, copy, rm, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, MSBuildDeps, MSBuildToolchain, MSBuild, VCVars, unix_path, msvc_runtime_flag, vs_layout
import os

required_conan_version = ">=1.52.0"


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
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
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

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = MSBuildDeps(self)
            tc.generate()
            tc = VCVars(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)

            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.append("--enable-soname-versions={}".format(yes_no(self.options.use_soname)))
            tc.configure_args.append("--enable-pie={}".format(yes_no(self.options.PIE)))

            env = tc.environment()

            # if self._is_mingw:
                # add libssp (gcc support library) for some missing symbols (e.g. __strcpy_chk)
                # FIXME how do I do this in conan v2?
                # autotools.libs.append("ssp")

            if self.settings.os == "Emscripten":
                # FIXME: this is an old comment/test, has not been re-tested with conan2 upgrade
                self.output.warn("os=Emscripten is not tested/supported by this recipe")
                # FIXME: ./dist-build/emscripten.sh does not respect options of this recipe

            tc.generate(env)

            env = VirtualBuildEnv(self)
            env.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _msvc_sln_folder(self):
        if self.settings.compiler == "Visual Studio":
            folder = {
                "10": "vs2010",
                "11": "vs2012",
                "12": "vs2013",
                "14": "vs2015",
                "15": "vs2017",
                "16": "vs2019",
            }
        elif self.settings.compiler == "msvc":
            folder = {
                "190": "vs2015",
                "191": "vs2017",
                "192": "vs2019",
            }
        else:
            raise ConanException("Should not call this function with any other compiler")

        if self.version != "1.0.18":
            if self.settings.compiler == "Visual Studio":
                folder["17"] = "vs2022"
            else:
                folder["193"] = "vs2022"

        return folder.get(str(self.settings.compiler.version))

    @property
    def _msvc_platform(self):
        return {
            "x86": "Win32",
            "x86_64": "x64",
        }[str(self.settings.arch)]

    # Method copied from xz_utils
    def _fix_msvc_platform_toolset(self, vcxproj_file, old_toolset):
        platform_toolset = {
            "Visual Studio": {
                "8": "v80",
                "9": "v90",
                "10": "v100",
                "11": "v110",
                "12": "v120",
                "14": "v140",
                "15": "v141",
                "16": "v142",
                "17": "v143",
            },
            "msvc": {
                "170": "v110",
                "180": "v120",
                "190": "v140",
                "191": "v141",
                "192": "v142",
                "193": "v143",
            }
        }.get(str(self.settings.compiler), {}).get(str(self.settings.compiler.version))
        if not platform_toolset:
            raise ConanException(
                f"Unknown platform toolset for {self.settings.compiler} {self.settings.compiler.version}",
            )
        replace_in_file(
            self,
            vcxproj_file,
            f"<PlatformToolset>{old_toolset}</PlatformToolset>",
            f"<PlatformToolset>{platform_toolset}</PlatformToolset>",
        )

    def _build_msvc(self):
        msvc_ver_subfolder = self._msvc_sln_folder or ("vs2022" if self.version != "1.0.18" else "vs2019")
        msvc_sln_folder = os.path.join(self.build_folder, self.source_folder, "builds", "msvc", msvc_ver_subfolder)

        msvc_sln_path = os.path.join(msvc_sln_folder, "libsodium.sln")

        # 1.0.18 only supported up to vs2019. Add support for newer toolsets.
        if self.version == "1.0.18" and msvc_ver_subfolder == "vs2019":
            vcxproj_path = os.path.join(msvc_sln_folder, "libsodium", "libsodium.vcxproj")
            self._fix_msvc_platform_toolset(vcxproj_path, "v142")

        build_type = "{}{}".format(
            "Dyn" if self.options.shared else "Static",
            "Debug" if self.settings.build_type == "Debug" else "Release",
        )

        platform = {
            "x86": "Win32",
            "x86_64": "x64",
        }[str(self.settings.arch)]

        msbuild = MSBuild(self)
        msbuild.build_type = build_type
        msbuild.platform = platform
        msbuild.build(msvc_sln_path)


    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "*LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        if is_msvc(self):
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            inc_src = os.path.join(self.source_folder, "src", self.name, "include")
            copy(self, "*.h", src=inc_src, dst=os.path.join(self.package_folder, "include"), keep_path=True, excludes=("*/private/*"))
        else:
            autotools = Autotools(self)
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsodium")
        self.cpp_info.libs = ["{}sodium".format("lib" if is_msvc(self) else "")]
        if not self.options.shared:
            self.cpp_info.defines = ["SODIUM_STATIC"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
        if self._is_mingw:
            self.cpp_info.system_libs.append("ssp")
