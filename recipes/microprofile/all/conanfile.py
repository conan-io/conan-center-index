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
    topics = ("conan", "profiler", "embedded", "timer")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "microprofile_enabled": [True, False],
        "use_miniz": [True, False],
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
        "enable_gl_timers": [True, False],
        "enable_d3d11_timers": [True, False],
        "enable_d3d12_timers": [True, False],
        "enable_vulkan_timers": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "microprofile_enabled": True,
        "use_miniz": False,
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
        "enable_gl_timers": False,
        "enable_d3d11_timers": False,
        "enable_d3d12_timers": False,
        "enable_vulkan_timers": False
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
        else:
            del self.options.enable_d3d11_timers
            del self.options.enable_d3d12_timers

    def _validate_max_groups(self):
        try:
            _max_groups = int(self.options.max_groups)
            if _max_groups % 32 != 0:
                raise ConanInvalidConfiguration("max_groups must be multiple of 32.")
        except ValueError:
            raise ConanInvalidConfiguration("max_groups must be a number.")

    def _validate_timers(self):
        _timers_enabled_count = 0
        if self.options.enable_gl_timers:
            _timers_enabled_count += 1
        if self.options.get_safe("enable_d3d11_timers", self.default_options["enable_d3d11_timers"]):
            _timers_enabled_count += 1
        if self.options.get_safe("enable_d3d12_timers", self.default_options["enable_d3d12_timers"]):
            _timers_enabled_count += 1
        if self.options.enable_vulkan_timers:
            _timers_enabled_count += 1
        if _timers_enabled_count > 1:
            raise ConanInvalidConfiguration("Cannot choose multiple GPU timers. Choose only one GPU timer.")
        if _timers_enabled_count == 1 and self.options.enable_gpu_timer_callbacks:
            raise ConanInvalidConfiguration("Cannot mix GPU callbacks and GPU timers.")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        self._validate_max_groups()
        self._validate_timers()

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.use_miniz:
            self.requires("miniz/2.2.0")
        if self.options.enable_gl_timers:
            self.requires("glad/0.1.34")
        if self.options.enable_vulkan_timers:
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
        self._cmake.definitions["MP_MINIZ"] = self.options.use_miniz
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
        self._cmake.definitions["MP_GPU_TIMERS_GL"] = self.options.enable_gl_timers
        self._cmake.definitions["MP_GPU_TIMERS_D3D11"] = self.options.get_safe("enable_d3d11_timers", self.default_options["enable_d3d11_timers"])
        self._cmake.definitions["MP_GPU_TIMERS_D3D12"] = self.options.get_safe("enable_d3d12_timers", self.default_options["enable_d3d12_timers"])
        self._cmake.definitions["MP_GPU_TIMERS_VULKAN"] = self.options.enable_vulkan_timers
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("microprofile.h", dst=os.path.join("include", self.name), src=self._source_subfolder)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def _create_defines(self):
        defines = []
        if not self.options.shared:
            defines.append("_MICROPROFILE_STATIC")
        defines.append("MICROPROFILE_ENABLED=" + ("1" if self.options.microprofile_enabled else "0"))
        defines.append("MICROPROFILE_DEBUG=" + ("1" if self.settings.build_type == "Debug" else "0"))
        defines.append("MICROPROFILE_MINIZ=" + ("1" if self.options.use_miniz else "0"))
        defines.append("MICROPROFILE_BIG_ENDIAN=" + ("1" if self.options.use_big_endian else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS=" + ("1" if (self.options.enable_gl_timers or
                                                            self.options.get_safe("enable_d3d11_timers", self.default_options["enable_d3d11_timers"]) or
                                                            self.options.get_safe("enable_d3d12_timers", self.default_options["enable_d3d12_timers"]) or
                                                            self.options.enable_vulkan_timers) else "0"))
        defines.append("MICROPROFILE_GPU_TIMER_CALLBACKS=" + ("1" if self.options.enable_gpu_timer_callbacks else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_GL=" + ("1" if self.options.enable_gl_timers else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_D3D11=" + ("1" if self.options.get_safe("enable_d3d11_timers", self.default_options["enable_d3d11_timers"]) else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_D3D12=" + ("1" if self.options.get_safe("enable_d3d12_timers", self.default_options["enable_d3d12_timers"]) else "0"))
        defines.append("MICROPROFILE_GPU_TIMERS_VULKAN=" + ("1" if self.options.enable_vulkan_timers else "0"))
        defines.append("DMICROPROFILE_PER_THREAD_BUFFER_SIZE=" + str(self.options.thread_buffer_size))
        defines.append("DMICROPROFILE_PER_THREAD_GPU_BUFFER_SIZE=" + str(self.options.thread_gpu_buffer_size))
        defines.append("DMICROPROFILE_MAX_FRAME_HISTORY=" + str(self.options.max_frame_history))
        defines.append("DMICROPROFILE_WEBSERVER_PORT=" + str(self.options.webserver_port))
        defines.append("DMICROPROFILE_WEBSERVER_MAXFRAMES=" + str(self.options.webserver_maxframes))
        defines.append("DMICROPROFILE_WEBSERVER_SOCKET_BUFFER_SIZE=" + str(self.options.webserver_socket_buffer_size))
        defines.append("DMICROPROFILE_GPU_FRAME_DELAY=" + str(self.options.gpu_frame_delay))
        defines.append("DMICROPROFILE_NAME_MAX_LEN=" + str(self.options.name_max_length))
        defines.append("DMICROPROFILE_MAX_TIMERS=" + str(self.options.max_timers))
        defines.append("DMICROPROFILE_MAX_THREADS=" + str(self.options.max_threads))
        defines.append("DMICROPROFILE_MAX_STRING=" + str(self.options.max_string_length))
        defines.append("DMICROPROFILE_TIMELINE_MAX_TOKENS=" + str(self.options.timeline_max_tokens))
        defines.append("DMICROPROFILE_THREAD_LOG_FRAMES_REUSE=" + str(self.options.thread_log_frames_reuse))
        defines.append("DMICROPROFILE_MAX_GROUPS=" + str(self.options.max_groups))
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

