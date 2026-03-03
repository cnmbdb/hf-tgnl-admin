import logging
import json
import time
import math
import requests
import re
import hashlib
import http.client
import base58
import hmac
import telegram
import subprocess
import random
import os
import sqlite3
import threading
import asyncio
import urllib3.exceptions
import mysql.connector
from mysql.connector import errors
from telegram import ReplyKeyboardRemove
from threading import Thread
from tronapi import Tron
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from multiprocessing import Pool
from telegram.ext import CallbackQueryHandler
from concurrent.futures import ThreadPoolExecutor
from tronapi.exceptions import TransportError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from datetime import datetime
from telegram import ForceReply
from requests.exceptions import ReadTimeout, ConnectionError
from telegram.utils.helpers import mention_html
from telegram import ChatMemberUpdated
from telegram.error import NetworkError,TelegramError
import pytz
from config_watcher import start_config_watcher
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from logging.handlers import RotatingFileHandler
API_KEY="df73b433-41c7-4545-889b-5fde2d70656c"

# 配置日志：使用轮转文件处理器，限制日志大小和数量
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# 配置根日志记录器
log_file = os.path.join(logs_dir, 'bot.log')
# 使用轮转文件处理器：每个文件最大 10MB，保留 5 个备份文件
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 控制台处理器（用于 Docker 日志）
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

# 创建支付相关的logger，可以通过日志级别控制DEBUG输出
payment_logger = logging.getLogger('payment')
payment_logger.setLevel(logging.INFO)  # 生产环境使用INFO，调试时可改为DEBUG

