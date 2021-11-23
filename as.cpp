#include <string.h>
#include <condition_variable>
#include <cstdio>
#include <iostream>
#include <mutex>
#include <queue>
#include <sstream>
#include <string>

// Socket.IO C++ Client의 헤더 파일
#include <sio_client.h>

class SampleClient
{
public:
    // Socket.IO의 인스턴스
    sio::client client;
    sio::socket::ptr socket;

    // sio의 스레드와 메인 스레드의 동기화를 위한 mutex 종류
    std::mutex sio_mutex;
    std::condition_variable_any sio_cond;
    // sio 메시지를 쌓기 위한 큐
    std::queue<sio::message::ptr> sio_queue;

    bool is_connected = false;

    // 절단시 호출되는 이벤트 리스너
    void on_close()
    {
        std::cout << "切断しました。" << std::endl;
        exit(EXIT_FAILURE);
    }

    //에러발생시 호출되는 이벤트 리스너
    void on_fail()
    {
        std::cout << "エラーがありました。" << std::endl;
        exit(EXIT_FAILURE);
    }

    // 접속 시에 호출되는 이벤트 리스너
    void on_open()
    {
        std::cout << "接続しました。" << std::endl;
        std::unique_lock<std::mutex> lock(sio_mutex);
        is_connected = true;
        // 접속 처리가 끝난 후 기다리고 있는 메인 스레드를 깨우다
        sio_cond.notify_all();
    }

    // "run" 명령어 이벤트 리스나
    void on_run(sio::event &e)
    {
        std::unique_lock<std::mutex> lock(sio_mutex);
        sio_queue.push(e.get_message());
        // 이벤트를 큐에 등록하고 기다리고 있는 메인 스레드를 일으키다
        sio_cond.notify_all();
    }

    // 메인 처리
    void run(const std::string &url, const std::string &name)
    {
        // 접속 및 에러 이벤트 리스너 설정하기
        client.set_close_listener(std::bind(&SampleClient::on_close, this));
        client.set_fail_listener(std::bind(&SampleClient::on_fail, this));
        client.set_open_listener(std::bind(&SampleClient::on_open, this));

        // 접속 요구를 내다
        client.connect(url);
        {
            // 별도 스레드에서 움직이는 접속 처리가 끝날 때까지 기다리다
            std::unique_lock<std::mutex> lock(sio_mutex);
            if (!is_connected)
            {
                sio_cond.wait(sio_mutex);
            }
        }

        // "run" 명령어 리스너를 등록하다
        socket = client.socket();
        socket->on("run", std::bind(&SampleClient::on_run, this, std::placeholders::_1));

        {
            sio::message::ptr send_data(sio::object_message::create());
            std::map<std::string, sio::message::ptr> &map = send_data->get_map();

            // object 멤버 type과 name 설정하기
            map.insert(std::make_pair("type", sio::string_message::create("native")));
            map.insert(std::make_pair("name", sio::string_message::create(name)));

            // join 명령어를 서버로 보내다
            socket->emit("join", send_data);
        }

        while (true)
        {
            // 이벤트 큐가 빈 경우 큐가 보충될 때까지 기다림
            std::unique_lock<std::mutex> lock(sio_mutex);
            while (sio_queue.empty())
            {
                sio_cond.wait(lock);
            }

            // 이벤트 큐에서 등록된 데이터를 꺼내다
            sio::message::ptr recv_data(sio_queue.front());
            std::stringstream output;
            char buf[1024];

            FILE *fp = nullptr;
            // object의 command 멤버 값을 취득하다
            std::string command = recv_data->get_map().at("command")->get_string();
            std::cout << "run:" << command << std::endl;
            // command를 실행하여 실행 결과를 문자열로 가져오다
            if ((fp = popen(command.c_str(), "r")) != nullptr)
            {
                while (!feof(fp))
                {
                    size_t len = fread(buf, 1, sizeof(buf), fp);
                    output << std::string(buf, len);
                }
            }
            else
            {
                // 에러를 검출했을 경우는 에러 메시지를 가져온다
                output << strerror(errno);
            }

            pclose(fp);

            sio::message::ptr send_data(sio::object_message::create());
            std::map<std::string, sio::message::ptr> &map = send_data->get_map();

            // 명령어 실행 결과를 object의 output로 설정하다
            map.insert(std::make_pair("output", sio::string_message::create(output.str())));

            // sio::message를 서버로 보내기
            socket->emit("reply", send_data);

            // 처리가 끝난 이벤트를 큐에서 제거하다
            sio_queue.pop();
        }
    }
};

int main(int argc, char *argv[])
{
    SampleClient client;
    client.run();

    return EXIT_SUCCESS;
}