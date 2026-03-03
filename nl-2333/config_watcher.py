import os
import time
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_file_path, reload_callback):
        self.config_file_path = config_file_path
        self.reload_callback = reload_callback
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # 检查是否是我们监听的配置文件
        if os.path.abspath(event.src_path) == os.path.abspath(self.config_file_path):
            # 防止重复触发
            current_time = time.time()
            if current_time - self.last_modified > 1:  # 1秒内只触发一次
                self.last_modified = current_time
                logging.info(f"检测到配置文件变化: {event.src_path}")
                try:
                    self.reload_callback()
                    logging.info("配置重载成功")
                except Exception as e:
                    logging.error(f"配置重载失败: {e}")

# 全局变量
observer = None
reload_flag_thread = None
stop_flag_monitoring = False

def start_config_watcher(config_file_path, reload_callback):
    """启动配置文件监听器"""
    global observer, reload_flag_thread, stop_flag_monitoring
    
    try:
        # 启动文件系统监听器
        event_handler = ConfigFileHandler(config_file_path, reload_callback)
        observer = Observer()
        
        # 监听配置文件所在的目录
        config_dir = os.path.dirname(os.path.abspath(config_file_path))
        observer.schedule(event_handler, config_dir, recursive=False)
        observer.start()
        
        # 启动重载标记文件监听线程
        stop_flag_monitoring = False
        reload_flag_thread = threading.Thread(target=monitor_reload_flag, args=(reload_callback,))
        reload_flag_thread.daemon = True
        reload_flag_thread.start()
        
        logging.info(f"配置文件监听器已启动，监听: {config_file_path}")
        
    except Exception as e:
        logging.error(f"启动配置文件监听器失败: {e}")

def stop_config_watcher():
    """停止配置文件监听器"""
    global observer, stop_flag_monitoring
    
    try:
        stop_flag_monitoring = True
        
        if observer:
            observer.stop()
            observer.join()
            observer = None
            
        logging.info("配置文件监听器已停止")
        
    except Exception as e:
        logging.error(f"停止配置文件监听器失败: {e}")

def monitor_reload_flag(reload_callback):
    """监听重载标记文件"""
    global stop_flag_monitoring
    
    reload_flag_path = '.reload_flag'
    last_check_time = 0
    
    while not stop_flag_monitoring:
        try:
            if os.path.exists(reload_flag_path):
                # 检查文件修改时间
                file_mtime = os.path.getmtime(reload_flag_path)
                
                if file_mtime > last_check_time:
                    last_check_time = file_mtime
                    logging.info("检测到重载标记文件，开始重载配置...")
                    
                    try:
                        reload_callback()
                        logging.info("通过重载标记文件重载配置成功")
                        
                        # 删除标记文件
                        os.remove(reload_flag_path)
                        
                    except Exception as e:
                        logging.error(f"通过重载标记文件重载配置失败: {e}")
                        
            time.sleep(1)  # 每秒检查一次
            
        except Exception as e:
            logging.error(f"监听重载标记文件时出错: {e}")
            time.sleep(5)  # 出错时等待5秒再继续