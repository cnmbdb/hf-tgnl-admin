import logging
import json
import time
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
from config_watcher import start_config_watcher, stop_config_watcher
API_KEY="eb2cadbc-f19a-4f-466b605f4545"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

utotrc_huilv=11.5
tron = Tron()
filename = '监听.txt'
contract_address='TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
last_message_id = None
user_payment_amount = {}
INPUT_ADDRESS = 1
delete_ADDRESS=4
# 从环境变量读取数据库配置，避免硬编码
config = {
        'user': 'nl-admin',
        'password': 'nl-admin',
        'host': '127.0.0.1',
        'database': 'nl-admin',
        'port': 3306,
        'charset': 'utf8mb4'
    }

# 能量池 API（从 config.txt 加载，可热重载）
energy_pool_api = os.getenv('ENERGY_POOL_API', '').strip()


def check_pricing_conflicts() -> str:
    """
    检查 hour_price / day_price / three_day_price 组合是否出现价格冲突。
    如果同一个金额对应多个套餐（例如 1小时2次 与 1天5次 价格相同），
    返回一段提示文案（否则返回空字符串）。
    """
    try:
        # 使用微单位避免浮点误差
        micros = lambda x: int(round(float(x) * 1_000_000))

        price_map = {}

        def add(label: str, price_trx: float):
            key = micros(price_trx)
            price_map.setdefault(key, []).append(label)

        # 仅当价格 > 0 时才参与冲突检测
        if hour_price > 0:
            add("1小时1次", hour_price)
            add("1小时2次", hour_price * 2)
            add("1小时5次", hour_price * 5)
            add("1小时10次", hour_price * 10)

        if day_price > 0:
            add("1天5次", day_price * 5)
            add("1天10次", day_price * 10)
            add("1天20次", day_price * 20)
            add("1天50次", day_price * 50)

        if three_day_price > 0:
            add("3天内每天10次", three_day_price * 30)
            add("3天内每天20次", three_day_price * 60)
            add("3天内每天30次", three_day_price * 90)
            add("3天内每天50次", three_day_price * 150)

        conflicts = [
            (price_micro, labels)
            for price_micro, labels in price_map.items()
            if len(labels) > 1
        ]

        if not conflicts:
            return ""

        # 组装提示文案（价格用 TRX 显示）
        lines = ["⚠️ 检测到套餐价格冲突，请在后台调整："]
        for price_micro, labels in conflicts:
            price_trx = price_micro / 1_000_000
            joined = " / ".join(labels)
            lines.append(f"- {joined} 的价格都为 {price_trx:g} TRX")

        lines.append("建议：确保不同套餐的单价组合不相同，避免机器人无法区分是哪个套餐。")
        return "\n".join(lines)
    except Exception as e:
        logging.error(f"检查价格冲突时出错: {e}")
        return ""

# 验证必要的环境变量是否已设置
required_env_vars = ['TG_DB_USER', 'TG_DB_PASSWORD', 'TG_DB_HOST', 'TG_DB_NAME']
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
        api_url = "http://localhost:3000/api/bot-register-user"
        data = {
            "chat_id": chat_id,
            "user_nickname": user_nickname,
            "username": username
        }
        response = requests.post(api_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"User {chat_id} registered/updated successfully")
            else:
                print(f"API error in handle_start_command: {result.get('message')}")
        else:
            print(f"HTTP error in handle_start_command: {response.status_code}")
    except Exception as e:
        print(f"API request error in handle_start_command: {e}")


def create_database():
    # 机器人现在通过API调用前端，不再需要直接连接数据库
    print('Robot is now using API calls to frontend instead of direct database connection')
    print('Database operations will be handled by the frontend API')

