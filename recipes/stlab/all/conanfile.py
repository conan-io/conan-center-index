from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import check_min_vs, is_msvc

import os

required_conan_version = ">=1.52.0"

class Stlab(ConanFile):
    name = 'stlab'
    description = 'The Software Technology Lab libraries.'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/stlab/libraries'
    license = 'BSL-1.0'
    topics = 'concurrency', 'futures', 'channels'

    settings = "arch", "os", "compiler", "build_type",

    options = {
        "with_boost": [True, False],
        "no_std_coroutines": [True, False],
        "future_coroutines": [True, False],
        "task_system": ["portable", "libdispatch", "emscripten", "pnacl", "windows", "auto"],
        "thread_system": ["win32", "pthread", "pthread-emscripten", "pthread-apple", "none", "auto"],
    }

    default_options = {
        "with_boost": False,
        "no_std_coroutines": True,          #TODO: how to make checks similar to what are made in Cmake https://github.com/stlab/libraries/blob/main/cmake/StlabUtil.cmake#L35
        "future_coroutines": False,
        "task_system": "auto",
        "thread_system": "auto",
    }

    short_paths = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "9",
                "Visual Studio": "15.8",
                "clang": "8",
                "apple-clang": "13",
                }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _requires_libdispatch(self):
        # On macOS it is not necessary to use the libdispatch conan package, because the library is
        # included in the OS.
        return self.options.task_system == "libdispatch" and self.settings.os != "Macos"

    def build_requirements(self):
        self.build_requires("cmake/3.23.3")

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.80.0")

        if self._requires_libdispatch():
            self.requires("libdispatch/5.3.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def _default_task_system(self):
        if self.settings.os == "Macos":
            return "libdispatch"

        if self.settings.os == "Windows":
            return "windows"

        return "portable"

    def _validate_task_system_libdispatch(self):
        if self.settings.os == "Linux":
            if self.settings.compiler != "clang":
                raise ConanInvalidConfiguration(f"{self.ref} task_system=libdispatch needs Clang compiler when using OS: {self.settings.os}. Use Clang compiler or switch to task_system=portable or task_system=auto")
        elif self.settings.os != "Macos":
            raise ConanInvalidConfiguration(f"{self.ref} task_system=libdispatch is not supported on {self.settings.os}. Try using task_system=auto")

    def _validate_task_system(self):
        if self.options.task_system == "libdispatch":
            self._validate_task_system_libdispatch()
        elif self.options.task_system == "windows":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration(f"{self.ref} task_system=windows is not supported on {self.settings.os}. Try using task_system=auto")

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
        if self.options.thread_system == "pthread-apple" and self.settings.os != "Macos":
                raise ConanInvalidConfiguration("{}/{} thread_system=pthread-apple is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))
        elif self.options.thread_system == "pthread" and self.settings.os != "Linux":
                raise ConanInvalidConfiguration("{}/{} thread_system=pthread is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))
        elif self.options.thread_system == "win32" and self.settings.os != "Windows":
                raise ConanInvalidConfiguration("{}/{} thread_system=win32 is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))
        elif self.options.thread_system == "pthread-emscripten" and self.settings.os != "Emscripten":
                raise ConanInvalidConfiguration("{}/{} thread_system=pthread-emscripten is not supported on {}. Try using thread_system=auto".format(self.name, self.version, self.settings.os))

    def _validate_boost_components(self):
        if self.settings.os != "Macos": return
        if self.settings.compiler != "apple-clang": return
        if Version(self.settings.compiler.version) >= "12": return
        if self.options.with_boost: return
        #
        # On Apple we have to force the usage of boost.variant and boost.optional, because Apple's implementation of C++17
        # is not complete.
        #
        raise ConanInvalidConfiguration(f"Apple-Clang versions less than 12 do not correctly support std::optional or std::variant, so we will use boost::optional and boost::variant instead. Try -o {self.name}:with_boost=True.")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        def _lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        check_min_vs(self, "192")
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if not minimum_version:
                self.output.warn(f"{self.name} {self.version} requires C++20. Your compiler is unknown. Assuming it supports C++20.")
            elif _lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
                raise ConanInvalidConfiguration(f"{self.name} {self.version} requires C++20, which your compiler does not support.")
            if self.info.settings.compiler == "clang" and str(self.info.settings.compiler.version) in ("13", "14"):
                raise ConanInvalidConfiguration(f"{self.ref} currently does not work with Clang {self.info.settings.compiler.version} on CCI, it enters in an infinite build loop (smells like a compiler bug). Contributions are welcomed!")

        self._validate_task_system()
        self._validate_thread_system()
        self._validate_boost_components()

    def configure(self):
        if self.options.task_system == "auto":
            self.options.task_system = self._default_task_system()

        if self.options.thread_system == "auto":
            self.options.thread_system = self._default_thread_system()

        self.output.info("STLab With Boost: {}.".format(self.options.with_boost))
        self.output.info("STLab Future Coroutines: {}.".format(self.options.future_coroutines))
        self.output.info("STLab No Standard Coroutines: {}.".format(self.options.no_std_coroutines))
        self.output.info("STLab Task System: {}.".format(self.options.task_system))
        self.output.info("STLab Thread System: {}.".format(self.options.thread_system))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        tc.variables['BUILD_TESTING'] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.variables["STLAB_USE_BOOST_CPP17_SHIMS"] = self.options.with_boost
        tc.variables["STLAB_NO_STD_COROUTINES"] = self.options.no_std_coroutines
        tc.variables["STLAB_THREAD_SYSTEM"] = self.options.thread_system
        tc.variables["STLAB_TASK_SYSTEM"] = self.options.task_system

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        #TODO: is header only but needs a header modified by cmake
        # self.info.settings.clear()
        # self.info.header_only()
        pass

    def package_info(self):
        future_coroutines_value = 1 if self.options.future_coroutines else 0

        self.cpp_info.defines = [
            'STLAB_FUTURE_COROUTINES={}'.format(future_coroutines_value)
        ]

        if self.settings.os == "Windows":
            self.cpp_info.defines = ['NOMINMAX']

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