# 加载环境变量从 .env 文件
def load_env_file(file_path):
    """加载环境变量文件"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 加载 .env 文件
env_file_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
load_env_file(env_file_path)

# 计算前端API基地址，支持容器网络访问
APP_PORT = os.getenv('PORT') or '3000'
APP_BASE_PATH = os.getenv('APP_BASE_PATH') or ''
if APP_BASE_PATH and not APP_BASE_PATH.startswith('/'):
    APP_BASE_PATH = '/' + APP_BASE_PATH
# 在 Docker Compose 网络中，默认通过服务名访问 Nuxt 应用
DEFAULT_HOST = 'app' if os.getenv('DB_HOST') == 'db' else 'localhost'
APP_HOST = os.getenv('APP_HOST') or DEFAULT_HOST
API_BASE = f"http://{APP_HOST}:{APP_PORT}{APP_BASE_PATH}"
# Webhook 配置（可选）
BOT_WEBHOOK_URL = os.getenv('BOT_WEBHOOK_URL', '').strip()  # 例如 https://your.domain.com/bot
BOT_WEBHOOK_PORT = int(os.getenv('BOT_WEBHOOK_PORT', '8443'))
BOT_WEBHOOK_PATH = os.getenv('BOT_WEBHOOK_PATH', '').strip()  # 默认使用 TOKEN 作为 url_path

utotrc_huilv=11.5
tron = Tron()
filename = '监听.txt'
contract_address='TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
last_message_id = None
user_payment_amount = {}
INPUT_ADDRESS = 1
delete_ADDRESS=4
INPUT_RECHARGE_AMOUNT = 5
INPUT_BISHU_ADDRESS = 6  # 输入笔数套餐地址
# 能量池API地址 - 从config.txt读取，支持热重载
# 默认值留空，强制由 config.txt 中的 energy_pool_api 决定，避免指向历史的上游地址
energy_pool_api = ''  # 会在 reload_config()/main() 中从 config.txt 读取
# 机器人回调地址 - 从config.txt读取，支持热重载（能量池系统回调机器人用）
bot_notify_url = None  # 会在reload_config()中从config.txt读取，如果没有配置则使用默认值
# USDT转TRX出款私钥 - 从config.txt读取，支持热重载（用于给用户出TRX）
usdt2trx_private_key = None  # 会在reload_config()中从config.txt读取，必须配置，不能使用默认privateKey
# 机器人用户名 - 用于在API调用中标识机器人
# API充值订单的付款地址
RECHARGE_PAYMENT_ADDRESS = "TJdtCWfm4iaqcQVMJchrobkbP5Y9yqNpPf"
bot_username = None  # 会在main()中从bot_id或bot.get_me()获取
# 全局 bot 对象（在 main() 中初始化，供 HTTP 服务器使用）
bot = None

# 主键盘菜单配置（从 config.txt 加载，支持热重载）
# 默认键盘布局（9个按钮的 key 固定，label 可配置）
MAIN_MENU_DEFAULT_KEYS = [
    ['bishu'],
    ['yucun', 'usdt2trx'],
    ['check_tx', 'trx2energy'],
    ['monitored_addresses', 'toggle_monitor'],
    ['recharge', 'profile']
]
main_menu_layout = None  # 从配置加载的键盘布局 [{key, label, chain_id}, ...]
label_to_key = {}  # label -> key 映射（向后兼容）
label_to_chain_id = {}  # label -> chain_id 映射，用于功能路由
# 关键词回复数据（从 keyword_replies.json 加载，支持热重载）
keyword_replies_data = {}  # 存储关键词回复配置

# 从环境变量读取数据库配置（统一使用 DB_* 配置）
config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'database': 'tgnl',
        'port': 3306,
        'charset': 'utf8mb4'
    }

# 验证必要的环境变量是否已设置（统一使用 DB_* 配置）
required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

class DatabaseConnection:
    def __init__(self, config):
        self.config = config
        self.conn = self.connect()

    def connect(self):
        return mysql.connector.connect(**self.config)

    def reconnect(self):
        self.conn.close()
        self.conn = self.connect()

    def cursor(self):
        while True:
            try:
                cursor = self.conn.cursor()
                break
            except (errors.InterfaceError, errors.OperationalError):
                self.reconnect()

        return cursor

    def close(self):
        self.conn.close()


def handle_start_command(chat_id, user_nickname, username,):
    try:
        # 使用HTTP请求调用前端API
        api_url = f"{API_BASE}/api/bot-register-user"
        data = {
            "chat_id": chat_id,
            "user_nickname": user_nickname,
            "username": username
        }
        logging.info(f"[REGISTER_USER] 调用注册API: {api_url}, chat_id={chat_id}, username={username}, nickname={user_nickname}")
        response = requests.post(api_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logging.info(f"[REGISTER_USER] 用户注册成功: chat_id={chat_id}, action={result.get('action', 'unknown')}")
                print(f"User {chat_id} registered/updated successfully")
            else:
                error_msg = result.get('message') or result.get('error', 'Unknown error')
                logging.error(f"[REGISTER_USER] API返回错误: chat_id={chat_id}, error={error_msg}")
                print(f"API error in handle_start_command: {error_msg}")
        else:
            error_text = response.text[:200] if response.text else 'No response body'
            logging.error(f"[REGISTER_USER] HTTP错误: status={response.status_code}, url={api_url}, response={error_text}")
            print(f"HTTP error in handle_start_command: {response.status_code}, response: {error_text}")
    except requests.exceptions.Timeout as e:
        logging.error(f"[REGISTER_USER] 请求超时: url={api_url}, error={e}")
        print(f"API request timeout in handle_start_command: {e}")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"[REGISTER_USER] 连接错误: url={api_url}, error={e}")
        print(f"API connection error in handle_start_command: {e}")
    except Exception as e:
        logging.error(f"[REGISTER_USER] 未知错误: url={api_url}, error={e}", exc_info=True)
        print(f"API request error in handle_start_command: {e}")


def create_database():
    # 机器人现在通过API调用前端，不再需要直接连接数据库
    print('Robot is now using API calls to frontend instead of direct database connection')
    print('Database operations will be handled by the frontend API')

def get_user_data(chat_id):
    try:
        # 使用HTTP请求调用前端API
        api_url = f"{API_BASE}/api/bot-user-data"
        params = {"chat_id": chat_id}
        logging.debug(f"[GET_USER_DATA] 调用API: {api_url}, chat_id={chat_id}")
        response = requests.get(api_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                logging.debug(f"[GET_USER_DATA] 获取用户数据成功: chat_id={chat_id}")
                return data.get("data")
            else:
                error_msg = data.get('error', 'Unknown error')
                logging.warning(f"[GET_USER_DATA] API返回错误: chat_id={chat_id}, error={error_msg}")
                print(f"API error in get_user_data: {error_msg}")
                return None
        else:
            error_text = response.text[:200] if response.text else 'No response body'
            logging.error(f"[GET_USER_DATA] HTTP错误: status={response.status_code}, url={api_url}, response={error_text}")
            print(f"HTTP error in get_user_data: {response.status_code}, response: {error_text}")
            return None
    except requests.exceptions.Timeout as e:
        logging.error(f"[GET_USER_DATA] 请求超时: url={api_url}, error={e}")
        print(f"API request timeout in get_user_data: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        logging.error(f"[GET_USER_DATA] 连接错误: url={api_url}, error={e}")
        print(f"API connection error in get_user_data: {e}")
        return None
    except Exception as e:
        logging.error(f"[GET_USER_DATA] 未知错误: url={api_url}, error={e}", exc_info=True)
        print(f"API request error in get_user_data: {e}")
        return None
def get_username_from_update(update: Update):
    username = "None"
    user = update.effective_user
    if user and user.username:
        username = user.username
    return username
def load_keyword_replies():
    """加载关键词回复配置"""
    global keyword_replies_data
    try:
        keyword_replies_path = 'keyword_replies.json'
        if os.path.exists(keyword_replies_path):
            with open(keyword_replies_path, 'r', encoding='utf-8') as f:
                keyword_replies_data = json.load(f)
            logging.info("关键词回复配置已加载")
        else:
            # 如果文件不存在，使用空字典（后续会从API获取默认值）
            keyword_replies_data = {}
            logging.warning("keyword_replies.json 文件不存在，使用空配置")
    except Exception as e:
        logging.error(f"加载关键词回复配置失败: {e}")
        keyword_replies_data = {}

def send_keyword_reply_modules(update: Update, command_key: str):
    """按照模块顺序发送关键词回复"""
    global keyword_replies_data
    
    if not keyword_replies_data or 'commands' not in keyword_replies_data:
        # 如果配置为空，使用默认文本回复
        default_text = "欢迎使用机器人！"
        if update.message.chat.type == 'private':
            if main_menu_layout:
                keyboard = [[btn['label'] for btn in row] for row in main_menu_layout]
            else:
                keyboard = [
                    ["📦笔数套餐"],
                    ["🛎预存扣费", "✅USDT转TRX"],
                    ["⏰查交易", "⚡️TRX转能量"],
                    ["📢已监听地址", "🔔开始/结束监听"],
                    ["💰我要充值", "👤个人中心"],
                ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            update.message.reply_text(default_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            update.message.reply_text(default_text, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown', disable_web_page_preview=True)
        return
    
    command_modules = keyword_replies_data.get('commands', {}).get(command_key, [])
    if not command_modules:
        # 如果没有找到对应命令的模块，使用默认回复
        default_text = "欢迎使用机器人！"
        if update.message.chat.type == 'private':
            if main_menu_layout:
                keyboard = [[btn['label'] for btn in row] for row in main_menu_layout]
            else:
                keyboard = [
                    ["📦笔数套餐"],
                    ["🛎预存扣费", "✅USDT转TRX"],
                    ["⏰查交易", "⚡️TRX转能量"],
                    ["📢已监听地址", "🔔开始/结束监听"],
                    ["💰我要充值", "👤个人中心"],
                ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            update.message.reply_text(default_text, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            update.message.reply_text(default_text, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown', disable_web_page_preview=True)
        return
    
    # 按 order 排序模块
    sorted_modules = sorted(command_modules, key=lambda x: x.get('order', 0))
    
    # 获取用户信息用于变量替换
    username = get_username_from_update(update)
    user = update.effective_user
    user_nickname = f"{user.first_name} {user.last_name}" if user and user.last_name else (user.first_name if user else '')
    chat_id = update.message.chat_id
    
    # 准备键盘布局（只在最后一个模块发送时附加）
    if update.message.chat.type == 'private':
        if main_menu_layout:
            keyboard = [[btn['label'] for btn in row] for row in main_menu_layout]
        else:
            keyboard = [
                ["📦笔数套餐"],
                ["🛎预存扣费", "✅USDT转TRX"],
                ["⏰查交易", "⚡️TRX转能量"],
                ["📢已监听地址", "🔔开始/结束监听"],
                ["💰我要充值", "👤个人中心"],
            ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    else:
        reply_markup = ReplyKeyboardRemove()
    
    # 遍历模块并按顺序发送
    last_message = None
    for i, module in enumerate(sorted_modules):
        module_type = module.get('type', 'text')
        is_last = (i == len(sorted_modules) - 1)
        
        # 变量替换
        content = module.get('content', '')
        content = content.replace('{username}', user_nickname or '用户')
        content = content.replace('{user_id}', str(chat_id))
        content = content.replace('{chat_id}', str(chat_id))
        
        if module_type == 'text':
            # 纯文本回复
            if is_last and update.message.chat.type == 'private':
                last_message = update.message.reply_text(
                    content, 
                    reply_markup=reply_markup, 
                    parse_mode='Markdown', 
                    disable_web_page_preview=True
                )
            else:
                last_message = update.message.reply_text(
                    content, 
                    parse_mode='Markdown', 
                    disable_web_page_preview=True
                )
        
        elif module_type == 'image':
            # 图片回复
            image_path = module.get('image', '')
            if image_path and os.path.exists(image_path):
                if is_last and update.message.chat.type == 'private':
                    last_message = update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    last_message = update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        parse_mode='Markdown'
                    )
        
        elif module_type == 'text_buttons':
            # 文本 + 内联按钮
            buttons = module.get('buttons', [])
            inline_keyboard = []
            for row in buttons:
                keyboard_row = []
                for btn in row:
                    if btn.get('url'):
                        keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                    elif btn.get('callback_data'):
                        keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']))
                if keyboard_row:
                    inline_keyboard.append(keyboard_row)
            
            inline_markup = InlineKeyboardMarkup(inline_keyboard) if inline_keyboard else None
            
            if is_last and update.message.chat.type == 'private':
                last_message = update.message.reply_text(
                    content,
                    reply_markup=inline_markup if inline_markup else reply_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            else:
                last_message = update.message.reply_text(
                    content,
                    reply_markup=inline_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
        
        elif module_type == 'image_text_buttons':
            # 图片 + 文本 + 内联按钮
            image_path = module.get('image', '')
            buttons = module.get('buttons', [])
            inline_keyboard = []
            for row in buttons:
                keyboard_row = []
                for btn in row:
                    if btn.get('url'):
                        keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                    elif btn.get('callback_data'):
                        keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']))
                if keyboard_row:
                    inline_keyboard.append(keyboard_row)
            
            inline_markup = InlineKeyboardMarkup(inline_keyboard) if inline_keyboard else None
            
            if image_path and os.path.exists(image_path):
                if is_last and update.message.chat.type == 'private':
                    last_message = update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=content,
                        reply_markup=inline_markup if inline_markup else reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    last_message = update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=content,
                        reply_markup=inline_markup,
                        parse_mode='Markdown'
                    )
            else:
                # 如果图片不存在，只发送文本和按钮
                if is_last and update.message.chat.type == 'private':
                    last_message = update.message.reply_text(
                        content,
                        reply_markup=inline_markup if inline_markup else reply_markup,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                else:
                    last_message = update.message.reply_text(
                        content,
                        reply_markup=inline_markup,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )

def start(update: Update, context: CallbackContext):
    if update.message.chat.type == 'private':
        # 使用关键词回复模块发送消息
        send_keyword_reply_modules(update, '/start')
        username = get_username_from_update(update)
        user = update.effective_user
        user_nickname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        handle_start_command(update.message.chat_id, user_nickname, username)
    else:
        # 群组中只发送文本回复
        send_keyword_reply_modules(update, '/start')

def read_config(file_path: str) -> dict:
    config = dict()
    with open(file_path, 'r') as file:
        for line in file.readlines():
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    return config

def load_main_menu_config(config: dict):
    """加载主键盘菜单配置"""
    global main_menu_layout, label_to_key, label_to_chain_id, label_to_chain_id
    
    try:
        # 从配置读取键盘布局 JSON
        menu_json_str = config.get('main_menu_buttons_json', '')
        if menu_json_str:
            # 解析 JSON 字符串
            menu_data = json.loads(menu_json_str)
            main_menu_layout = menu_data
            # 构建 label -> key 和 label -> chain_id 映射
            label_to_key = {}
            label_to_chain_id = {}
            for row in menu_data:
                for btn in row:
                    if isinstance(btn, dict) and 'key' in btn and 'label' in btn:
                        label_to_key[btn['label']] = btn['key']
                        # 如果配置了 chain_id，使用配置的值；否则使用 key 对应的默认 chain_id
                        if 'chain_id' in btn and btn['chain_id']:
                            label_to_chain_id[btn['label']] = int(btn['chain_id'])
                        else:
                            # 向后兼容：根据 key 计算默认 chain_id
                            key_to_chain = {
                                'bishu': 1, 'yucun': 2, 'usdt2trx': 3,
                                'check_tx': 4, 'trx2energy': 5,
                                'monitored_addresses': 6, 'toggle_monitor': 7,
                                'recharge': 8, 'profile': 9
                            }
                            label_to_chain_id[btn['label']] = key_to_chain.get(btn['key'], 0)
            logging.info(f"主键盘菜单配置已加载: {len(label_to_key)} 个按钮，chain_id 映射: {len(label_to_chain_id)} 个")
            # 详细日志：输出所有映射关系
            for label, chain_id in label_to_chain_id.items():
                logging.info(f"  label_to_chain_id: {repr(label)} -> chain_id={chain_id}")
        else:
            # 如果没有配置，使用默认布局（向后兼容）
            logging.warning("未找到 main_menu_buttons_json 配置，使用默认键盘布局")
            main_menu_layout = None
            label_to_key = {}
            label_to_chain_id = {}
    except Exception as e:
        logging.error(f"加载主键盘菜单配置失败: {e}")
        main_menu_layout = None
        label_to_key = {}
        label_to_chain_id = {}

def reload_config():
    """重新加载配置文件"""
    global CUSTOMER_SERVICE_ID, bot_id, group_link, control_address, privateKey, username, password
    global huilv_zhekou, admin_id, hour_price, day_price, yucun_price, three_day_price, message, energy_pool_api, bot_username
    global main_menu_layout, label_to_key, label_to_chain_id, bot_notify_url, keyword_replies_data, usdt2trx_private_key
    
    try:
        logging.info("开始重新加载配置文件...")
        config = read_config('config.txt')
        
        # 更新全局配置变量
        CUSTOMER_SERVICE_ID = config.get('CUSTOMER_SERVICE_ID', CUSTOMER_SERVICE_ID)
        bot_id = config.get('bot_id', bot_id)
        group_link = config.get('group_link', group_link)
        control_address = config.get('control_address', control_address)
        # 优先使用usdt2trx_private_key，如果没有则使用privateKey
        if 'usdt2trx_private_key' in config and config['usdt2trx_private_key'].strip():
            privateKey = config['usdt2trx_private_key'].strip()
        else:
            privateKey = config.get('privateKey', privateKey)
        username = config.get('username', username)
        password = config.get('password', password)
        
        # 更新数值类型的配置
        if 'huilv_zhekou' in config:
            huilv_zhekou = float(config['huilv_zhekou'])
        if 'admin_id' in config:
            admin_id = int(config['admin_id'])
        if 'hour_price' in config:
            hour_price = float(config['hour_price'])
        if 'day_price' in config:
            day_price = float(config['day_price'])
        if 'three_day_price' in config:
            three_day_price = float(config['three_day_price'])
        if 'yucun_price' in config:
            yucun_price = float(config['yucun_price'])
        # 唯一桥链：强制从 config.txt 读取 energy_pool_api
        if 'energy_pool_api' not in config or not config['energy_pool_api'].strip():
            logging.error("config.txt 中必须配置 energy_pool_api（能量池系统地址）")
        else:
            energy_pool_api = config['energy_pool_api'].strip()
            logging.info(f"能量池API（唯一桥链）已更新为: {energy_pool_api}")
        
        # 读取机器人回调地址（bot_notify_url），如果没有配置则使用默认值
        if 'bot_notify_url' in config and config['bot_notify_url'].strip():
            bot_notify_url = config['bot_notify_url'].strip()
            logging.info(f"机器人回调地址已更新为: {bot_notify_url}")
        else:
            # 默认值：本地开发用 host.docker.internal:8080，服务器部署时应在 config.txt 中配置
            notify_port = int(os.getenv('NOTIFY_SERVER_PORT', '8080'))
            bot_notify_url = f'http://host.docker.internal:{notify_port}/api/recharge-notify'
            logging.info(f"使用默认机器人回调地址: {bot_notify_url}")
        
        # 读取USDT转TRX出款私钥，优先使用usdt2trx_private_key，如果没有则使用privateKey
        if 'usdt2trx_private_key' in config and config['usdt2trx_private_key'].strip():
            usdt2trx_private_key = config['usdt2trx_private_key'].strip()
            logging.info(f"USDT转TRX出款私钥已更新")
        elif privateKey and privateKey.strip():
            # 如果没有配置usdt2trx_private_key，使用privateKey作为备用
            usdt2trx_private_key = privateKey.strip()
            logging.info(f"使用系统私钥作为USDT转TRX出款私钥")
        else:
            # 如果都没有配置，设置为None
            usdt2trx_private_key = None
            logging.warning(f"警告：未配置私钥，出币功能将被禁用")
        
        # 加载主键盘菜单配置
        load_main_menu_config(config)
        
        # 重新加载关键词回复配置
        load_keyword_replies()
        
        # 更新机器人用户名（从bot_id提取）
        if 'bot_id' in config:
            bot_id_value = config['bot_id']
            # 从 https://t.me/xxx 格式中提取用户名
            if bot_id_value.startswith('https://t.me/'):
                bot_username = bot_id_value.replace('https://t.me/', '').replace('@', '')
            elif bot_id_value.startswith('@'):
                bot_username = bot_id_value.replace('@', '')
            else:
                bot_username = bot_id_value.replace('@', '')
            logging.info(f"机器人用户名已更新为: {bot_username}")
            
        # 更新message变量
        message = f"\n`{control_address}`\n"
        
        logging.info("配置文件重新加载成功")
        
        # 发送通知给管理员（如果bot已初始化）
        if 'bot' in globals() and bot and admin_id:
            try:
                bot.send_message(
                    chat_id=admin_id,
                    text="🔄 配置已热重载\n\n配置文件已自动重新加载，无需重启机器人。",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logging.warning(f"发送配置重载通知失败: {e}")
                
    except Exception as e:
        logging.error(f"重新加载配置文件失败: {e}")


def get_u_trs_huilv():
    filenames='huilv.txt'
    if not os.path.exists(filenames):
        open(filename, "w").close()
    with open(filenames, 'r') as file:
        for line in file:
            utotrc_huilv = float(line.strip())
    return  utotrc_huilv

def get_account_info(address):

    url = f"https://apilist.tronscan.org/api/account?address={address}"
    headers = {
        'Content-Type': 'application/json',
        'TRON-PRO-API-KEY': "f5da801e-473e-4ffb-9055-eb20ae2e3954"
    }
    response = requests.get(url, headers=headers, timeout=2)
    account_info = response.json()

    balance = int(account_info["balance"]) / 1000000  # TRX 余额（单位：TRX）

    energy_used = account_info["bandwidth"]["energyUsed"]
    energy_limit = account_info["bandwidth"]["energyLimit"]
    energy_remaining = energy_limit - energy_used
    bandwidth_used = account_info["bandwidth"]["freeNetUsed"]
    bandwidth_limit = account_info["bandwidth"]["freeNetLimit"]
    bandwidth_remaining = bandwidth_limit - bandwidth_used

    trc20_balances = account_info.get("trc20token_balances", [])
    usdt_balance = None
    for balance_info in trc20_balances:
        if balance_info["tokenAbbr"] == "USDT":
            usdt_balance = int(balance_info["balance"]) / (10 ** balance_info["tokenDecimal"])
            break
    if usdt_balance==None:
        usdt_balance=0.0

    return energy_remaining, bandwidth_remaining, balance, usdt_balance

def check_trx_balance(tron_address):
    try:
        hex_address = tron.address.to_hex(tron_address)
        url = 'https://api.trongrid.io/wallet/getaccount'
        headers = {
            'Content-Type': 'application/json',
            'TRON-PRO-API-KEY': API_KEY
        }
        data = {'address': hex_address}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        if 'balance' in result and result['balance'] is not None:
            balance = int(result['balance']) / 1000000
            return balance;
        else:
            return 0.000
    except ValueError as e:
        return 0.000

def check_usdt_balance(tron_address):
    result = subprocess.check_output(['node', 'get_balance.js', tron_address])
    result_str = result.decode('utf-8').strip()
    balance = float(result_str)
    return balance

# def get_trxmultiSign(privateKey,mainAddress,toAddress,amount):
#     result = subprocess.check_output(['node', 'trxmultiSign.js', privateKey, mainAddress, toAddress, str(amount)])
#     trn= json.loads(result.decode('utf-8'))
#     return trn
def compare_amounts(transaction_data, address_amounts):
    successMatches = {}
    for chat_id, amount in transaction_data.items():
        if chat_id in address_amounts and address_amounts[chat_id] == amount:
            successMatches[chat_id] = amount
    return successMatches

def update_transaction_file(filename, from_address, amount, yuzi_trx):
    data = {}

    if not os.path.exists(filename):
        open(filename, 'w').close()

    with open(filename, 'r') as f:
        for line in f:
            address, value, trx = line.strip().split()
            data[address] = {"value": float(value), "yuzi_trx": int(trx)}

    if from_address in data:
        data[from_address]["value"] += amount
        data[from_address]["yuzi_trx"] += yuzi_trx
    else:
        data[from_address] = {"value": amount, "yuzi_trx": yuzi_trx}

    with open(filename, 'w') as f:
        for address, info in data.items():
            f.write(f'{address} {info["value"]} {info["yuzi_trx"]}\n')

def upload_to_server(data):
    try:
        # 使用HTTP请求调用前端API
        api_url = f"{API_BASE}/api/bot-update-balance"
        api_data = {
            "chat_id": data['chat_id'],
            "amount": data['amount']
        }
        response = requests.post(api_url, json=api_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("new_balance")
            else:
                print(f"API error in upload_to_server: {result.get('message')}")
                return 0
        else:
            print(f"HTTP error in upload_to_server: {response.status_code}")
            return 0
    except Exception as e:
        print(f"API request error in upload_to_server: {e}")
        return 0


def process_block(block, formatted_date_time, chat_id_jiantingaddress, dizhi_jiantingaddress,transaction_data,bot):
    try:
        with ThreadPoolExecutor() as executor:
            for transaction in block['transactions']:
                executor.submit(process_transaction, transaction, formatted_date_time, chat_id_jiantingaddress,
                                dizhi_jiantingaddress,transaction_data,bot)
    except Exception as e:
        print(f"区块处理错误，{e}")
        return

def process_transaction(transaction,formatted_date_time,chat_id_jiantingaddress,dizhi_jiantingaddress,transaction_data,bot):
    try:
        # 添加数据验证，防止越界和KeyError
        if not transaction or 'ret' not in transaction or not transaction.get('ret'):
            payment_logger.debug(f"交易数据格式异常: ret字段缺失")
            return
        if not transaction.get('txID'):
            payment_logger.debug(f"交易数据格式异常: txID字段缺失")
            return
        
        linshi = transaction['ret'][0]
        transaction_id = transaction['txID']
        keyboard = [
            [
                InlineKeyboardButton("自助服务", url=bot_id),
                InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        # 统一解析第一个合约
        parameter = transaction['raw_data']['contract'][0]
        linshizhi = parameter['parameter']['value']

        # 只有当 ret 成功时才处理
        if 'contractRet' in linshi and linshi['contractRet'] == 'SUCCESS':
            # trc20 监控（USDT）
            if (
                parameter['type'] == 'TriggerSmartContract'
                and '41a614f803b6fd780986a42c78ec9c7f77e6ded13c' == linshizhi['contract_address']
            ):
                to_address = tron.address.from_hex('41' + linshizhi['data'][32:72]).decode()
                if linshizhi['data'][:8] == 'a9059cbb':
                    if to_address == control_address:  # 23b872dd和a9059cbb
                        from_address = tron.address.from_hex(linshizhi['owner_address']).decode()
                        us_amount = int(linshizhi['data'][72:136], 16)
                        if us_amount >= 1000000:
                            sender_trx = gethuilv() * float(us_amount)  # sender_trx单位：sun (TRX的最小单位)
                            control_balance_sun = check_trx_balance(control_address) * 1000000  # 转换为sun单位
                            logging.info(f"[USDT转TRX] 收到USDT转账: {us_amount/1000000} USDT, 应转TRX: {sender_trx/1000000} TRX, control_address余额: {control_balance_sun/1000000} TRX")
                            if control_balance_sun >= sender_trx:  # 检查余额是否足够
                                # 检查是否配置了USDT转TRX出款私钥，必须配置才能出币
                                if not usdt2trx_private_key:
                                    logging.error(f"[USDT转TRX] 出币失败: 未配置出款私钥")
                                    try:
                                        bot.send_message(chat_id=admin_id, text=f'⚠️ USDT转TRX出币失败\n原因：未配置出款私钥\n用户地址：`{from_address}`\nUSDT金额：{float(us_amount) / 1000000} USDT\n应转TRX：{round(sender_trx/1000000, 2)} TRX\n\n请在后台配置"出款TRX私钥"后重试', parse_mode='Markdown')
                                    except Exception as e:
                                        print(f"Error sending message to admin_id {admin_id}: {e}")
                                    return  # 直接返回，不进行出币操作
                                
                                logging.info(f"[USDT转TRX] 使用出款私钥进行出币")
                                tron.private_key = usdt2trx_private_key
                                tron.default_address = tron.address.from_private_key(usdt2trx_private_key).base58
                            try:
                                trx_to_send = float(sender_trx) / 1000000
                                transaction = tron.trx.send_transaction(from_address, trx_to_send)
                                if transaction['result']:

                                    # 返利
                                    today = datetime.now().strftime('%Y-%m-%d')
                                    filename = f'transaction_records_{today}.txt'
                                    final_us_amount = (us_amount * 0.36) / 1000000
                                    with open(filename, 'a') as f:
                                        f.write(f'{from_address}\t{final_us_amount}\n')

                                    amount = transaction['transaction']['raw_data']['contract'][0]['parameter']['value']['amount']
                                    txid = transaction['txid']
                                    xiangqing = f"https://tronscan.org/?utm_source=tronlink #/transaction/{txid}?lang=zh"
                                    for chat_id in all_chats:
                                        try:
                                            text = (
                                                f"✅USDT 兑换 TRX成功\n➖➖➖➖➖➖➖➖\n"
                                                f"交易时间：{formatted_date_time}\n"
                                                f"兑换金额：{float(us_amount / 1000000)} USDT\n"
                                                f"TRX金额：{float(amount) / 1000000} TRX\n"
                                                f"兑换地址：{from_address[:8]}......{from_address[-8:]}\n"
                                                f"交易HASH：[{txid[:8]}......{txid[-8:]}]({xiangqing})"
                                            )
                                            bot.send_message(
                                                chat_id=chat_id,
                                                text=text,
                                                parse_mode='Markdown',
                                                disable_web_page_preview=True,
                                                reply_markup=reply_markup,
                                            )
                                        except Exception as e:
                                            print(f"2Error sending message to chat_id {chat_id}: {e}")
                            except Exception as e:
                                print(f"Error sending transaction: {e}")
                        else:
                            trx_to_send = round(float(sender_trx) / 1000000, 2)
                            logging.warning(f"[USDT转TRX] 余额不足: control_address余额={control_balance_sun/1000000} TRX, 需要={sender_trx/1000000} TRX")
                            try:
                                bot.send_message(chat_id=admin_id,text=f'⚠️ 余额不足，USDT转TRX交易失败  \n哈希：`{transaction_id}`  \n用户地址：`{from_address}`  \nUSDT金额：{float(us_amount) / 1000000} USDT\n应转TRX：{trx_to_send} TRX\ncontrol_address当前余额：{control_balance_sun/1000000} TRX',parse_mode='Markdown')
                            except Exception as e:
                                print(f"Error sending message to admin_id {admin_id}: {e}")
                else:
                    linshizhi_data=linshizhi['data']
                    from_address = tron.address.from_hex(linshizhi['owner_address']).decode()
                    if from_address in dizhi_jiantingaddress :  # 23b872dd和a9059cbb
                        us_amount = int(linshizhi_data[72:], 16)
                        if us_amount >= 1000000:
                            chat_ids = [chat_id for chat_id, jiantingaddress in chat_id_jiantingaddress if jiantingaddress == from_address]
                            for chat_id in chat_ids:
                                try:
                                    _, _, balance, usdt_balance = get_account_info(from_address)
                                    jiantingtext = f'❎*支出提醒  -{float(us_amount) / 1000000}USDT*\n付款地址：`{from_address}` \n收款地址：`{to_address}`\n交易时间：{formatted_date_time}\n交易金额：{float(us_amount) / 1000000}USDT' \
                                                   f'\n账户余额：{round(balance, 2)}TRX，{round(usdt_balance, 2)}USDT'
                                    bot.send_message(chat_id, jiantingtext, parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup)
                                except Exception as e:
                                    print(f"Error sending message to chat_id {chat_id}: {e}")
                                    continue
                    if to_address in dizhi_jiantingaddress :  # 收入
                        us_amount = int(linshizhi_data[72:], 16)
                        if us_amount >= 1000000:
                            chat_ids = [chat_id for chat_id, jiantingaddress in chat_id_jiantingaddress if jiantingaddress == to_address]
                            for chat_id in chat_ids:
                                try:
                                    _, _, balance, usdt_balance = get_account_info(to_address)
                                    jiantingtext = f'✅*收入到账  +{float(us_amount) / 1000000}USDT*\n付款地址：`{from_address}` \n收款地址：`{to_address}`\n交易时间：{formatted_date_time}\n交易金额：{float(us_amount) / 1000000}USDT' \
                                                   f'\n账户余额：{round(balance, 2)}TRX，{round(usdt_balance, 2)}USDT'
                                    bot.send_message(chat_id, jiantingtext, parse_mode='Markdown',disable_web_page_preview=True, reply_markup=reply_markup)
                                except Exception as e:
                                    print(f"Error sending message to chat_id {chat_id}: {e}")
                                    continue

        # TRX 充值（TransferContract）——用于匹配金额并给机器人账户充值余额
        if parameter['type'] == 'TransferContract':
            linshizhi = parameter['parameter']['value']
            to_address = tron.address.from_hex(linshizhi['to_address']).decode()
            from_address = tron.address.from_hex(linshizhi['owner_address']).decode()
            # 优化：移除频繁的DEBUG日志（每笔TransferContract都输出），只在真正收到支付时记录
            if to_address==control_address:
                us_amount = int(linshizhi['amount'])
                # 使用logger记录支付信息，可通过日志级别控制输出
                payment_logger.info(f"收到支付: {us_amount} sun ({us_amount/1000000} TRX), from={from_address}")
                # 直接在主代码中比较金额并提取匹配的chat_id
                matched_chat_id = None
                if len(transaction_data) > 0:
                    for chat_id, amount in transaction_data.items():
                        if amount * 1000000 == us_amount:
                            data_to_upload = {"chat_id": chat_id, "amount": us_amount}
                            balance = upload_to_server(data_to_upload)
                            try:
                                # 给用户发充值成功提示
                                bot.send_message(
                                    chat_id=chat_id,
                                    text=f'充值成功,您的余额已更新\n目前余额：{balance/1000000}TRX',
                                    reply_markup=reply_markup,
                                )
                                
                                # 给管理员发通知
                                bot.send_message(
                                    chat_id=admin_id,
                                    text=f'用户{chat_id}，充值{us_amount / 1000000}TRX,\n目前余额：{balance / 1000000}TRX',
                                )
                                
                                # 更新本地 orders 表中该用户最近一条待支付充值订单为已完成
                                try:
                                    amount_trx = us_amount / 1000000.0
                                    conn = mysql.connector.connect(**config)
                                    cursor = conn.cursor()
                                    update_query = """
                                    UPDATE orders
                                    SET status = 'completed', updated_at = NOW()
                                    WHERE chat_id = %s AND amount = %s AND status = 'pending'
                                    ORDER BY created_at DESC
                                    LIMIT 1
                                    """
                                    cursor.execute(update_query, (chat_id, amount_trx))
                                    conn.commit()
                                    if cursor.rowcount == 0:
                                        payment_logger.info(
                                            f"[充值订单] 未找到待支付订单可更新, chat_id={chat_id}, amount={amount_trx}"
                                        )
                                    else:
                                        payment_logger.info(
                                            f"[充值订单] 已更新为完成: chat_id={chat_id}, amount={amount_trx}"
                                        )
                                except Exception as order_err:
                                    payment_logger.error(
                                        f"[充值订单] 更新 orders 表失败, chat_id={chat_id}, us_amount={us_amount}, err={order_err}"
                                    )
                                finally:
                                    try:
                                        cursor.close()
                                        conn.close()
                                    except Exception:
                                        pass
                            except Exception as e:
                                print(f"Error sending message to chat_id {chat_id}: {e}")

                # 使用整数作为键避免浮点数精度问题
                energy_params = {
                    int(hour_price*1000000): (65000, "1小时1次", 0),
                    int(hour_price*1000000 * 2): (65000*2, "1小时2次", 0),
                    int(hour_price*1000000 * 5): (65000*5, "1小时5次", 0),
                    int(hour_price*1000000 * 10): (65000*10, "1小时10次", 0),
                    int(day_price*1000000 * 5): (65000*5, "1天5次", 1),
                    int(day_price*1000000 * 10): (65000*10, "1天10次", 1),
                    int(day_price*1000000 * 20): (65000*20, "1天20次", 1),
                    int(day_price*1000000 * 50): (65000*50, "1天50次", 1),
                    int(three_day_price*1000000 * 30): (65000*10, "3天内每天10次", 3),
                    int(three_day_price*1000000 * 60): (65000*20, "3天内每天20次", 3),
                    int(three_day_price*1000000 * 90): (65000*30, "3天内每天30次", 3),
                    int(three_day_price*1000000 * 150): (65000*50, "3天内每天50次", 3),
                }
                # 查找指定的 us_amount，支持容差匹配（±1000 sun = ±0.001 TRX）
                payment_logger.debug(f"检查energy_params, us_amount={us_amount}, 可用套餐={list(energy_params.keys())}")
                
                # 先尝试精确匹配
                matched_params = None
                if us_amount in energy_params:
                    matched_params = energy_params[us_amount]
                else:
                    # 容差匹配：允许 ±1000 sun 的误差
                    for price, params in energy_params.items():
                        if abs(us_amount - price) <= 1000:
                            payment_logger.debug(f"容差匹配成功: 支付金额={us_amount}, 套餐金额={price}, 差异={us_amount - price}")
                            matched_params = params
                            break
                
                if matched_params:
                    energy, desc, days = matched_params
                    payment_logger.info(f"匹配到能量套餐: {desc}, energy={energy}, days={days}, 接收地址={from_address}")

                    # result = energy_tran(energy, days, from_address)
                    # if result.get("success"):

                    result = energy_tran2(energy, days, from_address)
                    payment_logger.debug(f"能量API调用结果: {result}")
                    if result.get("success"):
                        txid = result.get("tx_hash")
                        transaction_url = f"https://tronscan.org/?utm_source=tronlink#/transaction/{txid}?lang=zh"
                        # 查询本系统的 API 用户余额（而不是上游的）
                        api_balance = 0
                        try:
                            balance_resp = requests.get(
                                f'{energy_pool_api}/v1/get_api_user_info',
                                params={'username': username, 'password': password},
                                timeout=5
                            )
                            if balance_resp.status_code == 200:
                                balance_info = balance_resp.json()
                                api_balance = balance_info.get('当前余额 (TRX)', 0)
                        except Exception as balance_error:
                            payment_logger.debug(f"查询API余额失败: {balance_error}")
                        
                        # 生成订单号
                        order_number = f"ENERGY_{int(time.time())}_{from_address[:8]}"
                        
                        # 保存订单到数据库（TRX转能量订单没有chat_id，使用0作为占位符）
                        try:
                            save_order_to_db(
                                chat_id=0,  # TRX转能量订单没有chat_id（用户直接转账），使用0作为占位符
                                order_number=order_number,
                                energy_amount=energy,
                                duration=desc,
                                receiver_address=from_address,
                                amount=us_amount / 1000000.0,
                                payment_method='trx',
                                status='completed',
                                tx_hash=txid,
                                remark=f"能量套餐：{desc}"
                            )
                            payment_logger.info(f"[能量订单] 保存成功: order_number={order_number}, 地址={from_address}, 金额={us_amount/1000000} TRX")
                        except Exception as order_err:
                            payment_logger.error(f"[能量订单] 保存失败: {order_err}")
                        
                        # 用户通知消息
                        user_text = (f"✅能量租用 下发完成\n➖2➖2➖2➖2➖2➖2➖2➖2\n"
                                f"套餐模式：笔数模式\n"
                                f"能量带宽：{energy}\n"
                                f"有效时长：{desc}\n"
                                f"接收地址：{from_address[:8]}......{from_address[-8:]}\n"
                                f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})"
                                f"")
                        
                        # 管理员通知消息
                        admin_text = (f"✅用户购买能量成功\n"
                                     f"订单号：{order_number}\n"
                                     f"支付金额：{us_amount/1000000} TRX\n"
                                     f"套餐：{desc}\n"
                                     f"能量：{energy}\n"
                                     f"接收地址：`{from_address}`\n"
                                     f"交易哈希：[{txid[:6]}...{txid[-6:]}]({transaction_url})\n"
                                     f"API余额：{api_balance} TRX")
                        
                        # 发送给管理员
                        try:
                            bot.send_message(
                                chat_id=admin_id,
                                text=admin_text,
                                disable_web_page_preview=True,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            payment_logger.error(f"发送管理员通知失败: {e}")
                        
                        # 发送给用户（如果用户地址在监听列表中）
                        for chat_id in all_chats:
                            try:
                                bot.send_message(
                                    chat_id=chat_id,
                                    text=user_text,
                                    parse_mode='Markdown',
                                    disable_web_page_preview=True,
                                    reply_markup=reply_markup,
                                )
                            except Exception as e:
                                payment_logger.debug(f"发送用户通知失败: chat_id={chat_id}, error={e}")
                    else:
                        # 能量下发失败，只通知管理员（不发送"兑换失败"给用户，因为用户购买能量是发送TRX，不需要兑币）
                        # 获取详细的错误信息
                        error_msg = result.get("message") or result.get("error") or result.get("msg") or str(result)
                        if not error_msg or error_msg == "{}":
                            error_msg = "能量池API调用失败，请检查API状态"
                        payment_logger.error(f"能量下发失败: 地址={from_address}, 金额={us_amount/1000000} TRX, 错误={error_msg}, result={result}")
                        
                        # 生成订单号并保存失败订单到数据库
                        order_number = f"ENERGY_FAIL_{int(time.time())}_{from_address[:8]}"
                        try:
                            save_order_to_db(
                                chat_id=0,  # TRX转能量订单没有chat_id（用户直接转账），使用0作为占位符
                                order_number=order_number,
                                energy_amount=energy,
                                duration=desc,
                                receiver_address=from_address,
                                amount=us_amount / 1000000.0,
                                payment_method='trx',
                                status='failed',
                                tx_hash=None,
                                remark=f"能量套餐失败：{desc}，错误：{error_msg[:50]}"  # 限制错误信息长度
                            )
                            payment_logger.info(f"[能量订单] 失败订单已保存: order_number={order_number}, 地址={from_address}, 金额={us_amount/1000000} TRX")
                        except Exception as order_err:
                            payment_logger.error(f"[能量订单] 保存失败订单失败: {order_err}")
                        
                        try:
                            # 使用HTML格式避免Markdown解析错误
                            admin_error_text = (
                                f"❌能量下发失败\n"
                                f"订单号：{order_number}\n"
                                f"支付地址：<code>{from_address}</code>\n"
                                f"支付金额：{us_amount/1000000} TRX\n"
                                f"套餐：{desc}\n"
                                f"能量：{energy}\n"
                                f"错误详情：{error_msg[:200]}\n"
                                f"请检查能量池API状态或手动处理"
                            )
                            bot.send_message(
                                chat_id=admin_id,
                                text=admin_error_text,
                                parse_mode='HTML',  # 改用HTML格式避免Markdown解析错误
                            )
                        except Exception as e:
                            payment_logger.error(f"发送管理员错误通知失败: {e}")
                            # 如果HTML格式也失败，尝试纯文本
                            try:
                                admin_error_text_plain = (
                                    f"❌能量下发失败\n"
                                    f"订单号：{order_number}\n"
                                    f"支付地址：{from_address}\n"
                                    f"支付金额：{us_amount/1000000} TRX\n"
                                    f"套餐：{desc}\n"
                                    f"能量：{energy}\n"
                                    f"错误详情：{error_msg[:200]}\n"
                                    f"请检查能量池API状态或手动处理"
                                )
                                bot.send_message(
                                    chat_id=admin_id,
                                    text=admin_error_text_plain,
                                )
                            except Exception as e2:
                                payment_logger.error(f"发送管理员错误通知（纯文本）也失败: {e2}")
                else:
                    # 未匹配到任何套餐，通知管理员（说明原因，便于理解）
                    payment_logger.warning(f"未匹配到套餐: 支付金额={us_amount} sun ({us_amount/1000000} TRX), 接收地址={from_address}")
                    try:
                        bot.send_message(
                            chat_id=admin_id,
                            text=(
                                "⚠️收到支付但未匹配套餐\n"
                                f"地址: `{from_address}`\n"
                                f"金额: {us_amount/1000000} TRX\n"
                                "说明: 收款金额不是任何固定套餐金额，可能是测试或非套餐转账，可按需忽略。\n"
                                f"可用套餐金额(sun): {list(energy_params.keys())}"
                            ),
                            parse_mode='Markdown',
                        )
                    except Exception as e:
                        print(f"Error sending unmatched notification: {e}")

            if to_address in dizhi_jiantingaddress:  # 收入
                us_amount = int(linshizhi['amount'])
                if us_amount >= 1000000:
                    chat_ids = [chat_id for chat_id, jiantingaddress in chat_id_jiantingaddress if
                                jiantingaddress == to_address]
                    for chat_id in chat_ids:
                        try:
                            _, _, balance, usdt_balance = get_account_info(to_address)
                            jiantingtext = f'✅*收入到账  +{float(us_amount) / 1000000}TRX*\n付款地址：`{from_address}` \n收款地址：`{to_address}`\n交易时间：{formatted_date_time}\n交易金额：{float(us_amount) / 1000000}TRX' \
                                           f'\n账户余额：{round(balance, 2)}TRX，{round(usdt_balance, 2)}USDT'
                            bot.send_message(chat_id, jiantingtext, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
                        except Exception as e:
                            print(f"Error sending message to chat_id {chat_id}: {e}")
                            continue
            if from_address in dizhi_jiantingaddress:  # 支出
                us_amount = int(linshizhi['amount'])
                if us_amount >= 1000000:
                    chat_ids = [chat_id for chat_id, jiantingaddress in chat_id_jiantingaddress if
                                jiantingaddress == from_address]
                    for chat_id in chat_ids:
                        try:
                            _, _, balance, usdt_balance = get_account_info(from_address)
                            jiantingtext = f'❎*支出提醒  -{float(us_amount) / 1000000}TRX*\n付款地址：`{from_address}` \n收款地址：`{to_address}`\n交易时间：{formatted_date_time}\n交易金额：{float(us_amount) / 1000000}TRX' \
                                           f'\n账户余额：{round(balance, 2)}TRX，{round(usdt_balance, 2)}USDT'
                            bot.send_message(chat_id, jiantingtext, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
                        except Exception as e:
                            print(f"Error sending message to chat_id {chat_id}: {e}")
                            continue
    except (KeyError, IndexError, ValueError, AttributeError) as e:
        # 数据格式错误，记录但不中断其他交易处理
        payment_logger.debug(f"交易数据解析错误 (txID: {transaction.get('txID', 'unknown')}): {type(e).__name__}: {e}")
    except Exception as e:
        # 其他未预期的错误，记录详细堆栈信息
        import traceback
        payment_logger.error(f"处理交易时发生未预期错误 (txID: {transaction.get('txID', 'unknown')}): {e}\n{traceback.format_exc()}")

def saokuai(bot):
    full_node = 'https://api.trongrid.io'
    solidity_node = 'https://api.trongrid.io'
    event_server = 'https://api.trongrid.io'

    tron = Tron(full_node=full_node,
                solidity_node=solidity_node,
                event_server=event_server,
                headers={
                    'TRON-PRO-API-KEY': API_KEY
                })

    current_block_number = tron.trx.get_current_block()['block_header']['raw_data']['number']
    # 在这里运行您的代码
    last_processed_block_number = None
    while True:

        start_time = time.time()  # 获取当前时间
        # Get the latest block number
        all_time = 3.0
        # 跳过已经处理过的块
        if last_processed_block_number == current_block_number:
            print(f"Skipping block {current_block_number} because it's already processed.")
            current_block_number += 1
            continue
        try:
            try:
                url = f"https://api.trongrid.io/wallet/getblockbynum"
                params = {"num": current_block_number}
                headers = {"TRON-PRO-API-KEY": API_KEY}
                response = requests.post(url, json=params, headers=headers, timeout=5)
                if response.status_code != 200:
                    time.sleep(2)
                    continue
                block = response.json()
                if not block:
                    print(f"Block data is empty for block number: {current_block_number}")
                    time.sleep(2)
                    continue
                if block.get("transactions") is None:
                    time.sleep(2)
                    current_block_number += 1
                    continue
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                payment_logger.warning(f"获取区块数据失败 (区块 {current_block_number}): {type(e).__name__}: {e}")
                time.sleep(5)  # 网络错误时等待更长时间
                continue
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                payment_logger.warning(f"解析区块数据失败 (区块 {current_block_number}): {type(e).__name__}: {e}")
                time.sleep(2)
                current_block_number += 1
                continue
            except Exception as e:
                import traceback
                payment_logger.error(f"获取区块时发生未预期错误 (区块 {current_block_number}): {e}\n{traceback.format_exc()}")
                time.sleep(5)
                continue
            transaction_data = []
            # 确保文件存在
            if not os.path.exists("transaction_data.txt"):
                open("transaction_data.txt", "w").close()
            if os.stat("transaction_data.txt").st_size != 0:
                transaction_data = read_data_from_file("transaction_data.txt")
            if 'transactions' in block and block['transactions']:
                qukuaitimestamp = block['block_header']['raw_data']['timestamp']
                date_time = datetime.fromtimestamp(qukuaitimestamp / 1000)
                formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
                if abs(int(time.time()) - qukuaitimestamp / 1000) > 5:
                    all_time = 1.8
                filename = '监听.txt'
                if not os.path.exists(filename):
                    open(filename, "w").close()
                chat_id_jiantingaddress = []
                dizhi_jiantingaddress = set()
                with open(filename, "r") as file:
                    for line_num, line in enumerate(file, 1):
                        try:
                            line = line.strip()
                            # 跳过空行和格式不正确的行
                            if not line or " - " not in line:
                                continue
                            
                            parts = line.split(" - ")
                            if len(parts) < 3:
                                payment_logger.debug(f"监听.txt 第{line_num}行格式错误: {line}")
                                continue
                            
                            timestamp, chat_id_str, address_str = parts[0], parts[1], parts[2]
                            if ": " not in chat_id_str or ": " not in address_str:
                                payment_logger.debug(f"监听.txt 第{line_num}行格式错误: {line}")
                                continue
                            
                            chat_id = chat_id_str.split(": ")[1]
                            jiantingaddress = address_str.split(": ")[1]
                            chat_id_jiantingaddress.append((chat_id, jiantingaddress))
                            dizhi_jiantingaddress.add(jiantingaddress)
                        except Exception as e:
                            payment_logger.warning(f"解析监听.txt 第{line_num}行失败: {line}, 错误: {e}")
                            continue
                # 在你的主循环中调用 process_block() 函数来处理区块
                process_block(block, formatted_date_time, chat_id_jiantingaddress, dizhi_jiantingaddress,transaction_data,bot)
            last_processed_block_number = current_block_number  # 更新已处理块编号
            current_block_number += 1
        except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
            # 网络错误，记录并继续
            payment_logger.warning(f"网络请求异常 (区块 {current_block_number}): {type(e).__name__}: {e}")
            time.sleep(5)  # 网络错误时等待更长时间
            continue
        except (KeyError, ValueError, TypeError) as e:
            # 数据格式错误，记录并继续
            payment_logger.warning(f"区块数据格式错误 (区块 {current_block_number}): {type(e).__name__}: {e}")
            current_block_number += 1
            continue
        except Exception as e:  # 其他未预期错误
            import traceback
            payment_logger.error(f'程序异常 (区块 {current_block_number})，请检查服务器: {e}\n{traceback.format_exc()}')
            time.sleep(5)  # 发生错误时等待一段时间再继续

        end_time = time.time()  # 获取当前时间
        elapsed_time = end_time - start_time  # 计算运行时间

        # Wait for the next poll
        interval = max(all_time - elapsed_time, 0)  # 确保interval不小于0
        time.sleep(interval)


def read_data_from_file(filename):
    data = {}
    lines_to_keep = []

    with open(filename, "r") as file:
        for line in file:
            record = line.strip().split(",")
            amount = float(record[0])
            expiration_time = record[1]
            chat_id = int( record[2])

            # 解析过期时间
            expiration_datetime = datetime.strptime(expiration_time, '%Y-%m-%d %H:%M:%S')

            # 获取当前时间
            now = datetime.now()

            # 如果当前时间小于过期时间，表示记录仍有效，则添加到数据字典中
            if now < expiration_datetime:
                data[chat_id] = amount
                lines_to_keep.append(line)
            # 否则，不要保留这行

    # 使用"lines_to_keep"中保留的行覆盖原始文件
    with open(filename, "w") as file:
        file.writelines(lines_to_keep)

    return data

def get_amount_from_file(filename, from_address):
    if not os.path.exists(filename):
        open(filename, "w").close()
    with open(filename, 'r') as f:
        for line in f:
            address, value = line.strip().split()
            if address == from_address:
                return float(value)
            else:
                return None
    return None
def get_amount_from_file(filename, from_address):
    if not os.path.exists(filename):
        open(filename, "w").close()
    with open(filename, 'r') as f:
        for line in f:
            address, value, _ = line.strip().split()
            if address == from_address:
                return float(value)
    return None


def get_yuzi_trx_from_address(filename, from_address):
    if not os.path.exists(filename):
        open(filename, "w").close()

    with open(filename, 'r') as f:
        for line in f:
            address, _, yuzi_trx = line.strip().split()

            if address == from_address:
                yuzi_trx_int = int(float(yuzi_trx))  # 先将字符串转换为浮点数，然后转换为整数
                return yuzi_trx_int
    return 0

def get_message_key(message_text: str) -> str:
    """根据消息文本获取对应的 key（用于功能路由，向后兼容）"""
    # 如果配置了 label_to_key 映射，优先使用
    if label_to_key and message_text in label_to_key:
        return label_to_key[message_text]
    # 向后兼容：如果没有配置，使用默认映射
    default_map = {
        '📦笔数套餐': 'bishu',
        '🛎预存扣费': 'yucun',
        '✅USDT转TRX': 'usdt2trx',
        '⏰查交易': 'check_tx',
        '⚡️TRX转能量': 'trx2energy',
        '📢已监听地址': 'monitored_addresses',
        '🔔开始/结束监听': 'toggle_monitor',
        '💰我要充值': 'recharge',
        '👤个人中心': 'profile'
    }
    return default_map.get(message_text, '')

def get_message_chain_id(message_text: str) -> int:
    """根据消息文本获取对应的 chain_id（用于功能路由）"""
    # 如果配置了 label_to_chain_id 映射，优先使用
    if label_to_chain_id and message_text in label_to_chain_id:
        chain_id = label_to_chain_id[message_text]
        if message_text in ['✅ USDT转TRX', '✅USDT转TRX']:
            logging.info(f"[DEBUG] get_message_chain_id: 从label_to_chain_id映射中找到 {repr(message_text)} -> chain_id={chain_id}")
        return chain_id
    # 向后兼容：如果没有配置，使用默认映射（根据 key 计算）
    message_key = get_message_key(message_text)
    key_to_chain = {
        'bishu': 1, 'yucun': 2, 'usdt2trx': 3,
        'check_tx': 4, 'trx2energy': 5,
        'monitored_addresses': 6, 'toggle_monitor': 7,
        'recharge': 8, 'profile': 9
    }
    chain_id = key_to_chain.get(message_key, 0)
    if message_text in ['✅ USDT转TRX', '✅USDT转TRX']:
        logging.warning(f"[DEBUG] get_message_chain_id: 未在label_to_chain_id中找到 {repr(message_text)}，回退到key映射: message_key={message_key}, chain_id={chain_id}")
        logging.warning(f"[DEBUG] 当前label_to_chain_id映射keys: {list(label_to_chain_id.keys()) if label_to_chain_id else 'None'}")
    return chain_id

def handle_message(update: Update, context: CallbackContext):
    # 声明全局变量
    global username, password
    
    # 添加详细日志，记录所有收到的消息
    if update.message is not None:
        logging.info(f"[DEBUG] handle_message 被调用: chat_type={update.message.chat.type}, message_text={repr(update.message.text) if update.message.text else 'None'}")
    
    if update.message is not None and update.message.chat.type == 'private':
        chat_id = update.effective_chat.id
        message_text = update.message.text if update.message.text else ''
        
        # 确保用户已注册：如果用户不存在，自动注册
        try:
            user_data = get_user_data(chat_id)
            if not user_data:
                # 用户不存在，自动注册
                username = get_username_from_update(update)
                user = update.effective_user
                user_nickname = f"{user.first_name} {user.last_name}" if user.last_name else (user.first_name or '')
                handle_start_command(chat_id, user_nickname, username)
                logging.info(f"[AUTO_REGISTER] 自动注册用户: chat_id={chat_id}, username={username}, nickname={user_nickname}")
        except Exception as e:
            logging.error(f"[AUTO_REGISTER] 自动注册用户失败: {e}")
            # 继续处理消息，不中断流程
        # 获取消息对应的 key（向后兼容）和 chain_id（用于功能路由）
        message_key = get_message_key(message_text)
        message_chain_id = get_message_chain_id(message_text)
        
        # 调试日志：记录查交易相关消息
        if "查交易" in message_text or message_chain_id == 4:
            logging.info(f"[DEBUG] 查交易消息: chat_id={chat_id}, message_text={repr(message_text)}, message_chain_id={message_chain_id}, message_key={message_key}")
        
        # 调试日志：记录所有消息（特别是按钮点击）
        if message_text in ['✅ USDT转TRX', '✅USDT转TRX'] or message_chain_id == 3:
            logging.info(f"[DEBUG] USDT转TRX按钮点击: chat_id={chat_id}, message_text={repr(message_text)}, message_chain_id={message_chain_id}, message_key={message_key}")
            logging.info(f"[DEBUG] label_to_chain_id映射: {label_to_chain_id}")
            logging.info(f"[DEBUG] label_to_key映射: {label_to_key}")
        if message_text == "查询后台信息":
            logging.info(f"[DEBUG] 收到查询后台信息消息，chat_id={chat_id}, message_text={repr(message_text)}, message_chain_id={message_chain_id}, message_key={message_key}")
            logging.info(f"[DEBUG] 检查条件: message_chain_id > 0 = {message_chain_id > 0}")
        #保存每天聊天记录
        # 优先根据 chain_id 路由功能（如果 chain_id 有效，只根据它路由；否则回退到 message_key）
        # 注意：如果"查询后台信息"有 chain_id，会被这里拦截，需要确保它没有 chain_id
        
        # 如果消息是纯地址（不在任何特殊状态），自动触发功能链4（查交易）
        if (message_chain_id == 0 and 
            tron.isAddress(message_text) and 
            context.user_data.get("bishu_add_address") != INPUT_BISHU_ADDRESS and
            context.user_data.get('recharge') != INPUT_RECHARGE_AMOUNT and
            context.user_data.get("bangding") != INPUT_ADDRESS and
            context.user_data.get("shanchu") != delete_ADDRESS):
            logging.info(f"[DEBUG] 检测到纯地址，自动触发功能链4（查交易）: {message_text}")
            try:
                usdt_tx = gettransaction(message_text)
                trx_tx = get_trx_transaction(message_text)
                result_text = f"您的交易记录：\n{usdt_tx}\n{trx_tx}\n--------------"
                update.message.reply_text(result_text, parse_mode='Markdown', disable_web_page_preview=True)
                logging.info(f"[DEBUG] 查交易 - 结果已发送（自动识别地址）")
            except Exception as e:
                logging.error(f"[查交易] 查询失败: {e}", exc_info=True)
                update.message.reply_text(f"查询交易记录时出错，请稍后重试\n错误: {str(e)}")
            return
        
        if message_chain_id > 0:
            if message_text == "查询后台信息":
                logging.warning(f"[DEBUG] 警告：查询后台信息被 message_chain_id={message_chain_id} 拦截！")
            # 只根据 chain_id 路由，不再检查 message_key
            if message_chain_id == 6:
                filename='监听.txt'
                if not os.path.exists(filename):
                    open(filename, "w").close()
                    update.message.reply_text("暂无地址")
                    return
                chat_id = update.effective_chat.id
                text = ""
                with open(filename, 'r') as f:
                    for line in f:
                        if str(chat_id) in line:
                            addresss = line.split('地址: ')[-1].strip()
                            text += f"`{addresss}`\n"
                if text != "":
                    update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
                else:
                    update.message.reply_text("此账户无监听地址")
                return
            elif message_chain_id == 7:
                # 检查消息是否包含地址（格式：开始监听 地址 或 结束监听 地址）
                if "开始监听 " in message_text or "结束监听 " in message_text:
                    # 用户输入了地址，执行监听逻辑
                    if "开始监听 " in message_text:
                        split_str = message_text.split(' ')
                        if len(split_str) >= 2 and tron.isAddress(split_str[1]):
                            address = split_str[1]
                            chat_id = update.effective_chat.id
                            
                            # 检查是否是禁止监听的地址
                            if address == control_address or address == "TSaRZDiBPD8Rd5vrvX8a4zgunHczM9mj8S":
                                update.message.reply_text("此地址暂不支持监听")
                                return
                            
                            # 检查地址是否已存在
                            filename = "监听.txt"
                            address_exists = False
                            if os.path.exists(filename):
                                with open(filename, "r") as file:
                                    for line in file:
                                        if f"chat_id: {chat_id}" in line and f"地址: {address}" in line:
                                            address_exists = True
                                            break
                            
                            if address_exists:
                                update.message.reply_text("地址已存在")
                            else:
                                # 添加新地址
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                with open(filename, "a") as file:
                                    file.write(f"{timestamp} - chat_id: {chat_id} - 地址: {address}\n")
                                update.message.reply_text(f"已添加监听地址: {address}")
                        else:
                            update.message.reply_text("请输入正确的TRX地址")
                    elif "结束监听 " in message_text:
                        split_str = message_text.split(' ')
                        if len(split_str) >= 2 and tron.isAddress(split_str[1]):
                            address = split_str[1]
                            filename = "监听.txt"
                            chat_id = update.effective_chat.id
                            
                            # 删除监听地址
                            if os.path.exists(filename):
                                with open(filename, "r") as file:
                                    lines = file.readlines()
                                with open(filename, "w") as file:
                                    removed = False
                                    for line in lines:
                                        if f"chat_id: {chat_id}" in line and f"地址: {address}" in line:
                                            removed = True
                                            continue
                                        file.write(line)
                                    if removed:
                                        update.message.reply_text(f"已结束监听地址: {address}")
                                    else:
                                        update.message.reply_text("该地址未在监听列表中")
                        else:
                            update.message.reply_text("请输入正确的TRX地址")
                else:
                    # 用户只点击了按钮，显示格式说明
                    update.message.reply_text("每次只支持输入一个地址,监听包含trc20和trx\n格式(结束同理)：开始监听 地址（中间有空格）\n开始监听 TEfbxrUwvwZY8dYJx8tt7RXLF3XXXXXXXX")
                return
            elif message_chain_id == 3:
                logging.info(f"[DEBUG] 进入功能链3处理: USDT转TRX, chat_id={chat_id}")
                try:
                    keyboard = [
                        [
                            InlineKeyboardButton("加入群组", url=group_link),
                            InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID)
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    now_huilv=gethuilv()
                    logging.info(f"[DEBUG] 获取汇率成功: now_huilv={now_huilv}")
                    balance = check_trx_balance(control_address) / now_huilv
                    rounded_balance = round(balance, 2)
                    logging.info(f"[DEBUG] 计算余额成功: balance={balance}, rounded_balance={rounded_balance}")
                    text = f"*当前可兑：{rounded_balance} USDT*\n" \
                           f"*当前兑换比例1:{now_huilv}*\n" \
                           f"24小时进U自动兑，1U起兑\n" \
                           f"收款trc20地址为：\n\n" \
                           f"`{control_address}`\n" \
                           "(点击可复制)\n" + "‼️*注意:请勿使用交易所转账,丢失自负*"
                    logging.info(f"[DEBUG] 准备发送USDT转TRX消息，text长度={len(text)}")
                    update.message.reply_text(text,parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
                    logging.info(f"[DEBUG] USDT转TRX消息已发送")
                    return
                except Exception as e:
                    logging.error(f"[ERROR] 功能链3处理失败: {e}", exc_info=True)
                    # 发送错误提示给用户
                    error_text = f"⚠️ 获取汇率失败，请稍后重试\n错误信息: {str(e)}"
                    update.message.reply_text(error_text)
                return
            elif message_chain_id == 5:
                try:
                    address_text = f"{control_address}"
                    filename = "能量按钮.txt"
                    # 默认按钮
                    button_text = "🔋联系客服"
                    button_url = CUSTOMER_SERVICE_ID
                    try:
                        buttons_data = read_buttons_from_txt(filename)
                        if buttons_data and len(buttons_data) > 0:
                            # 支持中文逗号和英文逗号
                            line = buttons_data[0]
                            if "，" in line:
                                button_text, button_url = line.split("，", 1)
                            elif "," in line:
                                button_text, button_url = line.split(",", 1)
                    except Exception as e:
                        print(f"读取能量按钮.txt失败: {e}")
                    # 创建按钮
                    button_list = [
                    [
                        InlineKeyboardButton("👇有效期1小时👇", callback_data="tittle"),

                    ],
                    [
                        InlineKeyboardButton("1次", callback_data="hour_1"),
                        InlineKeyboardButton("2次", callback_data="hour_2"),
                        InlineKeyboardButton("5次", callback_data="hour_5"),
                        InlineKeyboardButton("10次", callback_data="hour_10"),
                    ],
                    [
                        InlineKeyboardButton("👇有效期1天👇", callback_data="tittle"),

                    ],
                    # 注意这里添加了逗号
                    [
                        InlineKeyboardButton("5次", callback_data="day_5"),
                        InlineKeyboardButton("10次", callback_data="day_10"),
                        InlineKeyboardButton("20次", callback_data="day_20"),
                        InlineKeyboardButton("50次", callback_data="day_50"),

                    ],
                    [
                        InlineKeyboardButton("👇有效期3天（每天笔数）👇", callback_data="tittle"),

                    ],
                    [
                        InlineKeyboardButton("10次", callback_data="day3_10"),
                        InlineKeyboardButton("20次", callback_data="day3_20"),
                        InlineKeyboardButton("30次", callback_data="day3_30"),
                        InlineKeyboardButton("50次", callback_data="day3_50"),
                    ],
                        [
                            InlineKeyboardButton(button_text, url=button_url)
                        ]
                    ]
                    # 创建键盘布局
                    reply_markup = InlineKeyboardMarkup(button_list)
                    text = f'*提示：所示金额为对方有U的转账手续费，如对方无U请再次购买*\n' \
                           f"‼️24小时自动到账，兑能量暂时不支持其他金额！\n" \
                           f"收款trc20接收地址为：\n\n" \
                           f"`{address_text}`\n" \
                           "(点击可复制)\n" +"‼️*注意:请勿使用交易所转账,丢失自负*"
                    update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
                except Exception as e:
                    print(f"TRX转能量处理失败: {e}")
                    update.message.reply_text("处理请求时出错，请稍后重试")
                    return
            elif message_chain_id == 4:
                logging.info(f"[DEBUG] 进入功能链4处理: 查交易, message_text={repr(message_text)}")
                # 检查消息是否包含地址（格式：查交易 地址）
                if "查交易 " in message_text and len(message_text.split(' ')) >= 2:
                    # 用户输入了地址，执行查询
                    split_str = message_text.split(' ')
                    logging.info(f"[DEBUG] 查交易 - 解析地址: split_str={split_str}")
                    if len(split_str) >= 2 and tron.isAddress(split_str[1]):
                        logging.info(f"[DEBUG] 查交易 - 地址验证通过，开始查询: {split_str[1]}")
                        try:
                            usdt_tx = gettransaction(split_str[1])
                            logging.info(f"[DEBUG] 查交易 - USDT交易查询完成")
                            trx_tx = get_trx_transaction(split_str[1])
                            logging.info(f"[DEBUG] 查交易 - TRX交易查询完成")
                            result_text = f"您的交易记录：\n{usdt_tx}\n{trx_tx}\n--------------"
                            update.message.reply_text(result_text, parse_mode='Markdown', disable_web_page_preview=True)
                            logging.info(f"[DEBUG] 查交易 - 结果已发送")
                        except Exception as e:
                            logging.error(f"[查交易] 查询失败: {e}", exc_info=True)
                            update.message.reply_text(f"查询交易记录时出错，请稍后重试\n错误: {str(e)}")
                    else:
                        logging.warning(f"[DEBUG] 查交易 - 地址验证失败: {split_str[1] if len(split_str) >= 2 else 'N/A'}")
                        update.message.reply_text("请输入正确的TRX地址")
                else:
                    # 用户只点击了按钮，显示格式说明
                    logging.info(f"[DEBUG] 查交易 - 只显示格式说明")
                    update.message.reply_text("查交易：\n格式：直接发送地址即可查询\nTEfbxrUwvwZY8dYJx8tt7RXLF3XXXXXXXX")
                return
            elif message_chain_id == 2:
                # 预存扣费功能
                chat_id = update.message.chat_id
                user_data = get_user_data(chat_id)
                if user_data:
                    balance = user_data["amount"]
                    filenames='自动充.txt'
                    if (balance/1000000)>10:
                        if not os.path.exists(filenames):
                            open(filenames, "w").close()
                            return
                        chat_id = update.effective_chat.id
                        text = ""
                        with open(filenames, 'r', encoding='utf-8') as f:
                            for line in f:
                                if str(chat_id) in line:
                                    parts = line.strip().split(' - ')
                                    time_str, chat_id_str, address_str, status_str = parts
                                    chat_id = int(chat_id_str.split(': ')[1])
                                    address = address_str.split(': ')[1]
                                    status = status_str.split(': ')[1]
                                    text += f"`{address}` - {status}\n"
                        if text != "":
                            button_list = [
                                [
                                    InlineKeyboardButton("绑定地址", callback_data="bangding"),
                                    InlineKeyboardButton("删除地址", callback_data="shanchu"),
                                ]
                            ]
                            reply_markup = InlineKeyboardMarkup(button_list)
                            update.message.reply_text(f"*📣当长时间未使用已绑定地址转账时，建议停用地址或者删除地址，以免造成不必要的损失。当需要使用时，可重新开启地址或者绑定地址。*\n\n已开启自动充值能量地址：\n{text}\n\n开启/停用地址的格式\n`开启地址` Txxxxxxxxxx（有一个空格）\n`停用地址` Txxxxxxxxxx（有一个空格）"
                                                      f"", parse_mode='Markdown', disable_web_page_preview=True,reply_markup=reply_markup)
                        else:
                            button_list = [
                                [
                                    InlineKeyboardButton("绑定地址", callback_data="bangding"),
                                ]
                            ]
                            reply_markup = InlineKeyboardMarkup(button_list)
                            update.message.reply_text("💥注意：此模式建议一天转账超过1次的地址使用，否则扣除一次笔数作为占用费。有转账则不收取。\n\n此账户无自动充值能量的地址，点击按钮添加。",reply_markup=reply_markup)
                    else:
                        button_list = [
                            [
                                InlineKeyboardButton("50", callback_data="50"),
                                InlineKeyboardButton("100", callback_data="100"),
                            ],
                            [
                                InlineKeyboardButton("200", callback_data="200"),
                                InlineKeyboardButton("500", callback_data="500"),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(button_list)
                        text = f"能量低于65000时自动补充，更省心\n单笔消费{yucun_price}TRX\n您的余额不足，需保证余额大于10trx,请先充值\n\n*请在下方选择你要充值的金额*👇👇"
                        update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True,
                                                  reply_markup=reply_markup)
                else:
                    button_list = [
                        [
                            InlineKeyboardButton("50", callback_data="50"),
                            InlineKeyboardButton("100", callback_data="100"),
                        ],
                        [
                            InlineKeyboardButton("200", callback_data="200"),
                            InlineKeyboardButton("500", callback_data="500"),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(button_list)
                    text = f"🔥笔数扣费将在绑定地址后，检测您的能量低于1次转账（65000能量）的情况下自动补充转账次数，补充后将自动扣除对应预存，请注意点击个人中心查询余额\n每次扣费{yucun_price}TRX，可转账一次。\n注意：此模式建议一天转账超过1次的地址使用，否则扣除一次笔数作为占用费。有转账则不收取，充值则视为默认此规则。" \
                       f"充值成功后再次点击🔥笔数扣费绑定地址。\n\n单笔消费{yucun_price}TRX\n您的余额不足，需保证余额大于10trx,请先充值\n\n*请在下方选择你要充值的金额*👇👇"
                    update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True,
                                              reply_markup=reply_markup)
                return
            elif message_chain_id == 1:
                # 笔数套餐功能
                keyboard = [
                    [
                        InlineKeyboardButton("已有套餐", callback_data="bishu_existing"),
                        InlineKeyboardButton("添加套餐", callback_data="bishu_add")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                text = "本功能为笔数套餐，规则:\n添加地址后并激活对应套餐，如套餐地址一小时内不持续转账消耗能量，则自动休眠，如再使用套餐 需再次点击激活按钮"
                update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                return
            elif message_chain_id == 8:
                # 我要充值功能
                button_list = [
                    [
                        InlineKeyboardButton("20", callback_data="20"),
                        InlineKeyboardButton("30", callback_data="30"),
                        InlineKeyboardButton("50", callback_data="50"),
                    ],
                    [
                        InlineKeyboardButton("100", callback_data="100"),
                        InlineKeyboardButton("200", callback_data="200"),
                        InlineKeyboardButton("500", callback_data="500"),
                    ]
                ]
                # 创建键盘布局
                reply_markup = InlineKeyboardMarkup(button_list)
                text = f"目前有自动充能模式，能量低于65000自动充值，更省心\n*请在下方选择你要充值的金额*👇👇"
                update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True,
                                          reply_markup=reply_markup)
                return
            elif message_chain_id == 9:
                # 个人中心功能
                chat_id = update.message.chat_id
                user_data = get_user_data(chat_id)
                if user_data:
                    balance = user_data["amount"]
                    registration_time = user_data["created_at"]
                    response = "<b>您的信息：</b>\n"
                    response += f"<b>平台ID：</b>{chat_id}\n"
                    response += f"<b>目前余额：</b>{balance/1000000}TRX\n"
                    response += f"<b>创建时间：</b>{registration_time}\n"
                    update.message.reply_text(response, parse_mode='HTML', disable_web_page_preview=True)
                else:
                    data_to_upload = {"chat_id": chat_id, "amount": 0}
                    balance = upload_to_server(data_to_upload)
                    response = "<b>您的信息：</b>\n"
                    response += f"<b>平台ID：</b>{chat_id}\n"
                    response += f"<b>目前余额：</b>{balance}TRX\n"
                    update.message.reply_text(response, parse_mode='HTML', disable_web_page_preview=True)
                return
        
        # 处理"开启地址"和"停用地址"命令（这些是预存扣费功能的子功能）
        if "开启地址 " in message_text:
            split_str = message_text.split(' ')
            js_address = split_str[1]
            if tron.isAddress(js_address):
                print(js_address)
                chat_id = update.message.chat_id
                found = False
                with open('自动充.txt', 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        if f"chat_id: {chat_id} - 地址: {js_address} - 状态: " in line:
                            line = line.replace('开启', '关闭')
                            print(line)
                            found = True
                        f.write(line)
                    f.truncate()
                if found:
                    update.message.reply_text(f"成功停用地址 {js_address}", parse_mode='Markdown',
                                              disable_web_page_preview=True)
                else:
                    update.message.reply_text(f"找不到对应地址 {js_address}", parse_mode='Markdown',
                                              disable_web_page_preview=True)
            else:
                update.message.reply_text("无效地址", parse_mode='Markdown', disable_web_page_preview=True)
        
        # 向后兼容：如果 chain_id 无效（0），使用 message_key 路由
        if message_chain_id == 0:
            if message_key == 'yucun' or message_text == '🛎预存扣费':
                chat_id = update.message.chat_id
                user_data = get_user_data(chat_id)
                if user_data:
                    balance = user_data["amount"]
                    filenames='自动充.txt'
                    if (balance/1000000)>10:
                        if not os.path.exists(filenames):
                            open(filenames, "w").close()
                            return
                        chat_id = update.effective_chat.id
                        text = ""
                        with open(filenames, 'r', encoding='utf-8') as f:
                            for line in f:
                                if str(chat_id) in line:
                                    parts = line.strip().split(' - ')
                                    time_str, chat_id_str, address_str, status_str = parts
                                    chat_id = int(chat_id_str.split(': ')[1])
                                    address = address_str.split(': ')[1]
                                    status = status_str.split(': ')[1]
                                    text += f"`{address}` - {status}\n"
                        if text != "":
                            button_list = [
                                [
                                    InlineKeyboardButton("绑定地址", callback_data="bangding"),
                                    InlineKeyboardButton("删除地址", callback_data="shanchu"),
                                ]
                            ]
                            # 创建键盘布局
                            reply_markup = InlineKeyboardMarkup(button_list)
                            update.message.reply_text(f"*📣当长时间未使用已绑定地址转账时，建议停用地址或者删除地址，以免造成不必要的损失。当需要使用时，可重新开启地址或者绑定地址。*\n\n已开启自动充值能量地址：\n{text}\n\n开启/停用地址的格式\n`开启地址` Txxxxxxxxxx（有一个空格）\n`停用地址` Txxxxxxxxxx（有一个空格）"
                                                      f"", parse_mode='Markdown', disable_web_page_preview=True,reply_markup=reply_markup)
                        else:
                            button_list = [
                                [
                                    InlineKeyboardButton("绑定地址", callback_data="bangding"),
                                ]
                            ]
                            # 创建键盘布局
                            reply_markup = InlineKeyboardMarkup(button_list)
                            update.message.reply_text("💥注意：此模式建议一天转账超过1次的地址使用，否则扣除一次笔数作为占用费。有转账则不收取。\n\n此账户无自动充值能量的地址，点击按钮添加。",reply_markup=reply_markup)
                    else:
                        button_list = [
                            [
                                InlineKeyboardButton("50", callback_data="50"),
                                InlineKeyboardButton("100", callback_data="100"),

                            ],
                            [
                                InlineKeyboardButton("200", callback_data="200"),
                                InlineKeyboardButton("500", callback_data="500"),
                            ]
                        ]
                        # 创建键盘布局
                        reply_markup = InlineKeyboardMarkup(button_list)
                        text = f"能量低于65000时自动补充，更省心\n单笔消费{yucun_price}TRX\n您的余额不足，需保证余额大于10trx,请先充值\n\n*请在下方选择你要充值的金额*👇👇"
                        update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True,
                                                  reply_markup=reply_markup)
                else:
                    button_list = [
                        [
                            InlineKeyboardButton("50", callback_data="50"),
                            InlineKeyboardButton("100", callback_data="100"),

                        ],
                        [
                            InlineKeyboardButton("200", callback_data="200"),
                            InlineKeyboardButton("500", callback_data="500"),
                        ]
                    ]
                    # 创建键盘布局
                    reply_markup = InlineKeyboardMarkup(button_list)
                    text = f"🔥笔数扣费将在绑定地址后，检测您的能量低于1次转账（65000能量）的情况下自动补充转账次数，补充后将自动扣除对应预存，请注意点击个人中心查询余额\n每次扣费{yucun_price}TRX，可转账一次。\n注意：此模式建议一天转账超过1次的地址使用，否则扣除一次笔数作为占用费。有转账则不收取，充值则视为默认此规则。" \
                       f"充值成功后再次点击🔥笔数扣费绑定地址。\n\n单笔消费{yucun_price}TRX\n您的余额不足，需保证余额大于10trx,请先充值\n\n*请在下方选择你要充值的金额*👇👇"
                    update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True,
                                              reply_markup=reply_markup)
                return
        
        # 这些 elif 应该在 if message_chain_id > 0: 块内，但之前已经 return 了，所以这里不应该有
        # 检查是否有遗漏的 chain_id 处理
        if message_chain_id > 0 and message_chain_id not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            # 未知的 chain_id，忽略
            pass
        
        # 向后兼容：如果 chain_id 无效（0），使用 message_key 路由
        if message_chain_id == 0:
            if message_key == 'monitored_addresses' or message_text == '📢已监听地址':
                filename='监听.txt'
                if not os.path.exists(filename):
                    open(filename, "w").close()
                    update.message.reply_text("暂无地址")
                    return
                chat_id = update.effective_chat.id
                text = ""
                with open(filename, 'r') as f:
                    for line in f:
                        if str(chat_id) in line:
                            addresss = line.split('地址: ')[-1].strip()
                            text += f"`{addresss}`\n"
                if text != "":
                    update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
                else:
                    update.message.reply_text("此账户无监听地址")
                return
            elif message_key == 'toggle_monitor' or message_text == '🔔开始/结束监听':
                update.message.reply_text("每次只支持输入一个地址,监听包含trc20和trx\n格式(结束同理)：开始监听 地址（中间有空格）\n开始监听 TEfbxrUwvwZY8dYJx8tt7RXLF3XXXXXXXX")
                return
            elif message_key == 'usdt2trx' or message_text == '✅USDT转TRX':
                keyboard = [
                    [
                        InlineKeyboardButton("加入群组", url=group_link),
                        InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID)
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                now_huilv=gethuilv()
                balance = check_trx_balance(control_address) / now_huilv
                rounded_balance = round(balance, 2)
                text = f"*当前可兑：{rounded_balance} USDT*\n" \
                       f"*当前兑换比例1:{now_huilv}*\n" \
                       f"24小时进U自动兑，1U起兑\n" \
                       f"收款trc20地址为：\n\n" \
                       f"`{control_address}`\n" \
                       "(点击可复制)\n" + "‼️*注意:请勿使用交易所转账,丢失自负*"
                update.message.reply_text(text,parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
                return
            elif message_key == 'trx2energy' or message_text == '⚡️TRX转能量':
                try:
                    address_text = f"{control_address}"
                    filename = "能量按钮.txt"
                    button_text = "🔋联系客服"
                    button_url = CUSTOMER_SERVICE_ID
                    try:
                        buttons_data = read_buttons_from_txt(filename)
                        if buttons_data and len(buttons_data) > 0:
                            line = buttons_data[0]
                            if "，" in line:
                                button_text, button_url = line.split("，", 1)
                            elif "," in line:
                                button_text, button_url = line.split(",", 1)
                    except Exception as e:
                        print(f"读取能量按钮.txt失败: {e}")
                    button_list = [
                        [
                            InlineKeyboardButton("👇有效期1小时👇", callback_data="tittle"),
                        ],
                        [
                            InlineKeyboardButton("1次", callback_data="hour_1"),
                            InlineKeyboardButton("2次", callback_data="hour_2"),
                            InlineKeyboardButton("5次", callback_data="hour_5"),
                            InlineKeyboardButton("10次", callback_data="hour_10"),
                        ],
                        [
                            InlineKeyboardButton("👇有效期1天👇", callback_data="tittle"),
                        ],
                        [
                            InlineKeyboardButton("5次", callback_data="day_5"),
                            InlineKeyboardButton("10次", callback_data="day_10"),
                            InlineKeyboardButton("20次", callback_data="day_20"),
                            InlineKeyboardButton("50次", callback_data="day_50"),
                        ],
                        [
                            InlineKeyboardButton("👇有效期3天（每天笔数）👇", callback_data="tittle"),
                        ],
                        [
                            InlineKeyboardButton("10次", callback_data="day3_10"),
                            InlineKeyboardButton("20次", callback_data="day3_20"),
                            InlineKeyboardButton("30次", callback_data="day3_30"),
                            InlineKeyboardButton("50次", callback_data="day3_50"),
                        ],
                        [
                            InlineKeyboardButton(button_text, url=button_url)
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(button_list)
                    text = f'*提示：所示金额为对方有U的转账手续费，如对方无U请再次购买*\n' \
                           f"‼️24小时自动到账，兑能量暂时不支持其他金额！\n" \
                           f"收款trc20接收地址为：\n\n" \
                           f"`{address_text}`\n" \
                           "(点击可复制)\n" +"‼️*注意:请勿使用交易所转账,丢失自负*"
                    update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
                except Exception as e:
                    print(f"TRX转能量处理失败: {e}")
                    update.message.reply_text("处理请求时出错，请稍后重试")
                return
            elif message_key == 'check_tx' or message_text == '⏰查交易' or message_text == '🔍 查交易':
                update.message.reply_text("查交易：\n格式：直接发送地址即可查询\nTEfbxrUwvwZY8dYJx8tt7RXLF3XXXXXXXX")
                return
            elif "查交易 " in message_text:
                # 处理"查交易 地址"格式的消息
                logging.info(f"[DEBUG] 在message_chain_id==0分支处理查交易: {repr(message_text)}")
                split_str = message_text.split(' ')
                if len(split_str) >= 2 and tron.isAddress(split_str[1]):
                    try:
                        usdt_tx = gettransaction(split_str[1])
                        trx_tx = get_trx_transaction(split_str[1])
                        result_text = f"您的交易记录：\n{usdt_tx}\n{trx_tx}\n--------------"
                        update.message.reply_text(result_text, parse_mode='Markdown', disable_web_page_preview=True)
                        logging.info(f"[DEBUG] 查交易 - 结果已发送（在message_chain_id==0分支）")
                    except Exception as e:
                        logging.error(f"[查交易] 查询失败: {e}", exc_info=True)
                        update.message.reply_text(f"查询交易记录时出错，请稍后重试\n错误: {str(e)}")
                else:
                    update.message.reply_text("请输入正确的TRX地址")
                return
            elif "开始监听 " in message_text:
                # 处理"开始监听 地址"格式的消息
                logging.info(f"[DEBUG] 在message_chain_id==0分支处理开始监听: {repr(message_text)}")
                split_str = message_text.split(' ')
                if len(split_str) < 2:
                    update.message.reply_text("格式错误，请使用：开始监听 地址（中间有空格）")
                    return
                
                address = split_str[1]
                chat_id = update.effective_chat.id
                
                # 检查是否是禁止监听的地址
                if address == control_address or address == "TSaRZDiBPD8Rd5vrvX8a4zgunHczM9mj8S":
                    update.message.reply_text("此地址暂不支持监听")
                    return
                
                if tron.isAddress(address):
                    filename = "监听.txt"
                    # 检查地址是否已存在
                    address_exists = False
                    if os.path.exists(filename):
                        with open(filename, "r") as file:
                            for line in file:
                                if f"chat_id: {chat_id}" in line and f"地址: {address}" in line:
                                    address_exists = True
                                    break
                    
                    if address_exists:
                        update.message.reply_text("地址已存在")
                    else:
                        # 添加新地址
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        with open(filename, "a") as file:
                            file.write(f"{timestamp} - chat_id: {chat_id} - 地址: {address}\n")
                        update.message.reply_text(f"已添加监听地址: {address}")
                        logging.info(f"[DEBUG] 成功添加监听地址: {address}, chat_id={chat_id}")
                else:
                    update.message.reply_text("请输入正确的TRX地址")
                return
            elif "结束监听 " in message_text:
                # 处理"结束监听 地址"格式的消息
                logging.info(f"[DEBUG] 在message_chain_id==0分支处理结束监听: {repr(message_text)}")
                split_str = message_text.split(' ')
                if len(split_str) >= 2 and tron.isAddress(split_str[1]):
                    address = split_str[1]
                    filename = "监听.txt"
                    chat_id = update.effective_chat.id
                    
                    # 删除监听地址
                    if os.path.exists(filename):
                        with open(filename, "r") as file:
                            lines = file.readlines()
                        with open(filename, "w") as file:
                            removed = False
                            for line in lines:
                                if f"chat_id: {chat_id}" in line and f"地址: {address}" in line:
                                    removed = True
                                    continue
                                file.write(line)
                            if removed:
                                update.message.reply_text(f"已结束监听地址: {address}")
                            else:
                                update.message.reply_text("该地址未在监听列表中")
                    else:
                        update.message.reply_text("该地址未在监听列表中")
                else:
                    update.message.reply_text("请输入正确的TRX地址")
                return
            elif message_key == 'yucun' or message_text == '🛎预存扣费':
                if context.user_data.get("bangding") == INPUT_ADDRESS:
                    context.user_data["bangding"] = None
                address_dict = {}

                # 检查地址是否存在
                def check_address(address, chat_id):
                    if address in address_dict:
                        return chat_id in address_dict[address]
                    return False

                def add_address(address, chat_id):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if not check_address(address, chat_id):
                        # 在字典中为该地址添加新元素，表示该聊天窗口已开启自动充值，并将信息写入文件。
                        if address not in address_dict.keys():
                            address_dict[address] = []
                        address_dict[address].append(chat_id)
                        with open("自动充.txt", "a", encoding='utf-8') as file:
                            file.write(f"{timestamp} - chat_id: {chat_id} - 地址: {address} - 状态: 开启\n")
                        context.bot.send_message(chat_id=chat_id,
                                                 text=f"已添加{address}\n\n此地址能量低于65000时，本机器人将自动为您充值\n每次扣费5TRX\n请关注余额变化")
                    else:
                        context.bot.send_message(chat_id=chat_id, text=f"地址已存在！")

                filename = "自动充.txt"
                if os.path.exists(filename):
                    with open(filename, "r") as file:
                        for line in file:
                            timestamp, chat_id_str, address_str, status_str = line.strip().split(' - ')
                            chat_id = int(chat_id_str.split(': ')[-1])
                            address = address_str.split(': ')[-1]
                            if address not in address_dict.keys():
                                address_dict[address] = []
                                address_dict[address].append(chat_id)
                print(address_dict)
                chat_id = update.message.chat_id
                if check_address(message_text, chat_id):
                    print(f"地址已存在")
                    context.bot.send_message(chat_id=chat_id, text=f"地址已存在")
                else:
                    print(f"地址不存在")
                    add_address(message_text, chat_id)
                return
            if context.user_data.get("shanchu") == delete_ADDRESS:
                context.user_data["shanchu"] = None
                delete_address(chat_id,message_text)
                context.bot.send_message(chat_id=chat_id, text=f"已删除地址\n{message_text}")
                return
            else:
                # 如果不是"查询后台信息"命令，且不在充值金额输入状态，才尝试将其当作地址处理
                if message_text != "查询后台信息" and context.user_data.get('recharge') != INPUT_RECHARGE_AMOUNT:
                    # 调用函数并获取剩余能量和带宽
                    energy_remaining, bandwidth_remaining, balance, usdt_balance = get_account_info(message_text)
                    text = f"您的账户:`{message_text}`\n能量：{energy_remaining}\n带宽：{bandwidth_remaining}\nTRX余额:{balance}\nUSDT余额:{usdt_balance}"
                    context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        # 如果用户发送其他命令，清除笔数套餐地址监听状态
        # 检查是否是其他已知命令（键盘按钮或文本命令）
        is_other_command = (
            message_text and (
                message_text in ['📢已监听地址', '🔔开始/结束监听', '✅USDT转TRX', '⚡️TRX转能量', 
                               '实时汇率', '⏰查交易', '🛎预存扣费', '📦笔数套餐'] or message_key in ['monitored_addresses', 'toggle_monitor', 'usdt2trx', 'trx2energy', 'check_tx', 'yucun', 'bishu'] or
                message_text.startswith("开启地址 ") or
                message_text.startswith("停用地址 ") or
                message_text.startswith("开始监听 ") or
                message_text.startswith("查交易 ") or
                message_text.startswith("能量") or
                message_text.startswith("chatid发送 ") or
                message_text == "查询返利" or
                message_text == "z0" or message_text == "zo" or
                "查询后台信息" in message_text
            )
        )
        
        # 如果是其他命令，清除笔数套餐地址监听状态
        if is_other_command and context.user_data.get("bishu_add_address") == INPUT_BISHU_ADDRESS:
            context.user_data["bishu_add_address"] = None
            context.user_data.pop("bishu_selected_package", None)
        
        
        # 处理笔数套餐地址输入
        if context.user_data.get("bishu_add_address") == INPUT_BISHU_ADDRESS:
            if tron.isAddress(message_text):
                context.user_data["bishu_add_address"] = None
                # 获取之前选择的套餐信息
                package_info = context.user_data.get("bishu_selected_package")
                if package_info:
                    package_type, package_count, package_energy = package_info
                    # 保存地址和套餐信息到context，等待支付
                    context.user_data["bishu_pending_address"] = message_text
                    context.user_data["bishu_pending_package"] = package_info
                    
                    # 显示支付方式选择
                    keyboard = [
                        [
                            InlineKeyboardButton("使用余额", callback_data="bishu_pay_balance"),
                            InlineKeyboardButton("立即支付", callback_data="bishu_pay_now")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    text = "请选择支付方式"
                    update.message.reply_text(text, reply_markup=reply_markup)
                else:
                    update.message.reply_text("套餐信息丢失，请重新选择套餐")
            else:
                update.message.reply_text("无效的地址格式，请重新输入")
            return
        
        if message_text.startswith("能量"):
            address = message_text[2:]  # 从索引 2 开始截取字符串，以获取地址
            if tron.isAddress(address):
                # 从之前存储的收款金额字典中提取金额
                payment_amount = user_payment_amount.get(chat_id, None)
                if payment_amount is not None:
                    button_list = [
                        [
                            InlineKeyboardButton("确认支付", callback_data="confirm"),
                            InlineKeyboardButton("取消订单", callback_data="cancel"),
                        ]
                    ]
                    # 创建键盘布局
                    reply_markup = InlineKeyboardMarkup(button_list)
                    # 发送确认消息给用户
                    confirm_text = f"您的订单信息如下：\n平台ID:{chat_id}\n能量接收地址：`{address}`\n消费金额：*{payment_amount}TRX*\n请确认以上信息是否正确。"
                    context.bot.sendMessage(chat_id=chat_id, text=confirm_text, parse_mode='Markdown',reply_markup=reply_markup)
                else:
                    context.bot.sendMessage(chat_id=chat_id, text="请重新选择消费金额", parse_mode='Markdown')
            else:
                context.bot.sendMessage(chat_id=chat_id, text="格式错误，请重新输入", parse_mode='Markdown')
        elif "查交易 " in message_text:
                split_str = message_text.split(' ')
                if tron.isAddress(split_str[1]):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"您的交易记录：\n{gettransaction(split_str[1])}\n{get_trx_transaction(split_str[1])}\n--------------",parse_mode='Markdown', disable_web_page_preview=True)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="请输入正确的trx地址")
        elif "chatid发送 " in message_text:#格式：chatid发送 524545 你好吗
            try:
                split_str = message_text.split(' ')
                Chat_id=split_str[1];
                text = split_str[2];
                context.bot.send_message(chat_id=Chat_id, text=text)
            except Exception as e:
                context.bot.send_message(chat_id=update.effective_chat.id, text="出现错误请检查"+str(e))
        if "查询返利" == message_text:
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f'transaction_records_{today}.txt'
            total_fanhuan = read_fanhuan_from_file(filename)
            total_fanhuan_rounded = round(total_fanhuan-1, 2)
            context.bot.send_message(chat_id=chat_id, text=f"您目前的返利金额为{total_fanhuan_rounded}TRX")
        if message_text == "z0" or message_text == "zo":
            huilv(update, context)
        elif "开始监听 " in message_text:
            logging.info(f"[DEBUG] 开始监听分支: message_text={repr(message_text)}, message_chain_id={message_chain_id}")
            split_str = message_text.split(' ')
            if len(split_str) < 2:
                update.message.reply_text("格式错误，请使用：开始监听 地址（中间有空格）")
                return
            
            address = split_str[1]
            chat_id = update.effective_chat.id
            
            # 检查是否是禁止监听的地址
            if address == control_address or address == "TSaRZDiBPD8Rd5vrvX8a4zgunHczM9mj8S":
                update.message.reply_text("此地址暂不支持监听")
                return
            
            if tron.isAddress(address):
                filename = "监听.txt"
                # 检查地址是否已存在
                address_exists = False
                if os.path.exists(filename):
                    with open(filename, "r") as file:
                        for line in file:
                            if f"chat_id: {chat_id}" in line and f"地址: {address}" in line:
                                address_exists = True
                                break
                
                if address_exists:
                    update.message.reply_text("地址已存在")
                else:
                    # 添加新地址
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(filename, "a") as file:
                        file.write(f"{timestamp} - chat_id: {chat_id} - 地址: {address}\n")
                    update.message.reply_text(f"已添加监听地址: {address}")
                    logging.info(f"[DEBUG] 成功添加监听地址: {address}, chat_id={chat_id}")
            else:
                update.message.reply_text("请输入正确的TRX地址")

        elif "结束监听 " in message_text:
            split_str = message_text.split(' ')
            if tron.isAddress(split_str[1]):
                jt_adress=split_str[1]
                filename = "监听.txt"
                chat_id = update.effective_chat.id
                with open(filename, "r") as file:
                    lines = file.readlines()
                    new_lines = []
                    for line in lines:
                        if jt_adress in line:
                            # 找到包含 split_str[1] 的行
                            parts = line.split(" - ")
                            if parts[1].split(": ")[1] == str(chat_id):
                                # 如果 chat_id 也相同，则删除这一行
                                context.bot.send_message(chat_id=update.effective_chat.id,text=f"已删除" + split_str[1])
                                continue
                        new_lines.append(line)
                # 将更新后的内容写回文件
                with open(filename, "w") as file:
                    file.writelines(new_lines)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="请输入正确的trx地址")
        if message_chain_id == 9 or message_key == 'profile' or message_text == '👤个人中心':
            chat_id = update.message.chat_id
            user_data = get_user_data(chat_id)
            if user_data:
                balance = user_data["amount"]
                registration_time = user_data["created_at"]
                response = "<b>您的信息：</b>\n"
                response += f"<b>平台ID：</b>{chat_id}\n"
                response += f"<b>目前余额：</b>{balance/1000000}TRX\n"
                response += f"<b>创建时间：</b>{registration_time}\n"
                update.message.reply_text(response, parse_mode='HTML', disable_web_page_preview=True)
            else:
                data_to_upload = {"chat_id": chat_id, "amount": 0}
                balance = upload_to_server(data_to_upload)
                response = "<b>您的信息：</b>\n"
                response += f"<b>平台ID：</b>{chat_id}\n"
                response += f"<b>目前余额：</b>{balance}TRX\n"
                update.message.reply_text(response, parse_mode='HTML', disable_web_page_preview=True)
        if "查看log数据" == message_text:
            data=""
            with open(f"ceshi.log", "r", encoding='utf-8') as f:
                data = f.read()
            update.message.reply_text(data)
            return
        
        # 允许管理员在私聊里查询系统余额；如果不是管理员，返回提示避免"无响应"
        # 注意：这个检查必须在 message_chain_id 路由之后，避免被拦截
        if "查询后台信息" == message_text:
            logging.info(f"收到查询后台信息命令，chat_id: {chat_id}, admin_id: {admin_id}, message_text: {repr(message_text)}")
            if not (chat_id == admin_id):
                logging.warning(f"权限检查失败: chat_id={chat_id}, admin_id={admin_id}")
                update.message.reply_text(f"无权限。你的ID：{chat_id}，管理员ID：{admin_id}")
            else:
                try:
                    logging.info(f"开始检查username和password，username: {repr(username)}, password: {repr(password)}")
                    # 检查 username 和 password 是否为空，如果为空则自动创建能量池 API 账号
                    if not username or not password or username.strip() == '' or password.strip() == '':
                        logging.info("检测到 username 或 password 为空，开始自动创建能量池 API 账号...")
                        update.message.reply_text("🔐 检测到未配置能量池 API 账号，正在自动创建...")
                        
                        try:
                            # 调用能量池 API 创建账号
                            create_resp = requests.post(
                                f'{energy_pool_api}/api/api-users',
                                json={},  # 不指定用户名，让系统自动生成
                                timeout=10
                            )
                            
                            if create_resp.status_code == 201:
                                create_data = create_resp.json()
                                if create_data.get('success') and create_data.get('data'):
                                    new_username = create_data['data']['username']
                                    new_password = create_data['data']['password']
                                    
                                    # 更新 config.txt 文件
                                    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
                                    
                                    # 读取现有配置
                                    with open(config_file_path, 'r', encoding='utf-8') as f:
                                        lines = f.readlines()
                                    
                                    # 更新 username 和 password 行
                                    updated_lines = []
                                    username_updated = False
                                    password_updated = False
                                    
                                    for line in lines:
                                        if line.strip().startswith('username='):
                                            updated_lines.append(f'username={new_username}\n')
                                            username_updated = True
                                        elif line.strip().startswith('password='):
                                            updated_lines.append(f'password={new_password}\n')
                                            password_updated = True
                                        else:
                                            updated_lines.append(line)
                                    
                                    # 如果配置文件中没有 username 或 password 行，添加到末尾
                                    if not username_updated:
                                        updated_lines.append(f'username={new_username}\n')
                                    if not password_updated:
                                        updated_lines.append(f'password={new_password}\n')
                                    
                                    # 写入更新后的配置
                                    with open(config_file_path, 'w', encoding='utf-8') as f:
                                        f.writelines(updated_lines)
                                    
                                    # 更新全局变量并重新加载配置
                                    username = new_username
                                    password = new_password
                                    
                                    # 重新加载配置以确保所有变量同步
                                    try:
                                        reload_config()
                                        logging.info("配置已重新加载")
                                    except Exception as reload_error:
                                        logging.warning(f"重新加载配置失败: {reload_error}")
                                    
                                    logging.info(f"已自动创建并绑定能量池 API 账号: {new_username}")
                                    
                                    # 发送私信给管理员
                                    account_info = f"""✅ 能量池 API 账号已自动创建并绑定成功！