def get_user_data(chat_id):
    try:
        # 使用HTTP请求调用前端API
        api_url = "http://localhost:3000/api/bot-user-data"
        params = {"chat_id": chat_id}
        response = requests.get(api_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("data")
            else:
                print(f"API error in get_user_data: {data.get('error')}")
                return None
        else:
            print(f"HTTP error in get_user_data: {response.status_code}")
            return None
    except Exception as e:
        print(f"API request error in get_user_data: {e}")
        return None
def get_username_from_update(update: Update):
    username = "None"
    user = update.effective_user
    if user and user.username:
        username = user.username
    return username
def start(update: Update, context: CallbackContext):
    file_path = f"start.txt"
    data=""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()
    if update.message.chat.type == 'private':
        keyboard = [
            ["🛎预存扣费", "✅USDT转TRX"],
            ["⏰查交易", "⚡️TRX转能量"],
            ["📢已监听地址", "🔔开始/结束监听"],
            ["💰我要充值", "👤个人中心"],
        ]
        username = get_username_from_update(update)
        user = update.effective_user
        user_nickname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text(data, reply_markup=reply_markup, parse_mode='Markdown', disable_web_page_preview=True)
        handle_start_command(update.message.chat_id, user_nickname, username)
    else:
        update.message.reply_text(data, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown',disable_web_page_preview=True)

def read_config(file_path: str) -> dict:
    config = dict()
    with open(file_path, 'r') as file:
        for line in file.readlines():
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    return config

def reload_config():
    """重新加载配置文件"""
    global CUSTOMER_SERVICE_ID, bot_id, group_link, control_address, privateKey, username, password
    global huilv_zhekou, admin_id, hour_price, day_price, yucun_price, three_day_price, message, energy_pool_api
    
    try:
        logging.info("开始重新加载配置文件...")
        config = read_config('config.txt')
        
        # 更新全局配置变量
        CUSTOMER_SERVICE_ID = config.get('CUSTOMER_SERVICE_ID', CUSTOMER_SERVICE_ID)
        bot_id = config.get('bot_id', bot_id)
        group_link = config.get('group_link', group_link)
        control_address = config.get('control_address', control_address)
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
        # 预存功能已下线：允许配置缺失/为空时不报错
        if 'yucun_price' in config:
            _raw = (config.get('yucun_price') or '').strip()
            yucun_price = float(_raw) if _raw else 0.0
            
        # 更新能量池 API 地址
        if 'energy_pool_api' in config:
            energy_pool_api = (config.get('energy_pool_api') or '').strip()

        # 检查价格冲突并提示管理员
        conflict_msg = check_pricing_conflicts()
        if conflict_msg:
            logging.warning(conflict_msg)
            # 如果 bot 已初始化，则推送一条提示到管理员
            if 'bot' in globals() and bot and admin_id:
                try:
                    bot.send_message(chat_id=admin_id, text=conflict_msg)
                except Exception as e:
                    logging.warning(f"发送价格冲突提示失败: {e}")

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
        api_url = "http://localhost:3000/api/bot-update-balance"
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
    linshi = transaction['ret'][0]
    transaction_id = transaction['txID']
    keyboard = [
        [
            InlineKeyboardButton("自助服务", url=bot_id),
            InlineKeyboardButton("联系客服", url=CUSTOMER_SERVICE_ID),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    if 'ret' in transaction and 'contractRet' in linshi and linshi['contractRet'] == 'SUCCESS':
        parameter = transaction['raw_data']['contract'][0]
        linshizhi = parameter['parameter']['value']
        # trc20交易
        if 'TriggerSmartContract' == parameter['type'] and '41a614f803b6fd780986a42c78ec9c7f77e6ded13c'== linshizhi['contract_address']:
            to_address = tron.address.from_hex('41' + linshizhi['data'][32:72]).decode()
            if linshizhi['data'][:8]=='a9059cbb':
                if to_address == control_address :# 23b872dd和a9059cbb
                    from_address = tron.address.from_hex(linshizhi['owner_address']).decode()
                    us_amount = int(linshizhi['data'][72:136], 16)
                    if us_amount >= 1000000:
                        sender_trx = gethuilv() * float(us_amount)
                        if sender_trx < check_trx_balance(control_address) * 1000000:  # 检查余额是否够,ceshi
                            # trn = get_trxmultiSign(privateKey, control_address, from_address, sender_trx)  #多签调用
                            private_key = privateKey
                            tron.private_key = private_key
                            tron.default_address = tron.address.from_private_key(private_key).base58
                            try:
                                trx_to_send = float(sender_trx) / 1000000
                                transaction = tron.trx.send_transaction(from_address, trx_to_send)
                                if (transaction['result']):

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
                                            text = (f"✅USDT 兑换 TRX成功\n➖➖➖➖➖➖➖➖\n"
                                                    f"交易时间：{formatted_date_time}\n"
                                                    f"兑换金额：{float(us_amount / 1000000)} USDT\n"
                                                    f"TRX金额：{float(amount) / 1000000} TRX\n"
                                                    f"兑换地址：{from_address[:8]}......{from_address[-8:]}\n"
                                                    f"交易HASH：[{txid[:8]}......{txid[-8:]}]({xiangqing})")
                                            bot.send_message(chat_id=chat_id,
                                                             text=text,
                                                             parse_mode='Markdown', disable_web_page_preview=True,
                                                             reply_markup=reply_markup)
                                        except Exception as e:
                                            print(f"2Error sending message to chat_id {chat_id}: {e}")
                            except Exception as e:
                                print(f"2Error sending message to chat_id {chat_id}: {e}")
                        else:
                            trx_to_send = round(float(sender_trx) / 1000000 , 2)
                            try:
                                bot.send_message(chat_id=admin_id,text=f'余额不足，交易失败  \n哈希：`{transaction_id}`  \n地址：`{from_address}`  \nU金额：{float(us_amount) / 1000000}\n应转：{trx_to_send}TRX',parse_mode='Markdown')
                            except Exception as e:
                                print(f"1Error sending message to chat_id {chat_id}: {e}")
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
        elif 'TransferContract' == parameter['type']:
            linshizhi = parameter['parameter']['value']
            to_address = tron.address.from_hex(linshizhi['to_address']).decode()
            from_address = tron.address.from_hex(linshizhi['owner_address']).decode()
            if to_address==control_address:
                us_amount = int(linshizhi['amount'])
                # 直接在主代码中比较金额并提取匹配的chat_id
                matched_chat_id = None
                if len(transaction_data) > 0:
                    for chat_id, amount in transaction_data.items():
                        if amount*1000000 == us_amount:
                            data_to_upload = {"chat_id": chat_id, "amount": us_amount}
                            balance = upload_to_server(data_to_upload)
                            try:
                                bot.send_message(chat_id=chat_id,text=f'充值成功,您的余额已更新\n目前余额：{balance/1000000}TRX',reply_markup=reply_markup)
                                bot.send_message(chat_id=admin_id,
                                                 text=f'用户{chat_id}，充值{us_amount / 1000000}TRX,\n目前余额：{balance / 1000000}TRX')
                            except Exception as e:
                                print(f"Error sending message to chat_id {chat_id}: {e}")

                # 说明：能量池 API 的扣费是“每次调用”扣一次成本（day=0/1/3... 映射成本），
                # 所以「N次」必须调用 N 次接口，避免只扣 1 次成本。
                # energy 统一按 65000（1笔）下发。
                energy_params = {
                    hour_price*1000000: (1, "1小时1次", 0),
                    hour_price*1000000 * 2: (2, "1小时2次", 0),
                    hour_price*1000000 * 5: (5, "1小时5次", 0),
                    hour_price*1000000 * 10: (10, "1小时10次", 0),
                    day_price*1000000 * 5: (5, "1天5次", 1),
                    day_price*1000000 * 10: (10, "1天10次", 1),
                    day_price*1000000 * 20: (20, "1天20次", 1),
                    day_price*1000000 * 50: (50, "1天50次", 1),
                    three_day_price*1000000 * 30: (30, "3天内每天10次", 3),
                    three_day_price*1000000 * 60: (60, "3天内每天20次", 3),
                    three_day_price*1000000 * 90: (90, "3天内每天30次", 3),
                    three_day_price*1000000 * 150: (150, "3天内每天50次", 3),
                }
                # 查找指定的 us_amount
                if us_amount in energy_params:
                    count, desc, days = energy_params[us_amount]

                    txids = []
                    api_balance = None
                    last_result = None
                    for _ in range(int(count)):
                        last_result = energy_tran2(65000, days, from_address)
                        if not (isinstance(last_result, dict) and last_result.get("success")):
                            break
                        txid = last_result.get("tx_hash") or last_result.get("txHash")
                        if txid:
                            txids.append(txid)
                        api_balance = last_result.get("new_balance")

                    if len(txids) == int(count):
                        txid = txids[-1]
                        transaction_url = f"https://tronscan.org/?utm_source=tronlink#/transaction/{txid}?lang=zh"
                        # 提交订单
                        # result = nl_itrx(int(energy), days, from_address)
                        # # 检查errno是否为0
                        # if result.get('errno') == 0:
                        total_energy = 65000 * int(count)
                        text = (f"✅能量租用 下发完成（共{count}次）\n➖➖➖➖➖➖➖➖\n"
                                f"套餐模式：笔数模式\n"
                                f"能量带宽：{total_energy}（65000×{count}）\n"
                                f"有效时长：{desc}\n"
                                f"接收地址：{from_address[:8]}......{from_address[-8:]}\n"
                                f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})"
                                f"")
                        try:
                            text = f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})\n下发次数：{count}\n消耗能量{total_energy}\napi余额：{api_balance / 1000000 if api_balance is not None else '未知'}"
                            bot.send_message(chat_id=admin_id, text=text,
                                             disable_web_page_preview=True, parse_mode='Markdown')
                        except Exception as e:
                            print(f"私聊错误--{e}")
                        # 发送兑换成功的通知
                        for chat_id in all_chats:
                            try:
                                # 发送兑换成功的通知
                                bot.send_message(
                                    chat_id=chat_id,
                                    text=text,parse_mode='Markdown',disable_web_page_preview=True,
                                    reply_markup=reply_markup,
                                )
                            except Exception as e:
                                print(f"Error sending message to group {group_id}: {e}")
                    else:
                        try:
                            bot.send_message(
                                chat_id=admin_id,
                                text=f"下发失败/部分成功,地址{from_address}，已成功{len(txids)}/{count}次，详情{last_result}",
                                reply_markup=reply_markup,
                            )
                        except Exception as e:
                            print(f"Error sending message to chat_id {admin_id}: {e}")

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
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                time.sleep(2)
                continue
            transaction_data = []
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
                    for line in file:
                        timestamp, chat_id_str, address_str = line.strip().split(" - ")
                        chat_id = chat_id_str.split(": ")[1]
                        jiantingaddress = address_str.split(": ")[1]
                        chat_id_jiantingaddress.append((chat_id, jiantingaddress))
                        dizhi_jiantingaddress.add(jiantingaddress)
                    # 在你的主循环中调用 process_block() 函数来处理区块
                process_block(block, formatted_date_time, chat_id_jiantingaddress, dizhi_jiantingaddress,transaction_data,bot)
            last_processed_block_number = current_block_number  # 更新已处理块编号
            current_block_number += 1
        except Exception as e:  # 添加一个通用异常处理程序
            print(f'程序异常，请检查服务器{e}')

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

