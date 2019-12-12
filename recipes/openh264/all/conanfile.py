from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import fnmatch


class OpenH264Conan(ConanFile):
    name = "openh264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = 'http://www.openh264.org/'
    description = "Open Source H.264 Codec"
    topics = ("conan", "h264", "codec", "video", "compression", )
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {'shared': 'False'}
    _source_subfolder = "sources"

    exports_sources = ["platform-android.mk.patch"]

    def build_requirements(self):
        self.build_requires("nasm/2.13.02")
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ:
                self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _use_winbash(self):
        return tools.os_info.is_windows and (self.settings.compiler == 'gcc' or tools.cross_building(self.settings))

    def _format_path(self, path):
        return tools.unix_path(path) if self._use_winbash else path

    def build(self):
        with tools.vcvars(self.settings):
            tools.patch(os.path.join(self._source_subfolder, "build"), "platform-android.mk.patch")
            with tools.chdir(self._source_subfolder):
                prefix = os.path.abspath(self.package_folder)
                if tools.os_info.is_windows:
                    prefix = tools.unix_path(prefix)
                tools.replace_in_file('Makefile', 'PREFIX=/usr/local', 'PREFIX=%s' % prefix)
                if self.settings.os == "Android":
                    arch = str(self.settings.arch)
                    arch = {"armv7": "arm",
                            "armv8": "arm64"}.get(arch, arch)
                else:
                    if self.settings.arch == 'x86':
                        arch = 'i386'
                    elif self.settings.arch == 'x86_64':
                        arch = 'x86_64'
                    else:
                        arch = self.settings.arch

                args = ['ARCH=%s' % arch]

                env_build = AutoToolsBuildEnvironment(self)
                if self.settings.compiler == 'Visual Studio':
                    tools.replace_in_file(os.path.join('build', 'platform-msvc.mk'),
                                        'CFLAGS_OPT += -MT',
                                        'CFLAGS_OPT += -%s' % str(self.settings.compiler.runtime))
                    tools.replace_in_file(os.path.join('build', 'platform-msvc.mk'),
                                        'CFLAGS_DEBUG += -MTd -Gm',
                                        'CFLAGS_DEBUG += -%s -Gm' % str(self.settings.compiler.runtime))
                    args.append('OS=msvc')
                    env_build.flags.append('-FS')
                else:
                    if tools.os_info.is_windows:
                        args.append('OS=mingw_nt')
                    if self.settings.compiler == 'clang' and self.settings.compiler.libcxx == 'libc++':
                        tools.replace_in_file('Makefile', 'STATIC_LDFLAGS=-lstdc++', 'STATIC_LDFLAGS=-lc++\nLDFLAGS+=-lc++')
                    if self.settings.os == "Android":
                        args.append("NDKLEVEL=%s" % str(self.settings.os.api_level))
                        libcxx = str(self.settings.compiler.libcxx)
                        args.append("STL_LIB=" + ("$(NDKROOT)/sources/cxx-stl/llvm-libc++/libs/$(APP_ABI)/lib%s "
                                % "c++_static.a" if libcxx == "c++_static" else "c++_shared.so") +
                            "$(NDKROOT)/sources/cxx-stl/llvm-libc++/libs/$(APP_ABI)/libc++abi.a")
                        args.append('OS=android')
                        ndk_home = os.environ["ANDROID_NDK_HOME"]
                        args.append('NDKROOT=%s' % ndk_home)  # not NDK_ROOT here
                        target = "android-%s" % str(self.settings.os.api_level)
                        args.append('TARGET=%s' % target)
                        tools.replace_in_file(os.path.join("codec", "build", "android", "dec", "jni", "Application.mk"),
                            "APP_STL := stlport_shared",
                            "APP_STL := %s" % str(self.settings.compiler.libcxx))
                        tools.replace_in_file(os.path.join("codec", "build", "android", "dec", "jni", "Application.mk"),
                            "APP_PLATFORM := android-12",
                            "APP_PLATFORM := %s" % target)
                        args.append("CCASFLAGS=$(CFLAGS) -fno-integrated-as")
                env_build.make(args=args, target="libraries")
                args.append('install-' + ('shared' if self.options.shared else 'static-lib'))
                env_build.make(args=args)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.options.shared:
            exts = ['*.a']
        else:
            exts = ['*.dll', '*.so*', '*.dylib*']
        for root, _, filenames in os.walk(self.package_folder):
            for ext in exts:
                for filename in fnmatch.filter(filenames, ext):
                    os.unlink(os.path.join(root, filename))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        if self.settings.compiler == 'Visual Studio' and self.options.shared:
            self.cpp_info.libs = ['openh264_dll']
        else:
            self.cpp_info.libs = ['openh264']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['m', 'pthread'])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