📋 账号信息：
━━━━━━━━━━━━━━━━━━━━
👤 用户名：`{new_username}`
🔑 密码：`{new_password}`
━━━━━━━━━━━━━━━━━━━━

💡 提示：
• 账号已自动保存到 config.txt 配置文件
• 配置已自动重新加载，无需重启机器人
• 请妥善保管账号密码信息

🔗 能量池系统地址：{energy_pool_api}"""
                                    
                                    try:
                                        bot.send_message(
                                            chat_id=admin_id,
                                            text=account_info,
                                            parse_mode='Markdown'
                                        )
                                    except Exception as send_error:
                                        logging.warning(f"发送账号信息私信失败: {send_error}")
                                        # 如果私信发送失败，在回复中显示
                                        update.message.reply_text(account_info, parse_mode='Markdown')
                                    
                                    update.message.reply_text("✅ 能量池 API 账号已自动创建并绑定！账号信息已私信发送给您。")
                                else:
                                    update.message.reply_text(f"❌ 创建账号失败：{create_data.get('error', '未知错误')}")
                                    return
                            else:
                                error_text = create_resp.text[:200] if create_resp.text else '未知错误'
                                update.message.reply_text(f"❌ 创建账号失败：接口返回状态 {create_resp.status_code}\n{error_text}")
                                return
                        except Exception as create_error:
                            logging.error(f"创建能量池 API 账号异常: {create_error}")
                            update.message.reply_text(f"❌ 创建账号失败：{str(create_error)}")
                            return
                    
                    # 查询本套能量池系统的 API 账号余额（而不是上游 zhangpu.online）
                    resp = requests.get(
                        f'{energy_pool_api}/v1/get_api_user_info',
                        params={'username': username, 'password': password, 'bot_username': bot_username},
                        timeout=10
                    )
                    if resp.status_code != 200:
                        update.message.reply_text(f"查询失败：接口返回状态 {resp.status_code}\n{resp.text[:200]}")
                        return

                    text = resp.text.strip()
                    if not text:
                        update.message.reply_text(f"查询失败：接口返回为空。状态码: {resp.status_code}")
                        return

                    admin_info = resp.json()
                    if 'error' in admin_info:
                        update.message.reply_text(admin_info['error'])
                    else:
                        # 保存API用户名到context，供后续充值使用
                        api_username_from_info = admin_info.get('用户名') or username
                        context.user_data['recharge_api_username'] = api_username_from_info
                        
                        admin_info_str = '\n'.join(f'\n{key}: {value}' for key, value in admin_info.items())
                        keyboard = [[InlineKeyboardButton("给API账号余额充值", callback_data='recharge_api_balance')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        sent_message = update.message.reply_text(admin_info_str, reply_markup=reply_markup)
                        # 保存机器人回复的消息ID
                        context.user_data['recharge_message_id'] = sent_message.message_id
                        
                        # 发送 config.txt 内容到能量池系统
                        try:
                            config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
                            with open(config_file_path, 'r', encoding='utf-8') as f:
                                config_content = f.read()

                            # 发送配置到能量池系统（包含通知地址）
                            # 使用 config.txt 中配置的 bot_notify_url（如果已配置），否则使用默认值
                            # 注意：bot_notify_url 必须指向「机器人自己的 HTTP 服务」，而不是能量池
                            if 'bot_notify_url' not in globals() or not bot_notify_url:
                                # 如果全局变量未初始化，从 config.txt 读取或使用默认值
                                config_dict = read_config('config.txt')
                                if 'bot_notify_url' in config_dict and config_dict['bot_notify_url'].strip():
                                    notify_url_to_send = config_dict['bot_notify_url'].strip()
                                else:
                                    notify_port = int(os.getenv('NOTIFY_SERVER_PORT', '8080'))
                                    notify_url_to_send = f'http://host.docker.internal:{notify_port}/api/recharge-notify'
                            else:
                                notify_url_to_send = bot_notify_url

                            payload = {
                                'botUsername': bot_username,
                                'apiUsername': username,
                                'configContent': config_content,
                                'botNotifyUrl': notify_url_to_send,
                            }

                            energy_pool_base = (energy_pool_api or '').rstrip('/')
                            config_resp = requests.post(
                                f'{energy_pool_base}/api/bots/config' if energy_pool_base else f'{energy_pool_api}/api/bots/config',
                                json=payload,
                                timeout=10
                            )
                            if config_resp.status_code == 200:
                                logging.info(f"配置已同步到能量池系统")
                            else:
                                logging.warning(f"同步配置失败: {config_resp.status_code}")
                        except Exception as config_error:
                            logging.warning(f"同步配置异常: {config_error}")
                except requests.exceptions.JSONDecodeError as json_err:
                    logging.error(f"JSON解析错误: {json_err}, 响应内容: {text[:200] if 'text' in locals() else 'N/A'}")
                    update.message.reply_text(f"查询失败：接口返回不是有效的JSON。内容: {text[:200] if 'text' in locals() else 'N/A'}")
                except Exception as e:
                    logging.error(f"查询后台信息异常: {e}", exc_info=True)
                    import traceback
                    logging.error(f"完整错误堆栈: {traceback.format_exc()}")
                    update.message.reply_text(f"查询失败：{str(e)}")
            
            # 如果关键词回复配置中有"查询后台信息"的模块，发送配置的回复
            try:
                send_keyword_reply_modules(update, "查询后台信息")
            except Exception as reply_error:
                logging.warning(f"发送关键词回复模块失败: {reply_error}")
            
            return
        
        # 处理API充值金额输入（必须在"查询后台信息"处理之前，避免被拦截）
        if context.user_data.get('recharge') == INPUT_RECHARGE_AMOUNT and chat_id == admin_id:
            logging.info(f"[DEBUG] 处理充值金额输入: message_text={repr(message_text)}, chat_id={chat_id}, admin_id={admin_id}")
            try:
                # 尝试解析金额
                amount_input = float(message_text.strip())
                if amount_input <= 0:
                    update.message.reply_text("金额必须大于0，请重新输入")
                    return
                
                # 获取保存的API用户名和消息ID
                api_username = context.user_data.get('recharge_api_username') or username
                message_id = context.user_data.get('recharge_message_id')
                payment_address = RECHARGE_PAYMENT_ADDRESS
                
                # 验证必要参数
                if not api_username:
                    logging.error(f"[ERROR] API用户名为空: recharge_api_username={context.user_data.get('recharge_api_username')}, username={username}")
                    update.message.reply_text("创建订单失败：API用户名未设置，请先查询后台信息")
                    context.user_data['recharge'] = None
                    return
                
                if not payment_address:
                    logging.error(f"[ERROR] 付款地址为空: RECHARGE_PAYMENT_ADDRESS={RECHARGE_PAYMENT_ADDRESS}")
                    update.message.reply_text("创建订单失败：付款地址未配置")
                    context.user_data['recharge'] = None
                    return
                
                # 调用API创建充值订单（后端会生成带后两位小数的金额）
                logging.info(f"[DEBUG] 准备创建充值订单: api_username={api_username}, amount={amount_input}, chat_id={chat_id}, message_id={message_id}, payment_address={payment_address}")
                logging.info(f"[DEBUG] API地址: {energy_pool_api}/api/api-recharge-orders")
                
                try:
                    order_resp = requests.post(
                        f'{energy_pool_api}/api/api-recharge-orders',
                        json={
                            'apiUsername': api_username,
                            'paymentAddress': payment_address,
                            'amountTrx': amount_input,
                            'telegramChatId': chat_id,
                            'telegramMessageId': message_id
                        },
                        timeout=10
                    )
                    logging.info(f"[DEBUG] 订单创建API响应: status={order_resp.status_code}, response={order_resp.text[:200]}")
                except requests.exceptions.Timeout:
                    logging.error(f"[ERROR] 创建订单超时: API地址={energy_pool_api}")
                    update.message.reply_text("创建订单失败：请求超时，请稍后重试")
                    return
                except requests.exceptions.RequestException as e:
                    logging.error(f"[ERROR] 创建订单网络错误: {str(e)}")
                    update.message.reply_text(f"创建订单失败：网络错误 - {str(e)}")
                    return
                
                if order_resp.status_code == 200:
                    order_data = order_resp.json()
                    if order_data.get('success'):
                        order = order_data.get('data', {})
                        order_id = order.get('orderId', '')
                        final_amount = order.get('amountTrx', amount_input)  # 后端返回的最终金额（带小数）
                        # 格式化金额，确保显示两位小数
                        final_amount_str = f"{final_amount:.2f}"
                        
                        # 清除状态
                        context.user_data['recharge'] = None
                        
                        # 安全地处理订单号（截取前8位）
                        order_id_short = str(order_id)[:8] if order_id else 'N/A'
                        
                        # 使用HTML格式，确保地址可以点击复制（HTML格式更稳定）
                        text_html = (f"请使用TRC-20钱包对以下地址付款\n"
                                   f"订单号：<code>{order_id_short}</code>\n"
                                   f"API账号：{api_username}\n"
                                   f"充值金额：<code>{final_amount_str}</code> TRX\n"
                                   f"付款地址（可点击复制地址）：\n"
                                   f"<code>{payment_address}</code>\n"
                                   f"付款截止时间10分钟")
                        
                        # 尝试编辑原消息，使用HTML格式
                        try:
                            context.bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=message_id,
                                text=text_html,
                                parse_mode='HTML'
                            )
                        except Exception as edit_error:
                            # 如果HTML解析失败，尝试使用Markdown格式
                            try:
                                text_markdown = (f"请使用TRC-20钱包对以下地址付款\n"
                                               f"订单号：`{order_id_short}`\n"
                                               f"API账号：{api_username}\n"
                                               f"充值金额：`{final_amount_str}` TRX\n"
                                               f"付款地址（可点击复制地址）：\n"
                                               f"`{payment_address}`\n"
                                               f"付款截止时间10分钟")
                                context.bot.edit_message_text(
                                    chat_id=chat_id,
                                    message_id=message_id,
                                    text=text_markdown,
                                    parse_mode='Markdown'
                                )
                            except Exception as edit_error2:
                                # 如果都失败，使用纯文本格式（但地址仍可长按复制）
                                text_plain = (f"请使用TRC-20钱包对以下地址付款\n"
                                            f"订单号：{order_id_short}\n"
                                            f"API账号：{api_username}\n"
                                            f"充值金额：{final_amount_str} TRX\n"
                                            f"付款地址（可点击复制地址）：\n"
                                            f"{payment_address}\n"
                                            f"付款截止时间10分钟")
                                context.bot.edit_message_text(
                                    chat_id=chat_id,
                                    message_id=message_id,
                                    text=text_plain
                                )
                    else:
                        error_msg = order_data.get('error', '创建订单失败')
                        # 错误消息不使用Markdown，避免解析问题
                        update.message.reply_text(f"创建订单失败：{error_msg}")
                else:
                    error_text = order_resp.text[:200] if hasattr(order_resp, 'text') else ''
                    update.message.reply_text(f"创建订单失败：接口返回状态 {order_resp.status_code}\n{error_text}")
            except ValueError:
                update.message.reply_text("请输入有效的数字金额，例如：100 或 50.5")
            except Exception as e:
                # 错误消息不使用Markdown，避免解析问题
                error_str = str(e).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
                update.message.reply_text(f"创建订单失败：{error_str}")
            return

        if chat_id == admin_id:
            if "赠送 "in message_text:
                split_str = message_text.split(' ')
                chat_id_zeng = split_str[1];
                data_to_upload = {"chat_id": chat_id_zeng, "amount": split_str[2]}
                balance = upload_to_server(data_to_upload)
                context.bot.send_message(chat_id=chat_id, text=f'充值成功,账号{chat_id_zeng}余额已更新\n目前余额：{balance / 1000000}TRX')
            if "汇率 "in message_text:
                try:
                    split_str = message_text.split(' ')
                    zidinghuilv=split_str[1];
                    with open('huilv.txt', 'w') as f:
                        f.write(zidinghuilv)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"汇率已修改为：{zidinghuilv}")
                except Exception as e:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"出现错误请检查{e}")

    elif update.message is not None and (update.message.chat.type == 'group' or update.message.chat.type == 'supergroup'):
        save_group_id(update, context)
        message_text = update.message.text
        if message_text == "z0" or message_text == "zo":
            huilv(update, context)
        if tron.isAddress(message_text):
            # 调用函数并获取剩余能量和带宽
            energy_remaining, bandwidth_remaining, balance, usdt_balance = get_account_info(message_text)
            text = f"您的账户:`{message_text}`\n能量：{energy_remaining}\n带宽：{bandwidth_remaining}\nTRX余额:{balance}\nUSDT余额:{usdt_balance}"
            context.bot.send_message(chat_id= update.effective_chat.id, text=text, parse_mode='Markdown')

def save_group_id(update: Update, context: CallbackContext):
    # 确保消息来自群组
    if update.effective_chat.type in ['group', 'supergroup']:
        chat_id = update.message.chat_id
        if chat_id not in all_chats:
            all_chats.add(chat_id)  # 更改为add()方法
            with open('group_ids.txt', 'a') as f:
                f.write(f'{chat_id}\n')
def delete_address(chat_id, deleted_address, filename="自动充.txt"):
    with open(filename, "r", encoding='utf-8') as file:
        lines = file.readlines()
    with open(filename, "w", encoding='utf-8') as file:
        for line in lines:
            if str(chat_id) in line and deleted_address in line:
                # 如果该行包含 chat_id 和要删除的地址，则跳过该行
                continue
            file.write(line)

def read_fanhuan_from_file(filename):
    """读取返利记录文件，返回当日返利总额。支持容错（空行、格式错误行跳过）"""
    try:
        if not os.path.exists(filename):
            return 0.0
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.readlines()
        fanhuan_list = []
        for line in content:
            line = line.strip()
            if not line:
                continue
            try:
                parts = line.split('\t')
                if len(parts) >= 2:
                    fanhuan = float(parts[1])
                    if fanhuan > 0:
                        fanhuan_list.append(fanhuan)
            except (ValueError, IndexError):
                logging.warning(f"[返利] 跳过格式错误行: {line[:50]}...")
                continue
        return sum(fanhuan_list)
    except FileNotFoundError:
        return 0.0
    except Exception as e:
        logging.error(f"[返利] 读取文件失败: {filename}, 错误: {e}")
        return 0.0

def gethuilv():
     # 返回的是1u兑trx的官方汇率
    # 使用 CoinGecko API（免费，不需要API key）
    try:
        # CoinGecko API: 获取TRX的USD价格
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=usd'
        logging.info(f"[gethuilv] 调用CoinGecko API: {url}")
        response = requests.get(url, timeout=10)
        logging.info(f"[gethuilv] API响应状态码: {response.status_code}")
        response.raise_for_status()  # 检查 HTTP 状态码
        data = response.json()
        logging.info(f"[gethuilv] API响应数据: {data}")
        
        # CoinGecko返回格式: {"tron": {"usd": 0.123}}
        if 'tron' not in data:
            logging.error(f"[gethuilv] API响应中缺少tron键，完整响应: {data}")
            raise KeyError(f"API响应中缺少tron键: {data}")
        
        if 'usd' not in data['tron']:
            logging.error(f"[gethuilv] API响应中缺少usd键，完整响应: {data}")
            raise KeyError(f"API响应中缺少usd键: {data}")
        
        trx_price_in_usd = data['tron']['usd']
        logging.info(f"[gethuilv] 获取到TRX价格: {trx_price_in_usd} USD")
        exchange_rate = 1 * huilv_zhekou / float(trx_price_in_usd)
        result = round(exchange_rate, 2)
        logging.info(f"[gethuilv] 计算汇率成功: {result} (折扣系数: {huilv_zhekou})")
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"[gethuilv] API请求失败: {e}", exc_info=True)
        raise  # 重新抛出异常，让调用者知道失败
    except (KeyError, ValueError, TypeError) as e:
        logging.error(f"[gethuilv] 解析API响应失败: {e}，响应内容: {response.text if 'response' in locals() else 'N/A'}", exc_info=True)
        raise  # 重新抛出异常，让调用者知道失败

def gettransaction(address):
    text = 'USDT交易'
    url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?&only_confirmed=true'
    headers = {
        'TRON-PRO-API-KEY': API_KEY
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    if 'data' in data and data['data']:
        transactions = data['data']
        counter = 0
        for transaction in transactions:
            if 'transaction_id' in transaction:
                tx_id = transaction['transaction_id']
                amount = float(transaction['value']) / 10 ** 6
                if amount > 1:
                    timestamp = transaction['block_timestamp']
                    from_address = transaction['from']
                    str="+"
                    if from_address==address:
                        str="-"
                    to_address = transaction['to']
                    date_time = datetime.fromtimestamp(timestamp / 1000.0)
                    type = transaction['type']
                    token_info = transaction['token_info']
                    symbol = token_info['symbol']
                    if symbol == 'USDT':
                        if 'Approval' in type: type = "授权"
                        if 'Transfer' in type: type = "转账"
                        text += f'\n交易哈希:`{tx_id}` \n交易金额:*{str}{amount}{symbol}*类型：{type} \n发送地址:`{from_address}` \n接收地址:`{to_address}`\n交易时间:{date_time}\n-------------------------'
                        counter += 1
                        if counter == 5:
                            break
            else:
                text='此地址未找到交易记录.'
        return text
    else:
        return '此地址未找到交易记录.'


def get_trx_transaction(address):
        text = 'TRX交易:'
        url = f'https://api.trongrid.io/v1/accounts/{address}/transactions?only_confirmed=true'
        headers = {
            'TRON-PRO-API-KEY': API_KEY
        }
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        if 'data' in data and data['data']:
            transactions = data['data']
            counter = 0
            for data in transactions:
                if 'txID' in data:
                    transaction_hash = data['txID']
                    transaction_amount = data['raw_data']['contract'][0]['parameter']['value'].get('amount', 0)
                    transaction_amount = float(transaction_amount) / 10 ** 6
                    if transaction_amount > 1:
                        sender_address = data['raw_data']['contract'][0]['parameter']['value']['owner_address']
                        receiver_address = data['raw_data']['contract'][0]['parameter']['value'].get('to_address', " ")
                        currency_type = data['raw_data']['contract'][0]['type']
                        if currency_type == 'TransferContract':
                            currency_type = 'TRX转账'
                        if currency_type == 'TransferAssetContract':
                            currency_type = 'TRC10转账'
                        if currency_type == 'TriggerSmartContract':
                            currency_type = '合约调用'
                        time = data['block_timestamp']
                        date_time = datetime.fromtimestamp(time / 1000.0)
                        date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
                        sender_address = base58.b58encode_check(bytes.fromhex(sender_address)).decode('utf-8')
                        str = "+"
                        if sender_address == address:
                            str = "-"
                        if receiver_address != 'default_value':
                            receiver_address = base58.b58encode_check(bytes.fromhex(receiver_address)).decode('utf-8')
                        text += f'\n交易哈希:`{transaction_hash}` \n交易金额:*{str}{transaction_amount}*类型:{currency_type}\n发送地址:`{sender_address}` \n接收地址:`{receiver_address}`\n交易时间:{date_time}\n-------------------------'
                        counter += 1
                        if counter == 5:
                            break
                else:
                    text== '\n\n此地址未找到交易记录.'
            return text;
        else:
            return '\n\n此地址未找到交易记录.'


def create_sign(key: str, params: dict) -> str:
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    sign_string = key
    for k, v in sorted_params:
        sign_string += k + str(v)
    return hashlib.md5(sign_string.encode()).hexdigest()

def submit_order(receive_address: str, amount: str, freeze_day: str) -> str:
    conn = http.client.HTTPSConnection("api.tronqq.com")
    payload_params = {
        "uid": uid,
        "resource_type": "0",
        "receive_address": receive_address,
        "amount": amount,
        "freeze_day": freeze_day,
        "time": str(time.time())
    }

    sign = create_sign(api_key, payload_params)
    payload_params["sign"] = sign
    payload = json.dumps(payload_params)

    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/openapi/v2/order/submit", payload, headers)
    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")
def send_channel_message(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("自助服务", url=bot_id),
            InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    now_huilv = gethuilv()
    balance = check_trx_balance(control_address) / now_huilv
    rounded_balance = round(balance, 2)
    text = f"*当前可兑：{rounded_balance} USDT*\n" \
           f"*当前兑换比例1:{now_huilv}*\n" \
           f"24小时进U自动兑，1U起兑\n" \
           f"收款trc20地址为：\n\n" \
           f"`{control_address}`\n" \
           "(点击可复制)\n" + "‼️*注意:请勿使用交易所转账,丢失自负*"
    try:
        update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True,
                                  reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")
def send_channel_messagepower(update: Update, context: CallbackContext):
    address_text = f"{control_address}"
    filename = "能量按钮.txt"
    buttons_data = read_buttons_from_txt(filename)
    # 提取文件中的文本和链接
    button_text, button_url = create_button_data(buttons_data[0])
    # 创建按钮
    button_list = [
        [
            InlineKeyboardButton("👇有效期1小时👇", callback_data="tittle"),

        ],
        [
            InlineKeyboardButton("1次", callback_data="hour_1"),
            InlineKeyboardButton("2次", callback_data="hour_2"),
            InlineKeyboardButton("5次", callback_data="hour_5"),
            InlineKeyboardButton("10次", callback_data="hour_10"),
        ],
        [
            InlineKeyboardButton("👇有效期1天👇", callback_data="tittle"),

        ],
        # 注意这里添加了逗号
        [
            InlineKeyboardButton("5次", callback_data="day_5"),
            InlineKeyboardButton("10次", callback_data="day_10"),
            InlineKeyboardButton("20次", callback_data="day_20"),
            InlineKeyboardButton("50次", callback_data="day_50"),

        ],
        [
            InlineKeyboardButton("👇有效期3天（每天笔数）👇", callback_data="tittle"),

        ],
        [
            InlineKeyboardButton("10次", callback_data="day3_10"),
            InlineKeyboardButton("20次", callback_data="day3_20"),
            InlineKeyboardButton("30次", callback_data="day3_30"),
            InlineKeyboardButton("50次", callback_data="day3_50"),
        ],
        [
            InlineKeyboardButton(button_text, url=button_url),
            InlineKeyboardButton("✈️低价飞机号", url="https://t.me/mianfeituoyi1"),
        ],
        [
            InlineKeyboardButton("💹TRX闪兑", callback_data="💹TRX闪兑"),
            InlineKeyboardButton("🔥免费高速代理", url="https://t.me/hengda666"),
        ]
    ]
    # 创建键盘布局
    reply_markup = InlineKeyboardMarkup(button_list)
    text = f'*提示：所示金额为对方有U的转账手续费，如对方无U请再次购买*\n' \
           f"‼️24小时自动到账原地址，兑能量暂时不支持其他金额！\n"\
           f"收款trc20接收地址为：\n\n" \
           f"`{address_text}`\n" \
           "(点击可复制)\n" +"‼️*注意:请勿使用交易所转账,丢失自负*"
    try:
        update.message.reply_text(text,parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu
def read_buttons_from_txt(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        return [line.strip() for line in lines]
# 创建 Telegram 机器人按钮
def create_button_data(line):
    splitted_data = line.split("，", 1)
    button_text = splitted_data[0]
    button_url = splitted_data[-1]
    return button_text, button_url
def scheduled_message():
    global bot
    # 在您的代码中定义从文本文件读取按钮信息的逻辑
    file_path = f"广告.txt"
    data = ""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()
    file_text =data
    filename = "能量按钮.txt"
    buttons_data = read_buttons_from_txt(filename)
    # 提取文件中的文本和链接
    button_text, button_url = create_button_data(buttons_data[0])

    # 创建按钮
    button_list = [
        [
            InlineKeyboardButton("👇有效期1小时👇", callback_data="tittle"),

        ],
        [
            InlineKeyboardButton("1次", callback_data="hour_1"),
            InlineKeyboardButton("2次", callback_data="hour_2"),
            InlineKeyboardButton("5次", callback_data="hour_5"),
            InlineKeyboardButton("10次", callback_data="hour_10"),
        ],
        [
            InlineKeyboardButton("👇有效期1天👇", callback_data="tittle"),

        ],
        # 注意这里添加了逗号
        [
            InlineKeyboardButton("5次", callback_data="day_5"),
            InlineKeyboardButton("10次", callback_data="day_10"),
            InlineKeyboardButton("20次", callback_data="day_20"),
            InlineKeyboardButton("50次", callback_data="day_50"),

        ],
        [
            InlineKeyboardButton("👇有效期3天（每天笔数）👇", callback_data="tittle"),

        ],
        [
            InlineKeyboardButton("10次", callback_data="day3_10"),
            InlineKeyboardButton("20次", callback_data="day3_20"),
            InlineKeyboardButton("30次", callback_data="day3_30"),
            InlineKeyboardButton("50次", callback_data="day3_50"),
        ],
        [
            InlineKeyboardButton(button_text, url=button_url),
            InlineKeyboardButton("🎁买卖U代付", url="https://t.me/HFTGID"),
        ],
        [
            InlineKeyboardButton("💹TRX闪兑", callback_data="💹TRX闪兑"),
            InlineKeyboardButton("🔥免费高速代理", url="https://t.me/HFTGID"),
        ]

    ]
    # 创建键盘布局
    reply_markup = InlineKeyboardMarkup(button_list)
    edited_message_text = f"💹*实时汇率:1USDT={gethuilv()}TRX\n💹USDT转账仅需3TRX*\n{file_text}\n"

    for chat_id in all_chats:
        try:
            bot.send_message(chat_id=chat_id, text=edited_message_text, parse_mode='Markdown',disable_web_page_preview=True, reply_markup=reply_markup)
        except Exception as e:
            print(f"Error sending message to chat {chat_id}: {e}")


def huilv(update: Update, _: CallbackContext) -> None:
    if update.message:
        message_instance = update.message
    elif update.callback_query:
        message_instance = update.callback_query.message
        update.callback_query.answer()  # 在回调中调用answer()是个好习惯
    keyboard = [
        [
            InlineKeyboardButton("购买价格", callback_data="huilvbuy_all"),
            InlineKeyboardButton("出售价格", callback_data="huilvsell_all"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_instance.reply_text("*选择查看价格类别*👇", parse_mode='Markdown', reply_markup=reply_markup)

def get_existing_prices(filename):
    existing_prices = []
    try:
        with open(filename, "r") as f:
            for line in f.readlines():
                price, _, _ = line.strip().split(',')  # 注意：已调整，不再需要额外的“_”获取 chat_id
                existing_prices.append(float(price))
    except FileNotFoundError:
        pass
    return existing_prices


def on_chat_member_update(update: Update, _: CallbackContext) -> None:
    chat_member_updated_event = update.chat_member_updated
    new_chat_member = chat_member_updated_event.new_chat_member

    group_chat_id = chat_member_updated_event.chat.id

    if new_chat_member.user.id == YOUR_BOT_ID:
        with open("groups.txt", "a") as f:
            f.write(f"{group_chat_id}\n")
    else:
        # The bot was removed from a group
        if chat_member_updated_event.old_chat_member.status \
                in ["administrator","member"] and chat_member_updated_event.new_chat_member.status == "left":
            with open("groups.txt", "r") as f:
                lines = f.readlines()

            with open("groups.txt", "w") as f:
                for line in lines:
                    if line.strip() != str(group_chat_id):
                        f.write(line)


def generate_price(base_price, existing_prices):
    random_decimal = random.randint(1, 29)
    price = base_price + (random_decimal / 100)
    price = round(price, 2)

    if price in existing_prices:
        return generate_price(base_price, existing_prices)
    else:
        return price

def save_data_to_file(chat_id_to_update,final_price, current_time,  filename):
    # 检查文件是否存在，如果不存在则创建
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            pass
    existing_records = []
    # 读取文件中的现有记录
    with open(filename, "r") as file:
        for line in file:
            record = line.strip().split(",")
            existing_records.append(record)

    record_updated = False
    # 在现有记录中查找具有给定 chat_id 的记录并进行替换
    for i, record in enumerate(existing_records):
        if int(record[2]) == chat_id_to_update:  # 注意：在根据修改后的索引将 record[2] 转换为整数进行比较
            # 替换原始记录为新记录
            existing_records[i] = [str(final_price), current_time, str(chat_id_to_update)]
            record_updated = True
            break
    # 如果未找到匹配的 record，则添加新记录
    if not record_updated:
        new_record = [str(final_price), current_time, str(chat_id_to_update)]
        existing_records.append(new_record)
    # 将更新后的记录写入到文件中
    with open(filename, "w") as file:
        for record in existing_records:
            file.write(",".join(record) + "\n")

def update_transaction_data_file_remove_user(chat_id_to_remove, filename="transaction_data.txt"):
    with open(filename, "r") as file:
        lines = file.readlines()

    with open(filename, "w") as file:
        for line in lines:
            record = line.strip().split(",")
            transaction_amount, expiration_time, chat_id = record
            # 如果要删除的 chat_id 与当前记录的 chat_id 匹配，则跳过此行；否则，写入文件
            if chat_id == chat_id_to_remove:
                continue
            else:
                file.write(line)
def handle_callback(update, context) -> None:

    query = update.callback_query
    message_id = query.message.message_id
    address_text = f"{control_address}"
    chat_id=update.effective_chat.id
    
    # 如果用户点击其他按钮（非笔数套餐相关），清除笔数套餐地址监听状态
    if context.user_data.get("bishu_add_address") == INPUT_BISHU_ADDRESS:
        # 检查是否是笔数套餐相关的回调
        is_bishu_related = (
            query.data.startswith("bishu_") or
            query.data in ["bishu_existing", "bishu_add", "bishu_pay_balance", "bishu_pay_now"]
        )
        # 如果不是笔数套餐相关的回调，清除状态
        if not is_bishu_related:
            context.user_data["bishu_add_address"] = None
            context.user_data.pop("bishu_selected_package", None)
    
    if "huilvbuy_" in query.data:
        changehuilvbuy(query)
    elif "huilvsell_" in query.data:
        changehuilvsell(query)
    elif query.data == "back":
        backhuilv(query)
    elif query.data == "ujia":
        huilv(update, context)
    if query.data == "💹TRX闪兑":
        keyboard = [
            [
                InlineKeyboardButton("加入群组", url=group_link),
                InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        now_huilv = gethuilv()
        balance = check_trx_balance(control_address) / now_huilv
        rounded_balance = round(balance, 2)
        text = f"*当前可兑：{rounded_balance} USDT*\n" \
               f"*当前兑换比例1:{now_huilv}*\n" \
               f"24小时进U自动兑，1U起兑\n" \
               f"收款trc20地址为：\n\n" \
               f"`{control_address}`\n" \
               "(点击可复制)\n" + "‼️*注意:请勿使用交易所转账,丢失自负*"

        query.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
    chat_type = update.effective_chat.type
    if chat_type == "private":
        # 处理"给API账号余额充值"按钮点击
        if query.data == "recharge_api_balance":
            # 检查是否为管理员
            if chat_id == admin_id:
                # 确认收到回调（避免Telegram显示加载动画）
                query.answer()
                
                # 从context获取API用户名
                api_username = context.user_data.get('recharge_api_username') or username
                # 保存API用户名和消息ID到context，供后续使用
                context.user_data['recharge_api_username'] = api_username
                context.user_data['recharge_message_id'] = query.message.message_id
                # 设置状态，等待用户输入金额
                context.user_data['recharge'] = INPUT_RECHARGE_AMOUNT
                
                # 编辑消息，提示用户输入金额
                text = "请输入要充值的TRX金额"
                query.edit_message_text(text)
                return
            else:
                query.answer("无权限操作", show_alert=True)
                return

        keyboard = [
            [
                InlineKeyboardButton("余额支付", callback_data="yuezhifu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # 根据回调数据返回相应的信息
        query_to_params = {
            "hour_1": (hour_price, "1小时1次"),
            "hour_2": (hour_price * 2, "1小时2次"),
            "hour_5": (hour_price * 5, "1小时5次"),
            "hour_10": (hour_price * 10, "1小时10次"),
            "day_5": (day_price * 5, "1天内5次"),
            "day_10": (day_price * 10, "1天内10次"),
            "day_20": (day_price * 20, "1天内20次"),
            "day_50": (day_price * 50, "1天内50次"),
            "day3_10": (three_day_price * 30, "3天内每天10次"),
            "day3_20": (three_day_price * 60, "3天内每天20次"),
            "day3_30": (three_day_price * 90, "3天内每天30次"),
            "day3_50": (three_day_price * 150, "3天内每天50次"),
        }
        if query.data == "bangding":
            query.message.reply_text("请输入要预充绑定的地址：")
            context.user_data["bangding"] = INPUT_ADDRESS
            return INPUT_ADDRESS
        if query.data == "shanchu":
            query.message.reply_text("请输入要删除的地址：")
            context.user_data["shanchu"] = delete_ADDRESS
            return delete_ADDRESS
        
        # 处理笔数套餐相关回调
        if query.data == "bishu_existing":
            query.answer()
            # 显示已有套餐
            packages = get_bishu_packages(chat_id)
            if not packages:
                text = "您还没有添加任何笔数套餐地址"
                keyboard = [
                    [InlineKeyboardButton("添加套餐", callback_data="bishu_add")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text, reply_markup=reply_markup)
            else:
                text = "已添加以下地址：\n\n"
                keyboard = []
                for pkg in packages:
                    address = pkg['address']
                    package_type = pkg['package_type']
                    status = pkg['status']
                    package_id = pkg['id']
                    status_text = "✅已激活" if status == 'active' else "⏸已关闭" if status == 'inactive' else "😴已休眠"
                    text += f"`{address}`\n套餐：{package_type} {status_text}\n\n"
                    button_text = f"{address[:12]}...{address[-8:]} {status_text}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{package_id}")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            return
        
        if query.data == "bishu_add":
            query.answer()
            # 显示套餐选择
            keyboard = [
                [
                    InlineKeyboardButton("5笔/15T", callback_data="bishu_pkg_5_15"),
                    InlineKeyboardButton("15笔/45T", callback_data="bishu_pkg_15_45")
                ],
                [
                    InlineKeyboardButton("50笔/150T", callback_data="bishu_pkg_50_150"),
                    InlineKeyboardButton("100笔/300T", callback_data="bishu_pkg_100_300")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = "请选择笔数套餐笔数(不限时间)"
            query.edit_message_text(text, reply_markup=reply_markup)
            return
        
        # 处理套餐选择
        if query.data.startswith("bishu_pkg_"):
            query.answer()
            # 解析套餐信息
            parts = query.data.split("_")
            if len(parts) == 4:
                count = int(parts[2])
                energy = int(parts[3])
                package_type = f"{count}笔/{energy}T"
                
                # 保存套餐信息到context
                context.user_data["bishu_selected_package"] = (package_type, count, energy)
                context.user_data["bishu_add_address"] = INPUT_BISHU_ADDRESS
                
                text = "请输入并发送给我您的绑定钱包地址"
                query.edit_message_text(text)
            return
        
        # 处理笔数套餐支付方式选择
        if query.data == "bishu_pay_balance":
            query.answer()
            # 使用余额支付
            pending_address = context.user_data.get("bishu_pending_address")
            pending_package = context.user_data.get("bishu_pending_package")
            
            if not pending_address or not pending_package:
                query.edit_message_text("订单信息丢失，请重新操作")
                return
            
            package_type, package_count, package_energy = pending_package
            
            # 计算价格
            price_trx = calculate_bishu_package_price(package_count, package_energy)
            price_sun = int(price_trx * 1000000)
            
            # 获取用户余额
            user_data = get_user_data(chat_id)
            if not user_data:
                query.edit_message_text("获取用户信息失败，请重试")
                return
            
            balance = user_data.get("amount", 0)
            
            if balance < price_sun:
                query.edit_message_text(f"余额不足，需要 {price_trx} TRX，当前余额 {balance/1000000:.2f} TRX\n请先充值")
                return
            
            # 扣除余额
            new_balance = balance - price_sun
            update_balance(chat_id, new_balance)
            print(f"笔数套餐余额支付：用户{chat_id} 扣除 {price_trx} TRX，剩余 {new_balance/1000000:.2f} TRX")
            
            # 调用能量池API：1小时1笔（65000能量，day=0）
            # 笔数套餐使用1小时1笔的API，每次消耗1个API余额
            result = energy_tran2(65000, 0, pending_address)
            
            # 生成订单号
            order_number = f"BISHU_{int(time.time())}_{chat_id}"
            
            if result.get("success") or result.get("tx_hash"):
                # 能量下发成功
                tx_hash = result.get("tx_hash", order_number)
                
                # 保存订单
                save_order_to_db(
                    chat_id=chat_id,
                    order_number=order_number,
                    energy_amount=total_energy,
                    duration=f"笔数套餐-{package_type}",
                    receiver_address=pending_address,
                    amount=price_trx,
                    payment_method='balance',
                    status='completed',
                    tx_hash=tx_hash,
                    remark=f"笔数套餐：{package_type}"
                )
                
                # 保存套餐到数据库
                save_bishu_package(chat_id, pending_address, package_type, package_count, package_energy)
                
                # 清除pending数据
                context.user_data.pop("bishu_pending_address", None)
                context.user_data.pop("bishu_pending_package", None)
                
                # 显示已添加的地址列表给用户
                packages = get_bishu_packages(chat_id)
                text = "已添加以下地址：\n\n"
                keyboard = []
                for pkg in packages:
                    addr = pkg['address']
                    pkg_type = pkg['package_type']
                    pkg_status = pkg['status']
                    pkg_id = pkg['id']
                    status_text = "✅已激活" if pkg_status == 'active' else "⏸已关闭" if pkg_status == 'inactive' else "😴已休眠"
                    text += f"`{addr}`\n套餐：{pkg_type} {status_text}\n\n"
                    button_text = f"{addr[:12]}...{addr[-8:]} {status_text}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{pkg_id}")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                # 通知管理员笔数套餐余额支付成功
                try:
                    success_admin_text = (
                        f"✅笔数套餐余额支付成功\n"
                        f"用户：{chat_id}\n"
                        f"地址：`{pending_address}`\n"
                        f"套餐：{package_type}\n"
                        f"金额：{price_trx} TRX\n"
                        f"订单号：{order_number}\n"
                        f"能量交易哈希：{tx_hash}"
                    )
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=success_admin_text,
                        parse_mode='Markdown',
                        disable_web_page_preview=True,
                    )
                except Exception as e:
                    print(f"通知管理员笔数套餐余额支付成功失败: {e}")
            else:
                # 能量下发失败，但已扣费，需要退款或记录
                error_msg = result.get("message", "未知错误")
                save_order_to_db(
                    chat_id=chat_id,
                    order_number=order_number,
                    energy_amount=total_energy,
                    duration=f"笔数套餐-{package_type}",
                    receiver_address=pending_address,
                    amount=price_trx,
                    payment_method='balance',
                    status='failed',
                    tx_hash=None,
                    remark=f"笔数套餐失败: {error_msg}"
                )
                # 通知用户失败原因
                query.edit_message_text(
                    f"❌ 能量下发失败\n已扣除 {price_trx} TRX\n"
                    f"剩余余额：{new_balance/1000000:.2f} TRX\n"
                    f"失败原因：{error_msg}\n订单号：{order_number}\n请联系客服处理"
                )

                # 通知管理员失败详情
                try:
                    failed_admin_text = (
                        f"❌笔数套餐余额支付能量下发失败\n"
                        f"用户：{chat_id}\n"
                        f"地址：`{pending_address}`\n"
                        f"套餐：{package_type}\n"
                        f"金额：{price_trx} TRX\n"
                        f"订单号：{order_number}\n"
                        f"失败原因：{error_msg}"
                    )
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=failed_admin_text,
                        parse_mode='Markdown',
                        disable_web_page_preview=True,
                    )
                except Exception as e:
                    print(f"通知管理员笔数套餐余额支付失败信息失败: {e}")
            return
        
        if query.data == "bishu_pay_now":
            query.answer()
            # 立即支付（生成支付订单）
            pending_address = context.user_data.get("bishu_pending_address")
            pending_package = context.user_data.get("bishu_pending_package")
            
            if not pending_address or not pending_package:
                query.edit_message_text("订单信息丢失，请重新操作")
                return
            
            package_type, package_count, package_energy = pending_package
            
            # 计算价格
            price_trx = calculate_bishu_package_price(package_count, package_energy)
            
            # 生成带两位小数的金额
            base_amount = math.floor(price_trx)
            random_decimal = random.randint(0, 99)
            final_amount = base_amount + random_decimal / 100
            
            # 计算过期时间（10分钟后）
            expires_at = datetime.now() + timedelta(minutes=10)
            
            # 生成订单号
            order_number = f"BISHU_{int(time.time())}_{chat_id}"
            
            # 保存订单到数据库（pending状态）
            try:
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor()
                
                insert_query = """
                INSERT INTO orders (
                    order_number, chat_id, plan, amount, status, 
                    payment_method, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, 'pending', 'trx', NOW(), NOW())
                """
                
                # 将地址信息编码到plan中，格式：笔数套餐-5笔/15T|地址
                plan_with_address = f"笔数套餐-{package_type}|{pending_address}"
                
                cursor.execute(insert_query, (
                    order_number,
                    chat_id,
                    plan_with_address,
                    final_amount
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # 保存订单信息到context，用于支付成功后处理
                context.user_data["bishu_pending_order"] = {
                    "order_number": order_number,
                    "address": pending_address,
                    "package": pending_package,
                    "amount": final_amount
                }
                
                # 显示支付信息
                expires_time = expires_at.strftime("%Y-%m-%d %H:%M:%S")
                text = (f"请使用 TRC-20 钱包对以下地址付款\n\n"
                       f"订单号: {order_number[:8]}\n"
                       f"套餐: {package_type}\n"
                       f"充值金额: {final_amount:.2f} TRX\n"
                       f"付款地址(可点击复制地址):\n\n"
                       f"<code>{RECHARGE_PAYMENT_ADDRESS}</code>\n\n"
                       f"付款截止时间10分钟\n"
                       f"到期时间: {expires_time}")
                
                query.edit_message_text(text, parse_mode='HTML')
                
            except Exception as e:
                print(f"创建支付订单失败: {e}")
                query.edit_message_text(f"创建订单失败: {str(e)}")
            return
        
        # 处理地址按钮点击
        if query.data.startswith("bishu_address_"):
            query.answer()
            package_id = int(query.data.split("_")[-1])
            # 显示激活/关闭/删除按钮
            keyboard = [
                [
                    InlineKeyboardButton("激活", callback_data=f"bishu_activate_{package_id}"),
                    InlineKeyboardButton("关闭", callback_data=f"bishu_close_{package_id}"),
                    InlineKeyboardButton("删除", callback_data=f"bishu_delete_{package_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_reply_markup(reply_markup=reply_markup)
            return
        
        # 处理激活/关闭/删除操作
        if query.data.startswith("bishu_activate_"):
            query.answer("正在激活...")
            package_id = int(query.data.split("_")[-1])
            
            # 获取套餐信息
            packages = get_bishu_packages(chat_id)
            package = next((p for p in packages if p['id'] == package_id), None)
            
            if not package:
                query.answer("套餐不存在", show_alert=True)
                return
            
            address = package['address']
            
            # 调用能量池API：1小时1笔（65000能量，day=0）
            result = energy_tran2(65000, 0, address)
            
            if result.get("success") or result.get("tx_hash"):
                # 能量下发成功，更新状态为激活并记录激活时间
                try:
                    conn = mysql.connector.connect(**config)
                    cursor = conn.cursor()
                    
                    update_query = """
                    UPDATE bishu_packages
                    SET status = 'active', 
                        activated_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (package_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    query.answer("✅已激活并下发能量")
                except Exception as e:
                    print(f"更新激活状态失败: {e}")
                    query.answer("激活失败，请重试", show_alert=True)
                    return
            else:
                error_msg = result.get("message", "未知错误")
                query.answer(f"❌能量下发失败: {error_msg}", show_alert=True)
                return
            
            # 刷新地址列表
            update_bishu_package_status(package_id, 'active')
            # 刷新地址列表
            packages = get_bishu_packages(chat_id)
            text = "已添加以下地址：\n\n"
            keyboard = []
            for pkg in packages:
                address = pkg['address']
                package_type = pkg['package_type']
                status = pkg['status']
                pkg_id = pkg['id']
                status_text = "✅已激活" if status == 'active' else "⏸已关闭" if status == 'inactive' else "😴已休眠"
                text += f"`{address}`\n套餐：{package_type} {status_text}\n\n"
                button_text = f"{address[:12]}...{address[-8:]} {status_text}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{pkg_id}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            return
        
        if query.data.startswith("bishu_close_"):
            query.answer("已关闭")
            package_id = int(query.data.split("_")[-1])
            update_bishu_package_status(package_id, 'inactive')
            # 刷新地址列表
            packages = get_bishu_packages(chat_id)
            text = "已添加以下地址：\n\n"
            keyboard = []
            for pkg in packages:
                address = pkg['address']
                package_type = pkg['package_type']
                status = pkg['status']
                pkg_id = pkg['id']
                status_text = "✅已激活" if status == 'active' else "⏸已关闭" if status == 'inactive' else "😴已休眠"
                text += f"`{address}`\n套餐：{package_type} {status_text}\n\n"
                button_text = f"{address[:12]}...{address[-8:]} {status_text}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{pkg_id}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            return
        
        if query.data.startswith("bishu_delete_"):
            query.answer("已删除")
            package_id = int(query.data.split("_")[-1])
            delete_bishu_package(package_id)
            # 刷新地址列表
            packages = get_bishu_packages(chat_id)
            if not packages:
                text = "您还没有添加任何笔数套餐地址"
                keyboard = [
                    [InlineKeyboardButton("添加套餐", callback_data="bishu_add")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text, reply_markup=reply_markup)
            else:
                text = "已添加以下地址：\n\n"
                keyboard = []
                for pkg in packages:
                    address = pkg['address']
                    package_type = pkg['package_type']
                    status = pkg['status']
                    pkg_id = pkg['id']
                    status_text = "✅已激活" if status == 'active' else "⏸已关闭" if status == 'inactive' else "😴已休眠"
                    text += f"`{address}`\n套餐：{package_type} {status_text}\n\n"
                    button_text = f"{address[:12]}...{address[-8:]} {status_text}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{pkg_id}")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            return
        if query.data in query_to_params:
            payment_amount, desc = query_to_params[query.data]
            user_payment_amount[chat_id] = payment_amount
            text = f"收款金额：*{payment_amount}TRX*\n使用期限：*{desc}*\n24小时收款trc20地址为：\n`{address_text}`\n*TRX支付请直接转账能量即回原地址*"
            update_message_text(chat_id, message_id, new_text=text, reply_markup=reply_markup)
            return
        if query.data in ("20", "30", "50","100", "200", "500"):
            base_price = int(query.data)
            existing_prices = get_existing_prices("transaction_data.txt")
            final_price = generate_price(base_price, existing_prices)
            now = datetime.now()
            ten_minutes_later = now + timedelta(minutes=20)
            current_time = ten_minutes_later.strftime("%Y-%m-%d %H:%M:%S")
            # 写入本地待支付记录文件（用于金额匹配）
            save_data_to_file(chat_id, final_price, current_time, "transaction_data.txt")
            
            # 在机器人系统后台生成一条「普通用户余额充值」订单（待支付）
            try:
                order_number = f"RECHARGE_{int(time.time())}_{chat_id}"
                ok = save_order_to_db(
                    chat_id=chat_id,
                    order_number=order_number,
                    energy_amount=None,
                    duration=f"用户余额充值（待支付），截止：{current_time}",
                    receiver_address=control_address,
                    amount=float(final_price),
                    payment_method='recharge',
                    status='pending',
                    tx_hash=None,
                    remark="用户在机器人发起余额充值订单，等待链上支付",
                    username=None,
                )
                if ok:
                    payment_logger.info(
                        f"[充值订单] 创建待支付订单: chat_id={chat_id}, amount={final_price}, order_number={order_number}"
                    )
                else:
                    payment_logger.error(
                        f"[充值订单] 创建待支付订单失败(保存返回False): chat_id={chat_id}, amount={final_price}, order_number={order_number}"
                    )
            except Exception as order_err:
                payment_logger.error(
                    f"[充值订单] 创建待支付订单失败, chat_id={chat_id}, amount={final_price}, err={order_err}"
                )
            
            text = (
                f"用户ID：{chat_id}\n"
                f"订单金额：`{final_price}`TRX(点击可复制金额)"
                f"\n收款地址：`{control_address}`\n"
                f"‼️*请务必核对金额尾数，金额不对则无法确认*。\n"
                f"订单将于{current_time}过期，请尽快支付！"
            )
            update_message_text(chat_id, message_id, new_text=text)
            return
        if query.data == "yuezhifu":
            text = f"请输入您要充值的地址，格式：能量+地址例：\n`能量`TFZHf2TZDFND2GSJVDaLRmTkXXXXXXXX"
            update_message_text(chat_id, message_id, new_text=text)
        if query.data == "cancel":
            update_message_text(chat_id, message_id, new_text=f'订单已取消，如有需要请重新下单！')
        if query.data == "confirm":
            user_data = get_user_data(chat_id)
            if user_data:
                balance = user_data["amount"]
                address_search = re.search(r"能量接收地址：(.+)", query.message.text)
                if address_search:
                    address = address_search.group(1)
                else:
                    update_message_text(chat_id, message_id, "找不到有效的地址，请重试。")
                    return
                # 提取 payment_amount
                payment_amount_search = re.search(r"消费金额：(\d+(\.\d+)?)TRX", query.message.text)
                if payment_amount_search:
                    payment_amount = float(payment_amount_search.group(1))
                else:
                    update_message_text(chat_id, message_id, "找不到有效的支付金额，请重试。")
                    return
                us_amount = payment_amount * 1000000
                if balance>us_amount:
                    keyboard = [
                        [
                            InlineKeyboardButton("自助服务", url=bot_id),
                            InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    from_address=address

                    energy_params = {
                        hour_price*1000000: (65000, "1小时1次", 0),
                        hour_price*1000000 * 2: (65000*2, "1小时2次", 0),
                        hour_price*1000000 * 5: (65000*5, "1小时5次", 0),
                        hour_price*1000000 * 10: (65000*10, "1小时10次", 0),
                        day_price*1000000 * 5: (65000*5, "1天5次", 1),
                        day_price*1000000 * 10: (65000*10, "1天10次", 1),
                        day_price*1000000 * 20: (65000*20, "1天20次", 1),
                        day_price*1000000 * 50: (65000*50, "1天50次", 1),
                        three_day_price*1000000 * 30: (65000*10, "3天内每天10次", 3),
                        three_day_price*1000000 * 60: (65000*20, "3天内每天20次", 3),
                        three_day_price*1000000 * 90: (65000*30, "3天内每天30次", 3),
                        three_day_price*1000000 * 150: (65000*50, "3天内每天50次", 3),
                    }
                    # 查找指定的 us_amount
                    if us_amount in energy_params:
                        energy, desc, days = energy_params[us_amount]

                        # 【关键修改1】先扣除余额（无论后续成功失败）
                        new_balance = balance - us_amount
                        update_balance(chat_id, new_balance)
                        print(f"余额支付：用户{chat_id} 扣除 {us_amount/1000000} TRX，剩余 {new_balance/1000000} TRX")

                        # 【关键修改2】尝试下发能量
                        result = energy_tran2(energy, days, from_address)
                        
                        if result.get("success"):
                            # 能量下发成功
                            txid = result.get("tx_hash")
                            api_balance = result.get('new_balance')
                            transaction_url = f"https://tronscan.org/?utm_source=tronlink#/transaction/{txid}?lang=zh"
                            
                            # 【关键修改3】记录成功订单到orders表
                            save_order_to_db(
                                chat_id=chat_id,
                                order_number=txid,
                                energy_amount=energy,
                                duration=desc,
                                receiver_address=from_address,
                                amount=payment_amount,
                                payment_method='balance',
                                status='completed',
                                tx_hash=txid
                            )
                            
                            # 更新消息
                            text = (f"✅VIP客户 下发完成\n➖➖➖➖➖➖➖➖\n"
                                    f"套餐模式：笔数模式\n"
                                    f"能量带宽：{energy}\n"
                                    f"有效时长：{desc}\n"
                                    f"接收地址：{from_address[:8]}......{from_address[-8:]}\n"
                                    f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})"
                                    f"")
                            new_text = text + f"\n余额：{new_balance / 1000000} TRX"
                            update_message_text(chat_id, message_id, new_text)
                            try:
                                text = f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})\n消耗能量{energy}\napi余额：{api_balance / 1000000}"
                                bot.send_message(chat_id=admin_id, text=text,
                                                 disable_web_page_preview=True, parse_mode='Markdown')
                            except Exception as e:
                                print(f"私聊错误--{e}")
                            
                            for group_chat_id in all_chats:
                                try:
                                    # 发送兑换成功的通知
                                    bot.send_message(chat_id=group_chat_id,
                                                     text=text, disable_web_page_preview=True,
                                                     parse_mode='Markdown',
                                                     reply_markup=reply_markup)
                                except Exception as e:
                                    print(f"Error sending message to group {group_chat_id}: {e}")
                        else:
                            # 【关键修改4】能量下发失败，但仍记录失败订单
                            error_msg = result.get("message", "未知错误")
                            order_number = f"FAIL_{int(time.time())}_{chat_id}"
                            
                            save_order_to_db(
                                chat_id=chat_id,
                                order_number=order_number,
                                energy_amount=energy,
                                duration=desc,
                                receiver_address=from_address,
                                amount=payment_amount,
                                payment_method='balance',
                                status='failed',
                                tx_hash=None,
                                remark=f"下发失败: {error_msg}"
                            )
                            
                            update_message_text(chat_id, message_id, 
                                new_text=f"❌ 能量下发失败\n"
                                        f"已扣除 {payment_amount} TRX\n"
                                        f"剩余余额：{new_balance / 1000000} TRX\n"
                                        f"失败原因：{error_msg}\n"
                                        f"订单号：{order_number}\n"
                                        f"请联系客服处理")
                            
                            # 通知管理员
                            try:
                                admin_text = f"⚠️ 余额支付失败\n用户：{chat_id}\n金额：{payment_amount} TRX\n地址：{from_address}\n原因：{error_msg}\n订单：{order_number}"
                                bot.send_message(chat_id=admin_id, text=admin_text)
                            except Exception as e:
                                print(f"通知管理员错误--{e}")

                else:
                    update_message_text(chat_id, message_id, new_text=f'账户余额不足，请充值')
            else:
                update_message_text(chat_id, message_id, new_text=f'账户余额不足，请充值')
    if chat_type == "group" or chat_type == "supergroup":
        username=query.from_user.first_name
        query_to_params = {
            "hour_1": (hour_price, "1小时1次"),
            "hour_2": (hour_price * 2, "1小时2次"),
            "hour_5": (hour_price * 5, "1小时5次"),
            "hour_10": (hour_price * 10, "1小时10次"),
            "day_5": (day_price * 5, "1天内5次"),
            "day_10": (day_price * 10, "1天内10次"),
            "day_20": (day_price * 20, "1天内20次"),
            "day_50": (day_price * 50, "1天内50次"),
            "day3_10": (three_day_price * 30, "3天内每天10次"),
            "day3_20": (three_day_price * 60, "3天内每天20次"),
            "day3_30": (three_day_price * 90, "3天内每天30次"),
            "day3_50": (three_day_price * 150, "3天内每天50次"),
        }
        if query.data in query_to_params:
            price, desc = query_to_params[query.data]
            text = f"{username}\n\n收款金额：*{price}TRX*\n使用期限：*{desc}*\n24小时收款trc20地址为：\n`{address_text}`\n*TRX支付请直接转账能量即回原地址*"
            context.bot.send_message(chat_id, text, parse_mode="Markdown")

