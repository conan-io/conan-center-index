import os
import shutil
import subprocess
import time

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.files import copy

required_conan_version = ">=1.50.0"  # openjdk pattern: conan.tools API + conandata.yml


class PwaosSdkConan(ConanFile):
    name = "pwaos_sdk"
    # No `version` attribute: CCI's build service injects the version via
    # `--version=X` from config.yml (local flows must pass it too).
    description = (
        "pwaOS runtime client SDK: stable C ABI header, client import "
        "library (libpwaos_runtime_api), and the pwaos_server runtime bundle"
    )
    # LICENSE in the SDK tree is the standard MIT permission notice; the
    # upstream GitHub repository is likewise detected as MIT.
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/daqingzd/pwaos"
    topics = ("pwa", "runtime", "chromium", "webview", "pwaos", "browser")
    settings = "os", "arch", "compiler", "build_type"
    # The SDK ships prebuilt binaries fetched from the upstream git branches
    # (same scheme as the openjdk recipe: build_policy missing + upload skip;
    # no compilation happens in this recipe).
    build_policy = "missing"
    upload_policy = "skip"
    package_type = "shared-library"

    options = {"with_runtime": [True, False]}
    default_options = {"with_runtime": True}

    def package_id(self):
        # Prebuilt binaries: identical artifact regardless of the consumer's
        # compiler or build type (openjdk recipe pattern).
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        # Branch availability: conandata.yml keys are "{os}_{arch}".
        if self._artifact_key not in self.conan_data["sources"][self.version]:
            raise ConanInvalidConfiguration(
                f"pwaos_sdk/{self.version} has no SDK branch for "
                f"{self.settings.os}/{self.settings.arch}"
            )

    @property
    def _artifact_key(self):
        # conandata.yml keys: Linux_x86_64, Windows_x86 today; extend when
        # upstream publishes more SDK branches.
        return f"{self.settings.os}_{self.settings.arch}"

    def layout(self):
        # Non-buildable package: give local flows a sane layout.
        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = "build/generators"

    def source(self):
        # Prebuilt binary recipe (openjdk pattern): no settings access here
        # (source() is settings-independent); the SDK branch is fetched in
        # build() with the os/arch key.
        pass

    def build(self):
        # Fetch the SDK branch fresh on every run. git ls-remote resolves the
        # current tip on GitHub first, so every create picks up the newest
        # push (force update; no Conan download cache or release asset in
        # between). The per-os/arch branch name comes from conandata.yml.
        entry = self.conan_data["sources"][self.version][self._artifact_key]
        self._fetch_sdk_branch(entry["branch"])

    def _fetch_sdk_branch(self, branch):
        repo = self.conan_data["repository"]
        dest = os.path.join(self.build_folder, "sdk")
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        os.makedirs(dest)
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")

        def git(*args, timeout=None, cwd=None, env_extra=None):
            cmd = ["git", *args]
            run_env = dict(env, **env_extra) if env_extra else env
            try:
                res = subprocess.run(cmd, cwd=cwd, env=run_env, check=True,
                                     capture_output=True, text=True,
                                     timeout=timeout)
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or exc.stdout or "").strip()[-500:]
                raise ConanException(
                    f"{' '.join(cmd)} failed (exit {exc.returncode}): {detail}"
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise ConanException(
                    f"{' '.join(cmd)} timed out after {timeout}s "
                    f"(GitHub unreachable?)"
                ) from exc
            return res.stdout

        # 1. Resolve the branch tip on GitHub every single run: this is what
        #    makes every build fetch the newest push instead of replaying a
        #    cached or pinned copy. GitHub connectivity from build boxes is
        #    often intermittent, so every network step retries.
        commit = self._git_retry(
            git, "ls-remote", repo, f"refs/heads/{branch}",
            what=f"resolving branch {branch}", timeout=180).split()
        if not commit:
            raise ConanException(f"branch '{branch}' not found in {repo}")
        commit = commit[0]

        # 2. Shallow-fetch exactly that commit: no history, no other refs.
        #    (git ls-remote + fetch of a raw commit never triggers a
        #    credential prompt for a public repo, but GIT_TERMINAL_PROMPT=0
        #    is set anyway so a private/renamed repo fails fast instead of
        #    hanging the build.)
        git("-c", "core.autocrlf=false", "init", cwd=dest, timeout=60)
        git("remote", "add", "origin", repo, cwd=dest, timeout=60)
        # Abort stalled transfers (bytes/s, seconds) instead of hanging.
        # -c key=value must precede the subcommand (git exits 129 otherwise).
        self._git_retry(git, "-c", "http.lowSpeedLimit=1000",
                        "-c", "http.lowSpeedTime=120",
                        "fetch", "--depth", "1", "origin", commit,
                        cwd=dest, what="fetching SDK branch", timeout=3600)
        # Checkout with the LFS smudge filter disabled: otherwise checkout
        # itself downloads the ~112 MB object inline (and can blow any sane
        # timeout). The explicit, retried `git lfs pull` below materializes
        # the objects instead.
        git("checkout", "--force", "--detach", "FETCH_HEAD", cwd=dest,
            timeout=120, env_extra={"GIT_LFS_SKIP_SMUDGE": "1"})

        # 3. Materialize Git LFS objects: runtime/pwaos_server (Linux) and
        #    runtime/pwaos_server.exe (Windows) are LFS pointers inside the
        #    branches; the real ~112 MB binaries live on the LFS server.
        self._git_retry(git, "lfs", "pull", cwd=dest,
                        what="pulling Git LFS objects", timeout=3600)

        # 4. Defensive check: no LFS pointer may survive (a 134-byte pointer
        #    where a 112 MB binary belongs would ship a broken runtime).
        #    git lfs ls-files marks materialized files with '+' and still-
        #    pointer files with '-'.
        pointers = [line for line in
                    git("lfs", "ls-files", cwd=dest, timeout=120).splitlines()
                    if line.startswith("-")]
        if pointers:
            raise ConanException(
                "Git LFS objects were not materialized for: "
                + ", ".join(p.split()[-1] for p in pointers))

    @staticmethod
    def _git_retry(git_fn, *args, **kwargs):
        # 3 attempts with backoff: rides out GitHub's intermittent slow
        # phases; each attempt is safe to re-run (fetch/lfs pull are
        # idempotent against a partially populated object store).
        what = kwargs.pop("what", "git operation")
        timeout = kwargs.pop("timeout", None)
        last_error = None
        for attempt in range(3):
            try:
                return git_fn(*args, timeout=timeout, **kwargs)
            except ConanException as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
        raise ConanException(f"{what} failed after 3 attempts: {last_error}")

    def package(self):
        src = os.path.join(self.build_folder, "sdk")
        # C ABI header.
        copy(self, "*.h", src=os.path.join(src, "include"),
             dst=os.path.join(self.package_folder, "include"))
        # Client import library, per OS (branches use lib/linux vs lib/win;
        # Windows artifacts carry no "lib" prefix, the Linux .so does).
        lib_subdir = "win" if self.settings.os == "Windows" else "linux"
        if self.settings.os == "Windows":
            copy(self, "pwaos_runtime_api.dll",
                 src=os.path.join(src, "lib", lib_subdir),
                 dst=os.path.join(self.package_folder, "lib"))
            # MSVC links against the import library shipped next to the DLL.
            copy(self, "pwaos_runtime_api.lib",
                 src=os.path.join(src, "lib", lib_subdir),
                 dst=os.path.join(self.package_folder, "lib"))
        else:
            copy(self, "libpwaos_runtime_api.so",
                 src=os.path.join(src, "lib", lib_subdir),
                 dst=os.path.join(self.package_folder, "lib"))
        # Docs + licensing metadata (RELEASE_NOTES.md exists on the linux
        # branch only, hence the isfile guard).
        for f in ("README.md", "RELEASE_NOTES.md", "LICENSE"):
            if os.path.isfile(os.path.join(src, f)):
                copy(self, f, src=src,
                     dst=os.path.join(self.package_folder, "licenses"))
        # Optional heavy artifacts.
        if self.options.with_runtime:
            copy(self, "*", src=os.path.join(src, "runtime"),
                 dst=os.path.join(self.package_folder, "runtime"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pwaos_sdk")
        self.cpp_info.set_property("cmake_target_name", "pwaos::sdk")
        self.cpp_info.set_property("pkg_config_name", "pwaos_runtime_api")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["pwaos_runtime_api"]
        # pwaos_server is spawned by the client library; tell consumers where
        # the bundled runtime lives (unset when with_runtime=False).
        if self.options.with_runtime:
            runtime_dir = os.path.join(self.package_folder, "runtime")
            self.cpp_info.set_property("pwaos:runtime_dir", runtime_dir)
            self.buildenv_info.define_path("PWAOS_RUNTIME_DIR", runtime_dir)
            self.runenv_info.define_path("PWAOS_RUNTIME_DIR", runtime_dir)
            # TODO: remove `env_info` once the recipe is only compatible with
            # Conan >= 2.0 (no-op mock on 2.x; required by 1.x legacy flows).
            self.env_info.PWAOS_RUNTIME_DIR = runtime_dir
        else:
            # with_runtime=False: define_path would still bake the (missing)
            # package runtime path into the env; keep it unset instead.
            self.buildenv_info.define("PWAOS_RUNTIME_DIR", "")
            self.runenv_info.define("PWAOS_RUNTIME_DIR", "")
