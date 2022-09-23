from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, download, unzip, load, copy
from conan.tools.layout import basic_layout
import os
import re
import shutil

required_conan_version = ">=1.47.0"


class AndroidNDKConan(ConanFile):
    name = "android-ndk"
    description = "The Android NDK is a toolset that lets you implement parts of your app in native code, using languages such as C and C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.android.com/ndk/"
    topics = ("android", "ndk", "toolchain", "compiler")
    license = "Apache-2.0"

    settings = "os", "arch", "build_type", "compiler"

    short_paths = True
    exports_sources = "cmake-wrapper.cmd", "cmake-wrapper"

    @property
    def _is_universal2(self):
        return self.version in ["r23b", "r23c", "r24", "r25"] and self.settings.os == "Macos" and self.settings.arch in ["x86_64", "armv8"]

    @property
    def _arch(self):
        return "x86_64" if self._is_universal2 else self.settings.arch

    @property
    def _settings_os_supported(self):
        return self.conan_data["sources"][self.version].get(str(self.settings.os)) is not None

    @property
    def _settings_arch_supported(self):
        return self.conan_data["sources"][self.version].get(str(self.settings.os), {}).get(str(self._arch)) is not None

    def package_id(self):
        if self._is_universal2:
            self.info.settings.arch = "universal:armv8/x86_64"
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if not self._settings_os_supported:
            raise ConanInvalidConfiguration(f"os={self.settings.os} is not supported by {self.name} (no binaries are available)")
        if not self._settings_arch_supported:
            raise ConanInvalidConfiguration(f"os,arch={self.settings.os},{self.settings.arch} is not supported by {self.name} (no binaries are available)")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        pass

    def build(self):
        if self.version in ['r23', 'r23b', 'r23c', 'r24', 'r25']:
            data = self.conan_data["sources"][self.version][str(self.settings.os)][str(self._arch)]
            self._unzip_fix_symlinks(url=data["url"], target_folder=self.source_folder, sha256=data["sha256"])
        else:
            get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][str(self._arch)],
                  destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "*", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*NOTICE.toolchain", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "cmake-wrapper.cmd", src=os.path.join(self.source_folder, os.pardir), dst=self.package_folder)
        copy(self, "cmake-wrapper", src=os.path.join(self.source_folder, os.pardir), dst=self.package_folder)
        self._fix_broken_links()
        self._fix_permissions()

    # from here on, everything is assumed to run in 2 profile mode, using this android-ndk recipe as a build requirement

    @property
    def _platform(self):
        return {
            "Linux": "linux",
            "Macos": "darwin",
            "Windows": "windows",
        }.get(str(self.settings_build.os))

    @property
    def _android_abi(self):
        return {
            "armv7": "armeabi-v7a",
            "armv8": "arm64-v8a",
            "x86": "x86",
            "x86_64": "x86_64",
        }.get(str(self.settings_target.arch))

    @property
    def _llvm_triplet(self):
        arch = {
            "armv7": "arm",
            "armv8": "aarch64",
            "x86": "i686",
            "x86_64": "x86_64",
        }.get(str(self.settings_target.arch))
        abi = "androideabi" if self.settings_target.arch == "armv7" else "android"
        return f"{arch}-linux-{abi}"

    @property
    def _clang_triplet(self):
        arch = {
            "armv7": "armv7a",
            "armv8": "aarch64",
            "x86": "i686",
            "x86_64": "x86_64",
        }.get(str(self.settings_target.arch))
        abi = "androideabi" if self.settings_target.arch == "armv7" else "android"
        return f"{arch}-linux-{abi}"

    @property
    def _ndk_major_minor(self):
        match = re.search(r"r(\d+)(\w?)", self.version)
        assert match
        major, minor = match.groups()
        assert major
        return int(major), minor if minor else "a"

    @property
    def _ndk_version_major(self):
        return self._ndk_major_minor[0]

    @property
    def _ndk_version_minor(self):
        return self._ndk_major_minor[1]

    def _fix_permissions(self):
        if os.name != "posix":
            return
        for root, _, files in os.walk(self.package_folder):
            for filename in files:
                filename = os.path.join(root, filename)
                with open(filename, "rb") as f:
                    sig = f.read(4)
                    if isinstance(sig, str):
                        sig = [ord(s) for s in sig]
                    else:
                        sig = list(sig)
                    if len(sig) > 2 and sig[0] == 0x23 and sig[1] == 0x21:
                        self.output.info(f"chmod on script file: '{filename}'")
                        self._chmod_plus_x(filename)
                    elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                        self.output.info(f"chmod on ELF file: '{filename}'")
                        self._chmod_plus_x(filename)
                    elif sig in (
                        [0xCA, 0xFE, 0xBA, 0xBE],
                        [0xBE, 0xBA, 0xFE, 0xCA],
                        [0xFE, 0xED, 0xFA, 0xCF],
                        [0xCF, 0xFA, 0xED, 0xFE],
                        [0xFE, 0xEF, 0xFA, 0xCE],
                        [0xCE, 0xFA, 0xED, 0xFE]
                    ):
                        self.output.info(f"chmod on Mach-O file: '{filename}'")
                        self._chmod_plus_x(filename)

    def _fix_broken_links(self):
        # https://github.com/android/ndk/issues/1671
        # https://github.com/android/ndk/issues/1569
        if self.version in ["r23b", "r23c"] and self.settings.os in ["Linux", "Macos"]:
            platform = "darwin" if self.settings.os == "Macos" else "linux"
            links = {f"toolchains/llvm/prebuilt/{platform}-x86_64/aarch64-linux-android/bin/as": "../../bin/aarch64-linux-android-as",
                     f"toolchains/llvm/prebuilt/{platform}-x86_64/arm-linux-androideabi/bin/as": "../../bin/arm-linux-androideabi-as",
                     f"toolchains/llvm/prebuilt/{platform}-x86_64/x86_64-linux-android/bin/as": "../../bin/x86_64-linux-android-as",
                     f"toolchains/llvm/prebuilt/{platform}-x86_64/i686-linux-android/bin/as": "../../bin/i686-linux-android-as"}
            for path, target in links.items():
                path = os.path.join(self.package_folder, path)
                os.unlink(path)
                os.symlink(target, path)

    @property
    def _host(self):
        return f"{self._platform}-{self._arch}"

    @property
    def _ndk_root(self):
        return os.path.join(self.package_folder, "toolchains", "llvm", "prebuilt", self._host)

    def _wrap_executable(self, tool):
        suffix = ".exe" if self.settings_build.os == "Windows" else ""
        return f"{tool}{suffix}"

    def _tool_name(self, tool, bare=False):
        prefix = ""
        if "clang" in tool:
            suffix = ".cmd" if self.settings_build.os == "Windows" else ""
            prefix = "llvm" if bare else f"{self._clang_triplet}{self.settings_target.os.api_level}"
            return f"{prefix}-{tool}{suffix}"
        else:
            prefix = "llvm" if bare else f"{self._llvm_triplet}"
            executable = f"{prefix}-{tool}"
            return self._wrap_executable(executable)

    @property
    def _cmake_system_processor(self):
        cmake_system_processor = {
            "x86_64": "x86_64",
            "x86": "i686",
            "mips": "mips",
            "mips64": "mips64",
        }.get(str(self.settings.arch))
        if self.settings_target.arch == "armv8":
            cmake_system_processor = "aarch64"
        elif "armv7" in str(self.settings.arch):
            cmake_system_processor = "armv7-a"
        elif "armv6" in str(self.settings.arch):
            cmake_system_processor = "armv6"
        elif "armv5" in str(self.settings.arch):
            cmake_system_processor = "armv5te"
        return cmake_system_processor

    def _define_tool_var(self, name, value, bare = False):
        ndk_bin = os.path.join(self._ndk_root, "bin")
        path = os.path.join(ndk_bin, self._tool_name(value, bare))
        if not os.path.isfile(path):
            self.output.error(f"'Environment variable {name} could not be created: '{path}'")
            return "UNKNOWN"
        self.output.info(f"Creating {name} environment variable: {path}")
        return path

    def _define_tool_var_naked(self, name, value):
        ndk_bin = os.path.join(self._ndk_root, "bin")
        path = os.path.join(ndk_bin, self._wrap_executable(value))
        if not os.path.isfile(path):
            self.output.error(f"'Environment variable {name} could not be created: '{path}'")
            return "UNKNOWN"
        self.output.info(f"Creating {name} environment variable: {path}")
        return path

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        self.cpp_info.includedirs = []

        # test shall pass, so this runs also in the build as build requirement context
        # ndk-build: https://developer.android.com/ndk/guides/ndk-build
        self.cpp_info.bindirs.append(".")

        # You should use the ANDROID_NDK_ROOT environment variable to indicate where the NDK is located.
        # That's what most NDK-related scripts use (inside the NDK, and outside of it).
        # https://groups.google.com/g/android-ndk/c/qZjhOaynHXc
        self.buildenv_info.define_path("ANDROID_NDK_ROOT", self.package_folder)

        self.buildenv_info.define_path("ANDROID_NDK_HOME", self.package_folder)

        #  this is not enough, I can kill that .....
        if not hasattr(self, "settings_target"):
            return

        # interestingly I can reach that with
        # conan test --profile:build nsdk-default --profile:host default /Users/a4z/elux/conan/myrecipes/android-ndk/all/test_package android-ndk/r21d@
        if self.settings_target is None:
            return

        # And if we are not building for Android, why bother at all
        if not self.settings_target.os == "Android":
            self.output.warn(f"You've added {self.name}/{self.version} as a build requirement, while os={self.settings_target.os} != Android")
            return

        self.buildenv_info.define_path("NDK_ROOT", self._ndk_root)

        self.buildenv_info.define("CHOST", self._llvm_triplet)

        ndk_sysroot = os.path.join(self._ndk_root, "sysroot")
        self.buildenv_info.define_path("SYSROOT", ndk_sysroot)

        self.cpp_info.sysroot = ndk_sysroot

        self.buildenv_info.define("ANDROID_NATIVE_API_LEVEL", str(self.settings_target.os.api_level))

        # TODO: It's not clear how this all mechanism of cmake-wrapper should be emulated in conan v2,
        # and actually if it matters at all.
        # Is it not the purpose of the toolchain defined later to pass all these informations?
        self._chmod_plus_x(os.path.join(self.package_folder, "cmake-wrapper"))
        cmake_wrapper = "cmake-wrapper.cmd" if self.settings.os == "Windows" else "cmake-wrapper"
        cmake_wrapper = os.path.join(self.package_folder, cmake_wrapper)
        self.output.info(f"Creating CONAN_CMAKE_PROGRAM environment variable: {cmake_wrapper}")
        self.env_info.CONAN_CMAKE_PROGRAM = cmake_wrapper

        toolchain = os.path.join(self.package_folder, "build", "cmake", "android.toolchain.cmake")

        #CMakeToolchain automatically adds the standard Android toolchain file that ships with the NDK
        #when `tools.android:ndk_path` is provided, so there's no need to add it as a `user_toolchain`
        self.conf_info.define("tools.android:ndk_path", self.package_folder)

        self.buildenv_info.define_path("CC", self._define_tool_var("CC", "clang"))
        self.buildenv_info.define_path("CXX", self._define_tool_var("CXX", "clang++"))

        # Versions greater than 23 had the naming convention
        # changed to no longer include the triplet.
        bare = self._ndk_version_major >= 23
        self.buildenv_info.define_path("AR", self._define_tool_var("AR", "ar", bare))
        self.buildenv_info.define_path("AS", self._define_tool_var("AS", "as", bare))
        self.buildenv_info.define_path("RANLIB", self._define_tool_var("RANLIB", "ranlib", bare))
        self.buildenv_info.define_path("STRIP", self._define_tool_var("STRIP", "strip", bare))
        self.buildenv_info.define_path("ADDR2LINE", self._define_tool_var("ADDR2LINE", "addr2line", bare))
        self.buildenv_info.define_path("NM", self._define_tool_var("NM", "nm", bare))
        self.buildenv_info.define_path("OBJCOPY", self._define_tool_var("OBJCOPY", "objcopy", bare))
        self.buildenv_info.define_path("OBJDUMP", self._define_tool_var("OBJDUMP", "objdump", bare))
        self.buildenv_info.define_path("READELF", self._define_tool_var("READELF", "readelf", bare))
        # there doesn't seem to be an 'elfedit' included anymore.
        if self._ndk_version_major < 23:
            self.buildenv_info.define_path("ELFEDIT", self._define_tool_var("ELFEDIT", "elfedit", bare))

        # The `ld` tool changed naming conventions earlier than others
        if self._ndk_version_major >= 22:
            self.buildenv_info.define_path("LD", self._define_tool_var_naked("LD", "ld"))
        else:
            self.buildenv_info.define_path("LD", self._define_tool_var("LD", "ld"))

        self.buildenv_info.define("ANDROID_PLATFORM", f"android-{self.settings_target.os.api_level}")
        self.buildenv_info.define("ANDROID_TOOLCHAIN", "clang")
        self.buildenv_info.define("ANDROID_ABI", self._android_abi)
        libcxx_str = str(self.settings_target.compiler.libcxx)
        self.buildenv_info.define("ANDROID_STL", libcxx_str if libcxx_str.startswith("c++_") else "c++_shared")


        # TODO: conan v1 stuff to remove later
        self.env_info.PATH.append(self.package_folder)
        self.env_info.ANDROID_NDK_ROOT = self.package_folder
        self.env_info.ANDROID_NDK_HOME = self.package_folder
        cmake_system_processor = self._cmake_system_processor
        if cmake_system_processor:
            self.env_info.CONAN_CMAKE_SYSTEM_PROCESSOR = cmake_system_processor
        else:
            self.output.warn("Could not find a valid CMAKE_SYSTEM_PROCESSOR variable, supported by CMake")
        self.env_info.NDK_ROOT = self._ndk_root
        self.env_info.CHOST = self._llvm_triplet
        self.env_info.CONAN_CMAKE_FIND_ROOT_PATH = ndk_sysroot
        self.env_info.SYSROOT = ndk_sysroot
        self.env_info.ANDROID_NATIVE_API_LEVEL = str(self.settings_target.os.api_level)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain
        self.env_info.CC = self._define_tool_var("CC", "clang")
        self.env_info.CXX = self._define_tool_var("CXX", "clang++")
        self.env_info.AR = self._define_tool_var("AR", "ar", bare)
        self.env_info.AS = self._define_tool_var("AS", "as", bare)
        self.env_info.RANLIB = self._define_tool_var("RANLIB", "ranlib", bare)
        self.env_info.STRIP = self._define_tool_var("STRIP", "strip", bare)
        self.env_info.ADDR2LINE = self._define_tool_var("ADDR2LINE", "addr2line", bare)
        self.env_info.NM = self._define_tool_var("NM", "nm", bare)
        self.env_info.OBJCOPY = self._define_tool_var("OBJCOPY", "objcopy", bare)
        self.env_info.OBJDUMP = self._define_tool_var("OBJDUMP", "objdump", bare)
        self.env_info.READELF = self._define_tool_var("READELF", "readelf", bare)
        if self._ndk_version_major < 23:
            self.env_info.ELFEDIT = self._define_tool_var("ELFEDIT", "elfedit")
        if self._ndk_version_major >= 22:
            self.env_info.LD = self._define_tool_var_naked("LD", "ld")
        else:
            self.env_info.LD = self._define_tool_var("LD", "ld")
        self.env_info.ANDROID_PLATFORM = f"android-{self.settings_target.os.api_level}"
        self.env_info.ANDROID_TOOLCHAIN = "clang"
        self.env_info.ANDROID_ABI = self._android_abi
        self.env_info.ANDROID_STL = libcxx_str if libcxx_str.startswith("c++_") else "c++_shared"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_PROGRAM = "BOTH"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_LIBRARY = "BOTH"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_INCLUDE = "BOTH"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_PACKAGE = "BOTH"

    def _unzip_fix_symlinks(self, url, target_folder, sha256):
        # Python's built-in module 'zipfile' won't handle symlinks (https://bugs.python.org/issue37921)
        # Most of the logic borrowed from this PR https://github.com/conan-io/conan/pull/8100

        filename = "android_sdk.zip"
        download(self, url, filename, sha256=sha256)
        unzip(self, filename, destination=target_folder, strip_root=True)

        def is_symlink_zipinfo(zi):
            return (zi.external_attr >> 28) == 0xA

        full_path = os.path.normpath(target_folder)
        import zipfile
        with zipfile.ZipFile(filename, "r") as z:
            zip_info = z.infolist()

            names = [n.replace("\\", "/") for n in z.namelist()]
            common_folder = os.path.commonprefix(names).split("/", 1)[0]

            for file_ in zip_info:
                if is_symlink_zipinfo(file_):
                    rel_path = os.path.relpath(file_.filename, common_folder)
                    full_name = os.path.join(full_path, rel_path)
                    target = load(self, full_name)
                    os.unlink(full_name)

                    try:
                        os.symlink(target, full_name)
                    except OSError:
                        if not os.path.isabs(target):
                            target = os.path.normpath(os.path.join(os.path.dirname(full_name), target))
                        shutil.copy2(target, full_name)

        os.unlink(filename)
