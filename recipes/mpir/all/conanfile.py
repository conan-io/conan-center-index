import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import XCRun, to_apple_arch
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, is_msvc_static_runtime, msvc_runtime_flag

required_conan_version = ">=1.53.0"


class MpirConan(ConanFile):
    name = "mpir"
    description = ("MPIR is a highly optimised library for bignum arithmetic "
                  "forked from the GMP bignum library.")
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wbhart/mpir"
    topics = ("multiprecision", "math", "mathematics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
        "enable_gmpcompat": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": True,
        "enable_gmpcompat": True,
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
        if is_msvc(self) and self.options.shared:
            del self.options.enable_cxx
        if not self.options.get_safe("enable_cxx", False):
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")
        if self.options.enable_gmpcompat:
            self.provides = ["gmp"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building doesn't work (yet)")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("yasm/1.3.0")
        if not is_msvc(self):
            self.tool_requires("m4/1.4.19")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, keep_permissions=True)

    def _generate_msvc(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MSBuildToolchain(self)
        tc.generate()

    def _generate_autotools(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-silent-rules")
        tc.configure_args.append("--enable-cxx" if self.options.get_safe("enable_cxx") else "--disable-cxx")
        tc.configure_args.append("--enable-gmpcompat" if self.options.enable_gmpcompat else "--disable-gmpcompat")

        # compiler checks are written for C89 but compilers that default to C99 treat implicit functions as error
        tc.extra_cxxflags.append("-Wno-implicit-function-declaration")

        if self.settings.compiler == "apple-clang":
            if hasattr(self, "settings_build"):
                # there is no CFLAGS_FOR_BUILD/CXXFLAGS_FOR_BUILD
                sdk_path = XCRun(self).sdk_path
                tc.extra_cxxflags += [
                    "-Wno-implicit-function-declaration",
                    "-isysroot", sdk_path,
                    "-arch", to_apple_arch(self),
                ]
        # Disable docs
        tc.make_args.append("MAKEINFO=true")
        tc.generate()

    def generate(self):
        if is_msvc(self):
            self._generate_msvc()
        else:
            self._generate_autotools()

    @property
    def _platforms(self):
        return {"x86": "Win32", "x86_64": "x64"}

    @property
    def _dll_or_lib(self):
        return "dll" if self.options.shared else "lib"

    @property
    def _vs_ide_version(self):
        if str(self.settings.compiler) == "Visual Studio":
            return self.settings.compiler.version
        msvc_to_ide = {"170": "11", "180": "12", "190": "14", "191": "15", "192": "16", "193": "17"}
        return msvc_to_ide.get(str(self.settings.compiler.version), "17")

    @property
    def _vcxproj_paths(self):
        build_subdir = f"build.vc{self._vs_ide_version}"
        vcxproj_paths = [
            os.path.join(self.source_folder, build_subdir, f"{self._dll_or_lib}_mpir_gc", f"{self._dll_or_lib}_mpir_gc.vcxproj")
        ]
        if self.options.get_safe("enable_cxx"):
            vcxproj_paths.append(os.path.join(self.source_folder, build_subdir,
                                              "lib_mpir_cxx", "lib_mpir_cxx.vcxproj"))
        return vcxproj_paths

    def _build_msvc(self):
        if not self.options.shared:  # RuntimeLibrary only defined in lib props files
            build_type = "debug" if self.settings.build_type == "Debug" else "release"
            props_path = os.path.join(self.source_folder, "build.vc", f"mpir_{build_type}_lib.props")
            old_runtime = "MultiThreaded{}".format("Debug" if build_type == "debug" else "")
            new_runtime = "MultiThreaded{}{}".format(
                "Debug" if "d" in msvc_runtime_flag(self) else "",
                "DLL" if not is_msvc_static_runtime(self) else "",
            )
            replace_in_file(self, props_path, old_runtime, new_runtime)
        msbuild = MSBuild(self)
        for vcxproj_path in self._vcxproj_paths:
            msbuild.build(vcxproj_path)

    def _patch_new_msvc_version(self, ver, toolset):
        new_dir = os.path.join(self.source_folder, f"build.vc{ver}")
        copy(self, pattern="*", src=os.path.join(self.source_folder, "build.vc15"), dst=new_dir)

        for root, _, files in os.walk(new_dir):
            for file in files:
                full_file = os.path.join(root, file)
                replace_in_file(self, full_file, "<PlatformToolset>v141</PlatformToolset>", f"<PlatformToolset>{toolset}</PlatformToolset>", strict=False)
                replace_in_file(self, full_file, "prebuild skylake\\avx x64 15", f"prebuild skylake\\avx x64 {ver}", strict=False)
                replace_in_file(self, full_file, "prebuild p3 Win32 15", f"prebuild p3 Win32 {ver}", strict=False)
                replace_in_file(self, full_file, "prebuild gc Win32 15", f"prebuild gc Win32 {ver}", strict=False)
                replace_in_file(self, full_file, "prebuild gc x64 15", f"prebuild gc x64 {ver}", strict=False)
                replace_in_file(self, full_file, "prebuild haswell\\avx x64 15", f"prebuild haswell\\avx x64 {ver}", strict=False)
                replace_in_file(self, full_file, "prebuild core2 x64 15", f"prebuild core2 x64 {ver}", strict=False)
                replace_in_file(self, full_file, 'postbuild "$(TargetPath)" 15', f'postbuild "$(TargetPath)" {ver}', strict=False)
                replace_in_file(self, full_file, 'check_config $(Platform) $(Configuration) 15', f'check_config $(Platform) $(Configuration) {ver}', strict=False)

    def _patch_sources(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._patch_new_msvc_version(16, "v142")
            self._patch_new_msvc_version(17, "v143")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_msvc()
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.autoreconf()
                # relocatable shared lib on macOS
                replace_in_file(self, "configure", "-install_name \\$rpath/", "-install_name @rpath/")
                autotools.configure()
                autotools.make()

    def package(self):
        copy(self, "COPYING*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            lib_folder = os.path.join(
                self.source_folder,
                self._dll_or_lib,
                self._platforms.get(str(self.settings.arch)),
                str(self.settings.build_type),
            )
            include_folder = os.path.join(self.package_folder, "include")
            copy(self, "mpir.h", dst=include_folder, src=lib_folder, keep_path=True)
            if self.options.enable_gmpcompat:
                copy(self, "gmp.h", dst=include_folder, src=lib_folder, keep_path=True)
            if self.options.get_safe("enable_cxx"):
                copy(self, "mpirxx.h", dst=include_folder, src=lib_folder, keep_path=True)
                if self.options.enable_gmpcompat:
                    copy(self, "gmpxx.h", dst=include_folder, src=lib_folder, keep_path=True)
            copy(self, "*.dll*", dst=os.path.join(self.package_folder, "bin"), src=lib_folder, keep_path=False)
            copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=lib_folder, keep_path=False)
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        if self.options.get_safe("enable_cxx"):
            self.cpp_info.libs.append("mpirxx")
        self.cpp_info.libs.append("mpir")
        if self.options.enable_gmpcompat and not is_msvc(self):
            if self.options.get_safe("enable_cxx"):
                self.cpp_info.libs.append("gmpxx")
            self.cpp_info.libs.append("gmp")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("MSC_USE_DLL")
