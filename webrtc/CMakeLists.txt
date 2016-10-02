cmake_minimum_required(VERSION 3.2)
project(webrtc)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11 -DWEBRTC_POSIX -DWEBRTC_MAC")
set(CMAKE_SHARED_LINKER_FLAGS "-framework Foundation")

set(source_dir /Users/sam/workspace/read_the_fucking_source_code/webrtc)
include_directories(/Users/sam/workspace/read_the_fucking_source_code/webrtc)

set(SOURCE_FILES
${source_dir}/webrtc/base/arraysize.h
${source_dir}/webrtc/base/array_view.h
${source_dir}/webrtc/base/atomicops.h
${source_dir}/webrtc/base/bind.h
${source_dir}/webrtc/base/bitbuffer.cc
${source_dir}/webrtc/base/bitbuffer.h
${source_dir}/webrtc/base/buffer.h
${source_dir}/webrtc/base/bufferqueue.cc
${source_dir}/webrtc/base/bufferqueue.h
${source_dir}/webrtc/base/bytebuffer.cc
${source_dir}/webrtc/base/bytebuffer.h
${source_dir}/webrtc/base/byteorder.h
${source_dir}/webrtc/base/checks.cc
${source_dir}/webrtc/base/checks.h
${source_dir}/webrtc/base/constructormagic.h
${source_dir}/webrtc/base/copyonwritebuffer.cc
${source_dir}/webrtc/base/copyonwritebuffer.h
${source_dir}/webrtc/base/criticalsection.cc
${source_dir}/webrtc/base/criticalsection.h
${source_dir}/webrtc/base/deprecation.h
${source_dir}/webrtc/base/event.cc
${source_dir}/webrtc/base/event.h
${source_dir}/webrtc/base/event_tracer.cc
${source_dir}/webrtc/base/event_tracer.h
${source_dir}/webrtc/base/exp_filter.cc
${source_dir}/webrtc/base/exp_filter.h
${source_dir}/webrtc/base/file.cc
${source_dir}/webrtc/base/file.h
${source_dir}/webrtc/base/format_macros.h
${source_dir}/webrtc/base/function_view.h
${source_dir}/webrtc/base/ignore_wundef.h
${source_dir}/webrtc/base/location.h
${source_dir}/webrtc/base/location.cc
${source_dir}/webrtc/base/md5.cc
${source_dir}/webrtc/base/md5.h
${source_dir}/webrtc/base/md5digest.cc
${source_dir}/webrtc/base/md5digest.h
${source_dir}/webrtc/base/mod_ops.h
${source_dir}/webrtc/base/onetimeevent.h
${source_dir}/webrtc/base/optional.cc
${source_dir}/webrtc/base/optional.h
${source_dir}/webrtc/base/platform_file.cc
${source_dir}/webrtc/base/platform_file.h
${source_dir}/webrtc/base/platform_thread.cc
${source_dir}/webrtc/base/platform_thread.h
${source_dir}/webrtc/base/platform_thread_types.h
${source_dir}/webrtc/base/race_checker.cc
${source_dir}/webrtc/base/race_checker.h
${source_dir}/webrtc/base/random.cc
${source_dir}/webrtc/base/random.h
${source_dir}/webrtc/base/rate_statistics.cc
${source_dir}/webrtc/base/rate_statistics.h
${source_dir}/webrtc/base/rate_limiter.cc
${source_dir}/webrtc/base/rate_limiter.h
${source_dir}/webrtc/base/ratetracker.cc
${source_dir}/webrtc/base/ratetracker.h
${source_dir}/webrtc/base/refcount.h
${source_dir}/webrtc/base/safe_conversions.h
${source_dir}/webrtc/base/safe_conversions_impl.h
${source_dir}/webrtc/base/sanitizer.h
${source_dir}/webrtc/base/scoped_ref_ptr.h
${source_dir}/webrtc/base/stringencode.cc
${source_dir}/webrtc/base/stringencode.h
${source_dir}/webrtc/base/stringutils.cc
${source_dir}/webrtc/base/stringutils.h
${source_dir}/webrtc/base/swap_queue.h
${source_dir}/webrtc/base/systeminfo.cc
${source_dir}/webrtc/base/systeminfo.h
${source_dir}/webrtc/base/template_util.h
${source_dir}/webrtc/base/thread_annotations.h
${source_dir}/webrtc/base/thread_checker.h
${source_dir}/webrtc/base/thread_checker_impl.cc
${source_dir}/webrtc/base/thread_checker_impl.h
${source_dir}/webrtc/base/timestampaligner.cc
${source_dir}/webrtc/base/timestampaligner.h
${source_dir}/webrtc/base/timeutils.cc
${source_dir}/webrtc/base/timeutils.h
${source_dir}/webrtc/base/trace_event.h
${source_dir}/webrtc/base/type_traits.h

# os_posix
${source_dir}/webrtc/base/file_posix.cc

# '-framework Foundation
${source_dir}/webrtc/base/logging.cc
${source_dir}/webrtc/base/logging.h
${source_dir}/webrtc/base/logging_mac.mm
    )

add_library(rtc_base_approved STATIC ${SOURCE_FILES})

add_library(rtc_task_queue STATIC
${source_dir}/webrtc/base/sequenced_task_checker.h
${source_dir}/webrtc/base/sequenced_task_checker_impl.cc
${source_dir}/webrtc/base/sequenced_task_checker_impl.h
${source_dir}/webrtc/base/task_queue.h
${source_dir}/webrtc/base/task_queue_posix.h
${source_dir}/webrtc/base/task_queue_gcd.cc
${source_dir}/webrtc/base/task_queue_posix.cc
        )
target_link_libraries(rtc_task_queue rtc_base_approved)

add_executable(test_event test_event.cc)
target_link_libraries(test_event rtc_base_approved)

add_executable(test_taskqueue test_taskqueue.cc)
target_link_libraries(test_taskqueue rtc_task_queue)
