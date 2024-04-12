from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, NMakeToolchain, MSBuild, MSBuildToolchain, msvs_toolset
import os
import re
import shutil


required_conan_version = ">=1.55.0"


class LibjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("image", "format", "jpg", "jpeg", "picture", "multimedia", "graphics")
    license = "IJG"
    homepage = "http://ijg.org"

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
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _msbuild_platform(self):
        if self.settings.arch == 'x86':
            return "Win32"
        elif self.settings.arch == "x86_64":
            return "Win64"
        elif self.settings.arch == 'armv8':
            return "ARM64"

    def export_sources(self):
        copy(self, "Win32.Mak", src=self.recipe_folder, dst=self.export_sources_folder)
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

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not (is_msvc(self) or self. _is_clang_cl):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self) or self._is_clang_cl:
            # clean environment variables that might affect on the build (e.g. if set by Jenkins)
            env = Environment()
            env.define("PROFILE", None)
            env.define("TUNE", None)
            env.define("NODEBUG", None)
            env.vars(self).save_script("conanbuildenv_nmake_unset_env")
            tc = NMakeToolchain(self)
            tc.generate()
            if is_msvc(self):
                tc = MSBuildToolchain(self)
                tc.configuration = self._msbuild_configuration
                tc.platform = self._msbuild_platform
                tc.cflags.append("-DLIBJPEG_BUILDING {}".format("" if self.options.shared else "-DLIBJPEG_STATIC"))
                tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.extra_defines.append("LIBJPEG_BUILDING")
            tc.generate()

    def _build_nmake(self):
        copy(self, "Win32.Mak", src=os.path.join(self.source_folder, os.pardir), dst=self.source_folder)
        with chdir(self, self.source_folder):
            # export symbols if shared
            replace_in_file(
                self,
                "Win32.Mak",
                "\nccommon = -c ",
                "\nccommon = -c -DLIBJPEG_BUILDING {}".format("" if self.options.shared else "-DLIBJPEG_STATIC "),
            )
            shutil.copy("jconfig.vc", "jconfig.h")
            make_args = [
                "nodebug=1" if self.settings.build_type != "Debug" else "",
            ]
            if self._is_clang_cl:
                compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
                buildenv_vars = VirtualBuildEnv(self).vars()
                cl = compilers_from_conf.get("c", buildenv_vars.get("CC", "clang-cl"))
                link = buildenv_vars.get("LD", "lld-link")
                lib = buildenv_vars.get("AR", "llvm-lib")
                rc = compilers_from_conf.get("rc", buildenv_vars.get("RC", "llvm-rc"))
                replace_in_file(self, "Win32.Mak", "cc     = cl", f"cc     = {cl}")
                replace_in_file(self, "Win32.Mak", "link   = link", f"link   = {link}")
                replace_in_file(self, "Win32.Mak", "implib = lib", f"implib = {lib}")
                replace_in_file(self, "Win32.Mak", "rc     = Rc", f"rc     = {rc}")
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if is_msvc(self):
                msbuild = MSBuild(self)
                if is_msvc_static_runtime(self):
                    replace_in_file(self, "makefile.vs", "(cvars)", "(cvarsmt)")
                    replace_in_file(self, "makefile.vs", "(conlibs)", "(conlibsmt)")
                solution_version = 17 if msvs_toolset(self) == "v143" else 16
                vcxproj_file = f"makejvcx.v{solution_version}"
                if self.options.shared:
                    replace_in_file(
                        self, vcxproj_file,
                        "<ConfigurationType>StaticLibrary</ConfigurationType>",
                        "<ConfigurationType>DynamicLibrary</ConfigurationType>"
                    )
                conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
                replace_in_file(
                    self, vcxproj_file,
                    "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                    f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                )
                make_args.append(f"setupcopy-v{solution_version}")
                self.run("nmake /f makefile.vs {}".format(" ".join(make_args)))
                msbuild.build(sln="jpeg.sln")
            else:
                replace_in_file(self, "makefile.vc", "(cvars)", "(cvarsdll)")
                replace_in_file(self, "makefile.vc", "(conlibs)", "(conlibsdll)")
                target = "{}/libjpeg.lib".format("shared" if self.options.shared else "static")
                self.run("nmake -f makefile.vc {} {}".format(" ".join(make_args), target))

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self) or self._is_clang_cl:
            self._build_nmake()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "README", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self) or self._is_clang_cl:
            for filename in ["jpeglib.h", "jerror.h", "jconfig.h", "jmorecfg.h"]:
                copy(self, filename, src=self.source_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)

            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            if self.options.shared:
                copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            if self.settings.os == "Windows" and self.options.shared:
                rm(self, "*[!.dll]", os.path.join(self.package_folder, "bin"))
            else:
                rmdir(self, os.path.join(self.package_folder, "bin"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            fix_apple_shared_install_name(self)

        for fn in ("jpegint.h", "transupp.h",):
            copy(self, fn, src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

        for fn in ("jinclude.h", "transupp.c",):
            copy(self, fn, src=self.source_folder, dst=os.path.join(self.package_folder, "res"))

        # Remove export decorations of transupp symbols
        for relpath in os.path.join("include", "transupp.h"), os.path.join("res", "transupp.c"):
            path = os.path.join(self.package_folder, relpath)
            save(self, path, re.subn(r"(?:EXTERN|GLOBAL)\(([^)]+)\)", r"\1", load(self, path))[0])

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "JPEG")
        self.cpp_info.set_property("cmake_target_name", "JPEG::JPEG")
        self.cpp_info.set_property("pkg_config_name", "libjpeg")
        prefix = "lib" if self._is_clang_cl else ""
        self.cpp_info.libs = [f"{prefix}jpeg"]
        self.cpp_info.resdirs = ["res"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBJPEG_STATIC")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "JPEG"
