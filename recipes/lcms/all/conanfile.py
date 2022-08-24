from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os
import re
import shutil

required_conan_version = ">=1.36.0"


class LcmsConan(ConanFile):
    name = "lcms"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A free, open source, CMM engine."
    license = "MIT"
    homepage = "https://github.com/mm2/Little-CMS"
    topics = ("lcms", "cmm", "icc", "cmm-engine")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        compiler_version = tools.Version(self.settings.compiler.version)
        if (self.settings.compiler == "Visual Studio" and compiler_version >= "14") or \
           str(self.settings.compiler) == "msvc":
            # since VS2015 vsnprintf is built-in
            path = os.path.join(self._source_subfolder, "src", "lcms2_internal.h")
            tools.replace_in_file(path, "#       define vsnprintf  _vsnprintf", "")
        if (self.settings.compiler == "Visual Studio" and compiler_version >= "16") or \
           (str(self.settings.compiler) == "msvc" and compiler_version >= "192"):
            # since VS2019, don't need to specify the WindowsTargetPlatformVersion
            path = os.path.join(self._source_subfolder, "Projects", "VC2015", "lcms2_static", "lcms2_static.vcxproj")
            tools.replace_in_file(path, "<WindowsTargetPlatformVersion>8.1</WindowsTargetPlatformVersion>", "")
        if self.settings.os == "Android" and self._settings_build.os == "Windows":
            # remove escape for quotation marks, to make ndk on windows happy
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g",
                                  "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")

    def _build_visual_studio(self):
        if tools.Version(self.version) <= "2.11":
            vc_sln_subdir = "VC2013"
        else:
            vc_sln_subdir = "VC2015"
        with tools.chdir(os.path.join(self._source_subfolder, "Projects", vc_sln_subdir )):
            target = "lcms2_DLL" if self.options.shared else "lcms2_static"
            if self.settings.compiler == "Visual Studio" and \
               tools.Version(self.settings.compiler.version) <= "12":
                upgrade_project = False
            else:
                upgrade_project = True
            # Enable LTO when CFLAGS contains -GL
            if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))):
                lto = "true"
            else:
                lto = "false"
            properties = {
                "WholeProgramOptimization": lto,
            }
            # run build
            msbuild = MSBuild(self)
            msbuild.build("lcms2.sln", targets=[target], platforms={"x86": "Win32"},
                          upgrade_project=upgrade_project, properties=properties)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--without-tiff",
            "--without-jpeg",
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_visual_studio()
        else:
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                        os.path.join(self._source_subfolder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                        os.path.join(self._source_subfolder, "config.guess"))
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)
            if self.options.shared:
                self.copy(pattern="*.lib", src=os.path.join(self._source_subfolder, "bin"), dst="lib", keep_path=False)
                self.copy(pattern="*.dll", src=os.path.join(self._source_subfolder, "bin"), dst="bin", keep_path=False)
            else:
                self.copy(pattern="*.lib", src=os.path.join(self._source_subfolder, "Lib", "MS"), dst="lib",
                          keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            # remove utilities
            if self.settings.os == "Windows" and self.options.shared:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*[!.dll]")
            else:
                tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "lcms2")
        suffix = "_static" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.libs = ["lcms2{}".format(suffix)]
        if self._is_msvc and self.options.shared:
            self.cpp_info.defines.append("CMS_DLL")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")

        self.cpp_info.names["pkg_config"] = "lcms2"