def update_message_text(chat_id, message_id, new_text, reply_markup=None):
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode='Markdown',
                                      disable_web_page_preview=True, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error when updating message text: {e}")

def update_balance(chat_id, new_balance):
    try:
        # 使用HTTP请求调用前端API
        api_url = "http://localhost:3000/api/bot-set-balance"
        data = {
            "chat_id": chat_id,
            "new_balance": new_balance
        }
        response = requests.post(api_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"Balance updated successfully for user {chat_id}")
            else:
                print(f"API error in update_balance: {result.get('message')}")
        else:
            print(f"HTTP error in update_balance: {response.status_code}")
    except Exception as e:
        print(f"API request error in update_balance: {e}")

def save_order_to_db(
    chat_id,
    order_number,
    energy_amount,
    duration,
    receiver_address,
    amount,
    payment_method='balance',
    status='completed',
    tx_hash=None,
    remark=None,
    username=None,
):
    """
    保存订单到数据库（对齐 nl-admin.sql 中的 orders 表结构）

    当前数据库表结构为：
      id, order_number, chat_id, username, plan, amount, status,
      payment_method, created_at, updated_at

    我们把机器人内部的字段映射为：
      - chat_id       -> chat_id
      - order_number  -> order_number
      - username      -> username（如果有的话）
      - plan          -> 聚合说明文案（套餐 / 能量 / 地址 / 备注 等信息）
      - amount        -> 支付金额(TRX)
      - status        -> 订单状态（completed/failed/pending 等）
      - payment_method-> 支付方式（balance/trx 等）
    """
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # 组装一个可读的 plan 文本，方便在后台订单管理里查看
        detail_parts = []
        if duration:
            detail_parts.append(str(duration))
        if energy_amount is not None:
            try:
                detail_parts.append(f"能量: {float(energy_amount)}")
            except Exception:
                detail_parts.append(f"能量: {energy_amount}")
        if receiver_address:
            detail_parts.append(f"地址: {receiver_address}")
        if tx_hash:
            # 只展示前后几位，避免太长
            tx_short = str(tx_hash)
            if len(tx_short) > 14:
                tx_short = f"{tx_short[:6]}...{tx_short[-6:]}"
            detail_parts.append(f"TX: {tx_short}")
        if remark:
            detail_parts.append(f"备注: {remark}")

        plan_text = " | ".join(detail_parts) if detail_parts else "能量订单"
        # 防止超出数据库 plan 字段长度 (varchar(100))
        if len(plan_text) > 95:
            plan_text = plan_text[:95] + "..."
        
        insert_query = """
        INSERT INTO orders (
            order_number,
            chat_id,
            username,
            plan,
            amount,
            status,
            payment_method,
            created_at,
            updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

        cursor.execute(
            insert_query,
            (
                str(order_number),
                int(chat_id),
                username,
                plan_text,
            float(amount),
            status,
                payment_method,
            ),
        )
        
        conn.commit()
        payment_logger.info(f"订单保存成功: {order_number}, 用户: {chat_id}, 状态: {status}, 金额: {amount}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        payment_logger.error(f"保存订单到数据库失败: {e}")
        return False

def get_address_energy(address):
    """查询地址的当前能量余额"""
    try:
        # 使用get_account_info函数查询地址能量
        energy_remaining, _, _, _ = get_account_info(address)
        return energy_remaining
    except Exception as e:
        print(f"查询地址能量失败 {address}: {e}")
        # 如果查询失败，返回None表示查询错误
        return None

def calculate_bishu_package_price(package_count, package_energy):
    """计算笔数套餐价格
    价格直接等于package_energy（TRX数量）
    例如：5笔/15T = 15 TRX, 15笔/45T = 45 TRX, 50笔/150T = 150 TRX, 100笔/300T = 300 TRX
    """
    # 价格直接等于能量数量（TRX）
    return float(package_energy)

def save_bishu_package(chat_id, address, package_type, package_count, package_energy):
    """保存笔数套餐到数据库"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO bishu_packages (
            chat_id, address, package_type, package_count, package_energy, 
            status, last_transfer_time, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, 'active', NULL, NOW(), NOW())
        """
        
        cursor.execute(insert_query, (
            chat_id,
            address,
            package_type,
            package_count,
            package_energy
        ))
        
        conn.commit()
        print(f"笔数套餐保存成功: 用户{chat_id}, 地址{address}, 套餐{package_type}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"保存笔数套餐失败: {e}")
        return False

def get_bishu_packages(chat_id):
    """获取用户的笔数套餐列表"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        select_query = """
        SELECT id, address, package_type, package_count, package_energy, 
               status, last_transfer_time, activated_at, created_at
        FROM bishu_packages
        WHERE chat_id = %s
        ORDER BY created_at DESC
        """
        
        cursor.execute(select_query, (chat_id,))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"获取笔数套餐失败: {e}")
        return []

def update_bishu_package_status(package_id, status):
    """更新笔数套餐状态"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        update_query = """
        UPDATE bishu_packages
        SET status = %s, updated_at = NOW()
        WHERE id = %s
        """
        
        cursor.execute(update_query, (status, package_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"更新笔数套餐状态失败: {e}")
        return False

def delete_bishu_package(package_id):
    """删除笔数套餐"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        delete_query = "DELETE FROM bishu_packages WHERE id = %s"
        cursor.execute(delete_query, (package_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"删除笔数套餐失败: {e}")
        return False

def process_bishu_payment_success(chat_id, order_number, tx_hash, bot_instance):
    """处理笔数套餐支付成功后的逻辑"""
    try:
        # 从数据库获取订单信息
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        select_query = """
        SELECT order_number, chat_id, plan, amount, status
        FROM orders
        WHERE order_number = %s AND status = 'pending'
        """
        cursor.execute(select_query, (order_number,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            return False
        
        # 从plan中提取套餐信息和地址（格式：笔数套餐-5笔/15T|地址）
        plan = order['plan']
        if '笔数套餐-' in plan and '|' in plan:
            # 解析：笔数套餐-5笔/15T|地址
            parts = plan.split('|')
            if len(parts) == 2:
                package_info_str = parts[0].replace('笔数套餐-', '')
                address = parts[1]
                
                # 解析套餐信息：5笔/15T -> count=5, energy=15
                pkg_parts = package_info_str.split('笔/')
                if len(pkg_parts) == 2:
                    package_count = int(pkg_parts[0])
                    package_energy = int(pkg_parts[1].replace('T', ''))
                    package_type = f"{package_count}笔/{package_energy}T"
                    
                    # 调用能量池API：1小时1笔（65000能量，day=0）
                    # 笔数套餐使用1小时1笔的API，每次消耗1个API余额
                    result = energy_tran2(65000, 0, address)
                    
                    if result.get("success") or result.get("tx_hash"):
                        # 能量下发成功
                        energy_tx_hash = result.get("tx_hash", tx_hash)
                        
                        # 更新订单状态
                        update_query = """
                        UPDATE orders
                        SET status = 'completed', updated_at = NOW()
                        WHERE order_number = %s
                        """
                        cursor.execute(update_query, (order_number,))
                        conn.commit()
                        
                        # 保存套餐到数据库（状态为active，已激活）
                        save_bishu_package(chat_id, address, package_type, package_count, package_energy)
                        
                        # 更新激活时间
                        try:
                            update_pkg_query = """
                            UPDATE bishu_packages
                            SET status = 'active', 
                                activated_at = NOW(),
                                updated_at = NOW()
                            WHERE chat_id = %s AND address = %s
                            """
                            cursor.execute(update_pkg_query, (chat_id, address))
                            conn.commit()
                        except Exception as e:
                            print(f"更新套餐激活时间失败: {e}")
                        
                        # 显示地址列表给用户
                        packages = get_bishu_packages(chat_id)
                        text = "✅支付成功！订单已处理\n\n已添加以下地址：\n\n"
                        keyboard = []
                        for pkg in packages:
                            addr = pkg['address']
                            pkg_type = pkg['package_type']
                            pkg_status = pkg['status']
                            pkg_id = pkg['id']
                            status_text = "✅已激活" if pkg_status == 'active' else "⏸已关闭" if pkg_status == 'inactive' else "😴已休眠"
                            text += f"`{addr}`\n套餐：{pkg_type} {status_text}\n\n"
                            button_text = f"{addr[:12]}...{addr[-8:]} {status_text}"
                            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{pkg_id}")])
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        try:
                            bot_instance.send_message(
                                chat_id=chat_id,
                                text=text,
                                parse_mode='Markdown',
                                reply_markup=reply_markup
                            )
                        except Exception as e:
                            print(f"发送消息失败: {e}")
                        
                        # 通知管理员笔数套餐TRX支付成功
                        try:
                            admin_text = (
                                f"✅笔数套餐TRX支付成功\n"
                                f"用户：{chat_id}\n"
                                f"地址：{address}\n"
                                f"套餐：{package_type}\n"
                                f"订单号：{order_number}\n"
                                f"能量交易哈希：{energy_tx_hash}"
                            )
                            bot_instance.send_message(chat_id=admin_id, text=admin_text)
                        except Exception as e:
                            print(f"通知管理员笔数套餐TRX支付成功失败: {e}")
                        
                        cursor.close()
                        conn.close()
                        return True
                    else:
                        # 能量下发失败
                        error_msg = result.get("message", "未知错误")
                        update_query = """
                        UPDATE orders
                        SET status = 'failed', updated_at = NOW()
                        WHERE order_number = %s
                        """
                        cursor.execute(update_query, (order_number,))
                        conn.commit()
                        
                        try:
                            # 通知用户
                            bot_instance.send_message(
                                chat_id=chat_id,
                                text=f"❌ 能量下发失败\n订单号：{order_number[:8]}\n失败原因：{error_msg}\n请联系客服处理"
                            )
                        except Exception as e:
                            print(f"通知用户笔数套餐能量下发失败消息失败: {e}")

                        # 通知管理员
                        try:
                            admin_text = (
                                f"❌笔数套餐TRX支付后能量下发失败\n"
                                f"用户：{chat_id}\n"
                                f"地址：{address}\n"
                                f"套餐：{package_type}\n"
                                f"订单号：{order_number}\n"
                                f"失败原因：{error_msg}"
                            )
                            bot_instance.send_message(chat_id=admin_id, text=admin_text)
                        except Exception as e:
                            print(f"通知管理员笔数套餐能量下发失败消息失败: {e}")
                        
                        cursor.close()
                        conn.close()
                        return False
        
        cursor.close()
        conn.close()
        return False
    except Exception as e:
        print(f"处理笔数套餐支付成功失败: {e}")
        return False

def show_bishu_addresses(update, context, chat_id):
    """显示用户的笔数套餐地址列表"""
    packages = get_bishu_packages(chat_id)
    
    if not packages:
        text = "您还没有添加任何笔数套餐地址"
        keyboard = [
            [InlineKeyboardButton("添加套餐", callback_data="bishu_add")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)
        return
    
    text = "已添加以下地址：\n\n"
    keyboard = []
    
    for pkg in packages:
        address = pkg['address']
        package_type = pkg['package_type']
        status = pkg['status']
        package_id = pkg['id']
        
        # 显示地址和套餐信息
        status_text = "✅已激活" if status == 'active' else "⏸已关闭" if status == 'inactive' else "😴已休眠"
        text += f"`{address}`\n套餐：{package_type} {status_text}\n\n"
        
        # 创建地址按钮（每行一个）
        button_text = f"{address[:12]}...{address[-8:]} {status_text}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"bishu_address_{package_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

def changehuilvbuy(query) -> None:
    method = query.data.split("huilvbuy_")[1]
    url = f"https://www.okx.com/v3/c2c/tradingOrders/books?quoteCurrency=CNY&baseCurrency=USDT&side=sell&paymentMethod={method}&userType=blockTrade&showTrade=false&receivingAds=false&showFollow=false&showAlreadyTraded=false&isAbleFilter=false&urlId=2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()

        # 根据不同的支付方式设置标题
        if method == "bank":
            title = "【银行卡实时购买汇率】"
            method_button_text = "✅银行卡"
        elif method == "aliPay":
            title = "【支付宝实时购买汇率】"
            method_button_text = "✅支付宝"
        elif method == "wxPay":
            title = "【微信实时购买汇率】"
            method_button_text = "✅微信"
        elif method == "all":
            title = "【实时购买汇率】"
            method_button_text = "✅所有"

        sendvalue = f"<b><a href='https://www.okx.com/cn/p2p-markets/cny/buy-usdt'>🐻OKX欧易</a>{title}</b>\n\n"
        allprice = 0
        element_count = min(10, len(json_data["data"]["sell"]))
        for index in range(element_count):
            element = json_data['data']['sell'][index]
            emoji_number = f'{index + 1}\ufe0f⃣' if index + 1 != 10 else '🔟'
            sendvalue += f'{emoji_number}  {element["price"]}  {element["nickName"]}\n'
            allprice += float(element['price'])

        sendvalue += f"\n实时价格：1 USDT * {format(allprice / 10, '.5f')} = {format((allprice / 10), '.2f')}"

        # 添加当前时间显示
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        sendvalue += f"\n数据获取时间：{current_time}"

        method_buttons = [
            ("✅所有" if method == "all" else "所有", "huilvbuy_all"),
            ("✅微信" if method == "wxPay" else "微信", "huilvbuy_wxPay"),
            ("✅支付宝" if method == "aliPay" else "支付宝", "huilvbuy_aliPay"),
            ("✅银行卡" if method == "bank" else "银行卡", "huilvbuy_bank"),
        ]
        inline_keyboard = [
            [InlineKeyboardButton(text=text, callback_data='bot_{}'.format(data)) for text, data in method_buttons],
            [InlineKeyboardButton("返回", callback_data="back")],
        ]
        query.edit_message_text(
            text=sendvalue,
            disable_web_page_preview=True,
            parse_mode="HTML",  # 添加此行以解析 HTML 格式
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
        )

def backhuilv(query) -> None:
    inline_keyboard = [
        [
            InlineKeyboardButton("购买价格", callback_data="huilvbuy_all"),
            InlineKeyboardButton("出售价格", callback_data="huilvsell_all")
        ]
    ]
    query.edit_message_text(text="<b>选择查看价格类别👇</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard),
                            parse_mode="HTML")

def changehuilvsell(query):
    method = query.data.split("huilvsell_")[1]
    url = f'https://www.okx.com/v3/c2c/tradingOrders/books?quoteCurrency=CNY&baseCurrency=USDT&side=buy&paymentMethod={method}&userType=blockTrade'  # aliPay wxPay

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        body = response.json()

        sendvalue = ""
        yhk = "银行卡"
        zfb = "支付宝"
        wx = "微信"
        all = "所有"

        if method == "bank":
            sendvalue = "<b><a href='https://www.okx.com/cn/p2p-markets/cny/buy-usdt'>🐻OKX欧意</a>【银行卡实时出售汇率】</b>\n\n"
            yhk = "✅银行卡"
        elif method == "aliPay":
            sendvalue = "<b><a href='https://www.okx.com/cn/p2p-markets/cny/buy-usdt'>🐻OKX欧意</a>【支付宝实时出售汇率】</b>\n\n"
            zfb = "✅支付宝"
        elif method == "wxPay":
            sendvalue = "<b><a href='https://www.okx.com/cn/p2p-markets/cny/buy-usdt'>🐻OKX欧意</a>【微信实时出售汇率】</b>\n\n"
            wx = "✅微信"
        elif method == "all":
            sendvalue = "<b><a href='https://www.okx.com/cn/p2p-markets/cny/buy-usdt'>🐻OKX欧意</a>【实时出售汇率】</b>\n\n"
            all = "✅所有"

        allprice = 0
        try:
            element_count = min(10, len(body['data']['buy']))
            for index in range(element_count):
                element = body['data']['buy'][index]
                emoji_number = f'{index + 1}\ufe0f⃣' if index + 1 != 10 else '🔟'
                sendvalue += f'{emoji_number}  {element["price"]}  {element["nickName"]}\n'
                allprice += float(element['price'])

            sendvalue += f"\n实时价格：1 USDT * {format(allprice / element_count, '.5f')} = {format((allprice / element_count), '.2f')}"
            # 添加当前时间显示
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            sendvalue += f"\n数据获取时间：{current_time}"

            query.edit_message_text(
                sendvalue,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text=all, callback_data="huilvsell_all"),
                    InlineKeyboardButton(text=wx, callback_data="huilvsell_wxPay"),
                    InlineKeyboardButton(text=zfb, callback_data="huilvsell_aliPay"),
                    InlineKeyboardButton(text=yhk, callback_data="huilvsell_bank"),
                ], [
                    InlineKeyboardButton(text="返回", callback_data="back")
                ]]))
        except Exception as e:
            print(e)
            return
def group_id(update: Update, context: CallbackContext):
    # 当机器人被添加到群组时检查
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.username == "new_texts_bot":  # 使用您的 bot 用户名更改此处
                chat_id = update.message.chat_id
                if not os.path.exists('group_ids.txt'):
                    with open('group_ids.txt', 'w') as f:
                        pass
                    # 检查group_ids.txt文件是否已包含群组ID
                write_id = True
                with open('group_ids.txt', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip() == str(chat_id):
                            write_id = False
                            break
                # 如果没有找到相同的ID，则将群组ID写入文件
                if write_id:
                    with open('group_ids.txt', 'a') as f:
                        f.write(f'{chat_id}\n')

def reload_config_command(update: Update, context: CallbackContext):
    """手动重载配置命令"""
    user_id = update.effective_user.id
    
    # 检查是否为管理员
    if user_id != admin_id:
        update.message.reply_text("❌ 权限不足，只有管理员可以使用此命令。")
        return
    
    try:
        update.message.reply_text("🔄 正在重新加载配置...")
        reload_config()
        update.message.reply_text("✅ 配置重新加载成功！\n\n所有配置已从 config.txt 文件重新读取。")
    except Exception as e:
        update.message.reply_text(f"❌ 配置重新加载失败：{str(e)}")
        logging.error(f"手动重载配置失败: {e}")
                        
def scheduled_message_fanhuan():
    """
    每日自动结算 USDT转TRX 返利到代理地址。
    仅当 enable_fanhuan_settlement=1 且当日有返利且金额 >= 最小金额时执行。
    默认执行时间：11:00（可在 config.txt 中通过 fanhuan_settlement_hour 和 fanhuan_settlement_minute 配置）
    """
    try:
        config = read_config('config.txt')
        enable = str(config.get('enable_fanhuan_settlement', '0')).strip() in ('1', 'true', 'yes')
        if not enable:
            logging.info("[返利结算] 已禁用，跳过")
            return
        
        daili_addres = config.get('fanhuan_settlement_address', 'TKYp9dbDs6kHKtFhFR6srEJvDARNYkq9Qe').strip()
        if not daili_addres or len(daili_addres) < 30:
            logging.warning("[返利结算] 代理地址未配置或无效，跳过")
            return
        
        min_amount = float(config.get('fanhuan_min_amount', '0.1') or '0.1')
    except Exception as e:
        logging.error(f"[返利结算] 读取配置失败: {e}")
        return

    # 读取前一天的返利记录（因为结算的是前一天的返利）
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    filename = f'transaction_records_{yesterday}.txt'
    total_fanhuan = read_fanhuan_from_file(filename)
    total_fanhuan_rounded = round(total_fanhuan - 1, 2)

    if total_fanhuan_rounded < min_amount:
        logging.info(f"[返利结算] 返利金额不足: {total_fanhuan_rounded} TRX < {min_amount} TRX，跳过结算")
        return

    private_key = usdt2trx_private_key if usdt2trx_private_key else privateKey
    if not private_key:
        logging.error("[返利结算] 未配置私钥，无法执行结算")
        try:
            bot.send_message(chat_id=admin_id, text="⚠️返利结算失败: 未配置私钥", parse_mode=None)
        except Exception:
            pass
        return

    try:
        logging.info(f"[返利结算] 开始结算，目标地址: {daili_addres}, 金额: {total_fanhuan_rounded} TRX")
        tron.private_key = private_key
        tron.default_address = tron.address.from_private_key(private_key).base58
        
        # 发送交易
        transaction = tron.trx.send_transaction(daili_addres, total_fanhuan_rounded)
        
        if transaction.get('result'):
            amount = transaction['transaction']['raw_data']['contract'][0]['parameter']['value']['amount']
            txid = transaction.get('txid', '')
            xiangqing = f"https://tronscan.org/#/transaction/{txid}?lang=zh"
            actual_amount = float(amount) / 1000000
            msg = f"✅结算成功,向账号{daili_addres}转账{actual_amount}TRX\n[点击查看交易详情]({xiangqing})"
            
            bot.send_message(chat_id=admin_id, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
            logging.info(f"[返利结算] 结算成功: 已向 {daili_addres} 转账 {actual_amount} TRX, 交易ID: {txid}")
        else:
            error_msg = f"交易失败: {transaction}"
            logging.warning(f"[返利结算] {error_msg}")
            try:
                bot.send_message(chat_id=admin_id, text=f"⚠️返利结算失败: {error_msg[:200]}", parse_mode=None)
            except Exception:
                pass
    except Exception as e:
        error_msg = f"执行失败: {str(e)}"
        logging.error(f"[返利结算] {error_msg}")
        try:
            bot.send_message(chat_id=admin_id, text=f"⚠️返利结算失败: {error_msg[:200]}", parse_mode=None)
        except Exception:
            pass

                        
def error_handler(update, context):
    print(f'Error: {context.error}')
    if isinstance(context.error, NetworkError):
        time.sleep(5)  # 休眠5秒后重试
def getaccountresource(address):
    hex_address = tron.address.to_hex(address)
    url = 'https://api.trongrid.io/wallet/getaccountresource'
    headers = {
        'Content-Type': 'application/json',
        'TRON-PRO-API-KEY': API_KEY
    }
    data = {'address': hex_address}
    response = requests.post(url, headers=headers, data=json.dumps(data),timeout=8)
    if response.status_code == 200:
        result = response.json()
        if result.get('EnergyLimit') is not None:
            energy_usage = result['EnergyLimit']
            remaining_energy = energy_usage
            if result.get('EnergyUsed') is not None:
                remaining_energy = energy_usage - result['EnergyUsed']
            return remaining_energy
        else:
            return 0
    else:
        print(response.text)
        return None
def read_addresses():
    addresses = {}
    file_name = '自动充.txt'
    # 检查文件是否存在，如果不存在则创建一个
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8'):
            pass
    with open(file_name, 'r', encoding='utf-8') as txt_file:
        for line in txt_file:
            match = re.search(r'chat_id: (\d+) - 地址: (\w+) - 状态: ([\w-]+)', line)
            if match:
                chat_id = int(match.group(1))
                address = match.group(2)
                status = match.group(3)
                if status == '开启':
                    if address not in addresses:
                        addresses[address] = [chat_id]
                    else:
                        addresses[address].append(chat_id)
    return addresses
def update_recharge_count_in_file(address):
    try:
        # 从文件中读取数据
        with open('recharge_counts.txt', 'r') as file:
            data = json.load(file)

        # 如果地址在数据中，则增加其计数值；否则添加新条目并设置计数值为1
        if address in data:
            data[address] += 1
        else:
            data[address] = 1

        # 将更新后的数据写回文件
        with open('recharge_counts.txt', 'w') as file:
            json.dump(data, file)

        # 返回最新的兑换次数
        return data[address]

    except Exception as e:
        print(f"update_recharge_count_in_file error: {e}")
def query_and_recharge(bot):
    addresses = read_addresses()
    try:
        for from_address, chat_ids in addresses.items():
            for chat_id in chat_ids:
                user_data = get_user_data(chat_id)
                if user_data:
                    balance = user_data["amount"]
                    if balance/1000000 > 8:
    
                        keyboard = [
                            [
                                InlineKeyboardButton("自助服务", url=bot_id),
                                InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID),
                            ]
                        ]
                        energy_remaining = getaccountresource(from_address)
                        time.sleep(0.18)
                        if energy_remaining is not None and energy_remaining < 25000:
                            energy=65000
                            us_amount = yucun_price*1000000
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            result = delegate_prestored(energy, 1, from_address)
                            # 修复：检查 success 是否为真值（True/true/"成功"）或存在 tx_hash
                            if result.get("success") or result.get("tx_hash") or (isinstance(result.get("success"), str) and "成功" in str(result.get("success"))):
                                txid = result.get("tx_hash")
                                transaction_url = f"https://tronscan.org/?utm_source=tronlink#/transaction/{txid}?lang=zh"
                                # 查询本系统的 API 用户余额（而不是上游的）
                                api_balance = 0
                                try:
                                    balance_resp = requests.get(
                                        f'{energy_pool_api}/v1/get_api_user_info',
                                        params={'username': username, 'password': password},
                                        timeout=5
                                    )
                                    if balance_resp.status_code == 200:
                                        balance_info = balance_resp.json()
                                        api_balance = balance_info.get('当前余额 (TRX)', 0)
                                except Exception as balance_error:
                                    print(f"[DEBUG] 查询API余额失败: {balance_error}")

                                new_balance = balance - us_amount
                                # 更新用户的余额
                                update_balance(chat_id, new_balance)
                                text = (f"✅VIP客户 下发完成\n➖2➖2➖2➖2➖2➖2➖2➖2\n"
                                        f"套餐模式：预存扣费模式\n"
                                        f"能量带宽：{energy}\n"
                                        f"有效时长：一天\n"
                                        f"接收地址：{from_address[:8]}......{from_address[-8:]}\n"
                                        f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})"
                                        f"")
                                new_text = text + f'\n账户余额：{new_balance / 1000000}'
                                try:
                                    text = f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})\n消耗能量{energy}\napi余额：{api_balance}"
                                    bot.send_message(chat_id=admin_id, text=text,
                                                     disable_web_page_preview=True, parse_mode='Markdown')
                                except Exception as e:
                                    print(f"私聊错误--{e}")
                                try:
                                    bot.send_message(chat_id=chat_id, text=new_text,disable_web_page_preview=True,parse_mode='Markdown', reply_markup=reply_markup)
                                except Exception as e:
                                    print(e)
                                for chat_id in all_chats:
                                    try:
                                        bot.send_message(chat_id=chat_id,
                                                         text=text,disable_web_page_preview=True,parse_mode='Markdown',
                                                         reply_markup=reply_markup)
                                    except Exception as e:
                                        print(e)

    except Exception as e:
        bot.send_message(chat_id=admin_id, text=f'能量兑换失败，{e}')
