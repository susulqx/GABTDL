import subprocess
import time
import signal
import sys

def monitor_aria2(aria2_args):
    """
    启动Aria2进程，监测其输出，当检测到下载完成时终止进程
    
    参数:
        aria2_args: 传递给aria2c的命令行参数列表
    """
    try:
        # 启动Aria2进程，捕获 stdout 和 stderr
        process = subprocess.Popen(
            ['aria2c'] + aria2_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("Aria2 进程已启动，开始监测...")
        print(f"Aria2启动参数: {' '.join(aria2_args)}")
        
        # 监测输出的关键词，不区分大小写
        target_keyword = "Download complete"
        
        # 实时读取输出
        for line in process.stdout:
            # 打印Aria2的输出
            print(line.strip())
            
            # 检查是否包含任务完成的关键词（不区分大小写）
            if target_keyword.lower() in line.lower():
                print("\n检测到下载任务完成，准备终止Aria2进程...")
                time.sleep(5)
                # 先尝试优雅终止
                process.send_signal(signal.SIGTERM)
                
                # 等待几秒，看是否能正常退出
                for _ in range(5):
                    if process.poll() is not None:
                        print("Aria2进程已正常终止")
                        return
                    time.sleep(5)
                
                # 如果优雅终止失败，强制终止
                print("优雅终止失败，尝试强制终止Aria2进程...")
                process.kill()
                print("Aria2进程已强制终止")
                return
        
        # 检查进程是否已经结束
        return_code = process.wait()
        print(f"Aria2进程已结束，返回代码: {return_code}")
        
    except KeyboardInterrupt:
        print("\n用户中断，准备终止Aria2进程...")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
        print("程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    # 直接获取命令行参数（排除脚本名称本身）
    if len(sys.argv) < 2:
        print("请提供Aria2的启动参数，例如下载链接或种子文件路径")
        print("使用示例: python aria2_monitor.py --dir ./downloads http://example.com/file.zip")
        sys.exit(1)
    
    # 所有参数（从索引1开始）都传递给aria2
    aria2_arguments = sys.argv[1:]
    monitor_aria2(aria2_arguments)
