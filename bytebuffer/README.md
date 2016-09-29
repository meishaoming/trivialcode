## webrtc - bytebuffer

几个 private 数据：

```cpp
  char* bytes_;	    // 指向 new 出来的缓冲区，类型为 char
  size_t size_;     // 缓冲区的大小。每次 resize 会以 1.5 倍增长
  size_t start_;    // 有效数据的起始位置
  size_t end_;	    // 有效数据的结束位置
  int version_;	    // 每次 resize 或 clear，version_ 加1。
  ByteOrder byte_order_; // 字节序
```

默认大小 size_ 为 4096。

默认字节序为「网络字节序」，即 big-endian

`SetReadPosition()` 方法会直接操作 start_，此时会检查 version_ 的值是否匹配。这也限制了 `SetReadPosition()` 必须与 `GetReadPosition()` 一起使用，先拿到当前 ByteBuffer::ReadPosition 值，更改完之后立即使用。

每次 Read 操作之后，start_ 向后移动。

每次 Write 操作，如果「增加的长度」大于「当前缓冲区的剩余空间」，则进行一次 Resize。如果缓冲区总长度还够，则 memmove 把数据移到最前；如果不够，则分配更大的一片空间，并把之前数据复制过去。

每次重新分配内存大小的算法是：取 「需要尺寸」与 「当前 size_*1.5」两者中大的值。

muduo 中有个 Buffer 的实现与 ByteBuffer 类似，主要区别有：

- muduo 的缓冲区使用 `std::vector<char> buffer_;` 实现；ByteBuffer 里是 `char* bytes_` + new。
- muduo 缓冲区默认大小是 1024；ByteBuffer 是 4096。Libevent 里的 evbuffer 每个 chain 大小跟 muduo 一样都是 1024。实际使用中我甚至觉得 1024 大小都很少用到，经常 TCP 的传输都是一些小的协议包。
- muduo 缓冲区有 prepend 功能，预留了 8 字节的空间，所以实际的默认缓冲区的大小是 1024+8。
- ByteBuffer 里增加了「字节序」的处理。ReadUInt8/16/24/32 时会直接读到 Host 字节序的值；WriteUInt8/16/24/32 时会实际写成网络字节序的值。byteorder.h 里默认是按 little-endian 来写的。
- muduo 里一直使用 boost::noncopyable；ByteBuffer 使用宏来实现 `DISALLOW_COPY_AND_ASSIGN(xxx)`。

另外，与 ByteBuffer 一起，webrtc 也实现了一个 Buffer 类。该类的功能与 std::string/vector 功能类似，但是在缓冲区分配时不会做初始化操作。

这里抽出 ByteBuffer 和 它的单元测试。去掉了其中对 Buffer 类的依赖，因为 Buffer 里使用了 scoped_ptr。