def energy_tran2(energy,day,receiver_address):
    url = f"{energy_pool_api}/v1/delegate_tran"
    data = {
        "username": username,
        "password": password,
        "energy": energy,
        "day": day,
        "receiver_address": receiver_address,
        "bot_username": bot_username
    }
    headers = {
        'Content-Type': 'application/json'
    }

    print(f"[energy_tran2] 准备调用能量池API: URL={url}, 能量={energy}, 天数={day}, 接收地址={receiver_address}")
    print(f"[energy_tran2] API用户: {username}")
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=30)
        print(f"[energy_tran2] 能量池API响应: status={response.status_code}")
        
        # 安全解析 JSON 响应
        try:
            result = response.json()
            print(f"[energy_tran2] 能量池API响应内容: {json.dumps(result, ensure_ascii=False)[:500]}")
        except (ValueError, requests.exceptions.JSONDecodeError) as json_err:
            # 如果响应不是有效的 JSON，尝试获取文本内容
            text = response.text[:500] if hasattr(response, 'text') else str(response.content[:500])
            print(f"[energy_tran2] ⚠️ 响应不是有效的JSON: {text}")
            result = {
                "success": False,
                "error": text,
                "message": f"能量池API返回无效的JSON响应: HTTP {response.status_code}"
            }
        
        if response.status_code == 200:
            # 检查成功标识：支持布尔值、字符串、或存在 tx_hash
            if result.get("success") or result.get("tx_hash") or (isinstance(result.get("success"), str) and "成功" in str(result.get("success"))):
                print(f"[energy_tran2] ✅ 能量委托成功: 能量={energy}, 接收地址={receiver_address}")
            else:
                print(f"[energy_tran2] ⚠️ 能量池返回200但未成功: {result}")
        else:
            print(f"[energy_tran2] ❌ 能量池API调用失败: status={response.status_code}, result={result}")
        
        return result
    except requests.exceptions.Timeout:
        error_msg = "能量池API请求超时（30秒）"
        print(f"[energy_tran2] ❌ {error_msg}")
        return {"success": False, "error": error_msg, "message": error_msg}
    except requests.exceptions.ConnectionError as conn_err:
        error_msg = f"无法连接到能量池API: {str(conn_err)}"
        print(f"[energy_tran2] ❌ {error_msg}")
        return {"success": False, "error": error_msg, "message": error_msg}
    except Exception as e:
        error_msg = f"API调用异常: {str(e)}"
        print(f"[energy_tran2] ❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": error_msg, "message": error_msg}
 
