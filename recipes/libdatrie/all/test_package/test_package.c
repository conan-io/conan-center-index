#include <datrie/trie.h>

int main(void) {
    AlphaMap *en_map = alpha_map_new();
    if (!en_map)
        return 1;
    if (alpha_map_add_range(en_map, 0x0061, 0x007a) != 0)
        return 1;
    Trie *test_trie = trie_new(en_map);
    if (!test_trie)
        return 1;
    trie_free(test_trie);
    alpha_map_free(en_map);
    return 0;
}
