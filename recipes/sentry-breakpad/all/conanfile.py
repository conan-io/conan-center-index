from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, save
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.3"


class SentryBreakpadConan(ConanFile):
    name = "sentry-breakpad"
    description = "Client component that implements a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/breakpad"
    license = "Apache-2.0"
    topics = ("breakpad", "error-reporting", "crash-reporting")
    provides = "breakpad"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "0.5.4" else 17

    @property
    def _compilers_minimum_version(self):
        return {} if Version(self.version) < "0.5.4" else {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            # linux-syscal-support is a public dependency
            # see https://github.com/conan-io/conan-center-index/pull/16752#issuecomment-1487241864 
            self.requires("linux-syscall-support/cci.20200813", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.variables["LINUX"] = True
        tc.generate()

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
                    target_compile_features(breakpad_client PUBLIC cxx_std_11)
                    if(CMAKE_SYSTEM_NAME STREQUAL "Linux" OR CMAKE_SYSTEM_NAME STREQUAL "FreeBSD")
                        find_path(LINUX_SYSCALL_INCLUDE_DIR NAMES linux_syscall_support.h)
                        target_include_directories(breakpad_client PRIVATE ${LINUX_SYSCALL_INCLUDE_DIR})
                    endif()
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
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "external", "breakpad"),
                              dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "breakpad-client")
        self.cpp_info.libs = ["breakpad_client"]
        self.cpp_info.includedirs.append(os.path.join("include", "breakpad"))
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
