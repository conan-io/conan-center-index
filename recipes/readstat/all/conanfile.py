from conan import ConanFile, conan_version
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, load, save, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc, MSBuildDeps, MSBuildToolchain, MSBuild, unix_path
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
import os
import platform


required_conan_version = ">=1.57.0"

class ReadstatConan(ConanFile):
    name = "readstat"
    description = "Command-line tool (+ C library) for converting SAS, Stata, and SPSS files"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WizardMac/ReadStat"
    topics = ("spss", "stata", "sas", "sas7bdat", "readstats")
    package_type = "library"
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
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_clang_cl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows" and \
               self.settings.compiler.get_safe("runtime")

    @property
    def _msvc_tools(self):
        return ("clang-cl", "llvm-lib", "lld-link") if self._is_clang_cl else ("cl", "lib", "link")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    # if another tool than the compiler or autotools is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        # if self._settings_build.os == "Windows":
        #     self.win_bash = True
        #     if not self.conf.get("tools.microsoft.bash:path", check_type=str):
        #         self.tool_requires("msys2/cci.latest")
        #     self.win_bash = True
        if self._settings_build.os == "Macos":
            self.tool_requires("libtool/2.4.7")

    def _sys_compiler(self):
        return self.info.settings.compiler
    
    @property
    def _is_windows_msvc(self):
        try:
             return self.settings.os == "Windows"
        except:
            return self.info.settings.os == "Windows"
    
    def source(self):
        if platform.system() == "Windows": # 'self.settings' access in 'source()' method was forbidden
            print(self.conan_data["sources"][self.version][0])
            get(self, **self.conan_data["sources"][self.version][0], strip_root=True)
        else:
            get(self, **self.conan_data["sources"][self.version][1], strip_root=True)
        #get(self, **self.conan_data["sources"][self.version][1], strip_root=True)

    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"
    
    # def generate(self):
    #     if is_msvc(self):
    #         tc = MSBuildToolchain(self)
    #         tc.configuration = self._msbuild_configuration
    #         tc.generate()
    #         deps = MSBuildDeps(self)
    #         deps.configuration = self._msbuild_configuration
    #         deps.generate()
    #     else:
    #         env = VirtualBuildEnv(self)
    #         env.generate()
    #         if not cross_building(self):
    #             env = VirtualRunEnv(self)
    #             env.generate(scope="build")
    #         tc = AutotoolsToolchain(self)
    #         tc.generate()
    #         deps = AutotoolsDeps(self)
    #         deps.generate()

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            if self.settings.arch == "x86":
                tc.update_configure_args({
                    "--host": "i686-w64-mingw32",
                    "RC": "windres --target=pe-i386",
                    "WINDRES": "windres --target=pe-i386",
                })
            elif self.settings.arch == "x86_64":
                tc.update_configure_args({
                    "--host": "x86_64-w64-mingw32",
                    "RC": "windres --target=pe-x86-64",
                    "WINDRES": "windres --target=pe-x86-64",
                })
        msvc_version = {"Visual Studio": "12", "msvc": "180"}
        #if is_msvc(self) and Version(self.settings.compiler.version) >= msvc_version[str(self.settings.compiler)]:
            # https://github.com/conan-io/conan/issues/6514
        #    tc.extra_cflags.append("-FS")
        if cross_building(self) and is_msvc(self):
            triplet_arch_windows = {"x86_64": "x86_64", "x86": "i686", "armv8": "aarch64"}
            # ICU doesn't like GNU triplet of conan for msvc (see https://github.com/conan-io/conan/issues/12546)
            host_arch = triplet_arch_windows.get(str(self.settings.arch))
            build_arch = triplet_arch_windows.get(str(self._settings_build.arch))

            if host_arch and build_arch:
                host = f"{host_arch}-w64-mingw32"
                build = f"{build_arch}-w64-mingw32"
                tc.configure_args.extend([
                    f"--host={host}",
                    f"--build={build}",
                ])
        env = tc.environment()
        tc.generate(env)
    
    def _print_directory_structure(self, folder):
        self.output.info(f"Directory structure for: {folder}")
        for root, dirs, files in os.walk(folder):
            level = root.replace(folder, '').count(os.sep)
            indent = ' ' * 4 * level
            self.output.info(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                self.output.info(f"{subindent}{f}")
                
    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            msbuild = MSBuild(self)
            #msbuild.build_type = self._msbuild_configuration

            self._print_directory_structure(self.source_folder)
            self.output.info(f"Using solution file at: {self.source_folder}")

            platform_toolset = MSBuildToolchain(self).toolset
            vcxproj_file = os.path.join(self.source_folder, "VS17", "ReadStat.vcxproj")
            
            replace_in_file(self, vcxproj_file, "<WindowsTargetPlatformVersion>10.0.17763.0</WindowsTargetPlatformVersion>", "")
            replace_in_file(self, vcxproj_file, "<PlatformToolset>v141</PlatformToolset>", f"<PlatformToolset>v142</PlatformToolset>")
            
            msbuild.build(sln=os.path.join(self.source_folder, "VS17", "ReadStat.sln"))
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        # upstream didn't pack license file into distribution
        copy(self, "NEWS", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "readstat.h", src=os.path.join(self.source_folder, "headers"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "readstat")
        suffix = "_i" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"readstat{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")
