from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class JerryScriptStackConan(ConanFile):
    name = "jerryscript"
    license = "Apache-2.0"
    homepage = "https://github.com/jerryscript-project/jerryscript"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Ultra-lightweight JavaScript engine for the Internet of Things"
    topics = ["javascript", "iot", "jerryscript", "javascript-engine"]
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tool_cmdline": [True, False],
        "tool_cmdline_test": [True, False],
        "tool_cmdline_snapshot": [True, False],
        "default_port_implementation": [True, False],
        "jerry_ext": [True, False],
        "jerry_math": [True, False],
        "link_time_optimization": [True, False],
        "strip_symbols": [True, False],
        "amalgamated": [True, False],
        "debugger": [True, False],
        "keep_line_info": [True, False],
        "profile": "ANY",
        "promise_callback": [True, False],
        "external_context": [True, False],
        "snapshot_execution": [True, False],
        "snapshot_saving": [True, False],
        "parser": [True, False],
        "enable_dump_bytecode": [True, False],
        "enable_dump_regexp_bytecode": [True, False],
        "strict_regexp": [True, False],
        "error_messages": [True, False],
        "logging": [True, False],
        "memory_statistics": [True, False],
        "heap_size": "ANY",
        "gc_limit": "ANY",
        "gc_mark_limit": "ANY",
        "stack_limit": "ANY",
        "cpointer_32_bit": [True, False],
        "system_allocator": [True, False],
        "valgrind": [True, False],
        "gc_before_each_alloc": [True, False],
        "vm_exec_stop": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tool_cmdline": True,
        "tool_cmdline_test": False,
        "tool_cmdline_snapshot": False,
        "default_port_implementation": True,
        "jerry_ext": True,
        "jerry_math": False,  # Initialized in `config_options`
        "link_time_optimization": False,  # Enabled by upstream, but disabled to be confirm cci (add -flto in your profile)
        "strip_symbols": True,
        "amalgamated": False,
        "debugger": False,
        "keep_line_info": False,
        "profile": None,  # Initialized in `config_options`
        "promise_callback": False,
        "external_context": False,
        "snapshot_execution": False,
        "snapshot_saving": False,
        "parser": True,
        "enable_dump_bytecode": False,
        "enable_dump_regexp_bytecode": False,
        "strict_regexp": False,
        "error_messages": False,
        "logging": False,
        "memory_statistics": False,
        "heap_size": 512,
        "gc_limit": 0,
        "gc_mark_limit": 8,
        "stack_limit": 0,
        "cpointer_32_bit": False,
        "system_allocator": False,
        "valgrind": False,
        "gc_before_each_alloc": False,
        "vm_exec_stop": False,
    }
    generators = "cmake"
    short_paths = True

    _cmake = None
    _predefined_profiles = ["es.next", "es5.1", "minimal"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _jerry_math(self):
        return self.options.get_safe("jerry_math", False)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # profile and jerry_match default option value depend on version
        if tools.Version(self.version) < "2.4.0":
            self.options.profile = "es5.1"
            self.options.jerry_math = True
            if self.settings.compiler == "Visual Studio":
                del self.options.jerry_math  # forced to False
        else:
            self.options.profile = "es.next"
            self.options.jerry_math = False

        if self.settings.os == "Macos":
            del self.options.jerry_math  # forced to False
            del self.options.link_time_optimization  # forced to False
            del self.options.strip  # forced to False

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

        if not self.options.debugger:
            del self.options.keep_line_info

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("jerryscript shared lib is not yet supported under windows")

    def validate(self):
        # validate integers
        try:
            checks = (
                (0 <= int(self.options.heap_size), "heap_size must be bigger than or equal to 0"),
                (0 <= int(self.options.gc_limit) <= 8192, "gc_limit must be in the range [0, 8192]"),
                (0 <= int(self.options.gc_mark_limit), "gc_mark_limit must be bigger than or equal to 0"),
                (0 <= int(self.options.stack_limit), "stack_limit must be bigger than or equal to 0"),
            )
            for check_res, txt in checks:
                if not check_res:
                    raise ConanInvalidConfiguration(txt)
        except ValueError as e:
            raise ConanInvalidConfiguration("jerryscript heap size, gc mark limit, stack limit, gc limit should be a positive integer")
        # validate profile file
        if self.options.profile not in self._predefined_profiles and not os.path.isfile(str(self.options.profile)):
            raise ConanInvalidConfiguration("Invalid profile option. Feature profile must either be a valid file or one of these: es.next, es5.1, minimal")
        # validate the use of the system allocator option
        if self.settings.arch == "x86_64" and self.options.system_allocator:
            raise ConanInvalidConfiguration("jerryscript system allocator not available on 64bit systems")
        if self.options.system_allocator and not self.options.cpointer_32_bit:
            raise ConanInvalidConfiguration("jerryscript system allocator must be used with 32 bit pointers")

    def package_id(self):
        if self.options.profile not in self._predefined_profiles:
            self.info.options.profile = tools.load(str(self.options.profile))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        amalgamation_definition = "ENABLE_AMALGAM"
        libmath_definition = "JERRY_MATH"
        if tools.Version(self.version) < tools.Version("2.4.0"):
            amalgamation_definition = "ENABLE_ALL_IN_ONE"
            libmath_definition = "JERRY_LIBM"
        self._cmake.definitions["JERRY_CMDLINE"] = self.options.tool_cmdline
        self._cmake.definitions["JERRY_CMDLINE_TEST"] = self.options.tool_cmdline_test
        self._cmake.definitions["JERRY_CMDLINE_SNAPSHOT"] = self.options.tool_cmdline_snapshot
        self._cmake.definitions["JERRY_PORT_DEFAULT"] = self.options.default_port_implementation
        self._cmake.definitions["JERRY_EXT"] = self.options.jerry_ext
        self._cmake.definitions[libmath_definition] = self._jerry_math
        self._cmake.definitions["ENABLE_STRIP"] = self.options.get_safe("jerry_strip", False)
        self._cmake.definitions["ENABLE_LTO"] = self.options.get_safe("link_time_optimization", False)
        self._cmake.definitions[amalgamation_definition] = self.options.amalgamated
        self._cmake.definitions["JERRY_DEBUGGER"] = self.options.debugger
        self._cmake.definitions["JERRY_LINE_INFO"] = self.options.get_safe("keep_line_info", False)
        self._cmake.definitions["JERRY_PROFILE"] = self.options.profile
        self._cmake.definitions["JERRY_EXTERNAL_CONTEXT"] = self.options.external_context
        self._cmake.definitions["JERRY_SNAPSHOT_EXEC"] = self.options.snapshot_execution
        self._cmake.definitions["JERRY_SNAPSHOT_SAVE"] = self.options.snapshot_saving
        self._cmake.definitions["JERRY_PARSER"] = self.options.parser
        self._cmake.definitions["JERRY_PARSER_DUMP_BYTE_CODE"] = self.options.enable_dump_bytecode
        self._cmake.definitions["JERRY_REGEXP_DUMP_BYTE_CODE"] = self.options.enable_dump_regexp_bytecode
        self._cmake.definitions["JERRY_REGEXP_STRICT_MODE"] = self.options.strict_regexp
        self._cmake.definitions["JERRY_ERROR_MESSAGES"] = self.options.error_messages
        self._cmake.definitions["JERRY_LOGGING"] = self.options.logging
        self._cmake.definitions["JERRY_MEM_STATS"] = self.options.memory_statistics
        self._cmake.definitions["JERRY_GLOBAL_HEAP_SIZE"] = "(%s)" % self.options.heap_size
        self._cmake.definitions["JERRY_GC_LIMIT"] = "(%s)" % self.options.gc_limit
        self._cmake.definitions["JERRY_GC_MARK_LIMIT"] = "(%s)" % self.options.gc_mark_limit
        self._cmake.definitions["JERRY_STACK_LIMIT"] = "(%s)" % self.options.stack_limit
        self._cmake.definitions["JERRY_CPOINTER_32_BIT"] = self.options.cpointer_32_bit
        self._cmake.definitions["JERRY_SYSTEM_ALLOCATOR"] = self.options.system_allocator
        self._cmake.definitions["JERRY_VALGRIND"] = self.options.valgrind
        self._cmake.definitions["JERRY_MEM_GC_BEFORE_EACH_ALLOC"] = self.options.gc_before_each_alloc
        self._cmake.definitions["JERRY_VM_EXEC_STOP"] = self.options.vm_exec_stop
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["libjerry-port-default"].names["pkg_config"] = ["libjerry-port-default"]
        self.cpp_info.components["libjerry-port-default"].libs = ["jerry-port-default"]

        if self._jerry_math:
            mathlibname = "jerry-libm" if tools.Version(self.version) < "2.4.0" else "jerry-math"
            self.cpp_info.components["libjerry-math"].names["pkg_config"] = "lib{}".format(mathlibname)
            self.cpp_info.components["libjerry-math"].libs = [mathlibname]
            self.cpp_info.components["libjerry-math"].requires = ["libjerry-port-default"]
            self.cpp_info.components["libjerry-core"].requires.append("libjerry-math")

        if tools.Version(self.version) < "2.4.0":
            self.cpp_info.components["libjerry-port-default-minimal"].names["pkg_config"] = ["libjerry-port-default-minimal"]
            self.cpp_info.components["libjerry-port-default-minimal"].libs = ["jerry-port-default-minimal"]
            self.cpp_info.components["libjerry-port-default"].requires.append("libjerry-port-default-minimal")

        self.cpp_info.components["libjerry-core"].names["pkg_config"] = "libjerry-core"
        self.cpp_info.components["libjerry-core"].libs = ["jerry-core"]
        # The pc file does not explicitly add the port. But it's needed for the test
        self.cpp_info.components["libjerry-core"].requires = ["libjerry-port-default"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["libjerry-core"].system_libs.append("m")

        self.cpp_info.components["libjerry-ext"].names["pkg_config"] = "libjerry-ext"
        self.cpp_info.components["libjerry-ext"].libs = ["jerry-ext"]
        self.cpp_info.components["libjerry-ext"].requires = ["libjerry-core"]
