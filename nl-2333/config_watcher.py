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
        self._last_mtime = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # 检查是否是我们监听的配置文件
        if os.path.abspath(event.src_path) == os.path.abspath(self.config_file_path):
            self._trigger_reload(event.src_path)

    # 处理“原子写入”(write temp + rename) 场景
    def on_created(self, event):
        if event.is_directory:
            return
        if os.path.abspath(event.src_path) == os.path.abspath(self.config_file_path):
            self._trigger_reload(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        # watchdog 的 moved 事件目标路径在 dest_path
        try:
            dest_path = getattr(event, 'dest_path', '')
        except Exception:
            dest_path = ''
        if dest_path and os.path.abspath(dest_path) == os.path.abspath(self.config_file_path):
            self._trigger_reload(dest_path)

    def _trigger_reload(self, changed_path: str):
        # 防止重复触发（1秒内只触发一次）
        current_time = time.time()
        if current_time - self.last_modified <= 1:
            return
        self.last_modified = current_time
        logging.info(f"检测到配置文件变化: {changed_path}")
        try:
            self.reload_callback()
            logging.info("配置重载成功")
        except Exception as e:
            logging.error(f"配置重载失败: {e}")

# 全局变量
observer = None
reload_flag_thread = None
polling_thread = None
stop_flag_monitoring = False

def start_config_watcher(config_file_path, reload_callback):
    """启动配置文件监听器（永不停止，自动恢复）"""
    global observer, reload_flag_thread, polling_thread
    
    # 启动文件系统监听器（watchdog）
    try:
        event_handler = ConfigFileHandler(config_file_path, reload_callback)
        observer = Observer()
        config_dir = os.path.dirname(os.path.abspath(config_file_path))
        observer.schedule(event_handler, config_dir, recursive=False)
        observer.start()
        logging.info(f"文件系统监听器（watchdog）已启动")
    except Exception as e:
        logging.error(f"启动文件系统监听器失败: {e}，将仅使用mtime轮询")
    
    # 启动重载标记文件监听线程（永不停止）
    try:
        reload_flag_thread = threading.Thread(target=monitor_reload_flag, args=(reload_callback,))
        reload_flag_thread.daemon = True
        reload_flag_thread.start()
        logging.info("重载标记文件监听线程已启动（永不停止）")
    except Exception as e:
        logging.error(f"启动重载标记文件监听线程失败: {e}")
    
    # 启动 mtime 轮询（永不停止，作为主要的热重载机制）
    try:
        polling_thread = threading.Thread(target=monitor_config_mtime, args=(config_file_path, reload_callback,))
        polling_thread.daemon = True
        polling_thread.start()
        logging.info("配置文件mtime轮询线程已启动（永不停止，每秒检查一次）")
    except Exception as e:
        logging.error(f"启动mtime轮询线程失败: {e}")
        # 即使失败也尝试重启
        time.sleep(2)
        try:
            polling_thread = threading.Thread(target=monitor_config_mtime, args=(config_file_path, reload_callback,))
            polling_thread.daemon = True
            polling_thread.start()
            logging.info("mtime轮询线程重启成功")
        except Exception as e2:
            logging.error(f"mtime轮询线程重启失败: {e2}")
    
    logging.info(f"配置文件热重载监听器已启动（永不停止），监听: {config_file_path}")

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

def monitor_config_mtime(config_file_path, reload_callback):
    """轮询监听配置文件 mtime，确保在 bind mount 环境中也能可靠触发热重载
    此函数永不停止，即使出错也会自动恢复
    同时监听 keyword_replies.json 文件的变化"""
    last_mtime = 0
    keyword_replies_path = 'keyword_replies.json'
    keyword_replies_last_mtime = 0
    
    while True:  # 永不停止
        try:
            # 监听 config.txt
            if os.path.exists(config_file_path):
                mtime = os.path.getmtime(config_file_path)
                if mtime > last_mtime:
                    last_mtime = mtime
                    logging.info(f"检测到配置文件mtime变化: {config_file_path}")
                    try:
                        reload_callback()
                        logging.info("通过mtime轮询重载配置成功")
                    except Exception as e:
                        logging.error(f"通过mtime轮询重载配置失败: {e}")
            
            # 监听 keyword_replies.json
            if os.path.exists(keyword_replies_path):
                keyword_mtime = os.path.getmtime(keyword_replies_path)
                if keyword_mtime > keyword_replies_last_mtime:
                    keyword_replies_last_mtime = keyword_mtime
                    logging.info(f"检测到关键词回复文件mtime变化: {keyword_replies_path}")
                    try:
                        reload_callback()  # 重新加载配置（包括关键词回复）
                        logging.info("通过mtime轮询重载关键词回复成功")
                    except Exception as e:
                        logging.error(f"通过mtime轮询重载关键词回复失败: {e}")
            
            time.sleep(1)
        except Exception as e:
            logging.error(f"轮询配置文件mtime时出错: {e}，将在1秒后继续")
            time.sleep(1)  # 出错后快速恢复，不等待5秒

def monitor_reload_flag(reload_callback):
    """监听重载标记文件
    此函数永不停止，即使出错也会自动恢复"""
    reload_flag_path = '.reload_flag'
    last_check_time = 0
    
    while True:  # 永不停止
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
            logging.error(f"监听重载标记文件时出错: {e}，将在1秒后继续")
            time.sleep(1)  # 出错后快速恢复