import os
import os.path
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

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
        "gc_limit": range(8193),
        "gc_mark_limit": "ANY",
        "stack_limit": "ANY",
        "cpointer_32_bit": [True, False],
        "system_allocator": [True, False],
        "valgrind": [True, False],
        "gc_before_each_alloc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "amalgamated": False,
        "debugger": False,
        "keep_line_info": False,
        "profile": "es.next",
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
    }
    generators = "cmake"
    short_paths = True

    _cmake = None
    predefined_profiles = ["es.next", "es5.1", "minimal"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
    
    def package_id(self):
        if not self.options.profile in self.predefined_profiles
            with open(self.options.profile, "r") as profile_file
                self.info.options.profile = profile_file.read()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

        if not self.options.debugger:
            del self.options.keep_line_info
        if (not self.options.profile in self.predefined_profiles) and not os.path.isfile(self.options.profile):
            raise ConanInvalidConfiguration("jerryscript feature profile must either be a valid file or one of these: es.next, es5.1, minimal")
        try:
            assert(int(self.options.heap_size) >= 0), "must be bigger than or equal to 0"
            assert(int(self.options.gc_mark_limit) >= 0), "must be bigger than or equal to 0"
            assert(int(self.options.stack_limit) >= 0), "must be bigger than or equal to 0"
        except:
            raise ConanInvalidConfiguration("jerryscript heap size, gc mark limit, stack limit should be a positive integer")
        if self.settings.arch == "x86_64":
            self.options.system_allocator = False
        if self.options.system_allocator:
            self.options.cpointer_32_bit = True

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("jerryscript shared lib is not yet supported under windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JERRY_CMDLINE"] = False
        self._cmake.definitions["ENABLE_LTO"] = False
        self._cmake.definitions["ENABLE_AMALGAM"] = self.options.amalgamated
        self._cmake.definitions["JERRY_DEBUGGER"] = self.options.debugger
        self._cmake.definitions["JERRY_LINE_INFO"] = self.options.keep_line_info
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
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
