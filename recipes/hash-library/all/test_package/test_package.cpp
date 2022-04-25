#include "crc32.h"
#include "keccak.h"
#include "md5.h"
#include "sha1.h"
#include "sha256.h"
#include "sha3.h"

int main(void) {
    if (CRC32()("abc") != "352441c2") { 
        return 1;
    }
    if (Keccak()("abc") != "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45") {
        return 2;
    }
    if (MD5()("abc") != "900150983cd24fb0d6963f7d28e17f72") {
        return 3;
    }
    if (SHA1()("abc") != "a9993e364706816aba3e25717850c26c9cd0d89d") {
        return 4;
    }
    if (SHA256()("abc") != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") {
        return 5;
    }
    if (SHA3()("abc") != "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532") {
        return 6;
    }

    return 0;
}
