from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
import os
import re


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

    def validate(self):
        if self.version == "9d" and self.settings.os == "Windows" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This version of libjpeg does not support ARM64, please use a newer version")

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
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.cflags.append("-DLIBJPEG_BUILDING")
            if not self.options.shared:
                tc.cflags.append(" -DLIBJPEG_STATIC")
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.extra_defines.append("LIBJPEG_BUILDING")
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run("nmake /f makefile.vs setupcopy-v16")

                # Rename target to 'libjpeg.lib' to match legacy behaviour (otherwise we break backwards compatibility)
                # static: "libjpeg.lib"
                # shared: "libjpeg.lib" (import), "libjpeg-9.dll" (DLL)
                jpeg_vcxproj = os.path.join(self.source_folder, "jpeg.vcxproj")
                target_name = "libjpeg-9" if self.options.shared else "libjpeg"
                replace_in_file(self, jpeg_vcxproj, """<PropertyGroup Label="UserMacros" />""",
                                f""" <PropertyGroup Label="UserMacros" /><PropertyGroup Label="TargetName"> <TargetName>{target_name}</TargetName></PropertyGroup>
                                """)
                if self.options.shared:
                    replace_in_file(self, jpeg_vcxproj, "</SubSystem>",
                                    "</SubSystem><ImportLibrary>$(OutDir)libjpeg.lib</ImportLibrary>")

                # Support static/shared
                if self.options.shared:
                    replace_in_file(self, jpeg_vcxproj,
                        "<ConfigurationType>StaticLibrary</ConfigurationType>",
                        "<ConfigurationType>DynamicLibrary</ConfigurationType>"
                    )

                # Don't force LTO
                replace_in_file(self, jpeg_vcxproj, "<WholeProgramOptimization>true</WholeProgramOptimization>", "")

                # Inject conan-generated .props file
                # Note: importing it right before Microsoft.Cpp.props also ensures we correctly
                #       handle the toolset setting
                conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
                replace_in_file(
                    self, jpeg_vcxproj,
                    """<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />""",
                    f"""<Import Project="{conantoolchain_props}" /><Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />""",
                )

                # Patch settings for a different build type
                if self.settings.build_type is not "Release":
                    replacements = {
                        "Release": str(self.settings.build_type)
                    }
                    if self.settings.build_type == "Debug":
                        replacements.update({
                            "<Optimization>Full": "<Optimization>Disabled",
                            "NDEBUG;": "_DEBUG;",
                        })
                    for key, value in replacements.items():
                        replace_in_file(self, jpeg_vcxproj, key, value)

                    replace_in_file(self, os.path.join(self.source_folder, "jpeg.sln"), "Release", str(self.settings.build_type))

                msbuild = MSBuild(self)
                if self.settings.arch == "x86":
                    # This .sln uses "Win32" instead of the usual "x86"
                    # as the solution platform, so need to override this
                    msbuild.platform = "Win32"
                msbuild.build(sln="jpeg.sln")
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
        prefix = "lib" if is_msvc(self) or self._is_clang_cl else ""
        self.cpp_info.libs = [f"{prefix}jpeg"]
        self.cpp_info.resdirs = ["res"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBJPEG_STATIC")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "JPEG"
