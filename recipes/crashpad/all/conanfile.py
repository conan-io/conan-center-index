from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
from io import StringIO
import os
import json
import re

class CrashpadConan(ConanFile):
    name = "crashpad"
    description = "Crashpad is a crash-reporting system."
    license = "Apache-2.0"
    homepage = "https://chromium.googlesource.com/crashpad/crashpad"
    url = "https://github.com/bincrafters/conan-crashpad"
    topics = ("crash-reporting", "logging", "minidump", "crash")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "linktime_optimization": [True, False],
        "force_embedded_zlib": [True, False]}
    default_options = {
        "linktime_optimization": False,
        "force_embedded_zlib": False}
    exports = [ "patches/*", "LICENSE.md" ]
    short_paths = True
    generators = "compiler_args"

    _commit_id = "c7d1d2a1dd7cf2442cbb8aa8da7348fa01d54182"
    _source_dir = "crashpad"
    _build_name = "out/Conan"
    _build_dir = os.path.join(_source_dir, _build_name)
    _patch_base = os.path.join(_source_dir, "third_party/mini_chromium/mini_chromium")

    def build_requirements(self):
        self.build_requires("depot_tools_installer/20200515@bincrafters/stable")
        self.build_requires("ninja/1.10.2")

    def _mangle_spec_for_gclient(self, solutions):
        return json.dumps(solutions)          \
                   .replace("\"", "\\\"")     \
                   .replace("false", "False") \
                   .replace("true", "True")

    def _make_spec(self):
        solutions = [{
            "url": "%s@%s" % (self.homepage, self._commit_id),
            "managed": False,
            "name": "%s" % (self.name),
        }]
        return "solutions=%s" % self._mangle_spec_for_gclient(solutions)

    def configure(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version.value) < "5.0":
            raise ConanInvalidConfiguration("gcc >= 5 is required")

    def source(self):
        self.run("gclient config --spec=\"%s\"" % self._make_spec(), run_environment=True)
        self.run("gclient sync --no-history", run_environment=True)

        tools.patch(base_path=self._patch_base,
                    patch_file="patches/buildsystem-adaptions.patch")

    def _get_target_cpu(self):
        arch = str(self.settings.arch)

        if arch == "x86":
            return "x86"
        elif arch == "x86_64":
            return "x64"

        # best effort... please contribute, if you actually tested those platforms
        elif arch.startswith("arm"):
            match = re.match('^armv([0-9]+)', arch)
            if int(match.group(1)) >= 8 and not "32" in arch:
                return "arm64"
            else:
                return "arm"
        elif arch.startswith("mips"):
            return "mipsel"

        raise ConanInvalidConfiguration("your architecture (%s) is not supported" % arch)

    def _set_env_arg(self, args, envvar, gnvar):
        val = os.getenv(envvar)
        if val:
            args += [ "%s=\\\"%s\\\"" % (gnvar, val) ]

    def _setup_args_gn(self):
        args = ["is_debug=%s" % ("true" if self.settings.build_type == "Debug" else "false"),
                "target_cpu=\\\"%s\\\"" % self._get_target_cpu()]

        if self.settings.os == "Macos" and self.settings.get_safe("os.version"):
            args += [ "mac_deployment_target=\\\"%s\\\"" % self.settings.os.version ]
        if self.settings.os == "Windows":
            args += [ "linktime_optimization=%s" % str(self.options.linktime_optimization).lower()]
        if self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime"):
            crt = str(self.settings.compiler.runtime)
            args += [ "dynamic_crt=%s" % ("true" if crt.startswith("MD") else "false") ]

        self._set_env_arg(args, "CC",       "custom_cc")
        self._set_env_arg(args, "CXX",      "custom_cxx")
        self._set_env_arg(args, "CFLAGS",   "extra_cflags_c")
        self._set_env_arg(args, "CFLAGS",   "extra_cflags_objc")
        self._set_env_arg(args, "CXXFLAGS", "extra_cflags_cc")
        self._set_env_arg(args, "CXXFLAGS", "extra_cflags_objcc")
        self._set_env_arg(args, "LDFLAGS",  "extra_ldflags")

        args += [ "custom_conan_compiler_args_file=\\\"@%s\\\"" % os.path.join(self.install_folder, "conanbuildinfo.args") ]

        if self.settings.compiler == "gcc":
            args += [ "custom_cxx_is_gcc=true" ]
        else:
            args += [ "custom_cxx_is_gcc=false" ]

        return " ".join(args)

    # This is a workaround for macOS builds where certain linker errors started
    # occuring. Apparently the crashpad build system does not package a few *.o
    # files properly. That leads to missing symbols when linking with 3rd party
    # projects. More details here:
    #
    #  * https://groups.google.com/a/chromium.org/forum/#!topic/crashpad-dev/XVggc7kvlNs
    def _export_mach_utils(self):
        mactools = tools.XCRun(self.settings)
        self.run("%s cr %s %s" %                                      \
            (mactools.ar,                                             \
             os.path.join(self._build_dir, "obj/util/libmachutil.a"), \
             os.path.join(self._build_dir, "obj", self._build_name, "gen/util/mach/*.o")))

    def build(self):

        if self.options.force_embedded_zlib:
            tools.patch(base_path=self._patch_base,
                        patch_file="patches/force-embedded-zlib.patch")

        targets = "crashpad_handler"
        if self._glibc_version_pre_2_27():
            targets += " compat"

        with tools.chdir(self._source_dir):
            self.run('gn gen %s --args="%s"' % (self._build_name, self._setup_args_gn()), run_environment=True)
            self.run("ninja -j%d -C %s %s" % (tools.cpu_count(), self._build_name, targets), run_environment=True)

        if self.settings.os == "Macos":
            self._export_mach_utils()

    def _copy_lib(self, src_dir):
        self.copy("*.a", dst="lib",
                  src=os.path.join(self._build_dir, src_dir), keep_path=False)
        self.copy("*.lib", dst="lib",
                  src=os.path.join(self._build_dir, src_dir), keep_path=False)

    def _copy_headers(self, dst_dir, src_dir):
        self.copy("*.h", dst=os.path.join("include", dst_dir),
                         src=os.path.join(self._source_dir, src_dir))

    def _copy_bin(self, src_bin):
        self.copy(src_bin, src=self._build_dir, dst="bin")
        self.copy("%s.exe" % src_bin, src=self._build_dir, dst="bin")

    def _glibc_version_pre_2_27(self):
        if self.settings.os != "Linux":
            return False

        buf = StringIO()
        self.run('ldd --version | head -1 | grep -o -E "[0-9]\.[0-9]+" | tail -1', output=buf)
        return buf.getvalue().rstrip() < "2.27"

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_dir,
                             ignore_case=True, keep_path=False)

        self._copy_headers("crashpad/client", "client")
        self._copy_headers("crashpad/util",   "util")
        self._copy_headers("mini_chromium",   "third_party/mini_chromium/mini_chromium")
        self._copy_lib("obj/client")
        self._copy_lib("obj/util")
        self._copy_lib("obj/third_party/mini_chromium")
        self._copy_bin("crashpad_handler")

        if self._glibc_version_pre_2_27():
            self._copy_lib("obj/compat")

    def package_info(self):
        self.cpp_info.includedirs = [ "include/crashpad", "include/mini_chromium" ]
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = ['client', 'util', 'base']

        if self._glibc_version_pre_2_27():
            self.cpp_info.libs += ['compat', 'dl', 'pthread']

        if self.settings.os == "Macos":
            self.cpp_info.libs.append('machutil')  # see _export_mach_utils
            self.cpp_info.exelinkflags.append("-framework CoreFoundation")
            self.cpp_info.exelinkflags.append("-framework CoreGraphics")
            self.cpp_info.exelinkflags.append("-framework CoreText")
            self.cpp_info.exelinkflags.append("-framework Foundation")
            self.cpp_info.exelinkflags.append("-framework IOKit")
            self.cpp_info.exelinkflags.append("-framework Security")
            self.cpp_info.exelinkflags.append("-lbsm")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
