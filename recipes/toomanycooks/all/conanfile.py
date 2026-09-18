from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=2.10"

class ToomanycooksConan(ConanFile):
    name = "toomanycooks"
    description = "The C++20 coroutine framework with no compromises. Excellent performance, simple syntax, and powerful features."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tzcnt/TooManyCooks"
    topics = ("tasking",
              "coroutine",
              "thread-pool",
              "i/o",
              "work-stealing",
              "lockfree",
              "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        # Dependency Options
        "with_hwloc": [True, False],
        "with_asio": [None, "standalone", "boost"],

        # Configs
        "work_item": ["CORO", "FUNCORO"],
        "trivial_task": [True, False],
        "nodiscard_await": [True, False],
        "priority_count": [None,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
        "more_threads": [True, False],
        "debug_task_alloc_count": [True, False],
        "debug_thread_creation": [True, False],

        # Build Modes - by default (both False), the library is header-only
        "standalone_compilation": [True, False],
        "windows_dll": [True, False],
    }
    default_options = {
        "with_hwloc": True,
        "with_asio": None,
        "work_item": "CORO",
        "trivial_task": False,
        "nodiscard_await": False,
        "priority_count": None,
        "more_threads": False,
        "debug_task_alloc_count": False,
        "debug_thread_creation": False,
        "standalone_compilation": False,
        "windows_dll": False,
    }
    options_description = {
        "with_hwloc": "See documentation for TMC_USE_HWLOC",
        "with_asio": "allows you to add standalone asio or boost::asio as an optional dependency",
        "work_item": "See documentation for TMC_WORK_ITEM",
        "trivial_task": "See documentation for TMC_TRIVIAL_TASK",
        "nodiscard_await": "See documentation for TMC_NODISCARD_AWAIT",
        "priority_count": "See documentation for TMC_PRIORITY_COUNT",
        "more_threads": "See documentation for TMC_MORE_THREADS",
        "debug_task_alloc_count": "See documentation for TMC_DEBUG_TASK_ALLOC_COUNT",
        "debug_thread_creation": "See documentation for TMC_DEBUG_THREAD_CREATION",
        "standalone_compilation": "See documentation for TMC_STANDALONE_COMPILATION",
        "windows_dll": "See documentation for TMC_WINDOWS_DLL",
    }

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.windows_dll

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "17",
            "clang": "17",
            "gcc": "14",
        }

    def requirements(self):
        if self.options.with_hwloc:
            self.requires("hwloc/[>=2.4]", transitive_headers=True, transitive_libs=True)
        if self.options.with_asio == "standalone":
            self.requires("asio/[>=1.28 <2]", transitive_headers=True)
        if self.options.with_asio == "boost":
            self.requires(f"boost/[>=1.84]", transitive_headers=True)

    def validate(self):
        if self.options.get_safe("windows_dll", False) and not self.options.standalone_compilation:
            raise ConanInvalidConfiguration("windows_dll requires standalone_compilation=True")
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration(
                "TooManyCooks is currently unsupported with MSVC due to a compiler bug: "
                "https://developercommunity.visualstudio.com/t/MSVC-incorrectly-caches-thread_local-var/11041371"
            )
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def layout(self):
        basic_layout(self)

    def package_id(self):
        self.info.settings.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=self.source_folder, dst=self.package_folder)
        copy(self, "*.ipp", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "TooManyCooks")
        self.cpp_info.set_property("cmake_target_name", "TooManyCooks::TooManyCooks")

        if self.options.with_hwloc:
            self.cpp_info.defines.append("TMC_USE_HWLOC")
        if self.options.with_asio == "boost":
            self.cpp_info.defines.append("TMC_USE_BOOST_ASIO")
        if self.options.work_item == "FUNCORO":
            self.cpp_info.defines.append("TMC_WORK_ITEM=FUNCORO")
        if self.options.trivial_task:
            self.cpp_info.defines.append("TMC_TRIVIAL_TASK")
        if self.options.nodiscard_await:
            self.cpp_info.defines.append("TMC_NODISCARD_AWAIT")
        if self.options.priority_count != None:
            self.cpp_info.defines.append(f"TMC_PRIORITY_COUNT={self.options.priority_count}")
        if self.options.more_threads:
            self.cpp_info.defines.append("TMC_MORE_THREADS")
        if self.options.debug_task_alloc_count:
            self.cpp_info.defines.append("TMC_DEBUG_TASK_ALLOC_COUNT")
        if self.options.debug_thread_creation:
            self.cpp_info.defines.append("TMC_DEBUG_THREAD_CREATION")
        if self.options.standalone_compilation and not self.options.get_safe("windows_dll", False):
            self.cpp_info.defines.append("TMC_STANDALONE_COMPILATION")
        if self.options.get_safe("windows_dll", False):
            self.cpp_info.defines.append("TMC_WINDOWS_DLL")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