def handle_message(update: Update, context: CallbackContext):
    if update.message is not None and update.message.chat.type == 'private':
        chat_id = update.effective_chat.id
        message_text = update.message.text
        #保存每天聊天记录
        if message_text == '📢已监听地址':
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
        if message_text == '🔔开始/结束监听':
            update.message.reply_text("每次只支持输入一个地址,监听包含trc20和trx\n格式(结束同理)：开始监听 地址（中间有空格）\n开始监听 TEfbxrUwvwZY8dYJx8tt7RXLF3XXXXXXXX")
        elif message_text == '✅USDT转TRX':
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
        elif message_text == '⚡️TRX转能量':
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
        elif message_text == '实时汇率':
            update.message.reply_text(f"实时 USDT 转 TRX 汇率：\n*{gethuilv()}*",parse_mode='Markdown', disable_web_page_preview=True)
        elif message_text == '⏰查交易':
            update.message.reply_text("查交易：\n格式：查交易 地址（中间有空格）\n查交易 TEfbxrUwvwZY8dYJx8tt7RXLF3XXXXXXXX")
        if "开启地址 " in message_text:
            split_str = message_text.split(' ')
            js_address = split_str[1]
            if tron.isAddress(js_address):
                chat_id = update.message.chat_id
                found = False
                with open('自动充.txt', 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        if f"chat_id: {chat_id} - 地址: {js_address} - 状态: " in line:
                            line = line.replace('关闭', '开启')
                            found = True
                        f.write(line)
                    f.truncate()
                if found:
                    update.message.reply_text(f"成功开启地址 {js_address}", parse_mode='Markdown',
                                              disable_web_page_preview=True)
                else:
                    update.message.reply_text(f"找不到对应地址 {js_address}", parse_mode='Markdown',
                                              disable_web_page_preview=True)
            else:
                update.message.reply_text("无效地址", parse_mode='Markdown', disable_web_page_preview=True)
        if "停用地址 " in message_text:
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
        if message_text == '🛎预存扣费':
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
        if tron.isAddress(message_text):
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
                # 调用函数并获取剩余能量和带宽
                energy_remaining, bandwidth_remaining, balance, usdt_balance = get_account_info(message_text)
                text = f"您的账户:`{message_text}`\n能量：{energy_remaining}\n带宽：{bandwidth_remaining}\nTRX余额:{balance}\nUSDT余额:{usdt_balance}"
                context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
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
            filename="监听.txt"
            address_dict = {}
            # 检查地址是否存在
            def check_address(address, chat_id):
                if address in address_dict and chat_id in address_dict[address]:
                    return True
                return False
            # 添加新地址
            def add_address(address, chat_id):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if not check_address(address, chat_id):
                    with open(filename, "a") as file:
                        file.write(f"{timestamp} - chat_id: {chat_id} - 地址: {address}\n")
                        if address not in address_dict:
                            address_dict[address] = []
                        address_dict[address].append(chat_id)
                context.bot.send_message(chat_id=chat_ids, text=f"已添加" + split_str[1])
            split_str = message_text.split(' ')
            chat_ids = update.effective_chat.id
            if split_str[1]==control_address or split_str[1]=="TSaRZDiBPD8Rd5vrvX8a4zgunHczM9mj8S":
                context.bot.send_message(chat_id=chat_ids, text=f"此地址暂不支持监听")
                return
            if tron.isAddress(split_str[1]):
                # 初始化字典
                if os.path.exists(filename):
                    with open(filename, "r") as file:
                        for line in file:
                            timestamp, chat_id_str, address_str = line.split(' - ')
                            chat_id = int(chat_id_str.split(': ')[-1])
                            address = address_str.split(': ')[-1].strip()
                            if address not in address_dict:
                                address_dict[address] = []
                            address_dict[address].append(chat_id)
                if check_address(split_str[1], chat_ids):
                    context.bot.send_message(chat_id=chat_ids, text=f"地址已存在" )
                else:
                    add_address(split_str[1], chat_ids)

            else:
                context.bot.send_message(chat_id=chat_ids, text="请输入正确的trx地址")

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
        if message_text == '💰我要充值':
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
        if message_text == '👤个人中心':
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
        if chat_id == admin_id or chat_id == 276600603 :
            if "查询后台信息" == message_text:
                # 假设你想要查询的是管理员的信息
                admin_info = requests.get('https://zhangpu.online/v1/get_user_info', params={'username': username}).json()
                if 'error' in admin_info:
                    update.message.reply_text(admin_info['error'])
                else:
                    admin_info_str = '\n'.join(f'\n{key}: {value}' for key, value in admin_info.items())
                # 将管理员的信息发送到聊天中
                update.message.reply_text(admin_info_str)
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
    try:
        with open(filename, 'r') as f:
            content = f.readlines()
        fanhuan_list = []
        for line in content:
            _, fanhuan_str = line.strip().split('\t')
            fanhuan = float(fanhuan_str)
            fanhuan_list.append(fanhuan)
        return sum(fanhuan_list)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return 0

def gethuilv():
     # 返回的是1u兑trx的官方汇率
    response = requests.get('https://min-api.cryptocompare.com/data/price?fsym=TRX&tsyms=USD')
    trx_price_in_usd = response.json()['USD']
    exchange_rate = 1* huilv_zhekou / float(trx_price_in_usd)
    return round(exchange_rate , 2)

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
        if query.data in query_to_params:
            payment_amount, desc = query_to_params[query.data]
            user_payment_amount[chat_id] = payment_amount
            text = f"收款金额：*{payment_amount}TRX*\n使用期限：*{desc}*\n24小时收款trc20地址为：\n`{address_text}`\n*TRX支付请直接转账能量即回原地址*"
            update_message_text(chat_id, message_id, new_text=text, reply_markup=reply_markup)
            return
        if query.data in ("20", "30", "50","100", "200", "500"):
            base_price= int(query.data)
            existing_prices = get_existing_prices("transaction_data.txt")
            final_price = generate_price(base_price, existing_prices)
            now = datetime.now()
            ten_minutes_later = now + timedelta(minutes=20)
            current_time = ten_minutes_later.strftime("%Y-%m-%d %H:%M:%S")
            save_data_to_file(chat_id, final_price, current_time, "transaction_data.txt")
            text = f"用户ID：{chat_id}\n订单金额：`{final_price}`TRX(点击可复制金额)" \
                   f"\n收款地址：`{control_address}`\n‼️*请务必核对金额尾数，金额不对则无法确认*。\n订单将于{current_time}过期，请尽快支付！"
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

                    # 同上：按“调用次数”计费，N次需调用 N 次接口
                    energy_params = {
                        hour_price*1000000: (1, "1小时1次", 0),
                        hour_price*1000000 * 2: (2, "1小时2次", 0),
                        hour_price*1000000 * 5: (5, "1小时5次", 0),
                        hour_price*1000000 * 10: (10, "1小时10次", 0),
                        day_price*1000000 * 5: (5, "1天5次", 1),
                        day_price*1000000 * 10: (10, "1天10次", 1),
                        day_price*1000000 * 20: (20, "1天20次", 1),
                        day_price*1000000 * 50: (50, "1天50次", 1),
                        three_day_price*1000000 * 30: (30, "3天内每天10次", 3),
                        three_day_price*1000000 * 60: (60, "3天内每天20次", 3),
                        three_day_price*1000000 * 90: (90, "3天内每天30次", 3),
                        three_day_price*1000000 * 150: (150, "3天内每天50次", 3),
                    }
                    # 查找指定的 us_amount
                    if us_amount in energy_params:
                        count, desc, days = energy_params[us_amount]

                        txids = []
                        api_balance = None
                        last_result = None
                        for _ in range(int(count)):
                            last_result = energy_tran2(65000, days, from_address)
                            if not (isinstance(last_result, dict) and last_result.get("success")):
                                break
                            txid = last_result.get("tx_hash") or last_result.get("txHash")
                            if txid:
                                txids.append(txid)
                            api_balance = last_result.get('new_balance')

                        if len(txids) == int(count):
                            txid = txids[-1]
                            transaction_url = f"https://tronscan.org/?utm_source=tronlink#/transaction/{txid}?lang=zh"
                            # 更新余额
                            new_balance = balance - us_amount
                            update_balance(chat_id, new_balance)
                            
                            # 更新消息
                            total_energy = 65000 * int(count)
                            text = (f"✅VIP客户 下发完成（共{count}次）\n➖➖➖➖➖➖➖➖\n"
                                    f"套餐模式：笔数模式\n"
                                    f"能量带宽：{total_energy}（65000×{count}）\n"
                                    f"有效时长：{desc}\n"
                                    f"接收地址：{from_address[:8]}......{from_address[-8:]}\n"
                                    f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})"
                                    f"")
                            new_text = text + f"\n余额：{new_balance / 1000000} TRX"
                            update_message_text(chat_id, message_id, new_text)
                            try:
                                text = f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})\n下发次数：{count}\n消耗能量{total_energy}\napi余额：{api_balance / 1000000 if api_balance is not None else '未知'}"
                                bot.send_message(chat_id=admin_id, text=text,
                                                 disable_web_page_preview=True, parse_mode='Markdown')
                            except Exception as e:
                                print(f"私聊错误--{e}")
                            
                            for chat_id in all_chats:
                                try:
                                    # 发送兑换成功的通知
                                    bot.send_message(chat_id=chat_id,
                                                     text=text, disable_web_page_preview=True,
                                                     parse_mode='Markdown',
                                                     reply_markup=reply_markup)
                                except Exception as e:
                                    print(f"Error sending message to group {group_id}: {e}")
                        else:
                            update_message_text(chat_id, message_id, new_text=f"能量兑换失败/部分成功：已成功{len(txids)}/{count}次，请联系客服 {last_result}")

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
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'transaction_records_{today}.txt'
    total_fanhuan = read_fanhuan_from_file(filename)
    total_fanhuan_rounded = round(total_fanhuan-1, 2)
    private_key = privateKey
    tron.private_key = private_key
    tron.default_address = tron.address.from_private_key(private_key).base58
    daili_addres="TKp5oE77pYD6ZetXageRHed2o7PjsdoymE"
    try:
        transaction = tron.trx.send_transaction(daili_addres, total_fanhuan_rounded)
        if (transaction['result']):
            amount = transaction['transaction']['raw_data']['contract'][0]['parameter']['value']['amount']
            txid = transaction['txid']
            xiangqing = f"https://tronscan.org/?utm_source=tronlink #/transaction/{txid}?lang=zh"
            bot.send_message(chat_id=admin_id,
                             text=f"✅结算成功,向账号{daili_addres}转账{float(amount) / 1000000}TRX\n[点击查看交易详情]({xiangqing})",
                             parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        print(f"2Error sending message to chat_id {admin_id}: {e}")

                        
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
                            if result.get("success") == "代理能量成功":
                                txid = result.get("tx_hash")
                                transaction_url = f"https://tronscan.org/?utm_source=tronlink#/transaction/{txid}?lang=zh"
                                api_balance = result.get('new_balance')

                                new_balance = balance - us_amount
                                # 更新用户的余额
                                update_balance(chat_id, new_balance)
                                text = (f"✅VIP客户 下发完成\n➖➖➖➖➖➖➖➖\n"
                                        f"套餐模式：预存扣费模式\n"
                                        f"能量带宽：{energy}\n"
                                        f"有效时长：一天\n"
                                        f"接收地址：{from_address[:8]}......{from_address[-8:]}\n"
                                        f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})"
                                        f"")
                                new_text = text + f'\n账户余额：{new_balance / 1000000}'
                                try:
                                    text = f"订单详情：[{txid[:6]}......{txid[-6:]}]({transaction_url})\n消耗能量{energy}\napi余额：{api_balance / 1000000}"
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
    # 统一走 config.txt 配置的能量池 API（本地开发用 host.docker.internal / 线上用域名）
    base = (energy_pool_api or "").rstrip("/")
    if not base:
        return {"success": False, "error": "energy_pool_api not configured"}

    # 笔数套餐：调用能量下发接口
    url = f"{base}/v1/delegate_meal"
    data = {
        "username": username,
        "password": password,
        "energy": energy,
        "day": day,
        "receiver_address": receiver_address
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=data, headers=headers, timeout=30)

    if response.status_code == 200:
        return response.json()
    else:
        return response.json()
 