def delegate_prestored(energy,day,receiver_address):
    url = f"{energy_pool_api}/v1/delegate_meal"
    data = {
        "username": username,
        "password": password,
        "energy": energy,
        "day": day,
        "receiver_address": receiver_address,
        "bot_username": bot_username
    }
    headers = {
        'Content-Type': 'application/json'
    }

    print(f"[delegate_prestored] 准备调用能量池API: URL={url}, 能量={energy}, 天数={day}, 接收地址={receiver_address}")
    print(f"[delegate_prestored] API用户: {username}")
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=30)
        print(f"[delegate_prestored] 能量池API响应: status={response.status_code}")
        
        # 安全解析 JSON 响应
        try:
            result = response.json()
            print(f"[delegate_prestored] 能量池API响应内容: {json.dumps(result, ensure_ascii=False)[:500]}")
        except (ValueError, requests.exceptions.JSONDecodeError) as json_err:
            # 如果响应不是有效的 JSON，尝试获取文本内容
            text = response.text[:500] if hasattr(response, 'text') else str(response.content[:500])
            print(f"[delegate_prestored] ⚠️ 响应不是有效的JSON: {text}")
            result = {
                "success": False,
                "error": text,
                "message": f"能量池API返回无效的JSON响应: HTTP {response.status_code}"
            }
        
        if response.status_code == 200:
            # 检查成功标识：支持布尔值、字符串、或存在 tx_hash
            if result.get("success") or result.get("tx_hash") or (isinstance(result.get("success"), str) and "成功" in str(result.get("success"))):
                print(f"[delegate_prestored] ✅ 能量委托成功: 能量={energy}, 接收地址={receiver_address}")
            else:
                print(f"[delegate_prestored] ⚠️ 能量池返回200但未成功: {result}")
        else:
            print(f"[delegate_prestored] ❌ 能量池API调用失败: status={response.status_code}, result={result}")
        
        return result
    except requests.exceptions.Timeout:
        error_msg = "能量池API请求超时（30秒）"
        print(f"[delegate_prestored] ❌ {error_msg}")
        return {"success": False, "error": error_msg, "message": error_msg}
    except requests.exceptions.ConnectionError as conn_err:
        error_msg = f"无法连接到能量池API: {str(conn_err)}"
        print(f"[delegate_prestored] ❌ {error_msg}")
        return {"success": False, "error": error_msg, "message": error_msg}
    except Exception as e:
        error_msg = f"API调用异常: {str(e)}"
        print(f"[delegate_prestored] ❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": error_msg, "message": error_msg}
        
