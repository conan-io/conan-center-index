#include <caches/queues/fifo_cache.tpp>
#include <caches/queues/lifo_cache.tpp>
#include <caches/stores/lru_cache.tpp>
#include <caches/stores/store_cache.tpp>
#include <cstddef>
#include <gtest/gtest.h>
#include <string>

using namespace caches;

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

class TestResource {
  public:
    std::string str;

    explicit TestResource(std::string str) : str(std::move(str)) {}

    TestResource(const TestResource &)            = delete;
    TestResource &operator=(const TestResource &) = delete;

    TestResource(TestResource &&resource) noexcept : str(std::move(resource.str)) {}

    TestResource &operator=(TestResource &&) = delete;

    ~TestResource() = default;

    bool operator==(const TestResource &rhs) const { return str == rhs.str; }
};

TEST(FIFOCache, Fill) {
    FIFOCache<int> cache(3);
    EXPECT_EQ(cache.size(), 0UL);
    EXPECT_EQ(cache.space(), 3UL);

    cache.push(1);
    EXPECT_EQ(cache.size(), 1UL);
    EXPECT_EQ(cache.space(), 2UL);
    EXPECT_EQ(cache.next(), 1);
    EXPECT_EQ(cache.last(), 1);

    cache.push(2);
    EXPECT_EQ(cache.size(), 2UL);
    EXPECT_EQ(cache.space(), 1UL);
    EXPECT_EQ(cache.next(), 1);
    EXPECT_EQ(cache.last(), 2);

    cache.push(3);
    EXPECT_EQ(cache.size(), 3UL);
    EXPECT_EQ(cache.space(), 0UL);
    EXPECT_EQ(cache.next(), 1);
    EXPECT_EQ(cache.last(), 3);

    cache.push(4);
    EXPECT_EQ(cache.size(), 3UL);
    EXPECT_EQ(cache.space(), 0UL);
    EXPECT_EQ(cache.next(), 2);
    EXPECT_EQ(cache.last(), 4);
}

TEST(LIFOCache, Fill) {
    LIFOCache<int> cache(3);
    EXPECT_EQ(cache.size(), 0UL);
    EXPECT_EQ(cache.space(), 3UL);

    cache.push(1);
    EXPECT_EQ(cache.size(), 1UL);
    EXPECT_EQ(cache.space(), 2UL);
    EXPECT_EQ(cache.next(), 1);
    EXPECT_EQ(cache.last(), 1);

    cache.push(2);
    EXPECT_EQ(cache.size(), 2UL);
    EXPECT_EQ(cache.space(), 1UL);
    EXPECT_EQ(cache.next(), 2);
    EXPECT_EQ(cache.last(), 1);

    cache.push(3);
    EXPECT_EQ(cache.size(), 3UL);
    EXPECT_EQ(cache.space(), 0UL);
    EXPECT_EQ(cache.next(), 3);
    EXPECT_EQ(cache.last(), 1);

    cache.push(4);
    EXPECT_EQ(cache.size(), 3UL);
    EXPECT_EQ(cache.space(), 0UL);
    EXPECT_EQ(cache.next(), 4);
    EXPECT_EQ(cache.last(), 2);
}

TEST(LRUCache, Lru) {
    LRUCache<std::string, int> cache(2);

    cache.store("a", 1);
    cache.store("b", 2);

    cache["a"];

    cache.store("c", 3);

    EXPECT_TRUE(cache.contains("a"));
    EXPECT_TRUE(cache.contains("c"));

    EXPECT_FALSE(cache.contains("b"));
}

TEST(StoreCache, Lru) {
    StoreCache<TestResource> cache(2);

    cache.store("a", TestResource("a"));
    cache.store("b", TestResource("b"));

    cache.at("a");

    cache.store("c", TestResource("c"));

    EXPECT_TRUE(cache.contains("a"));
    EXPECT_TRUE(cache.contains("c"));

    EXPECT_FALSE(cache.contains("b"));
}
