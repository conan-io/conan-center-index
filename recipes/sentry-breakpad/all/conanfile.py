from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class SentryBreakpadConan(ConanFile):
    name = "sentry-breakpad"
    description = "Client component that implements a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/breakpad"
    license = "Apache-2.0"
    topics = ("conan", "breakpad", "error-reporting", "crash-reporting")
    provides = "breakpad"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("linux-syscall-support/cci.20200813")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        if tools.Version(self.version) <= "0.4.1":
            if self.settings.os == "Android" or tools.is_apple_os(self.settings.os):
                raise ConanInvalidConfiguration("Versions <=0.4.1 do not support Apple or Android")
        if tools.Version(self.version) <= "0.2.6":
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Versions <=0.2.6 do not support Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # FIXME: convert to patches
        import textwrap

        files_to_patch = [
            # "src/tools/linux/md2core/minidump-2-core.cc",
            # "src/processor/testdata/linux_test_app.cc",
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
                os.path.join(self._source_subfolder, "external", "breakpad", file),
                "#include \"third_party/lss/linux_syscall_support.h\"",
                "#include <linux_syscall_support.h>"
            )

        tools.save(os.path.join(self._source_subfolder, "external", "CMakeLists.txt"),
                   textwrap.dedent("""\
                    install(TARGETS breakpad_client
                        ARCHIVE DESTINATION lib
                        LIBRARY DESTINATION lib
                        RUNTIME DESTINATION bin
                    )
                    file(GLOB COMMON_FILES breakpad/src/common/*.h)
                    install(FILES ${COMMON_FILES}
                        DESTINATION include/breakpad/common
                    )
                    set(PLATFORM_FOLDER)
                    if(IOS)
                        set(PLATFORM_FOLDER ios)
                    elseif(APPLE)
                        set(PLATFORM_FOLDER mac)
                    elseif(UNIX)
                        set(PLATFORM_FOLDER linux)
                    endif()
                    if(WIN32)
                        set(PLATFORM_FOLDER windows)
                    endif()
                    if(NOT PLATFORM_FOLDER)
                        message(FATAL_ERROR "Unknown os -> don't know how to install headers")
                    endif()
                    file(GLOB COMMON_PLATFORM_HEADERS breakpad/src/common/${PLATFORM_FOLDER}/*.h)
                    install(FILES ${COMMON_PLATFORM_HEADERS}
                        DESTINATION include/breakpad/common/${PLATFORM_FOLDER})
                    install(DIRECTORY breakpad/src/client/${PLATFORM_FOLDER}
                        DESTINATION include/breakpad/client
                        FILES_MATCHING PATTERN *.h
                    )
                    install(DIRECTORY breakpad/src/google_breakpad/common
                        DESTINATION include/breakpad/google_breakpad
                        FILES_MATCHING PATTERN *.h
                    )
                   """), append=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "external", "breakpad"))
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "breakpad-client"
        self.cpp_info.libs = ["breakpad_client"]
        self.cpp_info.includedirs.append(os.path.join("include", "breakpad"))
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
