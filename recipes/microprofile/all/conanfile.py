from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MicroprofileConan(ConanFile):
    name = "microprofile"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jonasmr/microprofile"
    description = "Microprofile is a embeddable profiler in a few files, written in C++"
    topics = ("profiler", "embedded", "timer")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "microprofile_enabled": [True, False],
        "with_miniz": [True, False],
        "thread_buffer_size": "ANY",
        "thread_gpu_buffer_size": "ANY",
        "max_frame_history": "ANY",
        "webserver_port": "ANY",
        "webserver_maxframes": "ANY",
        "webserver_socket_buffer_size": "ANY",
        "gpu_frame_delay": "ANY",
        "name_max_length": "ANY",
        "max_timers": "ANY",
        "max_threads": "ANY",
        "max_string_length": "ANY",
        "timeline_max_tokens": "ANY",
        "thread_log_frames_reuse": "ANY",
        "max_groups": "ANY",
        "use_big_endian": [True, False],
        "enable_gpu_timer_callbacks": [True, False],
        "enable_timer": [None, "gl", "d3d11", "d3d12", "vulkan"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "microprofile_enabled": True,
        "with_miniz": False,
        "thread_buffer_size": 2048 << 10,
        "thread_gpu_buffer_size": 128 << 10,
        "max_frame_history": 512,
        "webserver_port": 1338,
        "webserver_maxframes": 30,
        "webserver_socket_buffer_size": 16 << 10,
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
        "enable_timer": None
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

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
            "max_groups"
        ]
        for opt in positive_int_options:
            try:
                value = int(getattr(self.options, opt))
                if value < 0:
                    raise ValueError
            except ValueError:
                raise ConanInvalidConfiguration("microprofile:{} must be a positive integer".format(opt))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os != "Windows" and self.options.enable_timer in ["d3d11", "d3d12"]:
            raise ConanInvalidConfiguration("DirectX timers can only be used in Windows.")
        if self.options.enable_timer is not None and self.options.enable_gpu_timer_callbacks:
            raise ConanInvalidConfiguration("Cannot mix GPU callbacks and GPU timers.")

        self._validate_int_options()

        if int(self.options.max_groups) % 32 != 0:
            raise ConanInvalidConfiguration("microprofile:max_groups must be multiple of 32.")
        if int(self.options.webserver_port) > 2 ** 16 - 1:
            raise ConanInvalidConfiguration("microprofile:webserver_port must be between 0 and 65535.")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_miniz:
            self.requires("miniz/2.2.0")
        if self.options.enable_timer == "gl":
            self.requires("opengl/system")
        if self.options.enable_timer == "vulkan":
            self.requires("vulkan-loader/1.2.182")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0], strip_root=True, destination=self._source_subfolder)
        tools.download(filename="LICENSE", **self.conan_data["sources"][self.version][1])

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MP_ENABLED"] = self.options.microprofile_enabled
        self._cmake.definitions["MP_DEBUG"] = self.settings.build_type == "Debug"
        self._cmake.definitions["MP_MINIZ"] = self.options.with_miniz
        self._cmake.definitions["MP_THREAD_BUFFER_SIZE"] = self.options.thread_buffer_size
        self._cmake.definitions["MP_THREAD_GPU_BUFFER_SIZE"] = self.options.thread_gpu_buffer_size
        self._cmake.definitions["MP_MAX_FRAME_HISTORY"] = self.options.max_frame_history
        self._cmake.definitions["MP_WEBSERVER_PORT"] = self.options.webserver_port
        self._cmake.definitions["MP_WEBSERVER_MAXFRAMES"] = self.options.webserver_maxframes
        self._cmake.definitions["MP_WEBSERVER_SOCKET_BUFFER_SIZE"] = self.options.webserver_socket_buffer_size
        self._cmake.definitions["MP_GPU_FRAME_DELAY"] = self.options.gpu_frame_delay
        self._cmake.definitions["MP_NAME_MAX_LENGTH"] = self.options.name_max_length
        self._cmake.definitions["MP_MAX_TIMERS"] = self.options.max_timers
        self._cmake.definitions["MP_MAX_THREADS"] = self.options.max_threads
        self._cmake.definitions["MP_MAX_STRING_LENGTH"] = self.options.max_string_length
        self._cmake.definitions["MP_TIMELINE_MAX_TOKENS"] = self.options.timeline_max_tokens
        self._cmake.definitions["MP_THREAD_LOG_FRAMES_REUSE"] = self.options.thread_log_frames_reuse
        self._cmake.definitions["MP_MAX_GROUPS"] = self.options.max_groups
        self._cmake.definitions["MP_BIG_ENDIAN"] = self.options.use_big_endian
        self._cmake.definitions["MP_GPU_TIMER_CALLBACKS"] = self.options.enable_gpu_timer_callbacks
        self._cmake.definitions["MP_GPU_TIMERS_GL"] = self.options.enable_timer == "gl"
        self._cmake.definitions["MP_GPU_TIMERS_D3D11"] = self.options.enable_timer == "d3d11"
        self._cmake.definitions["MP_GPU_TIMERS_D3D12"] = self.options.enable_timer == "d3d12"
        self._cmake.definitions["MP_GPU_TIMERS_VULKAN"] = self.options.enable_timer == "vulkan"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def _create_defines(self):
        defines = []
        defines.append("MICROPROFILE_EXPORT")
        defines.append("MICROPROFILE_ENABLED=" + ("1" if self.options.microprofile_enabled else "0"))
        defines.append("MICROPROFILE_DEBUG=" + ("1" if self.settings.build_type == "Debug" else "0"))
        defines.append("MICROPROFILE_MINIZ=" + ("1" if self.options.with_miniz else "0"))
        defines.append("MICROPROFILE_BIG_ENDIAN=" + ("1" if self.options.use_big_endian else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS=" + ("1" if self.options.enable_timer is not None else "0"))
        defines.append("MICROPROFILE_GPU_TIMER_CALLBACKS=" + ("1" if self.options.enable_gpu_timer_callbacks else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_GL=" + ("1" if self.options.enable_timer == "gl" else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_D3D11=" + ("1" if self.options.enable_timer == "d3d11" else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_D3D12=" + ("1" if self.options.enable_timer == "d3d12" else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_VULKAN=" + ("1" if self.options.enable_timer == "vulkan" else "0"))
        defines.append("MICROPROFILE_PER_THREAD_BUFFER_SIZE=" + str(self.options.thread_buffer_size))
        defines.append("MICROPROFILE_PER_THREAD_GPU_BUFFER_SIZE=" + str(self.options.thread_gpu_buffer_size))
        defines.append("MICROPROFILE_MAX_FRAME_HISTORY=" + str(self.options.max_frame_history))
        defines.append("MICROPROFILE_WEBSERVER_PORT=" + str(self.options.webserver_port))
        defines.append("MICROPROFILE_WEBSERVER_MAXFRAMES=" + str(self.options.webserver_maxframes))
        defines.append("MICROPROFILE_WEBSERVER_SOCKET_BUFFER_SIZE=" + str(self.options.webserver_socket_buffer_size))
        defines.append("MICROPROFILE_GPU_FRAME_DELAY=" + str(self.options.gpu_frame_delay))
        defines.append("MICROPROFILE_NAME_MAX_LEN=" + str(self.options.name_max_length))
        defines.append("MICROPROFILE_MAX_TIMERS=" + str(self.options.max_timers))
        defines.append("MICROPROFILE_MAX_THREADS=" + str(self.options.max_threads))
        defines.append("MICROPROFILE_MAX_STRING=" + str(self.options.max_string_length))
        defines.append("MICROPROFILE_TIMELINE_MAX_TOKENS=" + str(self.options.timeline_max_tokens))
        defines.append("MICROPROFILE_THREAD_LOG_FRAMES_REUSE=" + str(self.options.thread_log_frames_reuse))
        defines.append("MICROPROFILE_MAX_GROUPS=" + str(self.options.max_groups))
        return defines

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = self.name
        self.cpp_info.names["cmake_find_package_multi"] = self.name
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.defines = self._create_defines()