def energy_tran(energy,day,receiver_address):
    url = f"{energy_pool_api}/v1/delegate_tran"
    data = {
        "username": username,
        "password": password,
        "energy": energy,
        "day": day,
        "receiver_address": receiver_address,
        "bot_username": bot_username
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return response.json()



def main():

    # 将 connection 作为参数传递给 create_database
    create_database()
    global CUSTOMER_SERVICE_ID, bot_id, group_link, control_address, privateKey, username, password,huilv_zhekou,message,admin_id,hour_price,day_price,yucun_price,three_day_price,energy_pool_api,bot_username,usdt2trx_private_key
    config = read_config('config.txt')
    TOKEN = os.getenv('BOT_TOKEN') or config.get('TOKEN', '')
    CUSTOMER_SERVICE_ID = config.get('CUSTOMER_SERVICE_ID', '')
    bot_id = config.get('bot_id', '')
    group_link = config.get('group_link', '')
    control_address = config.get('control_address', '')
    # 优先使用usdt2trx_private_key，如果没有则使用privateKey
    if 'usdt2trx_private_key' in config and config['usdt2trx_private_key'].strip():
        privateKey = config['usdt2trx_private_key'].strip()
        usdt2trx_private_key = privateKey
    else:
        privateKey = config.get('privateKey', '')
        usdt2trx_private_key = privateKey.strip() if privateKey and privateKey.strip() else None
        logging.warning(f"警告：未配置USDT转TRX出款私钥，出币功能将被禁用")
    username = config.get('username', '')
    password = config.get('password', '')
    ad_time = int((config.get('ad_time', '0') or '0'))
    if ad_time < 1:
        ad_time = 1
    huilv_zhekou = float((config.get('huilv_zhekou', '1') or '1'))
    admin_id = int((config.get('admin_id', '0') or '0'))
    hour_price = float((config.get('hour_price', '1') or '1'))
    day_price = float((config.get('day_price', '5') or '5'))
    three_day_price = float((config.get('three_day_price', '15') or '15'))
    yucun_price = float((config.get('yucun_price', '10') or '10'))
    # 唯一桥链：强制从 config.txt 读取 energy_pool_api，如果没有配置则报错
    if 'energy_pool_api' not in config or not config['energy_pool_api'].strip():
        raise ValueError("config.txt 中必须配置 energy_pool_api（能量池系统地址）")
    energy_pool_api = config['energy_pool_api'].strip()

    message = f"\n`{control_address}`\n"
    global bot
    global all_chats
    
    # 启动配置文件监听器
    config_file_path = os.path.abspath('config.txt')
    start_config_watcher(config_file_path, reload_config)
    logging.info("配置文件热重载功能已启用")
    
    # 初始化加载键盘配置
    load_main_menu_config(config)
    logging.info("主键盘菜单配置已初始化")
    
    # 初始化加载关键词回复配置
    load_keyword_replies()
    logging.info("关键词回复配置已初始化")
    if not os.path.exists('group_ids.txt'):
        with open('group_ids.txt', 'w') as f:
            pass

    with open("group_ids.txt", "r") as f:
        all_chats = {int(line.strip()) for line in f.readlines()}

    while True:
        try:
            updater = Updater(TOKEN, use_context=True)
            break
        except Exception as e:
            logging.error(f"TOKEN无效或未配置: {e}")
            time.sleep(5)
            config = read_config('config.txt')
            TOKEN = config.get('TOKEN', '')
    bot = updater.bot
    # 确保全局 bot 变量已设置（供 HTTP 服务器使用）
    globals()['bot'] = bot
    # 获取机器人用户名（优先从bot.get_me()获取，否则从bot_id提取）
    try:
        bot_info = bot.get_me()
        bot_username = bot_info.username if bot_info and bot_info.username else None
    except:
        bot_username = None
    
    # 如果get_me()失败，从bot_id提取
    if not bot_username and bot_id:
        if bot_id.startswith('https://t.me/'):
            bot_username = bot_id.replace('https://t.me/', '').replace('@', '')
        elif bot_id.startswith('@'):
            bot_username = bot_id.replace('@', '')
        else:
            bot_username = bot_id.replace('@', '')
    
    logging.info(f"机器人用户名: {bot_username}")
    #启动后台任务
    saokuai_thread = threading.Thread(target=saokuai, args=(bot,))
    saokuai_thread.setDaemon(True)    
    saokuai_thread.start()
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CommandHandler("send", send_channel_message))
    dp.add_handler(CommandHandler("power", send_channel_messagepower))
    dp.add_handler(CommandHandler("okx", huilv))
    dp.add_handler(CommandHandler("reload", reload_config_command))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    # 添加新的处理程序以处理聊天成员更新
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, group_id))
    dp.add_error_handler(error_handler)
    timezone = pytz.timezone('Asia/Shanghai')
    scheduler = BackgroundScheduler(timezone=timezone)
    # 设定一个每分钟检查的间隔
    scheduler.add_job(scheduled_message, 'interval', minutes=ad_time)
    # 返利结算功能已禁用（注释掉）
    # 如需启用，取消下面的注释并设置 config.txt 中 enable_fanhuan_settlement=1
    # if str(config.get('enable_fanhuan_settlement', '0')).strip() in ('1', 'true', 'yes'):
    #     # 支持从配置文件读取结算时间，默认 11:00
    #     settlement_hour = int(config.get('fanhuan_settlement_hour', '11') or '11')
    #     settlement_minute = int(config.get('fanhuan_settlement_minute', '0') or '0')
    #     # 确保时间范围有效
    #     settlement_hour = max(0, min(23, settlement_hour))
    #     settlement_minute = max(0, min(59, settlement_minute))
    #     
    #     scheduler.add_job(scheduled_message_fanhuan, 'cron', day_of_week='mon-sun', hour=settlement_hour, minute=settlement_minute)
    #     logging.info(f"[返利结算] 已启用，每日 {settlement_hour:02d}:{settlement_minute:02d} 执行")
    # else:
    #     logging.info("[返利结算] 未启用（config.txt 中设置 enable_fanhuan_settlement=1 可开启）")
    logging.info("[返利结算] 功能已禁用（代码已注释）")
    # 每2分钟检测一次笔数套餐订单支付状态
    scheduler.add_job(check_bishu_orders_payment, 'interval', minutes=2)
    # 每5分钟自动管理笔数套餐（检测能量并自动充能或关闭）
    scheduler.add_job(auto_manage_bishu_packages, 'interval', minutes=5)
    scheduler.add_job(
        query_and_recharge,
        'interval',
        seconds=30,
        args=(bot,)  # Pass the updater instance as an argument
    )
    scheduler.start()
    # 启动方式：优先使用 Webhook（需配置 BOT_WEBHOOK_URL），否则使用长轮询
    webhook_path = BOT_WEBHOOK_PATH or TOKEN
    if BOT_WEBHOOK_URL:
        listen_host = "0.0.0.0"
        updater.start_webhook(
            listen=listen_host,
            port=BOT_WEBHOOK_PORT,
            url_path=webhook_path,
        )
        webhook_full_url = f"{BOT_WEBHOOK_URL.rstrip('/')}/{webhook_path}"
        bot.set_webhook(webhook_full_url)
        logging.info(f"Webhook 已启动: listen={listen_host}:{BOT_WEBHOOK_PORT}, url={webhook_full_url}")
    else:
        updater.start_polling()
        logging.info("使用长轮询模式启动机器人")
    # 运行机器人，直到您按下Ctrl + C
    updater.idle()

