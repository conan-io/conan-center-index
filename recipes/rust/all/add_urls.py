#!/bin/env python
# Usage: ./add_urls.py <rust_version>
# The output is written to urls-<rust_version>.yml

import sys
from pathlib import Path
from time import sleep

import requests
import yaml

script_dir = Path(__file__).resolve().parent

# The subset of `rustc --print target-list` that has a stdlib binary available.
target_list = [
    "aarch64-apple-darwin",
    "aarch64-apple-ios-sim",
    "aarch64-apple-ios",
    "aarch64-linux-android",
    "aarch64-pc-windows-gnullvm",
    "aarch64-pc-windows-msvc",
    "aarch64-unknown-fuchsia",
    "aarch64-unknown-linux-gnu",
    "aarch64-unknown-linux-musl",
    "aarch64-unknown-linux-ohos",
    "aarch64-unknown-none-softfloat",
    "aarch64-unknown-none",
    "aarch64-unknown-uefi",
    "arm-linux-androideabi",
    "arm-unknown-linux-gnueabi",
    "arm-unknown-linux-gnueabihf",
    "arm-unknown-linux-musleabi",
    "arm-unknown-linux-musleabihf",
    "armebv7r-none-eabi",
    "armebv7r-none-eabihf",
    "armv5te-unknown-linux-gnueabi",
    "armv5te-unknown-linux-musleabi",
    "armv7-linux-androideabi",
    "armv7-unknown-linux-gnueabi",
    "armv7-unknown-linux-gnueabihf",
    "armv7-unknown-linux-musleabi",
    "armv7-unknown-linux-musleabihf",
    "armv7-unknown-linux-ohos",
    "armv7a-none-eabi",
    "armv7r-none-eabi",
    "armv7r-none-eabihf",
    "i586-pc-windows-msvc",
    "i586-unknown-linux-gnu",
    "i586-unknown-linux-musl",
    "i686-linux-android",
    "i686-pc-windows-gnu",
    "i686-pc-windows-msvc",
    "i686-unknown-freebsd",
    "i686-unknown-linux-gnu",
    "i686-unknown-linux-musl",
    "i686-unknown-uefi",
    "loongarch64-unknown-linux-gnu",
    "loongarch64-unknown-none-softfloat",
    "loongarch64-unknown-none",
    "nvptx64-nvidia-cuda",
    "powerpc-unknown-linux-gnu",
    "powerpc64-unknown-linux-gnu",
    "powerpc64le-unknown-linux-gnu",
    "riscv32i-unknown-none-elf",
    "riscv32im-unknown-none-elf",
    "riscv32imac-unknown-none-elf",
    "riscv32imc-unknown-none-elf",
    "riscv64gc-unknown-linux-gnu",
    "riscv64gc-unknown-none-elf",
    "riscv64imac-unknown-none-elf",
    "s390x-unknown-linux-gnu",
    "sparc64-unknown-linux-gnu",
    "sparcv9-sun-solaris",
    "thumbv6m-none-eabi",
    "thumbv7em-none-eabi",
    "thumbv7em-none-eabihf",
    "thumbv7m-none-eabi",
    "thumbv7neon-linux-androideabi",
    "thumbv7neon-unknown-linux-gnueabihf",
    "thumbv8m.base-none-eabi",
    "thumbv8m.main-none-eabi",
    "thumbv8m.main-none-eabihf",
    "wasm32-unknown-emscripten",
    "wasm32-unknown-unknown",
    "wasm32-wasi",
    "x86_64-apple-darwin",
    "x86_64-apple-ios",
    "x86_64-fortanix-unknown-sgx",
    "x86_64-linux-android",
    "x86_64-pc-solaris",
    "x86_64-pc-windows-gnu",
    "x86_64-pc-windows-gnullvm",
    "x86_64-pc-windows-msvc",
    "x86_64-unknown-freebsd",
    "x86_64-unknown-fuchsia",
    "x86_64-unknown-illumos",
    "x86_64-unknown-linux-gnu",
    "x86_64-unknown-linux-gnux32",
    "x86_64-unknown-linux-musl",
    "x86_64-unknown-netbsd",
    "x86_64-unknown-none",
    "x86_64-unknown-redox",
    "x86_64-unknown-uefi",
]


def get_hash(url):
    sha_url = f"{url}.sha256"
    response = requests.get(sha_url)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text.split()[0].strip()


def get_url_dict(version):
    url_dict = {"rustc": {}, "stdlib": {}}
    for target in target_list:
        url = f"https://static.rust-lang.org/dist/rust-{version}-{target}.tar.gz"
        hash = get_hash(url)
        if hash:
            url_dict["rustc"][target] = {
                "url": url,
                "sha256": get_hash(url),
            }
            print(f"{url}: {hash}")
        else:
            print(f"{url}: Not found")
        sleep(0.1)
    for target in target_list:
        url = f"https://static.rust-lang.org/dist/rust-std-{version}-{target}.tar.gz"
        hash = get_hash(url)
        if hash:
            url_dict["stdlib"][target] = {
                "url": url,
                "sha256": get_hash(url),
            }
            print(f"{url}: {hash}")
        else:
            print(f"{url}: Not found")
        sleep(0.1)
    return url_dict


if __name__ == "__main__":
    rust_version = sys.argv[1] if len(sys.argv) > 1 else None
    url_dict = get_url_dict(rust_version)
    with (script_dir / f"urls-{rust_version}.yml").open("w") as f:
        yaml.dump(url_dict, f)
