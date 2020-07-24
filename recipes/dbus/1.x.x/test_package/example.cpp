#include <cstdlib>
#include <iostream>

#include <dbus/dbus.h>

int main() {
	DBusError err;
	DBusConnection* conn;
	int ret;

	dbus_error_init(&err);
	conn = dbus_bus_get(DBUS_BUS_SESSION, &err);

	if (dbus_error_is_set(&err)) 
	{ 
		fprintf(stderr, "Connection Error (%s)\n", err.message); 
		dbus_error_free(&err); 
		exit(EXIT_FAILURE);
	}

	if (nullptr == conn) exit(EXIT_FAILURE);

	std::cout << "D-Bus is should work!\n";
}
