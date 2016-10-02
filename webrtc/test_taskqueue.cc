
#include <iostream>

#include <webrtc/base/task_queue.h>
#include <webrtc/base/platform_thread.h>
#include <webrtc/base/checks.h>
#include <webrtc/base/event.h>

using namespace rtc;

void PostCustomImplementation(void) {
    printf("\nstart %s\n", __func__);
    static const char kQueueName[] = "PostCustomImplementation";
    rtc::TaskQueue queue(kQueueName);

    rtc::Event event(false, false);

    class CustomTask : public rtc::QueuedTask {
        public:
            explicit CustomTask(rtc::Event *event) : event_(event) {  }

        private:
            bool Run() override {
                printf("PostCustomImplementation %d\n", rtc::CurrentThreadId());
                event_->Set();
                return false;
            }

            rtc::Event* const event_;
    } my_task(&event);

    queue.PostTask(std::unique_ptr<rtc::QueuedTask>(&my_task));
    event.Wait(1000);
}

void PostLambda(void) {
    printf("\nstart %s\n", __func__);
    static const char kQueueName[] = "PostLambda";
    TaskQueue queue(kQueueName);

    Event event(false, false);

    queue.PostTask([&event]() {
                   event.Set();
                   printf("PostLambda %d\n", rtc::CurrentThreadId());
                   });

    event.Wait(1000);
}

void PostAndReplyLambda(void) {
    printf("\nstart %s\n", __func__);
    static const char kPostQueue[] = "PostQueue";
    static const char kReplyQueue[] = "ReplyQueue";
    TaskQueue post_queue(kPostQueue);
    TaskQueue reply_queue(kReplyQueue);

    Event event(false, false);
    bool my_flag = false;
    post_queue.PostTaskAndReply([&my_flag]() {
                                    my_flag = true;
                                    printf("post_queue: current thread id %d\n", CurrentThreadId());
                                },
                                [&event]() {
                                    event.Set();
                                    printf("reply_queue: current thread id %d\n", CurrentThreadId());
                                },
                                &reply_queue);
    event.Wait(1000);
    printf("PostAndReplyLambda my_flag %d\n", my_flag);
}

int main(void) {
    printf("main pid %d\n", rtc::CurrentThreadId());
    PostCustomImplementation();
    PostLambda();
    PostAndReplyLambda();
    return 0;
}
