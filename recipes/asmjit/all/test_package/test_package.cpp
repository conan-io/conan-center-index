#include <asmjit/asmjit.h>

#include <stdio.h>

typedef int (*Func)(void);

int main(int argc, char* argv[]) {
  asmjit::JitRuntime rt;

  asmjit::CodeHolder code;
  code.init(rt.environment());

  asmjit::x86::Assembler a(&code);
  a.mov(asmjit::x86::eax, 1);
  a.ret();

  Func fn;
  asmjit::Error err = rt.add(&fn, &code);
  if (err) return 1;

  int result = fn();
  printf("%d\n", result);

  rt.release(fn);

  return 0;
}
