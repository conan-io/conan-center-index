import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, download, export_conandata_patches, get, save

required_conan_version = ">=1.53.0"


class MicroprofileConan(ConanFile):
    name = "microprofile"
    description = "Microprofile is a embeddable profiler in a few files, written in C++"
    license = "Unlicense"
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
            self.requires("vulkan-loader/1.3.239.0")

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
        get(self, **self.conan_data["sources"][self.version][0], strip_root=True)
        download(self, filename="LICENSE", **self.conan_data["sources"][self.version][1])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MP_MINIZ"] = self.options.with_miniz
        tc.variables["MP_GPU_TIMERS_VULKAN"] = self.options.enable_timer == "vulkan"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        self._create_defines_file(os.path.join(self.source_folder, "microprofile.config.h"))
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def _create_defines(self):
        return [
            "MICROPROFILE_EXPORT",
            ("MICROPROFILE_ENABLED", ("1" if self.options.microprofile_enabled else "0")),
            ("MICROPROFILE_DEBUG", ("1" if self.settings.build_type == "Debug" else "0")),
            ("MICROPROFILE_MINIZ", ("1" if self.options.with_miniz else "0")),
            ("MICROPROFILE_BIG_ENDIAN", ("1" if self.options.use_big_endian else "0")),
            ("MICROPROFILE_GPU_TIMERS", ("1" if self.options.enable_timer else "0")),
            ("MICROPROFILE_GPU_TIMER_CALLBACKS", ("1" if self.options.enable_gpu_timer_callbacks else "0")),
            ("MICROPROFILE_GPU_TIMERS_GL", ("1" if self.options.enable_timer == "gl" else "0")),
            ("MICROPROFILE_GPU_TIMERS_D3D11", ("1" if self.options.enable_timer == "d3d11" else "0")),
            ("MICROPROFILE_GPU_TIMERS_D3D12", ("1" if self.options.enable_timer == "d3d12" else "0")),
            ("MICROPROFILE_GPU_TIMERS_VULKAN", ("1" if self.options.enable_timer == "vulkan" else "0")),
            ("MICROPROFILE_PER_THREAD_BUFFER_SIZE", str(self.options.thread_buffer_size)),
            ("MICROPROFILE_PER_THREAD_GPU_BUFFER_SIZE", str(self.options.thread_gpu_buffer_size)),
            ("MICROPROFILE_MAX_FRAME_HISTORY", str(self.options.max_frame_history)),
            ("MICROPROFILE_WEBSERVER_PORT", str(self.options.webserver_port)),
            ("MICROPROFILE_WEBSERVER_MAXFRAMES", str(self.options.webserver_maxframes)),
            ("MICROPROFILE_WEBSERVER_SOCKET_BUFFER_SIZE", str(self.options.webserver_socket_buffer_size)),
            ("MICROPROFILE_GPU_FRAME_DELAY", str(self.options.gpu_frame_delay)),
            ("MICROPROFILE_NAME_MAX_LEN", str(self.options.name_max_length)),
            ("MICROPROFILE_MAX_TIMERS", str(self.options.max_timers)),
            ("MICROPROFILE_MAX_THREADS", str(self.options.max_threads)),
            ("MICROPROFILE_MAX_STRING", str(self.options.max_string_length)),
            ("MICROPROFILE_TIMELINE_MAX_TOKENS", str(self.options.timeline_max_tokens)),
            ("MICROPROFILE_THREAD_LOG_FRAMES_REUSE", str(self.options.thread_log_frames_reuse)),
            ("MICROPROFILE_MAX_GROUPS", str(self.options.max_groups)),
        ]

    def _create_defines_file(self, filename):
        defines = self._create_defines()
        defines_list = ["#pragma once\n"]
        for define in defines:
            if isinstance(define, tuple) or isinstance(define, list):
                defines_list.append(f"#define {define[0]} {define[1]}\n")
            else:
                defines_list.append(f"#define {define}\n")
        save(self, filename, "".join(defines_list))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.defines.append("MICROPROFILE_USE_CONFIG")
