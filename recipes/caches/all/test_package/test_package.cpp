#include <caches/queues/fifo_cache.tpp>
#include <caches/queues/lifo_cache.tpp>
#include <caches/stores/lru_cache.tpp>
#include <caches/stores/store_cache.tpp>
#include <string>

struct Resource {
    size_t id;
};

int main() {
    caches::LIFOCache<Resource>();
    caches::FIFOCache<Resource>();
    caches::LRUCache<std::string, Resource>();
    caches::StoreCache<std::string, Resource>();
}