def delegate_prestored(energy,day,receiver_address):
    url = "https://zhangpu.online/v1/delegate_meal"
    data = {
        "username": username,
        "password": password,
        "energy": energy,
        "day": day,
        "receiver_address": receiver_address
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return response.json()
        
def energy_tran(energy,day,receiver_address):
    url = "http://tronenergy.cyou/v1/delegate_tran"
    data = {
        "username": username,
        "password": password,
        "energy": energy,
        "day": day,
        "receiver_address": receiver_address
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
    global CUSTOMER_SERVICE_ID, bot_id, group_link, control_address, privateKey, username, password,huilv_zhekou,message,admin_id,hour_price,day_price,yucun_price,three_day_price
    global energy_pool_api
    config = read_config('config.txt')  # 指定你的文本文件路径
    TOKEN = config.get('TOKEN', '')
    CUSTOMER_SERVICE_ID = config.get('CUSTOMER_SERVICE_ID', '')
    bot_id = config.get('bot_id', '')
    group_link = config.get('group_link', '')
    control_address = config.get('control_address', '')
    privateKey = config.get('privateKey', '')
    username = config.get('username', '')
    password = config.get('password', '')
    ad_time = int(config.get('ad_time', ''))
    huilv_zhekou = float(config.get('huilv_zhekou', ''))
    admin_id = int(config.get('admin_id', ''))
    hour_price = float(config.get('hour_price', ''))
    day_price = float(config.get('day_price', ''))
    three_day_price = float(config.get('three_day_price', ''))
    # 预存功能已下线：允许配置缺失/为空时不报错
    _yucun_raw = (config.get('yucun_price') or '').strip()
    yucun_price = float(_yucun_raw) if _yucun_raw else 0.0

    # 能量池 API
    energy_pool_api = (config.get('energy_pool_api') or '').strip()

    # 启动时也做一次价格冲突检查（此时可能还没有 bot，只写日志）
    conflict_msg = check_pricing_conflicts()
    if conflict_msg:
        logging.warning(conflict_msg)

    message = f"\n`{control_address}`\n"
    global bot
    global all_chats
    
    # 启动配置文件监听器
    config_file_path = os.path.abspath('config.txt')
    start_config_watcher(config_file_path, reload_config)
    logging.info("配置文件热重载功能已启用")
    if not os.path.exists('group_ids.txt'):
        with open('group_ids.txt', 'w') as f:
            pass

    with open("group_ids.txt", "r") as f:
        all_chats = {int(line.strip()) for line in f.readlines()}

    updater = Updater(TOKEN, use_context=True)
    bot = updater.bot	
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
    scheduler.add_job(scheduled_message_fanhuan, 'cron', day_of_week='mon-sun', hour=23, minute=54)
    scheduler.add_job(
        query_and_recharge,
        'interval',
        seconds=30,
        args=(bot,)  # Pass the updater instance as an argument
    )
    scheduler.start()
    updater.start_polling()
        # 运行机器人，直到您按下Ctrl + C
    updater.idle()

if __name__ == '__main__':
    main()


