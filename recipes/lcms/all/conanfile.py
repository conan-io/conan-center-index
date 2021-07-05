from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.tools import Version
import os
import shutil

required_conan_version = ">=1.33.0"


class LcmsConan(ConanFile):
    name = "lcms"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A free, open source, CMM engine."
    license = "MIT"
    homepage = "https://github.com/mm2/Little-CMS"
    topics = ("conan", "lcms", "cmm", "icc", "cmm-engine")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("gnu-config/cci.20201022")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "14":
            # since VS2015 vsnprintf is built-in
            path = os.path.join(self._source_subfolder, "src", "lcms2_internal.h")
            tools.replace_in_file(path, "#       define vsnprintf  _vsnprintf", "")
        if self.settings.os == "Android" and tools.os_info.is_windows:
            # remove escape for quotation marks, to make ndk on windows happy
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g",
                                  "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")

    def _build_visual_studio(self):
        with tools.chdir(os.path.join(self._source_subfolder, "Projects", "VC2013")):
            target = "lcms2_DLL" if self.options.shared else "lcms2_static"
            upgrade_project = Version(self.settings.compiler.version) > "12"
            # run build
            msbuild = MSBuild(self)
            msbuild.build("lcms2.sln", targets=[target], platforms={"x86": "Win32"}, upgrade_project=upgrade_project)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = []
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        args.append("--without-tiff")
        args.append("--without-jpeg")
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _user_info_build(self):
        # If using the experimental feature with different context for host and
        # build, the 'user_info' attributes of the 'build_requires' packages
        # will be located into the 'user_info_build' object. In other cases they
        # will be located into the 'deps_user_info' object.
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
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
        if self.settings.compiler == "Visual Studio":
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
            # remove entire share directory
            tools.rmdir(os.path.join(self.package_folder, "share"))
            # remove pkgconfig
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            # remove la files
            la = os.path.join(self.package_folder, "lib", "liblcms2.la")
            if os.path.isfile(la):
                os.unlink(la)
            # remove binaries
            for bin_program in ["tificc", "linkicc", "transicc", "psicc", "jpgicc"]:
                for ext in ["", ".exe"]:
                    try:
                        os.remove(os.path.join(self.package_folder, "bin", bin_program + ext))
                    except:
                        pass

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["lcms2" if self.options.shared else "lcms2_static"]
            if self.options.shared:
                self.cpp_info.defines.append("CMS_DLL")
        else:
            self.cpp_info.libs = ["lcms2"]
        self.cpp_info.names["pkg_config"] = "lcms2"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
