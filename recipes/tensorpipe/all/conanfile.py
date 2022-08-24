from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class TensorpipeConan(ConanFile):
    name = "tensorpipe"
    description = "The TensorPipe project provides a tensor-aware channel to " \
                  "transfer rich objects from one process to another while " \
                  "using the fastest transport for the tensors contained " \
                  "therein (e.g., CUDA device-to-device copy)."
    license = "BSD-3-Clause"
    topics = ("tensorpipe", "tensor", "cuda")
    homepage = "https://github.com/pytorch/tensorpipe"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cuda": [True, False],
        "cuda_ipc": [True, False],
        "ibv": [True, False],
        "shm": [True, False],
        "cma": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cuda": False,
        "cuda_ipc": True,
        "ibv": True,
        "shm": True,
        "cma": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "pkg_config"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.ibv
            del self.options.shm
            del self.options.cma

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cuda:
            del self.options.cuda_ipc

    def requirements(self):
        self.requires("libnop/cci.20200728")
        self.requires("libuv/1.42.0")
        if self.options.cuda:
            raise ConanInvalidConfiguration("cuda recipe not yet available in CCI")
            self.requires("cuda/11.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 14)
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("tensorpipe doesn't support Windows")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TP_USE_CUDA"] = self.options.cuda
        self._cmake.definitions["TP_ENABLE_IBV"] = self.options.get_safe("ibv", False)
        self._cmake.definitions["TP_ENABLE_SHM"] = self.options.get_safe("shm", False)
        self._cmake.definitions["TP_ENABLE_CMA"] = self.options.get_safe("cma", False)
        self._cmake.definitions["TP_ENABLE_CUDA_IPC"] = self.options.get_safe("cuda_ipc", False)
        self._cmake.definitions["TP_BUILD_BENCHMARK"] = False
        self._cmake.definitions["TP_BUILD_PYTHON"] = False
        self._cmake.definitions["TP_BUILD_TESTING"] = False
        self._cmake.definitions["TP_BUILD_LIBUV"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        with tools.run_environment(self):
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        with tools.run_environment(self):
            cmake = self._configure_cmake()
            cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"tensorpipe": "Tensorpipe::Tensorpipe"},
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Tensorpipe")
        self.cpp_info.set_property("cmake_target_name", "tensorpipe")
        self.cpp_info.libs = ["tensorpipe"]
        if tools.apple.is_apple_os(self, self.settings.os):
            self.cpp_info.frameworks = ["CoreFoundation", "IOKit"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Tensorpipe"
        self.cpp_info.names["cmake_find_package_multi"] = "Tensorpipe"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
