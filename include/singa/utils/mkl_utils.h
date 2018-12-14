#ifndef SINGA_UTILS_MKLDNN_UTILS_H_
#define SINGA_UTILS_MKLDNN_UTILS_H_
#define MKL_CHECK(f)                                                               \
    do {                                                                       \
        mkldnn_status_t s = f;                                                 \
        if (s != mkldnn_success) {                                             \
            printf("[%s:%d] error: %s returns %d\n", __FILE__, __LINE__, #f,   \
                   s);                                                         \
            exit(2);                                                           \
        }                                                                      \
    } while (0)
#define CHECK_TRUE(expr)                                                       \
    do {                                                                       \
        int e_ = expr;                                                         \
        if (!e_) {                                                             \
            printf("[%s:%d] %s failed\n", __FILE__, __LINE__, #expr);          \
            exit(2);                                                           \
        }                                                                      \
    } while (0)
#endif // SINGA_UTILS_MKLDNN_UTILS_H_
