#include <stdio.h>
#include <stdlib.h>
#include <uv.h>

int main() {
#ifdef _WIN32
	// probably bug:
	// src/win/winapi.c assumes
	// that advapi32.dll has been already loaded,
	// so load it before using anything from winapi.c
	// for static build
	LoadLibrary("advapi32.dll");
#endif

	uv_loop_t *loop = malloc(sizeof(uv_loop_t));
	uv_loop_init(loop);

	printf("Package test completed successfully\n");
	uv_run(loop, UV_RUN_DEFAULT);

	uv_loop_close(loop);
	free(loop);

	return 0;
}
