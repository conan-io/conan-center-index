#include <caca.h>

int main()
{
    caca_canvas_t *cv = caca_create_canvas(32, 16);
    caca_free_canvas(cv);
}
