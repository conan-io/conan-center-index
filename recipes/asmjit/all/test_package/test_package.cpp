#include <asmjit/asmjit.h>
#if defined(USE_X86)
#include <asmjit/x86.h>
#endif

#if defined(USE_AARCH64)
#include <asmjit/a64.h>
#endif

#include <stdio.h>

typedef int (*Func)(void);

int main(int argc, char* argv[]) {
  asmjit::JitRuntime rt;

  asmjit::CodeHolder code;
  code.init(rt.environment());

#if defined(USE_X86)
  asmjit::x86::Assembler a(&code);
  a.mov(asmjit::x86::eax, 1);
  a.ret();
#elif defined(USE_AARCH64)
  asmjit::a64::Assembler a(&code);
  a.mov(asmjit::a64::w0, 1);
  a.ret(asmjit::a64::w0);
#else
  #error "Unsupported architecture"
#endif

  Func fn;
  asmjit::Error err = rt.add(&fn, &code);
  if (err) return 1;

  int result = fn();
  printf("%d\n", result);

  rt.release(fn);

  return 0;
}
