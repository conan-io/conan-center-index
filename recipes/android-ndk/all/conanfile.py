from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class AndroidNDKInstallerConan(ConanFile):
    name = "android-ndk"
    description = "The Android NDK is a toolset that lets you implement parts of your app in " \
                  "native code, using languages such as C and C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.android.com/ndk/"
    topics = ("NDK", "android", "toolchain", "compiler")
    license = "Apache-2.0"
    short_paths = True
    no_copy_source = True
    exports_sources = ["cmake-wrapper.cmd", "cmake-wrapper"]

    settings = {"os": ["Windows", "Linux", "Macos"],
                "arch": ["x86_64"]}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.arch != 'x86_64':
            raise ConanInvalidConfiguration("No binaries available for other than 'x86_64' architectures")

    def source(self):
        tarballs = self.conan_data["sources"][self.version]["url"]
        tools.get(**tarballs[str(self.settings.os)])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        pass # no build, but please also no warnings

    # from here on, everything is assumed to run in 2 profile mode, when using the ndk as a build requirement

    @property
    def _platform(self):
        return {"Windows": "windows",
                "Macos": "darwin",
                "Linux": "linux"}.get(str(self.settings_build.os))

    @property
    def _android_abi(self):
        return {"x86": "x86",
                "x86_64": "x86_64",
                "armv7": "armeabi-v7a",
                "armv8": "arm64-v8a"}.get(str(self.settings_target.arch))

    @property
    def _llvm_triplet(self):
        arch = {'armv7': 'arm',
                'armv8': 'aarch64',
                'x86': 'i686',
                'x86_64': 'x86_64'}.get(str(self.settings_target.arch))
        abi = 'androideabi' if self.settings_target.arch == 'armv7' else 'android'
        return '%s-linux-%s' % (arch, abi)

    @property
    def _clang_triplet(self):
        arch = {'armv7': 'armv7a',
                'armv8': 'aarch64',
                'x86': 'i686',
                'x86_64': 'x86_64'}.get(str(self.settings_target.arch))
        abi = 'androideabi' if self.settings_target.arch == 'armv7' else 'android'
        return '%s-linux-%s' % (arch, abi)

    def _fix_permissions(self):
        if os.name != 'posix':
            return
        for root, _, files in os.walk(self.package_folder):
            for filename in files:
                filename = os.path.join(root, filename)
                with open(filename, 'rb') as f:
                    sig = f.read(4)
                    if type(sig) is str:
                        sig = [ord(s) for s in sig]
                    else:
                        sig = [s for s in sig]
                    if len(sig) > 2 and sig[0] == 0x23 and sig[1] == 0x21:
                        self.output.info('chmod on script file: "%s"' % filename)
                        self._chmod_plus_x(filename)
                    elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                        self.output.info('chmod on ELF file: "%s"' % filename)
                        self._chmod_plus_x(filename)
                    elif sig == [0xCA, 0xFE, 0xBA, 0xBE] or \
                         sig == [0xBE, 0xBA, 0xFE, 0xCA] or \
                         sig == [0xFE, 0xED, 0xFA, 0xCF] or \
                         sig == [0xCF, 0xFA, 0xED, 0xFE] or \
                         sig == [0xFE, 0xEF, 0xFA, 0xCE] or \
                         sig == [0xCE, 0xFA, 0xED, 0xFE]:
                        self.output.info('chmod on Mach-O file: "%s"' % filename)
                        self._chmod_plus_x(filename)

    def package(self):
        self.copy(pattern="*", dst=".", src=self._source_subfolder, keep_path=True, symlinks=True)
        self.copy(pattern="*NOTICE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*NOTICE.toolchain", dst="licenses", src=self._source_subfolder)
        self.copy("cmake-wrapper.cmd")
        self.copy("cmake-wrapper")
        self._fix_permissions()

    @property
    def _host(self):
        return self._platform + "-x86_64"

    @property
    def _ndk_root(self):
        return os.path.join(self.package_folder, "toolchains", "llvm", "prebuilt", self._host)

    def _tool_name(self, tool):
        if 'clang' in tool:
            suffix = '.cmd' if self.settings_build.os == 'Windows' else ''
            return '%s%s-%s%s' % (self._clang_triplet, self.settings_target.os.api_level, tool, suffix)
        else:
            suffix = '.exe' if self.settings_build.os == 'Windows' else ''
            return '%s-%s%s' % (self._llvm_triplet, tool, suffix)

    def _define_tool_var(self, name, value):
        ndk_bin = os.path.join(self._ndk_root, 'bin')
        path = os.path.join(ndk_bin, self._tool_name(value))
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    # def package_id(self):
    #     self.info.include_build_settings()
    #     del self.info.settings.arch
    #     del self.info.settings.os.api_level

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        # test shall pass, so this runs also in the build as build requirement context
        # ndk-build: https://developer.android.com/ndk/guides/ndk-build
        self.env_info.PATH.append(self.package_folder)

        # You should use the ANDROID_NDK_ROOT environment variable to indicate where the NDK is located. 
        # That's what most NDK-related scripts use (inside the NDK, and outside of it).
        # https://groups.google.com/g/android-ndk/c/qZjhOaynHXc
        self.output.info('Creating ANDROID_NDK_ROOT environment variable: %s' % self.package_folder)
        self.env_info.ANDROID_NDK_ROOT = self.package_folder

        self.output.info('Creating ANDROID_NDK_HOME environment variable: %s' % self.package_folder)
        self.env_info.ANDROID_NDK_HOME = self.package_folder

        #  this is not enough, I can kill that .....
        if not hasattr(self, 'settings_target'):
            return

        # interestingly I can reach that with
        # conan test --profile:build nsdk-default --profile:host default /Users/a4z/elux/conan/myrecipes/android-ndk/all/test_package android-ndk/r21d@
        if  self.settings_target is None:
            return

        # And if we are not building for Android, why bother at all
        if not self.settings_target.os == "Android":
            return

        self.output.info('Creating NDK_ROOT environment variable: %s' % self._ndk_root)
        self.env_info.NDK_ROOT = self._ndk_root
        
        self.output.info('Creating CHOST environment variable: %s' % self._llvm_triplet)
        self.env_info.CHOST = self._llvm_triplet

        ndk_sysroot = os.path.join(self._ndk_root, 'sysroot')
        self.output.info('Creating CONAN_CMAKE_FIND_ROOT_PATH environment variable: %s' % ndk_sysroot)
        self.env_info.CONAN_CMAKE_FIND_ROOT_PATH = ndk_sysroot

        self.output.info('Creating SYSROOT environment variable: %s' % ndk_sysroot)
        self.env_info.SYSROOT = ndk_sysroot

        self.output.info('Creating self.cpp_info.sysroot: %s' % ndk_sysroot)
        self.cpp_info.sysroot = ndk_sysroot

        self.output.info('Creating ANDROID_NATIVE_API_LEVEL environment variable: %s' % self.settings_target.os.api_level)
        self.env_info.ANDROID_NATIVE_API_LEVEL = str(self.settings_target.os.api_level)

        self._chmod_plus_x(os.path.join(self.package_folder, "cmake-wrapper"))
        cmake_wrapper = "cmake-wrapper.cmd" if self.settings.os == "Windows" else "cmake-wrapper"
        cmake_wrapper = os.path.join(self.package_folder, cmake_wrapper)
        self.output.info('Creating CONAN_CMAKE_PROGRAM environment variable: %s' % cmake_wrapper)
        self.env_info.CONAN_CMAKE_PROGRAM = cmake_wrapper

        toolchain = os.path.join(self.package_folder, "build", "cmake", "android.toolchain.cmake")
        self.output.info('Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: %s' % toolchain)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain

        self.env_info.CC = self._define_tool_var('CC', 'clang')
        self.env_info.CXX = self._define_tool_var('CXX', 'clang++')
        self.env_info.LD = self._define_tool_var('LD', 'ld')
        self.env_info.AR = self._define_tool_var('AR', 'ar')
        self.env_info.AS = self._define_tool_var('AS', 'as')
        self.env_info.RANLIB = self._define_tool_var('RANLIB', 'ranlib')
        self.env_info.STRIP = self._define_tool_var('STRIP', 'strip')
        self.env_info.ADDR2LINE = self._define_tool_var('ADDR2LINE', 'addr2line')
        self.env_info.NM = self._define_tool_var('NM', 'nm')
        self.env_info.OBJCOPY = self._define_tool_var('OBJCOPY', 'objcopy')
        self.env_info.OBJDUMP = self._define_tool_var('OBJDUMP', 'objdump')
        self.env_info.READELF = self._define_tool_var('READELF', 'readelf')
        self.env_info.ELFEDIT = self._define_tool_var('ELFEDIT', 'elfedit')

        self.env_info.ANDROID_PLATFORM = "android-%s" % self.settings_target.os.api_level
        self.env_info.ANDROID_TOOLCHAIN = "clang"
        self.env_info.ANDROID_ABI = self._android_abi
        libcxx_str = str(self.settings_target.compiler.libcxx)
        self.env_info.ANDROID_STL = libcxx_str if libcxx_str.startswith('c++_') else 'c++_shared'

        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_PROGRAM = "BOTH"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_LIBRARY = "BOTH"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_INCLUDE = "BOTH"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_PACKAGE = "BOTH"
