#include <cstdlib>

#include <asmtk/asmtk.h>
#include <asmjit/asmjit.h>


int main(void) {
    asmjit::Environment env(asmjit::Arch::kX64);
    asmjit::CodeHolder code;
    code.init(env);

    asmjit::x86::Assembler assembler(&code);
    asmtk::AsmParser parser(&assembler);
    parser.parse(
    "mov rax, rbx\n"
    "vaddpd zmm0, zmm1, [rax + 128]\n");

    return EXIT_SUCCESS;
}