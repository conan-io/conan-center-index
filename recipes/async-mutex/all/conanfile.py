import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class AsyncMutexConan(ConanFile):
    name = "async-mutex"
    description = (
        "Awaitable, header-only, Asio-based asynchronous mutex for C++23 coroutines."
    )
    license = "AGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CatalinSerafimescu/async_mutex"
    topics = ("mutex", "async", "coroutines", "asio", "concurrency", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 23

    @property
    def _compilers_minimum_version(self):
        # C++23 floors — the binding features are std::expected and coroutines.
        #   gcc 12   : libstdc++ shipped <expected> in GCC 12.
        #   clang 17 : libc++ first shipped <expected> in 16, but it is only
        #              reliably complete from 17 (this header stores a move-only
        #              value in std::expected); a reviewer may lower to 16.
        #   apple-clang 16 : Apple's libc++ lags; <expected> is not complete
        #              before Xcode 16.
        #   msvc 193 : MSVC STL shipped <expected> in VS 2022 17.3 (_MSC_VER 1933).
        # Only clang 22 / gcc 13 are exercised in our CI (macOS uses Homebrew
        # LLVM, not apple-clang); these floors are researched, not all locally
        # built — CCI's CI matrix is the real gate and reviewers may tune them.
        return {
            "gcc": "12",
            "clang": "17",
            "apple-clang": "16",
            "msvc": "193",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # transitive_headers: the public header #includes <asio/...>, so any
        # consumer must see Asio's include dirs at compile time.
        # Range floor 1.26 is the lowest asio that compiles this header (1.24
        # lacks asio::awaitable/use_awaitable_t as used here); verified locally.
        # A range (not an exact pin) lets a consumer that also pins asio itself
        # — e.g. fixpp on 1.38.0 — resolve without a diamond conflict.
        self.requires("asio/[>=1.26 <2]", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum and Version(self.settings.compiler.version) < minimum:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which needs "
                f"{self.settings.compiler} >= {minimum} "
                f"(have {self.settings.compiler.version})."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        pass

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Match the in-tree CMake package so `find_package` consumers (e.g.
        # fixpp) keep linking the exact target the repo advertises.
        self.cpp_info.set_property("cmake_file_name", "catseraf-async-mutex")
        self.cpp_info.set_property("cmake_target_name", "catseraf::async_mutex")
        self.cpp_info.requires = ["asio::asio"]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")
