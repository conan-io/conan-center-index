from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rename, replace_in_file, rmdir, save
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.52.0"

class Stlab(ConanFile):
    name = 'stlab'
    description = 'The Software Technology Lab libraries.'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/stlab/libraries'
    license = 'BSL-1.0'
    topics = 'conan', 'c++', 'concurrency', 'futures', 'channels'

    settings = "arch", "os", "compiler", "build_type",

    options = {
        "use_boost": [True, False],
        "no_std_coroutines": [True, False],
        "future_coroutines": [True, False],
        "task_system": ["portable", "libdispatch", "emscripten", "pnacl", "windows", "auto"],
        "thread_system": ["win32", "pthread", "pthread-emscripten", "pthread-apple", "none", "auto"],
        # "main_executor": ["qt", "libdispatch", "emscripten", "none", "auto"],
        "test": [True, False],
    }

    default_options = {
        "use_boost": False,
        "no_std_coroutines": False,
        "future_coroutines": False,
        "task_system": "auto",
        "thread_system": "auto",
        "test": False,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    # no_copy_source = True
    # _source_subfolder = 'source_subfolder'

    def _requires_libdispatch(self):
        # On macOS it is not necessary to use the libdispatch conan package, because the library is
        # included in the OS.
        return self.options.task_system == "libdispatch" and self.settings.os != "Macos"

    def build_requirements(self):
        self.build_requires("cmake/3.23.3")

    def requirements(self):
        if self.options.use_boost:
            self.requires("boost/1.75.0")

        if self._requires_libdispatch():
            self.requires("libdispatch/5.3.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

        # extracted_dir = "libraries-" + self.version
        # os.rename(extracted_dir, self.source_folder)

    def _default_task_system(self):
        if self.settings.os == "Macos":
            return "libdispatch"

        if self.settings.os == "Windows":
            return "windows"

        return "portable"

    def _validate_task_system_libdispatch(self):
        if self.settings.os == "Linux":
            if self.settings.compiler != "clang":
                raise ConanInvalidConfiguration("{}/{} task_system=libdispatch needs Clang compiler when using OS: {}. Use Clang compiler or switch to task_system=portable or task_system=auto".format(self.name, self.version, self.settings.os))
        elif self.settings.os != "Macos":
            raise ConanInvalidConfiguration("{}/{} task_system=libdispatch is not supported on {}. Try using task_system=auto".format(self.name, self.version, self.settings.os))

    def _validate_task_system(self):
        if self.options.task_system == "libdispatch":
            self._validate_task_system_libdispatch()
        elif self.options.task_system == "windows":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("{}/{} task_system=windows is not supported on {}. Try using task_system=auto".format(self.name, self.version, self.settings.os))

    def _default_thread_system(self):
        if self.settings.os == "Macos":
            return "pthread-apple"

        if self.settings.os == "Linux":
            return "pthread"

        if self.settings.os == "Windows":
            return "win32"

        if self.settings.os == "Emscripten":
            return "pthread-emscripten"

        return "none"

    def _validate_thread_system(self):
        if self.options.thread_system == "pthread-apple":
            if self.settings.os != "Macos":
                raise ConanInvalidConfiguration("{}/{} thread_system=pthread-apple is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))
        elif self.options.thread_system == "pthread":
            if self.settings.os != "Linux":
                raise ConanInvalidConfiguration("{}/{} thread_system=pthread is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))
        elif self.options.thread_system == "win32":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("{}/{} thread_system=win32 is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))
        elif self.options.thread_system == "pthread-emscripten":
            if self.settings.os != "Emscripten":
                raise ConanInvalidConfiguration("{}/{} thread_system=pthread-emscripten is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))

    def _validate_boost_components(self):
        if self.settings.os != "Macos": return
        if self.settings.compiler != "apple-clang": return
        if Version(self.settings.compiler.version) >= "12": return
        if self.options.use_boost: return
        #
        # On Apple we have to force the usage of boost.variant and boost.optional, because Apple's implementation of C++17
        # is not complete.
        #
        raise ConanInvalidConfiguration("Apple-Clang versions less than 12 do not correctly support std::optional or std::variant, so we will use boost::optional and boost::variant instead. Try -o use_boost=True.")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9":
            raise ConanInvalidConfiguration("Need GCC >= 9")

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "8":
            raise ConanInvalidConfiguration("Need Clang >= 8")

        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) < "15.8":
            raise ConanInvalidConfiguration("Need Visual Studio >= 2017 15.8 (MSVC 19.15)")

        # Actually, we want *at least* 15.8 (MSVC 19.15), but we cannot check this for now with Conan.
        if self.settings.compiler == "msvc" and Version(self.settings.compiler.version) < "19.15":
            raise ConanInvalidConfiguration("Need msvc >= 19.15")

        self._validate_task_system()
        self._validate_thread_system()
        self._validate_boost_components()

    def configure(self):
        if self.options.task_system == "auto":
            self.options.task_system = self._default_task_system()

        if self.options.thread_system == "auto":
            self.options.thread_system = self._default_thread_system()

        self.output.info("STLab Use Boost: {}.".format(self.options.use_boost))
        self.output.info("STLab Future Coroutines: {}.".format(self.options.future_coroutines))
        self.output.info("STLab No Standard Coroutines: {}.".format(self.options.no_std_coroutines))
        self.output.info("STLab Task System: {}.".format(self.options.task_system))
        self.output.info("STLab Thread System: {}.".format(self.options.thread_system))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = self.options.test
        tc.variables["STLAB_USE_BOOST_CPP17_SHIMS"] = self.options.use_boost
        tc.variables["STLAB_NO_STD_COROUTINES"] = self.options.no_std_coroutines
        tc.variables["STLAB_THREAD_SYSTEM"] = self.options.thread_system
        tc.variables["STLAB_TASK_SYSTEM"] = self.options.task_system

        # # If main_executor == "auto" it will be detected by CMake scripts
        # if self.options.main_executor != "auto":
        #     tc.variables["STLAB_MAIN_EXECUTOR"] = self.options.main_executor

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # self.copy("*LICENSE", dst="licenses", keep_path=False)
        # self.copy("stlab/*", src=self.source_folder, dst='include/')
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        # self.info.header_only()
        self.info.options.use_boost = "ANY"
        self.info.options.test = "ANY"

    def package_info(self):
        future_coroutines_value = 1 if self.options.future_coroutines else 0

        self.cpp_info.defines = [
            'STLAB_FUTURE_COROUTINES={}'.format(future_coroutines_value)
        ]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
