import os
import shutil

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir

required_conan_version = ">=2.0.9"


class FastDDSPythonConan(ConanFile):
    name = "fast-dds-python"
    description = "Python bindings for eProsima Fast DDS, generated with SWIG"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eProsima/Fast-DDS-python"
    topics = ("dds", "middleware", "ipc", "python", "swig")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    # The SWIG extension module loads the fastdds library dynamically at
    # import time; linking a static fastdds into the extension is not
    # supported upstream.
    default_options = {
        "fast-dds/*:shared": True,
        "fast-cdr/*:shared": True,
    }

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        # Fast DDS <-> Fast DDS python version pairing follows the upstream
        # RELEASE_SUPPORT.md (e.g. the 2.4.x bindings track fast-dds 3.4.x).
        self.requires(f"fast-dds/{self.conan_data['fastdds_versions'][self.version]}")

    def validate(self):
        check_min_cppstd(self, 11)
        if not self.dependencies["fast-dds"].options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires fast-dds to be built as a shared library"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <5]")
        self.tool_requires("swig/4.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # The SWIG moduleimport preamble references $<TARGET_FILE_NAME:fastdds>,
        # which cannot be evaluated when fastdds is an imported target coming
        # from CMakeDeps. Strip the preamble; the loader finds fastdds through
        # the environment instead.
        replace_in_file(
            self,
            os.path.join(self.source_folder, "fastdds_python", "src", "swig", "fastdds.i"),
            "moduleimport=\"if __import__('os').name == 'nt': import win32api; win32api.LoadLibrary('$<TARGET_FILE_NAME:fastdds>')",
            'moduleimport="',
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="fastdds_python")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        self._relocate_python_module()

    def _relocate_python_module(self):
        # Upstream installs the module into the build interpreter's purelib
        # layout relative to the prefix (lib/pythonX.Y/site-packages, or
        # local/lib/pythonX.Y/dist-packages on Debian-patched interpreters).
        # Relocate it to a stable path so package_info() does not depend on
        # the build machine's Python layout.
        target_root = os.path.join(self.package_folder, "lib", "python")
        for root, _, files in os.walk(self.package_folder):
            if os.path.basename(root) == "fastdds" and "__init__.py" in files:
                origin_parent = os.path.dirname(root)
                if os.path.normpath(origin_parent) == os.path.normpath(target_root):
                    return
                os.makedirs(target_root, exist_ok=True)
                shutil.move(root, os.path.join(target_root, "fastdds"))
                # prune the emptied original directory chain
                while (
                    os.path.normpath(origin_parent) != os.path.normpath(self.package_folder)
                    and not os.listdir(origin_parent)
                ):
                    os.rmdir(origin_parent)
                    origin_parent = os.path.dirname(origin_parent)
                return
        raise ConanException("fastdds python module not found in the package folder")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.runenv_info.prepend_path(
            "PYTHONPATH", os.path.join(self.package_folder, "lib", "python")
        )
