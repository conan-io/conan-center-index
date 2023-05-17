#include "minitrace.h"

#ifdef _WIN32
#include <windows.h>
#define usleep(x) Sleep(x/1000)
#else
#include <unistd.h>
#endif

void c() {
	MTR_SCOPE("c++", "c()");
	usleep(10000);
}

void b() {
	MTR_SCOPE("c++", "b()");
	usleep(20000);
	c();
	usleep(10000);
}

void a() {
	MTR_SCOPE("c++", "a()");
	usleep(20000);
	b();
	usleep(10000);
}

int main() {
	int i;
	mtr_init("trace.json");
	mtr_register_sigint_handler();

	MTR_META_PROCESS_NAME("minitrace_test");
	MTR_META_THREAD_NAME("main thread");

	int long_running_thing_1;
	int long_running_thing_2;

	MTR_START("background", "long_running", &long_running_thing_1);
	MTR_START("background", "long_running", &long_running_thing_2);

	MTR_COUNTER("main", "greebles", 3);
	MTR_BEGIN("main", "outer");
	usleep(80000);
	for (i = 0; i < 3; i++) {
		MTR_BEGIN("main", "inner");
		usleep(40000);
		MTR_END("main", "inner");
		usleep(10000);
		MTR_COUNTER("main", "greebles", 3 * i + 10);
	}
	MTR_STEP("background", "long_running", &long_running_thing_1, "middle step");
	usleep(80000);
	MTR_END("main", "outer");
	MTR_COUNTER("main", "greebles", 0);

	usleep(10000);
	a();

	usleep(50000);
	MTR_INSTANT("main", "the end");
	usleep(10000);
	MTR_FINISH("background", "long_running", &long_running_thing_1);
	MTR_FINISH("background", "long_running", &long_running_thing_2);

	mtr_flush();
	mtr_shutdown();
	return 0;
}