def _get_bot_and_admin_id_for_notify():
    """获取用于发送通知的 bot 对象和 admin_id（兼容 __main__ / import 两种运行方式）"""
    try:
        import sys
        m = sys.modules.get('__main__') or sys.modules.get('al')
        bot_obj = getattr(m, 'bot', None) if m else None
        admin_id_val = getattr(m, 'admin_id', None) if m else None
        if bot_obj is None:
            bot_obj = globals().get('bot')
        if admin_id_val is None:
            admin_id_val = globals().get('admin_id')
        return bot_obj, admin_id_val
    except Exception:
        return globals().get('bot'), globals().get('admin_id')


def process_balance_change_notification(data: dict):
    """后台处理余额变动通知（发送 Telegram 消息）。HTTP 回调会先返回 200，不阻塞能量池。"""
    try:
        change_type = data.get('changeType', 'recharge')  # recharge, deduct, adjust, other
        api_username = data.get('apiUsername', '')
        amount_trx = data.get('amountTrx', 0)
        new_balance_trx = data.get('newBalanceTrx', '0')

        order_id = data.get('orderId', '')
        tx_hash = data.get('txHash', '')
        telegram_chat_id = data.get('telegramChatId')
        telegram_message_id = data.get('telegramMessageId')

        bot_obj, admin_id_val = _get_bot_and_admin_id_for_notify()
        if not bot_obj or not admin_id_val:
            print(f"[通知处理] ⚠️ bot 未初始化或 admin_id 未配置，跳过 Telegram 通知。api={api_username}, type={change_type}")
            return

        # 根据变动类型生成不同的通知消息
        if change_type == 'recharge':
            # 给用户回消息（可选）
            if telegram_chat_id:
                try:
                    chat_id_int = int(telegram_chat_id)
                    if chat_id_int:
                        success_text = (
                            f"✅API账号余额充值成功\n"
                                        f"订单号：{str(order_id)[:8] if order_id else 'N/A'}\n"
                                        f"API账号：{api_username}\n"
                                        f"充值金额：{float(amount_trx):.2f} TRX\n"
                                        f"当前余额：{new_balance_trx} TRX\n"
                            f"交易哈希：{tx_hash if tx_hash else 'N/A'}"
                        )
                        bot_obj.send_message(chat_id=chat_id_int, text=success_text)

                        # 如果原消息存在，尝试编辑它
                        if telegram_message_id:
                            try:
                                message_id_int = int(telegram_message_id)
                                if message_id_int:
                                    updated_text = (
                                        f"✅支付成功！\n"
                                                    f"订单号：{str(order_id)[:8] if order_id else 'N/A'}\n"
                                                    f"API账号：{api_username}\n"
                                                    f"充值金额：{float(amount_trx):.2f} TRX\n"
                                                    f"当前余额：{new_balance_trx} TRX\n"
                                        f"交易哈希：{tx_hash if tx_hash else 'N/A'}"
                                    )
                                    bot_obj.edit_message_text(
                                        chat_id=chat_id_int,
                                        message_id=message_id_int,
                                        text=updated_text,
                                    )
                            except Exception as edit_err:
                                print(f"[通知处理] 编辑消息失败: {edit_err}")
                except Exception as notify_err:
                    print(f"[通知处理] 通知用户失败: {notify_err}")

            # 通知管理员（充值成功）
            try:
                bot_obj.send_message(
                    chat_id=admin_id_val,
                    text=(
                        f"✅API充值成功\n"
                        f"用户：{api_username}\n"
                        f"金额：{float(amount_trx):.2f} TRX\n"
                        f"余额：{new_balance_trx} TRX\n"
                        f"交易：{tx_hash if tx_hash else 'N/A'}"
                    ),
                )
            except Exception as admin_err:
                print(f"通知管理员失败: {admin_err}")

        elif change_type == 'deduct':
            try:
                bot_obj.send_message(
                    chat_id=admin_id_val,
                    text=f"💰API账号余额扣费\n用户：{api_username}\n扣费金额：{abs(float(amount_trx)):.2f} TRX\n当前余额：{new_balance_trx} TRX"
                )
            except Exception as admin_err:
                print(f"通知管理员失败: {admin_err}")

        elif change_type == 'adjust':
            try:
                amt = float(amount_trx)
                amount_str = f"+{amt:.2f}" if amt >= 0 else f"{amt:.2f}"
                bot_obj.send_message(
                    chat_id=admin_id_val,
                    text=f"⚙️API账号余额调整\n用户：{api_username}\n调整金额：{amount_str} TRX\n当前余额：{new_balance_trx} TRX"
                )
                print(f"[通知处理] ✅已通知管理员：API账号余额调整")
            except Exception as admin_err:
                print(f"通知管理员失败: {admin_err}")

        elif change_type == 'delegation_failed':
            # 处理能量下发失败通知（余额不足等）
            try:
                error_msg = data.get('error', '未知错误')
                energy = data.get('energy')
                receiver_address = data.get('receiverAddress', '')
                order_type = data.get('orderType', 'delegate_meal')
                current_balance = data.get('currentBalanceTrx', new_balance_trx)
                
                # 构建失败通知消息
                error_text = (
                    f"❌能量下发失败\n"
                    f"API账号：{api_username}\n"
                    f"错误原因：{error_msg}\n"
                )
                if energy:
                    error_text += f"能量：{energy}\n"
                if receiver_address:
                    error_text += f"接收地址：{receiver_address[:20]}...\n"
                error_text += f"当前余额：{current_balance} TRX"
                
                bot_obj.send_message(
                    chat_id=admin_id_val,
                    text=error_text
                )
                print(f"[通知处理] ✅已通知管理员：能量下发失败 - {api_username}, 错误：{error_msg}")
            except Exception as admin_err:
                print(f"通知管理员失败: {admin_err}")

        else:
            try:
                bot_obj.send_message(
                    chat_id=admin_id_val,
                    text=f"📊API账号余额变动\n用户：{api_username}\n变动金额：{float(amount_trx):.2f} TRX\n当前余额：{new_balance_trx} TRX"
                )
            except Exception as admin_err:
                print(f"通知管理员失败: {admin_err}")
    except Exception as e:
        print(f"[通知处理] 处理余额变动通知异常: {e}")


# HTTP服务器用于接收能量池系统的支付通知
class RechargeNotifyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 重写日志方法，使用 logging 输出
        logging.info(f"HTTP请求: {format % args}")
    
    def log_error(self, format, *args):
        # 记录错误日志
        logging.error(f"HTTP错误: {format % args}")
    
    def do_POST(self):
        # 处理充值通知
        if self.path == '/api/recharge-notify':
            self.handle_recharge_notify()
        # 处理笔数套餐订单支付通知
        elif self.path == '/api/bishu-payment-notify':
            self.handle_bishu_payment_notify()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Not found'}).encode('utf-8'))
    
    def handle_recharge_notify(self):
        """接收能量池回调：先快速返回 200，再后台处理 Telegram 通知。"""
        try:
            print(f"[通知接收] 收到余额变动通知请求: {self.path}")
            content_length = int(self.headers.get('Content-Length', '0') or '0')
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8') or '{}')
            print(f"[通知接收] 通知数据: {json.dumps(data, ensure_ascii=False)}")

            # 先快速 ACK，避免能量池端 fetch/curl 等待
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'accepted'}).encode('utf-8'))
            self.wfile.flush()

            # 后台处理（发送 Telegram）
            try:
                threading.Thread(target=process_balance_change_notification, args=(data,), daemon=True).start()
            except Exception as bg_err:
                logging.error(f"[通知处理] 启动后台通知线程失败: {bg_err}", exc_info=True)
                print(f"[通知处理] 启动后台通知线程失败: {bg_err}", flush=True)
        except Exception as e:
            logging.error(f"[通知处理] 处理回调失败: {e}", exc_info=True)
            print(f"[通知处理] 处理回调失败: {e}", flush=True)
            try:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
                self.wfile.flush()
            except Exception:
                pass
    
    def handle_bishu_payment_notify(self):
        """处理笔数套餐订单支付通知"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            order_number = data.get('orderNumber', '')
            tx_hash = data.get('txHash', '')
            amount_trx = data.get('amountTrx', 0)
            
            if not order_number or not tx_hash:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': '缺少必要参数'}).encode('utf-8'))
                return
            
            # 处理支付成功
            if bot:
                # 从订单号中提取chat_id（格式：BISHU_timestamp_chat_id）
                parts = order_number.split('_')
                if len(parts) >= 3:
                    chat_id = int(parts[2])
                    success = process_bishu_payment_success(chat_id, order_number, tx_hash, bot)
                    
                    if success:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': True, 'message': '通知已处理'}).encode('utf-8'))
                    else:
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': False, 'error': '处理失败'}).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': '订单号格式错误'}).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': '机器人未初始化'}).encode('utf-8'))
        except Exception as e:
            print(f"处理笔数套餐支付通知失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
    
    def log_message(self, format, *args):
        # 禁用默认的日志输出
        pass

def auto_manage_bishu_packages():
    """自动管理笔数套餐：检测能量并自动充能或关闭"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有已激活的笔数套餐
        select_query = """
        SELECT id, chat_id, address, package_type, package_count, status, activated_at
        FROM bishu_packages
        WHERE status = 'active'
        ORDER BY activated_at DESC
        """
        cursor.execute(select_query)
        active_packages = cursor.fetchall()
        
        if not active_packages:
            cursor.close()
            conn.close()
            return
        
        for pkg in active_packages:
            try:
                address = pkg['address']
                package_id = pkg['id']
                activated_at = pkg['activated_at']
                
                # 查询地址的当前能量
                current_energy = get_address_energy(address)
                
                if current_energy is None or current_energy < 0:
                    continue
                
                # 计算激活时间（小时）
                if activated_at:
                    # 处理datetime对象或字符串
                    if isinstance(activated_at, datetime):
                        activated_time = activated_at
                    else:
                        try:
                            activated_time = datetime.strptime(str(activated_at), '%Y-%m-%d %H:%M:%S')
                        except:
                            activated_time = datetime.strptime(str(activated_at)[:19], '%Y-%m-%d %H:%M:%S')
                    hours_passed = (datetime.now() - activated_time).total_seconds() / 3600
                else:
                    hours_passed = 0
                
                # 规则1：如果能量低于100，自动充能
                if current_energy < 100:
                    # 检查剩余次数
                    if pkg['package_count'] <= 0:
                        print(f"笔数套餐次数已用尽: 地址{address[:12]}...")
                        update_query = """
                        UPDATE bishu_packages
                        SET status = 'finished', updated_at = NOW()
                        WHERE id = %s
                        """
                        cursor.execute(update_query, (package_id,))
                        conn.commit()
                        
                        # 通知用户
                        if bot:
                            try:
                                bot.send_message(
                                    chat_id=pkg['chat_id'],
                                    text=f"🔚 您的笔数套餐次数已用尽\n\n地址：`{address}`\n感谢使用",
                                    parse_mode='Markdown'
                                )
                            except:
                                pass
                        continue

                    print(f"笔数套餐自动充能: 地址{address[:12]}...能量{current_energy} < 100, 剩余次数: {pkg['package_count']}")
                    result = energy_tran2(65000, 0, address)
                    
                    if result.get("success") or result.get("tx_hash"):
                        # 更新激活时间并扣除次数
                        update_query = """
                        UPDATE bishu_packages
                        SET activated_at = NOW(), 
                            package_count = package_count - 1,
                            updated_at = NOW()
                        WHERE id = %s
                        """
                        cursor.execute(update_query, (package_id,))
                        conn.commit()
                        print(f"✅笔数套餐自动充能成功: 地址{address[:12]}... 剩余次数: {pkg['package_count'] - 1}")
                    else:
                        error_msg = result.get("message", "未知错误")
                        print(f"❌笔数套餐自动充能失败: 地址{address[:12]}... 错误: {error_msg}")
                
                # 规则2：如果超过1小时且能量>60000，自动关闭激活
                elif hours_passed >= 1 and current_energy > 60000:
                    print(f"笔数套餐自动关闭: 地址{address[:12]}... 超过1小时且能量{current_energy} > 60000")
                    update_query = """
                    UPDATE bishu_packages
                    SET status = 'inactive', updated_at = NOW()
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (package_id,))
                    conn.commit()
                    print(f"✅笔数套餐已自动关闭: 地址{address[:12]}...")
                    
                    # 通知用户
                    if bot:
                        try:
                            bot.send_message(
                                chat_id=pkg['chat_id'],
                                text=f"⏸ 您的笔数套餐地址已自动关闭\n\n地址：`{address}`\n原因：超过1小时未使用且能量充足\n如需继续使用，请手动激活",
                                parse_mode='Markdown'
                            )
                        except:
                            pass
            except Exception as e:
                print(f"处理笔数套餐自动管理失败 (ID: {pkg.get('id', 'unknown')}): {e}")
                continue
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"自动管理笔数套餐异常: {e}")

def check_bishu_orders_payment():
    """检测笔数套餐订单的支付状态（定时任务）"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有待支付的笔数套餐订单（未过期，30分钟内创建的）
        select_query = """
        SELECT order_number, chat_id, plan, amount, created_at
        FROM orders
        WHERE status = 'pending' 
        AND plan LIKE '笔数套餐-%'
        AND created_at > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
        ORDER BY created_at DESC
        LIMIT 20
        """
        cursor.execute(select_query)
        pending_orders = cursor.fetchall()
        
        if not pending_orders:
            cursor.close()
            conn.close()
            return
        
        RECHARGE_PAYMENT_ADDRESS = "TJdtCWfm4iaqcQVMJchrobkbP5Y9yqNpPf"
        API_KEY = "93ed8c29-bd1c-4940-ad6c-7eb53bf58bcb"
        
        # 查询该地址最近的TRX转账记录
        try:
            response = requests.get(
                f"https://api.trongrid.io/v1/accounts/{RECHARGE_PAYMENT_ADDRESS}/transactions?only_confirmed=true&limit=100",
                headers={'TRON-PRO-API-KEY': API_KEY},
                timeout=10
            )
            
            if response.status_code != 200:
                cursor.close()
                conn.close()
                return
            
            data = response.json()
            transactions = data.get('data', [])
            
            # 检查每个订单是否有匹配的支付
            for order in pending_orders:
                order_amount = float(order['amount'])
                order_time = order['created_at'].timestamp() * 1000  # 转换为毫秒
                
                for tx in transactions:
                    # 检查是否是TransferContract类型的TRX转账
                    if not tx.get('raw_data') or not tx['raw_data'].get('contract'):
                        continue
                    
                    contract = tx['raw_data']['contract'][0]
                    if contract.get('type') != 'TransferContract':
                        continue
                    
                    parameter = contract.get('parameter', {}).get('value')
                    if not parameter:
                        continue
                    
                    # 检查收款地址是否匹配
                    to_address = parameter.get('to_address')
                    if to_address != RECHARGE_PAYMENT_ADDRESS:
                        continue
                    
                    tx_amount = parameter.get('amount', 0) / 1e6  # 转换为TRX
                    tx_time = tx.get('block_timestamp') or tx.get('raw_data', {}).get('timestamp', 0)
                    
                    # 金额匹配（允许0.01 TRX的误差）且时间在订单创建之后
                    if abs(tx_amount - order_amount) < 0.01 and tx_time >= order_time:
                        tx_hash = tx.get('txID') or tx.get('txid')
                        
                        # 检查订单是否已处理（双重检查，避免重复处理）
                        check_query = "SELECT status FROM orders WHERE order_number = %s FOR UPDATE"
                        cursor.execute(check_query, (order['order_number'],))
                        check_result = cursor.fetchone()
                        
                        if check_result and check_result.get('status') == 'pending':
                            if not tx_hash:
                                continue
                            
                            # 先更新订单状态为processing，避免重复处理
                            update_query = "UPDATE orders SET status = 'processing' WHERE order_number = %s"
                            cursor.execute(update_query, (order['order_number'],))
                            conn.commit()
                            
                            # 处理支付成功
                            if bot:
                                try:
                                    success = process_bishu_payment_success(
                                        order['chat_id'],
                                        order['order_number'],
                                        tx_hash,
                                        bot
                                    )
                                    if success:
                                        print(f"✅笔数套餐订单支付成功: {order['order_number']}, 用户: {order['chat_id']}")
                                    else:
                                        # 如果处理失败，恢复订单状态
                                        rollback_query = "UPDATE orders SET status = 'pending' WHERE order_number = %s"
                                        cursor.execute(rollback_query, (order['order_number'],))
                                        conn.commit()
                                        print(f"⚠️笔数套餐订单处理失败，已恢复状态: {order['order_number']}")
                                except Exception as process_err:
                                    print(f"处理笔数套餐订单支付失败: {process_err}")
                                    # 恢复订单状态
                                    try:
                                        rollback_query = "UPDATE orders SET status = 'pending' WHERE order_number = %s"
                                        cursor.execute(rollback_query, (order['order_number'],))
                                        conn.commit()
                                    except:
                                        pass
                            break
        except Exception as e:
            print(f"检测笔数套餐订单支付失败: {e}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"检测笔数套餐订单支付异常: {e}")

def start_notify_server():
    """启动HTTP服务器来接收能量池系统的通知"""
    try:
        # 支持通过环境变量配置通知服务器端口（默认8080）
        notify_port = int(os.getenv('NOTIFY_SERVER_PORT', '8080'))
        server = HTTPServer(('0.0.0.0', notify_port), RechargeNotifyHandler)
        logging.info(f"充值通知服务器已启动，监听端口 {notify_port}")
        print(f"充值通知服务器已启动，监听端口 {notify_port}", flush=True)
        server.serve_forever()
    except Exception as e:
        logging.error(f"启动充值通知服务器失败: {e}", exc_info=True)
        print(f"启动充值通知服务器失败: {e}", flush=True)
        raise

if __name__ == '__main__':
    # 先启动机器人主程序（初始化 bot 变量）
    # 然后在后台线程中启动HTTP服务器（此时 bot 已初始化）
    import threading
    import time
    
    def start_bot_and_server():
        # 启动机器人主程序
        main()
        # main() 函数会阻塞，所以 HTTP 服务器在线程中启动
        # 但实际上 main() 会一直运行，所以 HTTP 服务器应该在 main() 之前启动
    
    # 在后台线程中启动HTTP服务器（daemon=True 确保主程序退出时也退出）
    notify_thread = threading.Thread(target=start_notify_server, daemon=True)
    notify_thread.start()
    
    # 等待一小段时间让 HTTP 服务器启动
    time.sleep(1)
    
    # 启动机器人主程序（会阻塞）
    main()
