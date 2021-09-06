from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class OpenH264Conan(ConanFile):
    name = "openh264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.openh264.org/"
    description = "Open Source H.264 Codec"
    topics = ("h264", "codec", "video", "compression", )
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": "False",
        "fPIC": True,
    }

    exports_sources = "patches/*"

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

    def build_requirements(self):
        if self.settings.arch in ("x86", "x86_64"):
            self.build_requires("nasm/2.15.05")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "build", "platform-msvc.mk"),
                                "CFLAGS_OPT += -MT",
                                "CFLAGS_OPT += -{}".format(self.settings.compiler.runtime))
            tools.replace_in_file(os.path.join(self._source_subfolder, "build", "platform-msvc.mk"),
                                "CFLAGS_DEBUG += -MTd -Gm",
                                "CFLAGS_DEBUG += -{} -Gm".format(self.settings.compiler.runtime))
        if self.settings.os == "Android":
            tools.replace_in_file(os.path.join(self._source_subfolder, "codec", "build", "android", "dec", "jni", "Application.mk"),
                                  "APP_STL := stlport_shared",
                                  "APP_STL := {}".format(self.settings.compiler.libcxx))
            tools.replace_in_file(os.path.join(self._source_subfolder, "codec", "build", "android", "dec", "jni", "Application.mk"),
                                  "APP_PLATFORM := android-12",
                                  "APP_PLATFORM := {}".format(self._android_target))

    @property
    def _library_filename(self):
        prefix = "" if self.settings.compiler == "Visual Studio" else "lib"
        if self.options.shared:
            if tools.is_apple_os(self.settings.os):
                suffix = ".dylib"
            elif self.settings.os == "Windows":
                suffix = ".dll"
            else:
                suffix = ".so"
        else:
            if self.settings.compiler == "Visual Studio":
                suffix = ".lib"
            else:
                suffix = ".a"
        return prefix + "openh264" + suffix

    @property
    def _make_arch(self):
        return {
            "armv7": "arm",
            "armv8": "arm64",
            "x86": "i386",
            "x86_64": "x86_64",
        }.get(str(self.settings.arch), str(self.settings.arch))

    @property
    def _android_target(self):
        return "android-{}".format(self.settings.os.api_level)

    @property
    def _make_args(self):
        prefix = os.path.abspath(self.package_folder)
        if tools.os_info.is_windows:
            prefix = tools.unix_path(prefix)
        args = [
            "ARCH={}".format(self._make_arch),
            "PREFIX={}".format(prefix),
        ]
        autotools = AutoToolsBuildEnvironment(self)
        if self.settings.compiler == "Visual Studio":
            autotools.flags.extend(["-nologo", "-{}".format(self.settings.compiler.runtime)])
            autotools.link_flags.insert(0, "-link")
            if tools.Version(self.settings.compiler.version) >= "12":
                autotools.flags.append("-FS")
        elif self.settings.compiler in ("apple-clang",):
            if self.settings.arch in ("armv8",):
                autotools.link_flags.append("-arch arm64")
        if self.options.shared:
            autotools.fpic = True
        args.extend(["{}={}".format(k, v) for k,v in autotools.vars.items()])

        if self.settings.compiler == "Visual Studio":
            args.append("OS=msvc")
            autotools.flags.append("-FS")
        else:
            if self.settings.os == "Windows":
                args.append("OS=mingw_nt")
            if self.settings.os == "Android":
                libcxx = str(self.settings.compiler.libcxx)
                stl_lib = "$(NDKROOT)/sources/cxx-stl/llvm-libc++/libs/$(APP_ABI)/lib{}".format("c++_static.a" if libcxx == "c++_static" else "c++_shared.so") \
                          + "$(NDKROOT)/sources/cxx-stl/llvm-libc++/libs/$(APP_ABI)/libc++abi.a"
                ndk_home = os.environ["ANDROID_NDK_HOME"]
                args.extend([
                    "NDKLEVEL={}".format(self.settings.os.api_level),
                    "STL_LIB={}".format(stl_lib),
                    "OS=android",
                    "NDKROOT={}".format(ndk_home),  # not NDK_ROOT here
                    "TARGET={}".format(self._android_target),
                    "CCASFLAGS=$(CFLAGS) -fno-integrated-as",
                ])

        return args

    def build(self):
        self._patch_sources()
        with tools.vcvars(self) if self.settings.compiler == "Visual Studio" else tools.no_op():
            with tools.chdir(self._source_subfolder):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=self._make_args, target=self._library_filename)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.vcvars(self) if self.settings.compiler == "Visual Studio" else tools.no_op():
            with tools.chdir(self._source_subfolder):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=self._make_args, target="install-" + ("shared" if self.options.shared else "static-lib"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.libs = ["openh264_dll"]
        else:
            self.cpp_info.libs = ["openh264"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.names["pkg_config"] = "openh264"
        libcxx = tools.stdcpp_library(self)
        if libcxx:
            self.cpp_info.system_libs.append(libcxx)
