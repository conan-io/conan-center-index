from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, replace_in_file, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("linux-syscall-support/cci.20200813")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if Version(self.version) <= "0.4.1":
            if self.settings.os == "Android" or is_apple_os(self):
                raise ConanInvalidConfiguration("Versions <=0.4.1 do not support Apple or Android")
        if Version(self.version) <= "0.2.6":
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Versions <=0.2.6 do not support Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
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
            replace_in_file(self,
                os.path.join(self.source_folder, "external", "breakpad", file),
                "#include \"third_party/lss/linux_syscall_support.h\"",
                "#include <linux_syscall_support.h>"
            )

        save(self, os.path.join(self.source_folder, "external", "CMakeLists.txt"),
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
        self._patch_sources()  # It can be apply_conandata_patches(self) only in case no more patches are needed
        cmake = CMake(self)
        cmake.configure(build_script_folder="external")
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "external", "breakpad"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "breakpad-client"
        self.cpp_info.libs = ["breakpad_client"]
        self.cpp_info.includedirs.append(os.path.join("include", "breakpad"))
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
