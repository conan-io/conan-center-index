from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import textwrap

required_conan_version = ">=1.33.0"

class BreakpadConan(ConanFile):
    name = "breakpad"
    description = "A set of client and server components which implement a crash-reporting system"
    topics = ["crash", "report", "breakpad"]
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/breakpad/breakpad/"
    settings = "os", "compiler", "build_type", "arch"
    provides = "breakpad"
    options = {
        "fPIC": [True, False]
    }
    default_options = {
        "fPIC": True
    }
    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("linux-syscall-support/cci.20200813")

    def _patch_sources(self):
        # Use Conan's lss instead of the submodule
        # 1. Remove from include dirs
        # 2. Remove from list of headers to install
        # 3. Patch all #include statements
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.in"),
                            "$(includegbc_HEADERS) $(includelss_HEADERS) ",
                            "$(includegbc_HEADERS) "
        )
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.in"),
                            "install-includelssHEADERS install-includepHEADERS ",
                            "iinstall-includepHEADERS "
        )
        files_to_patch = [
            "src/tools/linux/md2core/minidump-2-core.cc",
            "src/processor/testdata/linux_test_app.cc",
            "src/common/memory_allocator.h",
            "src/common/linux/memory_mapped_file.cc",
            "src/common/linux/file_id.cc",
            "src/common/linux/safe_readlink.cc",
            "src/client/minidump_file_writer.cc",
            "src/client/linux/handler/exception_handler.cc",
            "src/client/linux/handler/exception_handler_unittest.cc",
            "src/client/linux/log/log.cc",
            "src/client/linux/crash_generation/crash_generation_client.cc",
            "src/client/linux/minidump_writer/linux_dumper.cc",
            "src/client/linux/minidump_writer/linux_dumper_unittest_helper.cc",
            "src/client/linux/minidump_writer/proc_cpuinfo_reader.h",
            "src/client/linux/minidump_writer/minidump_writer.cc",
            "src/client/linux/minidump_writer/linux_ptrace_dumper.cc",
            "src/client/linux/minidump_writer/cpu_set.h",
            "src/client/linux/minidump_writer/directory_reader.h",
            "src/client/linux/minidump_writer/line_reader.h"
        ]

        for file in files_to_patch:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, file),
                "#include \"third_party/lss/linux_syscall_support.h\"",
                "#include <linux_syscall_support.h>"
            )

        # Let Conan handle fPIC
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "Makefile.in"),
            textwrap.dedent("""\
                @LINUX_HOST_TRUE@am__append_2 = -fPIC
                @LINUX_HOST_TRUE@am__append_3 = -fPIC"""),
            ""
        )

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            self._env_build.configure(configure_dir=self._source_subfolder)
        return self._env_build

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        if self.settings.os == "Linux":
            self._patch_sources()

        env_build = self._configure_autotools()
        env_build.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        env_build = self._configure_autotools()
        env_build.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info( self ):
        self.cpp_info.components["libbreakpad"].libs = ["breakpad"]
        self.cpp_info.components["libbreakpad"].includedirs.append(os.path.join("include", "breakpad"))
        self.cpp_info.components["libbreakpad"].names["pkg_config"] = "breakpad"

        self.cpp_info.components["client"].libs = ["breakpad_client"]
        self.cpp_info.components["client"].includedirs.append(os.path.join("include", "breakpad"))
        self.cpp_info.components["client"].names["pkg_config"] = "breakpad-client"

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["client"].frameworks.append("CoreFoundation")

        if self.settings.os == "Linux":
            self.cpp_info.components["libbreakpad"].system_libs.append("pthread")
            self.cpp_info.components["libbreakpad"].requires.append("linux-syscall-support::linux-syscall-support")

            self.cpp_info.components["client"].system_libs.append("pthread")
            self.cpp_info.components["client"].requires.append("linux-syscall-support::linux-syscall-support")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
