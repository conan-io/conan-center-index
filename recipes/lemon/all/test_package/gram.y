%include {
#include <math.h>
#include <stdio.h>
}

%extra_argument {double *res}
%token_type {double}

res ::= expr(B).                    { *res = B; }
expr(A) ::= expr(B) PLUS expr(C).   { A = B + C; }
expr(A) ::= expr(B) MINUS expr(C).  { A = B - C; }
expr(A) ::= expr(B) TIMES expr(C).  { A = B * C; }
expr(A) ::= expr(B) DIVIDE expr(C). { A = B / C;}
expr(A) ::= expr(B) MOD expr(C).    { A = modf(B, &C); }
expr(A) ::= LPAREN expr(B) RPAREN.  { A = B; }
expr(A) ::= VALUE(B).               { A = B; }
expr(A) ::= MINUS expr(B). [UMINUS] { A = -B; }

%left PLUS MINUS.
%left TIMES DIVIDE MOD.
%right UMINUS.

%code {

#include "gram.h"

typedef struct {
    int id;
    double val;
} input_item_t;

static input_item_t test_input[] = {
    {VALUE, 1.},
    {PLUS, 0.},
    {VALUE, 2.},
    {PLUS, 0.},
    {VALUE, 3.},
    {TIMES, 0.},
    {VALUE, 4.},
    {TIMES, 0.},
    {VALUE, 5.},
    {TIMES, 0.},
    {LPAREN, 0.},
    {VALUE, 6.},
    {MINUS, 0.},
    {VALUE, 7.},
    {RPAREN, 0.},
    {0., 0.},
};

#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *argv[]) {
    void *pParser = ParseAlloc(malloc);
    double result = -123456.;
    double val;
    input_item_t *input = test_input;
    while (1) {
        Parse(pParser, input->id, input->val, &result);
        if (input->id == 0) {
            break;
        }
        ++input;
    }
    ParseFree(pParser, free);
    printf("Result is %g.\n", result);
    return 0;
}

}
