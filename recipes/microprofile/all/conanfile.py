import os
from collections import OrderedDict

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, save, load
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class MicroprofileConan(ConanFile):
    name = "microprofile"
    license = "DocumentRef-README.md:LicenseRef-Unlicense"
    description = "Microprofile is a embeddable profiler in a few files, written in C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jonasmr/microprofile"
    topics = ("profiler", "embedded", "timer")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "microprofile_enabled": [True, False],
        "with_miniz": [True, False],
        "thread_buffer_size": ["ANY"],
        "thread_gpu_buffer_size": ["ANY"],
        "max_frame_history": ["ANY"],
        "webserver_port": ["ANY"],
        "webserver_maxframes": ["ANY"],
        "webserver_socket_buffer_size": ["ANY"],
        "gpu_frame_delay": ["ANY"],
        "name_max_length": ["ANY"],
        "max_timers": ["ANY"],
        "max_threads": ["ANY"],
        "max_string_length": ["ANY"],
        "timeline_max_tokens": ["ANY"],
        "thread_log_frames_reuse": ["ANY"],
        "max_groups": ["ANY"],
        "use_big_endian": [True, False],
        "enable_gpu_timer_callbacks": [True, False],
        "enable_timer": [None, "gl", "d3d11", "d3d12", "vulkan"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "microprofile_enabled": True,
        "with_miniz": False,
        "thread_buffer_size": 2097152,
        "thread_gpu_buffer_size": 131072,
        "max_frame_history": 512,
        "webserver_port": 1338,
        "webserver_maxframes": 30,
        "webserver_socket_buffer_size": 16384,
        "gpu_frame_delay": 5,
        "name_max_length": 64,
        "max_timers": 1024,
        "max_threads": 32,
        "max_string_length": 128,
        "timeline_max_tokens": 64,
        "thread_log_frames_reuse": 200,
        "max_groups": 128,
        "use_big_endian": False,
        "enable_gpu_timer_callbacks": False,
        "enable_timer": None,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt",
             src=self.recipe_folder,
             dst=os.path.join(self.export_sources_folder, "src"))


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_miniz:
            self.requires("miniz/3.0.2")
        if self.options.enable_timer == "gl":
            self.requires("opengl/system")
        if self.options.enable_timer == "vulkan":
            self.requires("vulkan-loader/1.3.268.0")
        if Version(self.version) >= "4.0":
            self.requires("stb/cci.20230920")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def _validate_int_options(self):
        positive_int_options = [
            "thread_buffer_size",
            "thread_gpu_buffer_size",
            "max_frame_history",
            "webserver_port",
            "webserver_maxframes",
            "webserver_socket_buffer_size",
            "gpu_frame_delay",
            "name_max_length",
            "max_timers",
            "max_threads",
            "max_string_length",
            "timeline_max_tokens",
            "thread_log_frames_reuse",
            "max_groups",
        ]
        for opt in positive_int_options:
            try:
                value = int(self.options.get_safe(opt))
                if value < 0:
                    raise ValueError
            except ValueError:
                raise ConanInvalidConfiguration(f"microprofile:{opt} must be a positive integer")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.os != "Windows" and self.options.enable_timer in ["d3d11", "d3d12"]:
            raise ConanInvalidConfiguration("DirectX timers can only be used in Windows.")
        if self.options.enable_timer and self.options.enable_gpu_timer_callbacks:
            raise ConanInvalidConfiguration("Cannot mix GPU callbacks and GPU timers.")

        self._validate_int_options()

        if int(self.options.max_groups) % 32 != 0:
            raise ConanInvalidConfiguration("microprofile:max_groups must be multiple of 32.")
        if int(self.options.webserver_port) > 2**16 - 1:
            raise ConanInvalidConfiguration("microprofile:webserver_port must be between 0 and 65535.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["MP_MINIZ"] = self.options.with_miniz
        tc.variables["MP_GPU_TIMERS_VULKAN"] = self.options.enable_timer == "vulkan"
        tc.variables["MICROPROFILE_USE_CONFIG_FILE"] = True
        tc.preprocessor_definitions["STB_SPRINTF_IMPLEMENTATION"] = 1
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        self._create_defines_file(os.path.join(self.source_folder, "microprofile.config.h"))
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_license(self):
        readme = load(self, os.path.join(self.source_folder, "README.md"),)
        return readme[readme.find("# License"):]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

    def _create_defines(self):
        defines = OrderedDict()
        defines["MICROPROFILE_EXPORT"] = None
        defines["MICROPROFILE_ENABLED"] = bool(self.options.microprofile_enabled)
        defines["MICROPROFILE_DEBUG"] = bool(self.settings.build_type == "Debug")
        defines["MICROPROFILE_MINIZ"] = bool(self.options.with_miniz)
        defines["MICROPROFILE_BIG_ENDIAN"] = bool(self.options.use_big_endian)
        defines["MICROPROFILE_GPU_TIMERS"] = bool(self.options.enable_timer)
        defines["MICROPROFILE_GPU_TIMER_CALLBACKS"] = bool(self.options.enable_gpu_timer_callbacks)
        defines["MICROPROFILE_GPU_TIMERS_GL"] = bool(self.options.enable_timer == "gl")
        defines["MICROPROFILE_GPU_TIMERS_D3D11"] = bool(self.options.enable_timer == "d3d11")
        defines["MICROPROFILE_GPU_TIMERS_D3D12"] = bool(self.options.enable_timer == "d3d12")
        defines["MICROPROFILE_GPU_TIMERS_VULKAN"] = bool(self.options.enable_timer == "vulkan")
        defines["MICROPROFILE_PER_THREAD_BUFFER_SIZE"] = self.options.thread_buffer_size
        defines["MICROPROFILE_PER_THREAD_GPU_BUFFER_SIZE"] = self.options.thread_gpu_buffer_size
        defines["MICROPROFILE_MAX_FRAME_HISTORY"] = self.options.max_frame_history
        defines["MICROPROFILE_WEBSERVER_PORT"] = self.options.webserver_port
        defines["MICROPROFILE_WEBSERVER_MAXFRAMES"] = self.options.webserver_maxframes
        defines["MICROPROFILE_WEBSERVER_SOCKET_BUFFER_SIZE"] = self.options.webserver_socket_buffer_size
        defines["MICROPROFILE_GPU_FRAME_DELAY"] = self.options.gpu_frame_delay
        defines["MICROPROFILE_NAME_MAX_LEN"] = self.options.name_max_length
        defines["MICROPROFILE_MAX_TIMERS"] = self.options.max_timers
        defines["MICROPROFILE_MAX_THREADS"] = self.options.max_threads
        defines["MICROPROFILE_MAX_STRING"] = self.options.max_string_length
        defines["MICROPROFILE_TIMELINE_MAX_TOKENS"] = self.options.timeline_max_tokens
        defines["MICROPROFILE_THREAD_LOG_FRAMES_REUSE"] = self.options.thread_log_frames_reuse
        defines["MICROPROFILE_MAX_GROUPS"] = self.options.max_groups
        return defines

    def _create_defines_file(self, filename):
        defines = self._create_defines()
        defines_list = ["#pragma once\n"]
        for define, value in defines.items():
            if value is None or value == "":
                defines_list.append(f"#define {define}\n")
            elif value in [True, False]:
                defines_list.append(f"#define {define} {'1' if value else '0'}\n")
            else:
                defines_list.append(f"#define {define} {value}\n")
        save(self, filename, "".join(defines_list))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if Version(self.version) < "4.0":
            self.cpp_info.includedirs.append(os.path.join("include", "microprofile"))
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
        self.cpp_info.defines.append("MICROPROFILE_USE_CONFIG")
