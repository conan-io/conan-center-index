#include "atomic_ops_stack.h"

#include <stdio.h>
#include <stdlib.h>

AO_t globalElement;

AO_stack_t globalStack = AO_STACK_INITIALIZER;

typedef struct {
    AO_t head;
    unsigned val;
} my_stack_t;

int main()
{
    AO_store_full(&globalElement, 1337);
    {
        AO_t val = AO_load_full(&globalElement);
        if (val != 1337) {
            fprintf(stderr, "Unexpected element after store/load: %u\n", (unsigned) val);
            return EXIT_FAILURE;
        }
    }

    {
        my_stack_t *newElem = (my_stack_t *) malloc(sizeof(my_stack_t));
        newElem->val = 4242;
        AO_stack_push_release(&globalStack, &newElem->head);
    }
    {
        my_stack_t *newElem = (my_stack_t *) malloc(sizeof(my_stack_t));
        newElem->val = 8484;
        AO_stack_push_release(&globalStack, &newElem->head);
    }

    {
        my_stack_t *fetchElement = (my_stack_t *) AO_stack_pop_acquire(&globalStack);
        if (fetchElement->val != 8484) {
            fprintf(stderr, "Unexpected element from stack: %u\n", (unsigned) fetchElement->val);
            return EXIT_FAILURE;
        }
        free(fetchElement);
    }
    {
        my_stack_t *fetchElement = (my_stack_t *) AO_stack_pop_acquire(&globalStack);
        if (fetchElement->val != 4242) {
            fprintf(stderr, "Unexpected element from stack: %u\n", (unsigned) fetchElement->val);
            return EXIT_FAILURE;
        }
        free(fetchElement);
    }
    return EXIT_SUCCESS;
}
