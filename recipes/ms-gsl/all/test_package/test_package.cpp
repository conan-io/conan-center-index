#include <gsl/gsl>

int main() 
{
	char stack_string[] = "Hello";
    gsl::string_span<> v = gsl::ensure_z(stack_string);
	return 0;
}
