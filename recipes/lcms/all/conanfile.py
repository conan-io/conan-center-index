import os

from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.tools import Version


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
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH") and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        if os.path.isdir("Little-CMS-lcms%s" % self.version):
            os.rename("Little-CMS-lcms%s" % self.version, self._source_subfolder)
        else:
            os.rename("Little-CMS-%s" % self.version, self._source_subfolder)

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

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_visual_studio()
        else:
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
