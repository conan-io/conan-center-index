from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os
import glob
import fnmatch


class PJSIPConan(ConanFile):
    name = "pjsip"
    version = "2.9"
    description = "PJSIP is a free and open source multimedia communication library written in C language " \
                  "implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE"
    topics = ("conan", "pjsip", "sip", "voip", "multimedia", "sdp", "rtp", "stun", "turn", "ice")
    url = "https://github.com/bincrafters/conan-pjsip"
    homepage = "https://www.pjsip.org/"
    license = "GPL-2.0-or-later"
    exports_sources = ["patches/*.patch"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = "openssl/1.1.1d"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            # https://www.pjsip.org/pjlib/docs/html/group__pj__dll__target.htm
            raise ConanInvalidConfiguration("shared MSVC builds are not supported")

    def source(self):
        # Windows users MUST download the .zip because the files have CRLF line-ends,
        # while the .bz2 has LF line-ends and is for Unix and Mac OS X systems
        if self.settings.os == "Windows":
            source_url = "https://github.com/pjsip/pjproject/archive/{v}.zip".format(v=self.version)
            sha256 = "be934b2e3cd70cd809243df0a51c517f05a09aa8cdd4539a716d3b5fe2e6c332"
        else:
            source_url = "https://github.com/pjsip/pjproject/archive/{v}.tar.gz".format(v=self.version)
            sha256 = "83996bb2ebc3ffb1b25dbe9ff697f2285efe39a2c8fc44303b229ba8019a67bc"
        tools.get(source_url, sha256=sha256)
        os.rename("pjproject-" + self.version, self._source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        for filename in sorted(glob.glob("patches/*.patch")):
            self.output.info('applying patch "%s"' % filename)
            tools.patch(base_path=self._source_subfolder, patch_file=filename)
        tools.replace_in_file(os.path.join(self._source_subfolder, "build", "vs", "pjproject-vs14-common-defaults.props"),
                              "<OutputFile>..\lib\$(ProjectName)-$(TargetCPU)-$(Platform)-vc$(VSVer)-$(Configuration).lib</OutputFile>",
                              "<OutputFile>..\lib\$(ProjectName)-.lib</OutputFile>")
        for root, _, filenames in os.walk(self._source_subfolder):
            for filename in filenames:
                if fnmatch.fnmatch(filename, "*.vcxproj"):
                    fullname = os.path.join(root, filename)
                    print("process", fullname)
                    tools.replace_in_file(fullname,
                                          "-$(TargetCPU)-$(Platform)-vc$(VSVer)-$(Configuration).lib</OutputFile>",
                                          "-.lib</OutputFile>",
                                          strict=False)
        #raise ConanInvalidConfiguration("enough")

        # https://trac.pjsip.org/repos/wiki/Getting-Started/Windows
        with tools.chdir(self._source_subfolder):
            tools.save(os.path.join("pjlib", "include", "pj", "config_site.h"), "")
            version = Version(str(self.settings.compiler.version))
            sln_file = "pjproject-vs14.sln" if version >= "14.0" else "pjproject-vs8.sln"
            build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            if str(self.settings.compiler.runtime) in ["MT", "MTd"]:
                build_type += "-Static"
            else:
                build_type += "-Dynamic"
            msbuild = MSBuild(self)
            msbuild.build(project_file=sln_file, targets=["pjsua"], build_type=build_type,
                          platforms={"x86": "Win32", "x86_64": "x64"})

    def _build_configure(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "build.mak.in"),
                              "export TARGET_NAME := @target@",
                              "export TARGET_NAME := ")
        with tools.chdir(self._source_subfolder):
            args = ["--with-ssl=%s" % self.deps_cpp_info["openssl"].rootpath]
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            # disable autodetect
            args.extend(["--disable-darwin-ssl",
                         "--enable-openssl",
                         "--disable-opencore-amr",
                         "--disable-silk",
                         "--disable-opus"])
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "pjlib", "include"),
                      dst="include", keep_path=True)
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "pjlib-util", "include"),
                      dst="include", keep_path=True)
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "pjnath", "include"),
                      dst="include", keep_path=True)
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "pjmedia", "include"),
                      dst="include", keep_path=True)
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "pjsip", "include"),
                      dst="include", keep_path=True)
            self.copy(pattern="*.lib", src=os.path.join(self._source_subfolder),
                      dst="lib", keep_path=False)

    def _format_lib(self, lib):
        return lib + "-"

    def package_info(self):
        is_win = self.settings.os == "Windows"
        libs = ["pjsua2-lib" if is_win else "pjsua2",
                "pjsua-lib" if is_win else "pjsua",
                "pjsip-ua",
                "pjsip-simple",
                "pjsip-core" if is_win else "pjsip",
                "pjmedia-codec",
                "pjmedia",
                "pjmedia-videodev",
                "pjmedia-audiodev",
                "pjnath",
                "pjlib-util",
                "libsrtp" if is_win else "srtp",
                "libresample" if is_win else "resample",
                "libgsmcodec" if is_win else "gsmcodec",
                "libspeex" if is_win else "speex",
                "libilbccodec" if is_win else "ilbccodec",
                "libg7221codec" if is_win else "g7221codec",
                "libyuv" if is_win else "yuv",
                "libwebrtc" if is_win else "webrtc",
                "pjlib" if is_win else "pj"]
        self.cpp_info.libs = [self._format_lib(lib) for lib in libs]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["m", "pthread"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreAudio",
                                        "CoreServices",
                                        "AudioUnit",
                                        "AudioToolbox",
                                        "Foundation",
                                        "AppKit",
                                        "AVFoundation",
                                        "CoreGraphics",
                                        "QuartzCore",
                                        "CoreVideo",
                                        "CoreMedia",
                                        "VideoToolbox",
                                        "Security"]
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(["wsock32", "ws2_32", "ole32", "dsound"])