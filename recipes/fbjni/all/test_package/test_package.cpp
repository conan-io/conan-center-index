#include <fbjni/fbjni.h>
#include <fbjni/detail/utf8.h>

#include <cstdio>
#include <string>

int main() {
  // Calling into the JNI core needs a running JVM; taking an address is enough to link it
  JNIEnv* (*volatile current)() = &facebook::jni::Environment::current;

  // Modified UTF-8 encodes NUL as two bytes, so "a\0b" is 4 bytes long
  const std::string str("a\0b", 3);
  const size_t length = facebook::jni::detail::modifiedLength(str);
  std::printf("fbjni: modifiedLength(\"a\\0b\") = %zu\n", length);
  return (length == 4 && current != nullptr) ? 0 : 1;
}
