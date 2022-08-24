from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
import os

required_conan_version = ">=1.33.0"


class Argon2Conan(ConanFile):
    name = "argon2"
    license = "Apache 2.0", "CC0-1.0"
    homepage = "https://github.com/P-H-C/phc-winner-argon2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Argon2 password hashing library"
    topics = ("argon2", "crypto", "password hashing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _kernel_name(self):
        if tools.is_apple_os(self.settings.os):
            return "Darwin"
        if self.settings.os == "Windows":
            return "MINGW"
        return {
            "Windows": "MINGW",
        }.get(str(self.settings.os), str(self.settings.os))

    @property
    def _make_args(self):
        return (
            "PREFIX={}".format(tools.unix_path(self.package_folder)),
            "LIBRARY_REL=lib",
            "KERNEL_NAME={}".format(self._kernel_name),
            "RUN_EXT={}".format(".exe" if self.settings.os == "Windows" else ""),
        )

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        vcxproj = os.path.join(self._source_subfolder, "vs2015", "Argon2OptDll", "Argon2OptDll.vcxproj")
        argon2_header = os.path.join(self._source_subfolder, "include", "argon2.h")
        if not self.options.shared:
            tools.replace_in_file(argon2_header, "__declspec(dllexport)", "")
            tools.replace_in_file(vcxproj, "DynamicLibrary", "StaticLibrary")
        tools.replace_in_file(vcxproj, "<ClCompile>", "<ClCompile><AdditionalIncludeDirectories>$(SolutionDir)include;%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>")
        tools.replace_in_file(vcxproj, "<WindowsTargetPlatformVersion>8.1</WindowsTargetPlatformVersion>", "")
        if self.settings.compiler == "Visual Studio":
            msbuild = MSBuild(self)
            msbuild.build(os.path.join(self._source_subfolder, "Argon2.sln"), targets=("Argon2OptDll",))#, platforms={"x86": "Win32"})
            if self.options.shared:
                tools.replace_in_file(argon2_header, "__declspec(dllexport)", "__declspec(dllimport)")
        else:
            with tools.chdir(self._source_subfolder):
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                with tools.environment_append(autotools.vars):
                    autotools.make(args=self._make_args, target="libs")

    def package(self):
        self.copy("*LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        if self.settings.compiler == "Visual Studio":
            self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
            self.copy("*.dll", src=os.path.join(self._source_subfolder, "vs2015", "build"), dst="bin")
            self.copy("*.lib", src=os.path.join(self._source_subfolder, "vs2015", "build"), dst="lib")
            os.rename(os.path.join(self.package_folder, "lib", "Argon2OptDll.lib"),
                      os.path.join(self.package_folder, "lib", "argon2.lib"))
        else:
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(autotools.vars):
                    autotools.install(args=self._make_args)
            # drop unneeded dirs
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
            if self.settings.os == "Windows" and self.options.shared:
                os.unlink(os.path.join(self.package_folder, "lib", "libargon2.a"))
                self.copy("libargon2.dll.a", src=self._source_subfolder, dst="lib")
                tools.mkdir(os.path.join(self.package_folder, "bin"))
                os.rename(os.path.join(self.package_folder, "lib", "libargon2.dll"),
                          os.path.join(self.package_folder, "bin", "libargon2.dll"))
            # drop unneeded libs
            if self.options.shared:
                if self.settings.os != "Windows":
                    tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.a*")
            else:
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.dll")
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.so")
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.so.*")
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.dylib")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libargon2"
        self.cpp_info.libs = ["argon2"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
