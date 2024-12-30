#include <solv/pool.h>
#include <solv/solver.h>


int main(void) {
    Pool* pool = pool_create();
    Solver *solv = solver_create(pool);
    pool_free(pool);
    solver_free(solv);
}
