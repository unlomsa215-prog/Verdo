import telebot
from telebot import types
import random
import time
import json
import os
from threading import Timer, Lock, RLock, Thread
from datetime import datetime, timedelta
import string
import hashlib
import sys
import signal
import functools

# ====================== КОНФИГУРАЦИЯ ======================
TOKEN = os.getenv('BOT_TOKEN', '8019174987:AAFd_qG434htnd94mnCOZfd2ejD0hgTGUJk')
ADMIN_PASSWORD_HASH = hashlib.sha256('Kyniksvs1832'.encode()).hexdigest()

OWNER_USERNAME = '@kyniks'  # для проверки владельца
OWNER_ID = None  # будет получено при старте

CHANNEL_USERNAME = '@werdoxz_wiinere'
CHAT_LINK = 'https://t.me/+B7u5OmPsako4MTAy'

# Файлы для хранения данных
DATA_FILE = 'bot_data.json'
USERNAME_CACHE_FILE = 'username_cache.json'
PROMO_FILE = 'promocodes.json'
BUSINESS_FILE = 'business_data.json'
CLAN_FILE = 'clan_data.json'
ACHIEVEMENTS_FILE = 'achievements.json'
QUESTS_FILE = 'quests_data.json'
EVENT_FILE = 'event_data.json'
CASES_FILE = 'cases_data.json'
ORDERS_FILE = 'orders.json'
CHEQUES_FILE = 'cheques.json'
MICE_FILE = 'mice_data.json'
PETS_FILE = 'pets_data.json'
BANK_FILE = 'bank_data.json'
PHONE_FILE = 'phone_data.json'
BONUS_FILE = 'bonus_data.json'
DUEL_FILE = 'duel_data.json'

MAX_BET = 100000000
GAME_TIMEOUT = 300

# Константы для игр
TOWER_MULTIPLIERS = {1: 1.0, 2: 1.5, 3: 2.5, 4: 4.0, 5: 6.0}
FOOTBALL_MULTIPLIER = 2.0
BASKETBALL_MULTIPLIER = 2.0
PYRAMID_CELLS = 10
PYRAMID_MULTIPLIER = 5.0
MINES_MULTIPLIERS = {
    1: {1: 1.1, 2: 1.2, 3: 1.3, 4: 1.4, 5: 1.5, 6: 1.6, 7: 1.7, 8: 1.8, 9: 1.9, 10: 2.0},
    2: {1: 1.2, 2: 1.4, 3: 1.6, 4: 1.8, 5: 2.0, 6: 2.2, 7: 2.4, 8: 2.6, 9: 2.8, 10: 3.0},
    3: {1: 1.3, 2: 1.6, 3: 2.0, 4: 2.4, 5: 2.8, 6: 3.2, 7: 3.6, 8: 4.0, 9: 4.5, 10: 5.0},
    4: {1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0, 5: 3.5, 6: 4.0, 7: 4.5, 8: 5.0, 9: 5.5, 10: 6.0},
    5: {1: 2.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 6.0, 6: 7.0, 7: 8.0, 8: 9.0, 9: 10.0, 10: 12.0}
}
BLACKJACK_MULTIPLIER = 2.0
SLOTS_SYMBOLS = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
SLOTS_PAYOUTS = {
    ('7️⃣', '7️⃣', '7️⃣'): 10.0,
    ('💎', '💎', '💎'): 5.0,
    ('🍇', '🍇', '🍇'): 3.0,
    ('🍊', '🍊', '🍊'): 2.0,
    ('🍋', '🍋', '🍋'): 1.5,
    ('🍒', '🍒', '🍒'): 1.2
}
HILO_MULT = 2.0
HILO_WIN_CHANCE = 0.5
ROULETTE_NUMBERS = list(range(37))
RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
ROULETTE_MULTIPLIERS = {
    'straight': 36,
    'red': 2,
    'black': 2,
    'even': 2,
    'odd': 2,
    '1-18': 2,
    '19-36': 2,
    'dozen': 3
}

# Ивент (отключён)
RELEASE_EVENT = {
    'active': False,
    'multiplier': 1.0,
    'end_time': 0
}

# ====================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ======================
users = {}
username_cache = {}
game_timers = {}
crash_update_timers = {}
crash_locks = {}
admin_users = set()
promocodes = {}
orders = {}
next_order_id = 1
cheques = {}
user_cases = {}
user_achievements = {}
user_quests = {}
duels = {}
clans = {}
businesses = {}
event_data = {'active': False, 'participants': {}, 'leaderboard': [], 'last_update': time.time()}
jackpot = {'total': 0, 'last_winner': None, 'last_win_time': None, 'history': []}
daily_reward = {}

# НОВЫЕ СИСТЕМЫ
bank_data = {
    'loans': {},
    'deposits': {},
    'transfers': [],
    'total_deposits': 0,
    'interest_rate': 0.05
}

phone_data = {
    'contacts': {},
    'calls': {},
    'messages': {},
    'phone_numbers': {}
}

bonus_data = {
    'daily': {},
    'weekly': {},
    'monthly': {},
    'referral_bonus': 5000
}

pets_data = {}
clans_data = {}
businesses_data = {}

# Блокировки для потокобезопасности
data_lock = RLock()
user_locks = {}

# ====================== VIP РОЛИ ======================
VIP_ROLES = {
    'admin': {'name': '🔥Admin🔥', 'permissions': ['admin_panel']},
    'tester': {'name': '🤎Тестер💜', 'permissions': ['tester_bonus']},
    'helper': {'name': '💫Helper💫', 'permissions': []},
    'coder': {'name': '💻к0д3(р💻', 'permissions': ['admin_panel', 'tester_bonus', 'helper_bonus']}
}

# ====================== СИСТЕМА МЫШЕК ======================
MICE_DATA = {
    'standard': {
        'name': '💖 Мышка - стандарт 💖',
        'price': 100000,
        'total': 100,
        'sold': 0,
        'rarity': 'обычная',
        'description': '👻 Для украшения аккаунта',
        'signature': 'kyn k.y 🌟',
        'version': 'стандарт',
        'income': 500,
        'income_interval': 3600,
        'icon': '🐭'
    },
    'china': {
        'name': '🤩 Мышка - чуньхаохаокакао 🤩',
        'price': 500000,
        'total': 100,
        'sold': 0,
        'rarity': 'средняя',
        'description': '💖 Китайская коллекционная мышка',
        'signature': 'chinalals k.y 💖',
        'version': 'china',
        'income': 1000,
        'income_interval': 3600,
        'icon': '🐹'
    },
    'world': {
        'name': '🌍 Мышка - мира 🌍',
        'price': 1000000,
        'total': 100,
        'sold': 0,
        'rarity': 'Lux',
        'description': '🍦 Эксклюзивная мышка мира',
        'signature': 'lux k.y 🖊️',
        'version': 'maximum',
        'income': 5000,
        'income_interval': 3600,
        'icon': '🐼'
    }
}

# ====================== СИСТЕМА ПИТОМЦЕВ ======================
PETS_DATA = {
    'dog': {
        'name': '🐕 Пёс',
        'price': 5000,
        'food_cost': 10,
        'happiness': 100,
        'income': 50,
        'rarity': 'обычный',
        'description': 'Верный друг, приносит небольшой доход'
    },
    'cat': {
        'name': '🐈 Кот',
        'price': 7500,
        'food_cost': 8,
        'happiness': 100,
        'income': 70,
        'rarity': 'обычный',
        'description': 'Независимый, но прибыльный'
    },
    'parrot': {
        'name': '🦜 Попугай',
        'price': 12000,
        'food_cost': 5,
        'happiness': 100,
        'income': 100,
        'rarity': 'редкий',
        'description': 'Говорящий, приносит хороший доход'
    },
    'hamster': {
        'name': '🐹 Хомяк',
        'price': 3000,
        'food_cost': 3,
        'happiness': 100,
        'income': 30,
        'rarity': 'обычный',
        'description': 'Маленький, но трудолюбивый'
    },
    'dragon': {
        'name': '🐲 Дракон',
        'price': 100000,
        'food_cost': 50,
        'happiness': 100,
        'income': 1000,
        'rarity': 'легендарный',
        'description': 'Мифическое существо, огромный доход'
    }
}

# ====================== СИСТЕМА БИЗНЕСА ======================
BUSINESS_DATA = {
    'kiosk': {
        'name': '🏪 Ларёк',
        'price': 10000,
        'income': 500,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 5000,
        'icon': '🏪',
        'description': 'Маленький, но стабильный доход'
    },
    'shop': {
        'name': '🏬 Магазин',
        'price': 50000,
        'income': 2000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 25000,
        'icon': '🏬',
        'description': 'Серьёзный бизнес'
    },
    'restaurant': {
        'name': '🍽️ Ресторан',
        'price': 200000,
        'income': 10000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 100000,
        'icon': '🍽️',
        'description': 'Премиум сегмент'
    },
    'factory': {
        'name': '🏭 Завод',
        'price': 1000000,
        'income': 50000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 500000,
        'icon': '🏭',
        'description': 'Промышленный масштаб'
    },
    'corporation': {
        'name': '🏢 Корпорация',
        'price': 10000000,
        'income': 500000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 5000000,
        'icon': '🏢',
        'description': 'Мировой уровень'
    }
}

# ====================== СИСТЕМА КЛАНОВ ======================
CLAN_DATA = {
    'create_cost': 100000,
    'max_members': 50,
    'war_cost': 50000,
    'bonus_per_member': 1000
}

# ====================== КЕЙСЫ ======================
CASES = {
    'case1': {'name': '😁 лол 😁', 'price': 3000, 'min_win': 1000, 'max_win': 5000, 'icon': '📦'},
    'case2': {'name': '🎮 лотус 🎮', 'price': 10000, 'min_win': 7500, 'max_win': 15000, 'icon': '🎮'},
    'case3': {'name': '💫 люкс кейс 💫', 'price': 50000, 'min_win': 35000, 'max_win': 65000, 'icon': '💫'},
    'case4': {'name': '💎 Платинум 💍', 'price': 200000, 'min_win': 175000, 'max_win': 250000, 'icon': '💎'},
    'case5': {'name': '💫 специальный кейс 👾', 'price': 1000000, 'min_win': 750000, 'max_win': 1250000, 'icon': '👾'},
    'case6': {'name': '🎉 ивентовый 🎊', 'price': 0, 'min_win': 12500, 'max_win': 75000, 'icon': '🎉'}
}

# ====================== ДОСТИЖЕНИЯ ======================
achievements = {
    'first_game': {'name': '🎮 Первый шаг', 'desc': 'Сыграть первую игру', 'reward': 1000},
    'millionaire': {'name': '💰 Миллионер', 'desc': 'Накопить 1,000,000 кредиксов', 'reward': 50000},
    'referral_master': {'name': '🤝 Реферал', 'desc': 'Пригласить 10 друзей', 'reward': 100000},
    'mice_collector': {'name': '🐭 Мышиный король', 'desc': 'Собрать всех видов мышек', 'reward': 150000},
    'pet_collector': {'name': '🐾 Зоофил', 'desc': 'Собрать всех питомцев', 'reward': 100000},
    'clan_leader': {'name': '👑 Лидер клана', 'desc': 'Создать клан', 'reward': 50000},
    'banker': {'name': '💳 Банкир', 'desc': 'Положить 1,000,000 в банк', 'reward': 75000},
    'businessman': {'name': '💼 Бизнесмен', 'desc': 'Купить 5 бизнесов', 'reward': 100000},
    'phone_addict': {'name': '📱 Телефономан', 'desc': 'Сделать 100 звонков', 'reward': 25000},
    'bonus_hunter': {'name': '🎁 Охотник за бонусами', 'desc': 'Забрать 30 ежедневных бонусов', 'reward': 50000}
}

# ====================== ИНИЦИАЛИЗАЦИЯ БОТА ======================
bot = telebot.TeleBot(TOKEN)

# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================
def atomic_json_save(file_path, data):
    """Атомарное сохранение JSON через временный файл."""
    temp = file_path + '.tmp'
    try:
        with open(temp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, file_path)
    except Exception as e:
        print(f"Ошибка сохранения {file_path}: {e}")

def safe_json_load(file_path, default_value=None):
    if default_value is None:
        default_value = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return default_value
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            return default_value
    return default_value

def load_data():
    global users, username_cache, promocodes, user_achievements, user_quests, event_data
    global user_cases, orders, next_order_id, cheques, jackpot, duels, clans, businesses
    global bank_data, phone_data, bonus_data, pets_data, clans_data, businesses_data
    global OWNER_ID

    with data_lock:
        users_data = safe_json_load(DATA_FILE, {})
        if users_data:
            users = {str(k): v for k, v in users_data.items()}
            for uid in users:
                if 'balance' not in users[uid]:
                    users[uid]['balance'] = 1000
                if 'krds_balance' not in users[uid]:
                    users[uid]['krds_balance'] = 0
                if 'mice' not in users[uid]:
                    users[uid]['mice'] = {}
                if 'mice_last_collect' not in users[uid]:
                    users[uid]['mice_last_collect'] = {}
                if 'pets' not in users[uid]:
                    users[uid]['pets'] = {}
                if 'pets_last_feed' not in users[uid]:
                    users[uid]['pets_last_feed'] = {}
                if 'businesses' not in users[uid]:
                    users[uid]['businesses'] = {}
                if 'businesses_last_collect' not in users[uid]:
                    users[uid]['businesses_last_collect'] = {}
                if 'clan' not in users[uid]:
                    users[uid]['clan'] = None
                if 'phone_number' not in users[uid]:
                    users[uid]['phone_number'] = None
                if 'phone_contacts' not in users[uid]:
                    users[uid]['phone_contacts'] = []
                if 'daily_bonus' not in users[uid]:
                    users[uid]['daily_bonus'] = {'last_claim': 0, 'streak': 0}
                if 'weekly_bonus' not in users[uid]:
                    users[uid]['weekly_bonus'] = {'last_claim': 0, 'streak': 0}
                if 'bank_deposit' not in users[uid]:
                    users[uid]['bank_deposit'] = {'amount': 0, 'time': 0}
                if 'bank_loan' not in users[uid]:
                    users[uid]['bank_loan'] = {'amount': 0, 'time': 0}
                if 'work_count' not in users[uid]:
                    users[uid]['work_count'] = 0
                if 'referrals' not in users[uid]:
                    users[uid]['referrals'] = 0
                if 'used_promos' not in users[uid]:
                    users[uid]['used_promos'] = []
                if 'game_history' not in users[uid]:
                    users[uid]['game_history'] = []
                if 'game' not in users[uid]:
                    users[uid]['game'] = None
                if 'banned' not in users[uid]:
                    users[uid]['banned'] = False
                # поле для роли и времени последней выдачи тестеру
                if 'role' not in users[uid]:
                    users[uid]['role'] = None
                if 'tester_last_payout' not in users[uid]:
                    users[uid]['tester_last_payout'] = 0

        username_cache = safe_json_load(USERNAME_CACHE_FILE, {})
        promocodes = safe_json_load(PROMO_FILE, {})
        
        mice_data = safe_json_load(MICE_FILE, {})
        if mice_data and 'mice_sold' in mice_data:
            for mouse_id, data in mice_data['mice_sold'].items():
                if mouse_id in MICE_DATA:
                    MICE_DATA[mouse_id]['sold'] = data

        orders_data = safe_json_load(ORDERS_FILE, {})
        if orders_data:
            orders = orders_data.get('orders', {})
            next_order_id = orders_data.get('next_id', 1)

        cheques = safe_json_load(CHEQUES_FILE, {})
        user_achievements = safe_json_load(ACHIEVEMENTS_FILE, {})
        user_quests = safe_json_load(QUESTS_FILE, {})
        user_cases = safe_json_load(CASES_FILE, {})
        duels = safe_json_load(DUEL_FILE, {})
        clans = safe_json_load(CLAN_FILE, {})
        businesses = safe_json_load(BUSINESS_FILE, {})

        bank_data = safe_json_load(BANK_FILE, {
            'loans': {},
            'deposits': {},
            'transfers': [],
            'total_deposits': 0,
            'interest_rate': 0.05
        })
        
        phone_data = safe_json_load(PHONE_FILE, {
            'contacts': {},
            'calls': {},
            'messages': {},
            'phone_numbers': {}
        })
        
        bonus_data = safe_json_load(BONUS_FILE, {
            'daily': {},
            'weekly': {},
            'monthly': {},
            'referral_bonus': 5000
        })
        
        pets_data = safe_json_load(PETS_FILE, {})
        clans_data = safe_json_load(CLAN_FILE, {})
        businesses_data = safe_json_load(BUSINESS_FILE, {})

        jackpot_data = safe_json_load('jackpot.json', {'total': 0})
        if jackpot_data:
            jackpot.update(jackpot_data)

        event_data = safe_json_load(EVENT_FILE, {
            'active': RELEASE_EVENT['active'],
            'participants': {},
            'leaderboard': [],
            'last_update': time.time()
        })

def save_data():
    with data_lock:
        try:
            atomic_json_save(DATA_FILE, users)
            atomic_json_save(USERNAME_CACHE_FILE, username_cache)
            atomic_json_save(PROMO_FILE, promocodes)
            atomic_json_save(ACHIEVEMENTS_FILE, user_achievements)
            atomic_json_save(QUESTS_FILE, user_quests)
            atomic_json_save(CASES_FILE, user_cases)
            atomic_json_save(DUEL_FILE, duels)
            atomic_json_save(CLAN_FILE, clans)
            atomic_json_save(BUSINESS_FILE, businesses)
            atomic_json_save('jackpot.json', jackpot)
            atomic_json_save(EVENT_FILE, event_data)
            atomic_json_save(BANK_FILE, bank_data)
            atomic_json_save(PHONE_FILE, phone_data)
            atomic_json_save(BONUS_FILE, bonus_data)
            atomic_json_save(PETS_FILE, pets_data)
            
            mice_data = {'mice_sold': {mid: MICE_DATA[mid]['sold'] for mid in MICE_DATA}}
            atomic_json_save(MICE_FILE, mice_data)
            
            orders_data = {'orders': orders, 'next_id': next_order_id}
            atomic_json_save(ORDERS_FILE, orders_data)
            
            atomic_json_save(CHEQUES_FILE, cheques)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

def get_user_lock(user_id):
    if user_id not in user_locks:
        user_locks[user_id] = RLock()
    return user_locks[user_id]

def get_locks_sorted(uid1, uid2):
    """Возвращает кортеж блокировок в порядке возрастания ID для предотвращения deadlock."""
    if uid1 < uid2:
        return get_user_lock(uid1), get_user_lock(uid2)
    else:
        return get_user_lock(uid2), get_user_lock(uid1)

def get_user(user_id):
    user_id = str(user_id)
    with get_user_lock(user_id):
        if user_id not in users:
            users[user_id] = {
                'balance': 1000,
                'krds_balance': 0,
                'game': None,
                'referrals': 0,
                'referrer': None,
                'banned': False,
                'bank': {'balance': 0, 'last_interest': time.time(), 'history': []},
                'used_promos': [],
                'clan': None,
                'total_wins': 0,
                'total_losses': 0,
                'games_played': 0,
                'win_streak': 0,
                'max_win_streak': 0,
                'total_lost': 0,
                'quests_completed': 0,
                'event_points': 0,
                'game_history': [],
                'daily_last_claim': 0,
                'daily_streak': 0,
                'last_case6_open': 0,
                'mice': {},
                'mice_last_collect': {},
                'pets': {},
                'pets_last_feed': {},
                'businesses': {},
                'businesses_last_collect': {},
                'phone_number': None,
                'phone_contacts': [],
                'daily_bonus': {'last_claim': 0, 'streak': 0},
                'weekly_bonus': {'last_claim': 0, 'streak': 0},
                'bank_deposit': {'amount': 0, 'time': 0},
                'bank_loan': {'amount': 0, 'time': 0},
                'work_count': 0,
                'role': None,
                'tester_last_payout': 0
            }
            save_data()
        return users[user_id]

def is_banned(user_id):
    user = get_user(user_id)
    return user.get('banned', False)

def is_admin(user_id):
    # Админ через пароль или по роли admin/coder
    if str(user_id) in admin_users:
        return True
    user = get_user(user_id)
    role = user.get('role')
    return role in ('admin', 'coder')

def update_username_cache(user_id, username):
    if username:
        with data_lock:
            username_cache[username.lower()] = str(user_id)
            save_data()

def parse_bet(bet_str):
    try:
        bet_str = bet_str.lower().strip()
        if 'кк' in bet_str:
            bet_str = bet_str.replace('кк', '')
            if bet_str == '':
                bet_str = '1'
            return int(float(bet_str) * 1000000)
        elif 'к' in bet_str:
            bet_str = bet_str.replace('к', '')
            if bet_str == '':
                bet_str = '1'
            return int(float(bet_str) * 1000)
        else:
            return int(bet_str)
    except:
        return None

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.1f}М"
    elif num >= 1000:
        return f"{num/1000:.1f}К"
    return str(num)

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        return f"{int(seconds/60)} мин"
    elif seconds < 86400:
        return f"{int(seconds/3600)} ч"
    else:
        return f"{int(seconds/86400)} д"

def get_event_multiplier():
    # Ивент отключён, всегда 1.0
    return 1.0

def unlock_achievement(user_id, achievement_id):
    if achievement_id not in achievements:
        return
    with data_lock:
        if user_id not in user_achievements:
            user_achievements[user_id] = {}
        if achievement_id in user_achievements[user_id]:
            return
        achievement = achievements[achievement_id]
        user_achievements[user_id][achievement_id] = time.time()
        
        user = get_user(user_id)
        user['balance'] += achievement['reward']
        save_data()
    
    try:
        bot.send_message(int(user_id), 
            f"🏆 ** ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО! ** 🏆\n\n"
            f"{achievement['name']}\n"
            f"{achievement['desc']}\n"
            f"💰 Награда: +{format_number(achievement['reward'])} кредиксов")
    except:
        pass

def update_game_stats(user_id, won, bet, win_amount=0):
    user = get_user(user_id)
    with get_user_lock(user_id):
        user['games_played'] = user.get('games_played', 0) + 1
        
        if won:
            user['total_wins'] = user.get('total_wins', 0) + 1
            user['win_streak'] = user.get('win_streak', 0) + 1
            if user['win_streak'] > user.get('max_win_streak', 0):
                user['max_win_streak'] = user['win_streak']
            if 'game_history' not in user:
                user['game_history'] = []
            user['game_history'].append({
                'time': time.time(),
                'game': 'game',
                'bet': bet,
                'result': 'win',
                'profit': win_amount - bet
            })
        else:
            user['total_losses'] = user.get('total_losses', 0) + 1
            user['win_streak'] = 0
            user['total_lost'] = user.get('total_lost', 0) + bet
            if 'game_history' not in user:
                user['game_history'] = []
            user['game_history'].append({
                'time': time.time(),
                'game': 'game',
                'bet': bet,
                'result': 'loss',
                'profit': -bet
            })
        
        save_data()
    
    # Проверка достижений
    if user['games_played'] == 1:
        unlock_achievement(user_id, 'first_game')
    
    if user['balance'] >= 1000000:
        unlock_achievement(user_id, 'millionaire')
    
    if len(user.get('mice', {})) >= 3:
        unlock_achievement(user_id, 'mice_collector')
    
    if len(user.get('pets', {})) >= 5:
        unlock_achievement(user_id, 'pet_collector')
    
    if len(user.get('businesses', {})) >= 5:
        unlock_achievement(user_id, 'businessman')
    
    if user.get('clan') is not None:
        unlock_achievement(user_id, 'clan_leader')
    
    if user.get('bank_deposit', {}).get('amount', 0) >= 1000000:
        unlock_achievement(user_id, 'banker')
    
    if len(user.get('phone_contacts', [])) >= 100:
        unlock_achievement(user_id, 'phone_addict')
    
    if user.get('daily_bonus', {}).get('streak', 0) >= 30:
        unlock_achievement(user_id, 'bonus_hunter')

def cancel_user_game(user_id):
    """Отмена игры пользователя с очисткой таймеров"""
    with get_user_lock(user_id):
        if user_id in crash_update_timers:
            try:
                crash_update_timers[user_id].cancel()
            except:
                pass
            del crash_update_timers[user_id]
        
        if user_id in game_timers:
            try:
                game_timers[user_id].cancel()
            except:
                pass
            del game_timers[user_id]
        
        user = get_user(user_id)
        if user.get('game') is not None:
            if user['game'].get('stage') == 'waiting_bet' and 'bet' in user['game']:
                user['balance'] += user['game']['bet']
            user['game'] = None
            save_data()
            return True
    return False

def cleanup_all_timers():
    """Очистка всех таймеров при завершении"""
    with data_lock:
        for user_id in list(crash_update_timers.keys()):
            try:
                crash_update_timers[user_id].cancel()
            except:
                pass
        for user_id in list(game_timers.keys()):
            try:
                game_timers[user_id].cancel()
            except:
                pass
        crash_update_timers.clear()
        game_timers.clear()

# ====================== НОВАЯ ФУНКЦИЯ ДЛЯ ТЕСТЕРОВ ======================
def give_tester_bonus():
    """Периодическая проверка и выдача бонуса тестерам (1M каждые 10 часов)"""
    while True:
        time.sleep(3600)  # проверка раз в час
        now = time.time()
        with data_lock:
            for uid, user in users.items():
                role = user.get('role')
                if role in ('tester', 'coder') and not user.get('banned', False):
                    last = user.get('tester_last_payout', 0)
                    if now - last >= 10 * 3600:  # 10 часов
                        # начисляем 1M
                        user['balance'] = user.get('balance', 0) + 1_000_000
                        user['tester_last_payout'] = now
                        try:
                            bot.send_message(int(uid),
                                f"🤎 ** БОНУС ТЕСТЕРА ** 🤎\n\n"
                                f"💰 Вам начислено +1 000 000 кредиксов!\n"
                                f"Следующее начисление через 10 часов.")
                        except:
                            pass
            save_data()

# ====================== ОБРАБОТЧИК КОМАНД БЕЗ СЛЭША ======================
def text_command_handler(message):
    """Обрабатывает текстовые сообщения как команды без слэша."""
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return

    text = message.text.strip().lower()
    if not text:
        return

    # Если сообщение начинается со слэша, пропускаем (обработают стандартные хендлеры)
    if text.startswith('/'):
        return

    parts = text.split()
    command = parts[0]

    # Словарь команд и соответствующих функций (без слэша)
    command_map = {
        'баланс': balance_command,
        'профиль': profile_command,
        'топ': top_command,
        'помощь': help_command,
        'игры': games_command,
        'работа': work_command,
        'банк': bank_command,
        'депозит': deposit_command,
        'снять': withdraw_command,
        'кредит': loan_command,
        'выплатить': repay_loan_command,
        'проценты': interest_command,
        'телефон': phone_command,
        'контакты': contacts_command,
        'добавить': add_contact_command,
        'позвонить': call_command,
        'бонус': bonus_command,
        'daily': daily_bonus_command,
        'weekly': weekly_bonus_command,
        'питомцы': pets_command,
        'магазинпитомцев': pet_shop_command,
        'купитьпитомца': buy_pet_command,
        'покормить': feed_pet_command,
        'бизнес': business_command,
        'магазинбизнеса': business_shop_command,
        'купитьбизнес': buy_business_command,
        'улучшить': upgrade_business_command,
        'собратьбизнес': collect_business_command,
        'клан': clan_command,
        'создатьклан': create_clan_command,
        'мышки': mice_shop_command,
        'купитьмышку': buy_mouse_command,
        'мыши': my_mice_command,
        'собратьмыши': collect_mice_command,
        'обменник': exchange_menu,
        'продатькрдс': sell_krds_command,
        'продать': sell_to_bot_command,
        'моиордера': my_orders_command,
        'ордера': all_orders_command,
        'купить': buy_krds_command,
        'отменитьордер': cancel_order_command,
        'сенд': send_krds_command,
        'дать': give_command,
        'донат': donate_command,
        'реф': ref_command,
        'cancel': cancel_game_command,
        'кости': dice_game_command,
        # TODO: добавить остальные игры по аналогии
    }

    if command in command_map:
        try:
            command_map[command](message)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка выполнения команды: {e}")
    else:
        game_commands = ['башня', 'футбол', 'баскетбол', 'пирамида', 'мины', 'джекпот', 
                         'фишки', 'x2', 'x3', 'x5', 'рулетка_рус', 'очко', 'краш', 'слоты', 'рулетка_каз', 'хило']
        if command in game_commands and len(parts) >= 2:
            game_handler(message)
        # Иначе — ничего не делаем, игнорируем сообщение (убрали ответ "неизвестная команда")
        # else:
        #     bot.send_message(message.chat.id, "❌ Неизвестная команда. Введите /помощь")

# Регистрируем обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Если сообщение начинается со слэша, пропускаем — оно будет обработано отдельными хендлерами команд
    if message.text and message.text.startswith('/'):
        return
    text_command_handler(message)

# ====================== НОВАЯ КОМАНДА /start ======================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    # Регистрируем пользователя, если нет
    user = get_user(user_id)
    update_username_cache(user_id, message.from_user.username)

    # Обработка реферала (если передан параметр)
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        # Проверяем, что реферер существует и не равен текущему пользователю
        if referrer_id != user_id and referrer_id in users and user.get('referrer') is None:
            with data_lock:
                user['referrer'] = referrer_id
                # Начисляем бонус пригласившему
                referrer = get_user(referrer_id)
                referrer['referrals'] = referrer.get('referrals', 0) + 1
                referrer['balance'] += bonus_data['referral_bonus']
                referrer['krds_balance'] += 5
                # Проверка достижения у реферера
                if referrer['referrals'] >= 10:
                    unlock_achievement(referrer_id, 'referral_master')
                save_data()
            try:
                bot.send_message(int(referrer_id),
                    f"👥 По вашей ссылке зарегистрировался новый игрок!\n"
                    f"💰 +{format_number(bonus_data['referral_bonus'])} кредиксов\n"
                    f"💎 +5 KRDS")
            except:
                pass

    # Приветствие
    text = (
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        f"🎰 Это игровой бот с множеством возможностей:\n"
        f"💰 Экономика, игры, бизнес, питомцы, мышки, кланы и многое другое!\n\n"
        f"📋 Основные команды:\n"
        f"/помощь - список всех команд\n"
        f"/баланс - твой баланс\n"
        f"/игры - список игр\n"
        f"/профиль - твой профиль\n\n"
        f"🔗 Наш канал: {CHANNEL_USERNAME}\n"
        f"💬 Чат: {CHAT_LINK}"
    )
    bot.send_message(message.chat.id, text)

# ====================== АДМИН КОМАНДЫ ======================
@bot.message_handler(commands=['Admin'])
def admin_login(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /Admin пароль")
        return
    
    password_hash = hashlib.sha256(args[1].encode()).hexdigest()
    if password_hash == ADMIN_PASSWORD_HASH:
        admin_users.add(user_id)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
            types.InlineKeyboardButton("💰 Выдать кредиксы", callback_data="admin_add_balance"),
            types.InlineKeyboardButton("💎 Выдать KRDS", callback_data="admin_add_krds"),
            types.InlineKeyboardButton("👥 Управление", callback_data="admin_users"),
            types.InlineKeyboardButton("🎟 Промокоды", callback_data="admin_promos"),
            types.InlineKeyboardButton("🐭 Мышки", callback_data="admin_mice"),
            types.InlineKeyboardButton("🏪 Бизнесы", callback_data="admin_business"),
            types.InlineKeyboardButton("🐾 Питомцы", callback_data="admin_pets"),
            types.InlineKeyboardButton("🏦 Банк", callback_data="admin_bank"),
            types.InlineKeyboardButton("📱 Телефон", callback_data="admin_phone"),
            types.InlineKeyboardButton("🎁 Бонусы", callback_data="admin_bonus"),
            types.InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
            types.InlineKeyboardButton("🚫 Забанить", callback_data="admin_ban"),
            types.InlineKeyboardButton("✅ Разбанить", callback_data="admin_unban"),
            types.InlineKeyboardButton("👥 Роли", callback_data="admin_roles"),
            types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_mail"),
            types.InlineKeyboardButton("💾 Сохранить", callback_data="admin_save"),
            types.InlineKeyboardButton("🚪 Выход", callback_data="admin_exit")
        )
        
        bot.send_message(
            message.chat.id,
            "🔑 ** АДМИН ПАНЕЛЬ ** 🔑\n\n"
            f"👤 Администратор: {message.from_user.first_name}\n"
            f"🆔 ID: {user_id}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Выберите действие:",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "🔑❌ Неверный пароль!")

# ====================== ОБРАБОТЧИКИ АДМИН КНОПОК ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    user_id = str(call.from_user.id)
    
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ У вас нет прав администратора!")
        return
    
    data = call.data
    
    if data == "admin_stats":
        with data_lock:
            total_users = len(users)
            total_balance = sum(u.get('balance', 0) for u in users.values())
            total_krds = sum(u.get('krds_balance', 0) for u in users.values())
            banned_count = sum(1 for u in users.values() if u.get('banned', False))
            total_mice = sum(len(u.get('mice', {})) for u in users.values())
            total_pets = sum(len(u.get('pets', {})) for u in users.values())
            total_businesses = sum(len(u.get('businesses', {})) for u in users.values())
            bank_total = bank_data.get('total_deposits', 0)
        
        text = (
            f"📊 ** СТАТИСТИКА БОТА ** 📊\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Пользователи: {total_users}\n"
            f"💰 Баланс всего: {format_number(total_balance)}\n"
            f"💎 KRDS всего: {total_krds}\n"
            f"⛔ Забанено: {banned_count}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🐭 Мышек: {total_mice}\n"
            f"🐾 Питомцев: {total_pets}\n"
            f"🏪 Бизнесов: {total_businesses}\n"
            f"🏦 В банке: {format_number(bank_total)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif data == "admin_exit":
        admin_users.remove(user_id)
        bot.edit_message_text(
            "👋 Вы вышли из режима администратора.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    elif data == "admin_save":
        save_data()
        bot.answer_callback_query(call.id, "✅ Данные сохранены!")
    
    elif data == "admin_add_balance":
        msg = bot.edit_message_text(
            "💰 ** Выдача кредиксов **\n\n"
            "Отправь команду:\n"
            "/addbalance @ник сумма",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    elif data == "admin_add_krds":
        msg = bot.edit_message_text(
            "💎 ** Выдача KRDS **\n\n"
            "Отправь команду:\n"
            "/addkrds @ник сумма",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    elif data == "admin_ban":
        msg = bot.edit_message_text(
            "🚫 ** Бан пользователя **\n\n"
            "Отправь команду:\n"
            "/ban @ник",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    elif data == "admin_unban":
        msg = bot.edit_message_text(
            "✅ ** Разбан пользователя **\n\n"
            "Отправь команду:\n"
            "/unban @ник",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    # раздел управления ролями
    elif data == "admin_roles":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔥Admin🔥", callback_data="admin_role_admin"),
            types.InlineKeyboardButton("🤎Тестер💜", callback_data="admin_role_tester"),
            types.InlineKeyboardButton("💫Helper💫", callback_data="admin_role_helper"),
            types.InlineKeyboardButton("💻к0д3(р💻", callback_data="admin_role_coder"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
        )
        bot.edit_message_text(
            "👥 ** УПРАВЛЕНИЕ РОЛЯМИ **\n\n"
            "Выберите роль для выдачи:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    elif data.startswith("admin_role_"):
        role = data.replace("admin_role_", "")
        # Запоминаем, какую роль хотим выдать, и просим username
        bot.edit_message_text(
            f"✏️ Введите @username пользователя, которому хотите выдать роль {VIP_ROLES[role]['name']}:",
            call.message.chat.id,
            call.message.message_id
        )
        # Используем register_next_step_handler
        bot.register_next_step_handler(call.message, process_role_assignment, role)
        bot.answer_callback_query(call.id)
    
    elif data == "admin_back":
        # Вернуться в главное меню админки
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
            types.InlineKeyboardButton("💰 Выдать кредиксы", callback_data="admin_add_balance"),
            types.InlineKeyboardButton("💎 Выдать KRDS", callback_data="admin_add_krds"),
            types.InlineKeyboardButton("👥 Управление", callback_data="admin_users"),
            types.InlineKeyboardButton("🎟 Промокоды", callback_data="admin_promos"),
            types.InlineKeyboardButton("🐭 Мышки", callback_data="admin_mice"),
            types.InlineKeyboardButton("🏪 Бизнесы", callback_data="admin_business"),
            types.InlineKeyboardButton("🐾 Питомцы", callback_data="admin_pets"),
            types.InlineKeyboardButton("🏦 Банк", callback_data="admin_bank"),
            types.InlineKeyboardButton("📱 Телефон", callback_data="admin_phone"),
            types.InlineKeyboardButton("🎁 Бонусы", callback_data="admin_bonus"),
            types.InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
            types.InlineKeyboardButton("🚫 Забанить", callback_data="admin_ban"),
            types.InlineKeyboardButton("✅ Разбанить", callback_data="admin_unban"),
            types.InlineKeyboardButton("👥 Роли", callback_data="admin_roles"),
            types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_mail"),
            types.InlineKeyboardButton("💾 Сохранить", callback_data="admin_save"),
            types.InlineKeyboardButton("🚪 Выход", callback_data="admin_exit")
        )
        bot.edit_message_text(
            "🔑 ** АДМИН ПАНЕЛЬ ** 🔑\n\n"
            f"👤 Администратор: {call.from_user.first_name}\n"
            f"🆔 ID: {user_id}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Выберите действие:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)

def process_role_assignment(message, role):
    """Обработчик ввода username для выдачи роли"""
    admin_id = str(message.from_user.id)
    if not is_admin(admin_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора!")
        return
    
    username = message.text.strip().replace('@', '').lower()
    with data_lock:
        target_id = username_cache.get(username)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        # Проверка на выдачу кодера: только владелец
        if role == 'coder' and target_id != OWNER_ID:
            bot.send_message(message.chat.id, "❌ Только владелец (@kyniks) может получить роль кодера!")
            return
        
        with get_user_lock(target_id):
            users[target_id]['role'] = role
            save_data()
    
    role_name = VIP_ROLES[role]['name']
    bot.send_message(message.chat.id, f"✅ Роль {role_name} успешно выдана пользователю @{username}!")
    try:
        bot.send_message(int(target_id), f"🎉 Вам выдана роль {role_name}!")
    except:
        pass

# ====================== АДМИН КОМАНДЫ (ТЕКСТОВЫЕ) ======================
@bot.message_handler(commands=['addbalance'])
def add_balance(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "❌ Использование: /addbalance @ник сумма")
        return
    
    target_username = args[1].replace('@', '').lower()
    try:
        amount = int(args[2])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    with data_lock:
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        with get_user_lock(target_user):
            users[target_user]['balance'] = users[target_user].get('balance', 1000) + amount
            save_data()
    
    bot.send_message(message.chat.id, 
        f"➕✅ Пользователю @{target_username} начислено {format_number(amount)} кредиксов.")

@bot.message_handler(commands=['addkrds'])
def add_krds(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "❌ Использование: /addkrds @ник сумма")
        return
    
    target_username = args[1].replace('@', '').lower()
    try:
        amount = int(args[2])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    with data_lock:
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        with get_user_lock(target_user):
            users[target_user]['krds_balance'] = users[target_user].get('krds_balance', 0) + amount
            save_data()
    
    bot.send_message(message.chat.id, 
        f"💎✅ Пользователю @{target_username} начислено {amount} KRDS.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /ban @ник")
        return
    
    target_username = args[1].replace('@', '').lower()
    
    with data_lock:
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        if target_user == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя забанить самого себя!")
            return
        
        with get_user_lock(target_user):
            users[target_user]['banned'] = True
            save_data()
    
    bot.send_message(message.chat.id, f"🔨✅ Пользователь @{target_username} забанен.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /unban @ник")
        return
    
    target_username = args[1].replace('@', '').lower()
    
    with data_lock:
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        with get_user_lock(target_user):
            users[target_user]['banned'] = False
            save_data()
    
    bot.send_message(message.chat.id, f"✅ Пользователь @{target_username} разбанен.")

# ====================== СИСТЕМА РАБОТЫ ======================
@bot.message_handler(commands=['работа'])
def work_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    with get_user_lock(user_id):
        reward = 55
        user['balance'] += reward
        user['work_count'] = user.get('work_count', 0) + 1
        save_data()
    
    text = (
        f"💼 ** РАБОТА ** 💼\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Ты получил: +{reward} кредиксов\n"
        f"💰 Текущий баланс: {format_number(user['balance'])} кредиксов\n"
        f"📊 Всего отработано раз: {user['work_count']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 Приходи за бонусом снова!"
    )
    bot.send_message(message.chat.id, text)

# ====================== СИСТЕМА БАНКА ======================
@bot.message_handler(commands=['банк'])
def bank_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    deposit = user.get('bank_deposit', {'amount': 0, 'time': 0})
    loan = user.get('bank_loan', {'amount': 0, 'time': 0})
    
    text = (
        f"🏦 ** БАНК ** 🏦\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Твой баланс: {format_number(user['balance'])}\n"
        f"💳 Депозит: {format_number(deposit['amount'])}\n"
        f"📉 Кредит: {format_number(loan['amount'])}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Доступные команды:\n"
        f"  /депозит [сумма] - положить под 5%\n"
        f"  /снять [сумма] - снять с депозита\n"
        f"  /кредит [сумма] - взять кредит\n"
        f"  /выплатить [сумма] - выплатить кредит\n"
        f"  /проценты - начислить проценты\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['депозит'])
def deposit_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /депозит [сумма]")
        return
    
    try:
        amount = int(args[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    user = get_user(user_id)
    if user['balance'] < amount:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}")
        return
    
    with get_user_lock(user_id):
        user['balance'] -= amount
        user['bank_deposit'] = {
            'amount': user.get('bank_deposit', {}).get('amount', 0) + amount,
            'time': time.time()
        }
        bank_data['total_deposits'] += amount
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ Вы положили {format_number(amount)} кредиксов на депозит!\n"
        f"💰 Баланс: {format_number(user['balance'])}")

@bot.message_handler(commands=['снять'])
def withdraw_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /снять [сумма]")
        return
    
    try:
        amount = int(args[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    user = get_user(user_id)
    deposit = user.get('bank_deposit', {}).get('amount', 0)
    
    if deposit < amount:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств на депозите! Депозит: {format_number(deposit)}")
        return
    
    with get_user_lock(user_id):
        user['balance'] += amount
        user['bank_deposit']['amount'] -= amount
        bank_data['total_deposits'] -= amount
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ Вы сняли {format_number(amount)} кредиксов с депозита!\n"
        f"💰 Баланс: {format_number(user['balance'])}")

@bot.message_handler(commands=['кредит'])
def loan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /кредит [сумма]")
        return
    
    try:
        amount = int(args[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
        if amount > 1000000:
            bot.send_message(message.chat.id, "❌ Максимальная сумма кредита: 1,000,000")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    user = get_user(user_id)
    current_loan = user.get('bank_loan', {}).get('amount', 0)
    
    if current_loan > 0:
        bot.send_message(message.chat.id, "❌ У вас уже есть активный кредит!")
        return
    
    with get_user_lock(user_id):
        user['balance'] += amount
        user['bank_loan'] = {
            'amount': amount,
            'time': time.time()
        }
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ Вы взяли кредит {format_number(amount)} кредиксов!\n"
        f"💰 Баланс: {format_number(user['balance'])}\n"
        f"⚠️ Не забудьте выплатить с процентами!")

@bot.message_handler(commands=['выплатить'])
def repay_loan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /выплатить [сумма]")
        return
    
    try:
        amount = int(args[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    user = get_user(user_id)
    loan = user.get('bank_loan', {}).get('amount', 0)
    
    if loan <= 0:
        bot.send_message(message.chat.id, "❌ У вас нет кредита!")
        return
    
    if amount > loan:
        amount = loan
    
    if user['balance'] < amount:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}")
        return
    
    with get_user_lock(user_id):
        user['balance'] -= amount
        user['bank_loan']['amount'] -= amount
        if user['bank_loan']['amount'] <= 0:
            user['bank_loan'] = {'amount': 0, 'time': 0}
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ Вы выплатили {format_number(amount)} кредиксов кредита!\n"
        f"💰 Баланс: {format_number(user['balance'])}\n"
        f"📉 Остаток кредита: {format_number(user['bank_loan']['amount'])}")

@bot.message_handler(commands=['проценты'])
def interest_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    deposit = user.get('bank_deposit', {})
    
    if deposit['amount'] <= 0:
        bot.send_message(message.chat.id, "❌ У вас нет депозита!")
        return
    
    time_passed = time.time() - deposit.get('time', time.time())
    if time_passed < 86400:  # меньше дня
        remaining = 86400 - time_passed
        bot.send_message(message.chat.id, 
            f"⏳ Проценты можно будет получить через {format_time(remaining)}")
        return
    
    interest = int(deposit['amount'] * bank_data['interest_rate'])
    
    with get_user_lock(user_id):
        user['balance'] += interest
        user['bank_deposit']['time'] = time.time()
        save_data()
    
    bot.send_message(message.chat.id, 
        f"💰 Вам начислены проценты: +{format_number(interest)} кредиксов!\n"
        f"💰 Баланс: {format_number(user['balance'])}")

# ====================== СИСТЕМА ТЕЛЕФОНА ======================
@bot.message_handler(commands=['телефон'])
def phone_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    phone = user.get('phone_number')
    
    if not phone:
        # Выдаем случайный номер
        phone = f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"
        with get_user_lock(user_id):
            user['phone_number'] = phone
            save_data()
    
    text = (
        f"📱 ** ТЕЛЕФОН ** 📱\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📞 Твой номер: {phone}\n"
        f"👥 Контактов: {len(user.get('phone_contacts', []))}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Доступные команды:\n"
        f"  /контакты - список контактов\n"
        f"  /добавить @ник - добавить контакт\n"
        f"  /позвонить @ник - позвонить\n"
        f"  /смс @ник текст - отправить смс\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['добавить'])
def add_contact_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /добавить @ник")
        return
    
    target_username = args[1].replace('@', '').lower()
    
    with data_lock:
        target_id = username_cache.get(target_username)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        if target_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя добавить самого себя!")
            return
        
        user = get_user(user_id)
        contacts = user.get('phone_contacts', [])
        
        if target_id in contacts:
            bot.send_message(message.chat.id, "❌ Этот пользователь уже в контактах!")
            return
        
        with get_user_lock(user_id):
            user['phone_contacts'].append(target_id)
            save_data()
    
    bot.send_message(message.chat.id, f"✅ @{target_username} добавлен в контакты!")

@bot.message_handler(commands=['контакты'])
def contacts_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    contacts = user.get('phone_contacts', [])
    
    if not contacts:
        bot.send_message(message.chat.id, "📱 У вас нет контактов. Добавьте: /добавить @ник")
        return
    
    text = "📱 ** ВАШИ КОНТАКТЫ ** 📱\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, contact_id in enumerate(contacts, 1):
        try:
            contact = bot.get_chat(int(contact_id))
            name = f"@{contact.username}" if contact.username else contact.first_name
            text += f"{i}. {name}\n"
        except:
            text += f"{i}. ID: {contact_id}\n"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['позвонить'])
def call_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /позвонить @ник")
        return
    
    target_username = args[1].replace('@', '').lower()
    
    with data_lock:
        target_id = username_cache.get(target_username)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        if target_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя позвонить самому себе!")
            return
        
        user = get_user(user_id)
        
        # Стоимость звонка
        call_cost = 100
        if user['balance'] < call_cost:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно: {call_cost}")
            return
        
        with get_user_lock(user_id):
            user['balance'] -= call_cost
            save_data()
        
        # Сохраняем в историю
        if user_id not in phone_data['calls']:
            phone_data['calls'][user_id] = []
        phone_data['calls'][user_id].append({
            'to': target_id,
            'time': time.time(),
            'duration': random.randint(30, 300)
        })
        
        # Проверка достижения
        if len(phone_data['calls'][user_id]) >= 100:
            unlock_achievement(user_id, 'phone_addict')
    
    bot.send_message(message.chat.id, 
        f"📞 Звонок @{target_username}...\n"
        f"💰 Стоимость: {call_cost} кредиксов\n"
        f"✅ Звонок завершён!")
    
    try:
        bot.send_message(int(target_id),
            f"📞 Вам звонил @{message.from_user.username or 'Игрок'}!\n"
            f"💰 Вы получили {call_cost//2} кредиксов за звонок!")
    except:
        pass

# ====================== СИСТЕМА БОНУСОВ ======================
@bot.message_handler(commands=['бонус'])
def bonus_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    
    text = (
        f"🎁 ** БОНУСЫ ** 🎁\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 Ежедневный бонус\n"
        f"  • Текущий стрик: {user['daily_bonus']['streak']} дней\n"
        f"  • Команда: /daily\n\n"
        f"📆 Еженедельный бонус\n"
        f"  • Текущий стрик: {user['weekly_bonus']['streak']} недель\n"
        f"  • Команда: /weekly\n\n"
        f"👥 Реферальный бонус\n"
        f"  • За каждого друга: {format_number(bonus_data['referral_bonus'])}\n"
        f"  • Команда: /реф\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['daily'])
def daily_bonus_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    now = time.time()
    last_claim = user['daily_bonus']['last_claim']
    
    if now - last_claim < 86400:  # меньше дня
        remaining = 86400 - (now - last_claim)
        bot.send_message(message.chat.id, 
            f"⏳ Следующий бонус можно будет получить через {format_time(remaining)}")
        return
    
    # Расчет бонуса
    streak = user['daily_bonus']['streak'] + 1
    base_bonus = 1000
    bonus = base_bonus * streak
    
    with get_user_lock(user_id):
        user['balance'] += bonus
        user['daily_bonus']['last_claim'] = now
        user['daily_bonus']['streak'] = streak
        save_data()
    
    text = (
        f"🎁 ** ЕЖЕДНЕВНЫЙ БОНУС ** 🎁\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ День {streak}\n"
        f"💰 Получено: +{format_number(bonus)} кредиксов\n"
        f"🔥 Стрик: {streak} дней\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Баланс: {format_number(user['balance'])}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['weekly'])
def weekly_bonus_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    now = time.time()
    last_claim = user['weekly_bonus']['last_claim']
    
    if now - last_claim < 604800:  # меньше недели
        remaining = 604800 - (now - last_claim)
        bot.send_message(message.chat.id, 
            f"⏳ Следующий бонус можно будет получить через {format_time(remaining)}")
        return
    
    # Расчет бонуса
    streak = user['weekly_bonus']['streak'] + 1
    base_bonus = 10000
    bonus = base_bonus * streak
    
    with get_user_lock(user_id):
        user['balance'] += bonus
        user['weekly_bonus']['last_claim'] = now
        user['weekly_bonus']['streak'] = streak
        save_data()
    
    text = (
        f"🎁 ** ЕЖЕНЕДЕЛЬНЫЙ БОНУС ** 🎁\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Неделя {streak}\n"
        f"💰 Получено: +{format_number(bonus)} кредиксов\n"
        f"🔥 Стрик: {streak} недель\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Баланс: {format_number(user['balance'])}"
    )
    bot.send_message(message.chat.id, text)

# ====================== СИСТЕМА ПИТОМЦЕВ ======================
@bot.message_handler(commands=['питомцы'])
def pets_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    pets = user.get('pets', {})
    
    text = "🐾 ** МОИ ПИТОМЦЫ ** 🐾\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if not pets:
        text += "У тебя пока нет питомцев!\nКупить: /магазинпитомцев\n\n"
    else:
        total_income = 0
        now = time.time()
        
        for pet_id, pet_data in pets.items():
            if pet_id in PETS_DATA:
                data = PETS_DATA[pet_id]
                last_feed = user.get('pets_last_feed', {}).get(pet_id, now)
                time_passed = now - last_feed
                happiness = max(0, 100 - (time_passed // 3600))  # -1 в час
                
                income = data['income']
                if happiness < 50:
                    income = income // 2
                total_income += income
                
                text += (
                    f"{data['name']}\n"
                    f"  😊 Счастье: {happiness}%\n"
                    f"  💵 Доход: {format_number(income)}/час\n"
                    f"  🍖 Корм: {pet_data.get('food', 0)} шт\n\n"
                )
        
        text += f"━━━━━━━━━━━━━━━━━━━━━━\n💰 Доход в час: {format_number(total_income)}\n\n"
    
    text += (
        f"📋 Команды:\n"
        f"  /магазинпитомцев - купить питомца\n"
        f"  /покормить [тип] - покормить\n"
        f"  /собратьпитомцы - собрать доход\n"
        f"  /продатьпитомца [тип] - продать"
    )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['магазинпитомцев'])
def pet_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    
    text = "🛒 ** МАГАЗИН ПИТОМЦЕВ ** 🛒\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for pet_id, data in PETS_DATA.items():
        text += (
            f"{data['name']}\n"
            f"  • 💰 Цена: {format_number(data['price'])}\n"
            f"  • 💵 Доход: {data['income']}/час\n"
            f"  • 🍖 Расход корма: {data['food_cost']}/день\n"
            f"  • ✨ Редкость: {data['rarity']}\n"
            f"  • 📝 {data['description']}\n"
            f"  • /купитьпитомца {pet_id}\n\n"
        )
    
    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Твой баланс: {format_number(user['balance'])}\n"
        f"🍖 Корм: 5 шт (выдаётся раз в день)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьпитомца'])
def buy_pet_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /купитьпитомца [тип]")
        return
    
    pet_id = args[1]
    if pet_id not in PETS_DATA:
        bot.send_message(message.chat.id, "❌ Такого питомца нет! Типы: dog, cat, parrot, hamster, dragon")
        return
    
    user = get_user(user_id)
    pet_data = PETS_DATA[pet_id]
    
    if user['balance'] < pet_data['price']:
        bot.send_message(message.chat.id, 
            f"❌ Недостаточно средств! Нужно: {format_number(pet_data['price'])}")
        return
    
    with get_user_lock(user_id):
        user['balance'] -= pet_data['price']
        if 'pets' not in user:
            user['pets'] = {}
        user['pets'][pet_id] = {'food': 0, 'bought': time.time()}
        if 'pets_last_feed' not in user:
            user['pets_last_feed'] = {}
        user['pets_last_feed'][pet_id] = time.time()
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ Ты купил {pet_data['name']}!\n"
        f"💰 Баланс: {format_number(user['balance'])}")

@bot.message_handler(commands=['покормить'])
def feed_pet_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /покормить [тип]")
        return
    
    pet_id = args[1]
    user = get_user(user_id)
    
    if pet_id not in user.get('pets', {}):
        bot.send_message(message.chat.id, "❌ У тебя нет такого питомца!")
        return
    
    pet_data = PETS_DATA[pet_id]
    food_needed = pet_data['food_cost']
    
    # Проверка корма
    if user.get('pet_food', 0) < food_needed:
        bot.send_message(message.chat.id, "❌ Недостаточно корма! Корм обновляется каждый день.")
        return
    
    with get_user_lock(user_id):
        user['pet_food'] -= food_needed
        user['pets_last_feed'][pet_id] = time.time()
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ Ты покормил {pet_data['name']}!\n"
        f"🍖 Осталось корма: {user['pet_food']}")

# ====================== СИСТЕМА БИЗНЕСА ======================
@bot.message_handler(commands=['бизнес'])
def business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    businesses = user.get('businesses', {})
    
    text = "🏢 ** МОЙ БИЗНЕС ** 🏢\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if not businesses:
        text += "У тебя пока нет бизнеса!\nКупить: /магазинбизнеса\n\n"
    else:
        total_income = 0
        now = time.time()
        
        for biz_id, biz_data in businesses.items():
            if biz_id in BUSINESS_DATA:
                data = BUSINESS_DATA[biz_id]
                level = biz_data.get('level', 1)
                income = data['income'] * level
                total_income += income
                
                last_collect = user.get('businesses_last_collect', {}).get(biz_id, now)
                time_passed = now - last_collect
                hours_passed = time_passed / 3600
                pending = int(income * hours_passed)
                
                text += (
                    f"{data['icon']} {data['name']} lvl.{level}\n"
                    f"  💵 Доход: {format_number(income)}/час\n"
                    f"  ⏳ Накоплено: {format_number(pending)}\n"
                    f"  📈 Улучшить: /улучшить {biz_id}\n\n"
                )
        
        text += f"━━━━━━━━━━━━━━━━━━━━━━\n💰 Доход в час: {format_number(total_income)}\n\n"
    
    text += (
        f"📋 Команды:\n"
        f"  /магазинбизнеса - купить бизнес\n"
        f"  /собратьбизнес - собрать доход\n"
        f"  /улучшить [тип] - улучшить бизнес"
    )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['магазинбизнеса'])
def business_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    
    text = "🏪 ** МАГАЗИН БИЗНЕСА ** 🏪\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for biz_id, data in BUSINESS_DATA.items():
        text += (
            f"{data['icon']} {data['name']}\n"
            f"  • 💰 Цена: {format_number(data['price'])}\n"
            f"  • 💵 Доход: {data['income']}/час\n"
            f"  • 📈 Макс уровень: {data['max_level']}\n"
            f"  • 📝 {data['description']}\n"
            f"  • /купитьбизнес {biz_id}\n\n"
        )
    
    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Твой баланс: {format_number(user['balance'])}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьбизнес'])
def buy_business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /купитьбизнес [тип]")
        return
    
    biz_id = args[1]
    if biz_id not in BUSINESS_DATA:
        bot.send_message(message.chat.id, "❌ Такого бизнеса нет! Типы: kiosk, shop, restaurant, factory, corporation")
        return
    
    user = get_user(user_id)
    biz_data = BUSINESS_DATA[biz_id]
    
    if user['balance'] < biz_data['price']:
        bot.send_message(message.chat.id, 
            f"❌ Недостаточно средств! Нужно: {format_number(biz_data['price'])}")
        return
    
    if biz_id in user.get('businesses', {}):
        bot.send_message(message.chat.id, "❌ У тебя уже есть такой бизнес!")
        return
    
    with get_user_lock(user_id):
        user['balance'] -= biz_data['price']
        if 'businesses' not in user:
            user['businesses'] = {}
        user['businesses'][biz_id] = {'level': 1, 'bought': time.time()}
        if 'businesses_last_collect' not in user:
            user['businesses_last_collect'] = {}
        user['businesses_last_collect'][biz_id] = time.time()
        save_data()
    
    # Проверка достижения
    if len(user['businesses']) >= 5:
        unlock_achievement(user_id, 'businessman')
    
    bot.send_message(message.chat.id, 
        f"✅ Ты купил {biz_data['icon']} {biz_data['name']}!\n"
        f"💰 Баланс: {format_number(user['balance'])}")

@bot.message_handler(commands=['улучшить'])
def upgrade_business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /улучшить [тип]")
        return
    
    biz_id = args[1]
    user = get_user(user_id)
    
    if biz_id not in user.get('businesses', {}):
        bot.send_message(message.chat.id, "❌ У тебя нет такого бизнеса!")
        return
    
    biz_data = BUSINESS_DATA[biz_id]
    current_level = user['businesses'][biz_id]['level']
    
    if current_level >= biz_data['max_level']:
        bot.send_message(message.chat.id, "❌ Бизнес уже максимального уровня!")
        return
    
    upgrade_cost = biz_data['upgrade_cost'] * current_level
    
    if user['balance'] < upgrade_cost:
        bot.send_message(message.chat.id, 
            f"❌ Недостаточно средств! Нужно: {format_number(upgrade_cost)}")
        return
    
    with get_user_lock(user_id):
        user['balance'] -= upgrade_cost
        user['businesses'][biz_id]['level'] += 1
        save_data()
    
    bot.send_message(message.chat.id, 
        f"✅ {biz_data['icon']} {biz_data['name']} улучшен до {current_level + 1} уровня!\n"
        f"💰 Баланс: {format_number(user['balance'])}")

@bot.message_handler(commands=['собратьбизнес'])
def collect_business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    businesses = user.get('businesses', {})
    
    if not businesses:
        bot.send_message(message.chat.id, "❌ У тебя нет бизнеса!")
        return
    
    now = time.time()
    total_collected = 0
    collected_text = []
    
    with get_user_lock(user_id):
        for biz_id, biz_data in businesses.items():
            if biz_id in BUSINESS_DATA:
                data = BUSINESS_DATA[biz_id]
                level = biz_data.get('level', 1)
                income = data['income'] * level
                
                last_collect = user.get('businesses_last_collect', {}).get(biz_id, now)
                time_passed = now - last_collect
                hours_passed = time_passed / 3600
                earned = int(income * hours_passed)
                
                if earned > 0:
                    total_collected += earned
                    user['businesses_last_collect'][biz_id] = now
                    collected_text.append(f"{data['icon']} {data['name']}: +{format_number(earned)}")
        
        if total_collected > 0:
            user['balance'] += total_collected
            save_data()
    
    if total_collected > 0:
        text = (
            f"✅ ** СБОР ДОХОДА С БИЗНЕСА ** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{chr(10).join(collected_text)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Всего собрано: +{format_number(total_collected)} кредиксов\n"
            f"💸 Новый баланс: {format_number(user['balance'])}"
        )
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, 
            "⏳ Доход ещё не накопился! Приходи через час.")

# ====================== СИСТЕМА КЛАНОВ ======================
@bot.message_handler(commands=['клан'])
def clan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    clan_id = user.get('clan')
    
    if clan_id and clan_id in clans:
        clan = clans[clan_id]
        text = (
            f"👥 ** КЛАН {clan['name']} ** 👥\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👑 Лидер: {clan['leader']}\n"
            f"👥 Участников: {len(clan.get('members', []))}/{CLAN_DATA['max_members']}\n"
            f"💰 Казна: {format_number(clan.get('treasury', 0))}\n"
            f"📊 Рейтинг: {clan.get('rating', 0)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Команды клана:\n"
            f"  /клан инфо - информация\n"
            f"  /клан топ - топ кланов\n"
            f"  /клан пригласить @ник - пригласить\n"
            f"  /клан кикнуть @ник - исключить\n"
            f"  /клан передать @ник - передать лидерство\n"
            f"  /клан казна [сумма] - положить в казну\n"
            f"  /клан выйти - покинуть клан\n"
            f"  /клан распустить - распустить клан (только лидер)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
    else:
        text = (
            f"👥 ** КЛАНЫ ** 👥\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Ты не состоишь в клане!\n\n"
            f"📋 Команды:\n"
            f"  /создатьклан [название] - создать клан (100,000 кредиксов)\n"
            f"  /клан поиск - найти клан\n"
            f"  /клан топ - топ кланов\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['создатьклан'])
def create_clan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ Использование: /создатьклан [название]")
        return
    
    clan_name = ' '.join(args[1:])
    if len(clan_name) > 30:
        bot.send_message(message.chat.id, "❌ Название клана не должно превышать 30 символов!")
        return
    
    user = get_user(user_id)
    
    if user.get('clan'):
        bot.send_message(message.chat.id, "❌ Ты уже состоишь в клане!")
        return
    
    if user['balance'] < CLAN_DATA['create_cost']:
        bot.send_message(message.chat.id, 
            f"❌ Недостаточно средств! Нужно: {format_number(CLAN_DATA['create_cost'])}")
        return
    
    clan_id = f"clan_{int(time.time())}_{random.randint(1000, 9999)}"
    
    with data_lock:
        clans[clan_id] = {
            'name': clan_name,
            'leader': user_id,
            'members': [user_id],
            'treasury': 0,
            'rating': 0,
            'created': time.time()
        }
        
        with get_user_lock(user_id):
            user['balance'] -= CLAN_DATA['create_cost']
            user['clan'] = clan_id
            save_data()
    
    unlock_achievement(user_id, 'clan_leader')
    
    bot.send_message(message.chat.id, 
        f"✅ Клан '{clan_name}' успешно создан!\n"
        f"💰 С баланса списано: {format_number(CLAN_DATA['create_cost'])}")

# ====================== СИСТЕМА МЫШЕК ======================
@bot.message_handler(commands=['мышки'])
def mice_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    text = (
        "🐭 ** МАГАЗИН МЫШЕК ** 🐭\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Каждая мышка приносит пассивный доход каждый час!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    for mouse_id, data in MICE_DATA.items():
        available = data['total'] - data['sold']
        emoji = "✅" if available > 0 else "❌"
        text += (
            f"{emoji} {data['icon']} {data['name']}\n"
            f"   💰 Цена: {format_number(data['price'])} кредиксов\n"
            f"   ✨ Редкость: {data['rarity']}\n"
            f"   💵 Доход: +{format_number(data['income'])} кредиксов/час\n"
            f"   📦 Осталось: {available}/100 шт.\n\n"
        )
    
    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Твой баланс: {format_number(user['balance'])} кредиксов\n"
        f"🐭 Твои мышки: {sum(user.get('mice', {}).values())} шт.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Команды:\n"
        f"  /купитьмышку [тип] - купить мышку\n"
        f"  /мыши - мои мышки\n"
        f"  /собратьмыши - собрать доход\n\n"
        f"Типы: standard, china, world"
    )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьмышку'])
def buy_mouse_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, 
            "❌ Использование: /купитьмышку [тип]\n"
            "Типы: standard, china, world")
        return
    
    mouse_id = args[1].lower()
    if mouse_id not in MICE_DATA:
        bot.send_message(message.chat.id, "❌ Такой мышки нет! Доступны: standard, china, world")
        return
    
    user = get_user(user_id)
    mouse = MICE_DATA[mouse_id]
    available = mouse['total'] - mouse['sold']
    
    if available <= 0:
        bot.send_message(message.chat.id, f"❌ {mouse['name']} закончились!")
        return
    
    if user['balance'] < mouse['price']:
        bot.send_message(message.chat.id, 
            f"❌ Недостаточно средств! Нужно: {format_number(mouse['price'])} кредиксов\n"
            f"💰 Твой баланс: {format_number(user['balance'])} кредиксов")
        return
    
    with get_user_lock(user_id):
        user['balance'] -= mouse['price']
        # Защищаем изменение глобального счётчика блокировкой данных
        with data_lock:
            mouse['sold'] += 1
        
        if 'mice' not in user:
            user['mice'] = {}
        user['mice'][mouse_id] = user['mice'].get(mouse_id, 0) + 1
        
        if 'mice_last_collect' not in user:
            user['mice_last_collect'] = {}
        user['mice_last_collect'][mouse_id] = time.time()
        
        save_data()
    
    text = (
        f"✅ ** ПОКУПКА УСПЕШНА! ** ✅\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mouse['icon']} Ты купил: {mouse['name']}\n"
        f"💰 Цена: {format_number(mouse['price'])} кредиксов\n"
        f"💵 Доход: +{format_number(mouse['income'])} кредиксов/час\n"
        f"📦 Осталось в магазине: {mouse['total'] - mouse['sold']}/100\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🐭 Всего мышек: {sum(user['mice'].values())} шт.\n"
        f"💰 Баланс: {format_number(user['balance'])} кредиксов"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['мыши'])
def my_mice_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    mice = user.get('mice', {})
    
    if not mice:
        bot.send_message(message.chat.id, 
            "🐭 У тебя пока нет мышек! Купи в магазине: /мышки")
        return
    
    text = "🐭 ** МОИ МЫШКИ ** 🐭\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    total_income = 0
    now = time.time()
    
    for mouse_id, count in mice.items():
        if count > 0 and mouse_id in MICE_DATA:
            data = MICE_DATA[mouse_id]
            income = data['income'] * count
            total_income += income
            
            last_collect = user.get('mice_last_collect', {}).get(mouse_id, now)
            time_passed = now - last_collect
            hours_passed = time_passed / 3600
            pending = int(income * hours_passed)
            
            text += (
                f"{data['icon']} {data['name']} — {count} шт.\n"
                f"   💵 Доход в час: +{format_number(income)} кредиксов\n"
                f"   ⏳ Накоплено: +{format_number(pending)} кредиксов\n\n"
            )
    
    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Общий доход в час: +{format_number(total_income)} кредиксов\n"
        f"💎 Баланс KRDS: {user['krds_balance']}\n"
        f"💸 Кредиксы: {format_number(user['balance'])}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Собрать доход: /собратьмыши"
    )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['собратьмыши'])
def collect_mice_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    mice = user.get('mice', {})
    
    if not mice:
        bot.send_message(message.chat.id, 
            "🐭 У тебя нет мышек! Купи в магазине: /мышки")
        return
    
    now = time.time()
    total_collected = 0
    collected_text = []
    
    with get_user_lock(user_id):
        for mouse_id, count in mice.items():
            if count > 0 and mouse_id in MICE_DATA:
                data = MICE_DATA[mouse_id]
                last_collect = user.get('mice_last_collect', {}).get(mouse_id, now)
                time_passed = now - last_collect
                hours_passed = time_passed / 3600
                income = data['income'] * count
                earned = int(income * hours_passed)
                
                if earned > 0:
                    total_collected += earned
                    if 'mice_last_collect' not in user:
                        user['mice_last_collect'] = {}
                    user['mice_last_collect'][mouse_id] = now
                    collected_text.append(f"{data['icon']} {data['name']}: +{format_number(earned)}")
        
        if total_collected > 0:
            user['balance'] += total_collected
            save_data()
    
    if total_collected > 0:
        text = (
            f"✅ ** СБОР ДОХОДА ** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{chr(10).join(collected_text)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Всего собрано: +{format_number(total_collected)} кредиксов\n"
            f"💸 Новый баланс: {format_number(user['balance'])} кредиксов"
        )
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, 
            "⏳ Доход ещё не накопился! Приходи через час.")

# ====================== ОБМЕННИК KRDS (P2P) ======================
@bot.message_handler(commands=['обменник'])
def exchange_menu(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    text = (
        "💱 ** P2P ОБМЕННИК KRDS ** 💱\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 Ты можешь продавать KRDS другим игрокам\n"
        "💰 Цену за 1 KRDS устанавливаешь сам (от 1000 до 100000)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 ** Доступные команды: **\n\n"
        "➤ /продатькрдс [количество] [цена] — выставить на продажу\n"
        "   Пример: /продатькрдс 10 5000\n\n"
        "➤ /моиордера — мои активные ордера\n\n"
        "➤ /ордера — все активные ордера на продажу\n\n"
        "➤ /купить [ID ордера] [количество] — купить KRDS\n"
        "   Пример: /купить 5 3\n\n"
        "➤ /отменитьордер [ID] — отменить свой ордер\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 Твой баланс KRDS: {user['krds_balance']}\n"
        f"💰 Твой баланс кредиксов: {format_number(user['balance'])}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['продатькрдс'])
def sell_krds_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    global next_order_id
    args = message.text.split()
    
    if len(args) != 3:
        bot.send_message(message.chat.id, 
            "❌ Использование: /продатькрдс [количество] [цена за 1 KRDS]\n"
            "Пример: /продатькрдс 10 5000")
        return
    
    try:
        amount = int(args[1])
        price_per_one = int(args[2])
        
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Количество должно быть положительным!")
            return
        
        if price_per_one < 1000 or price_per_one > 100000:
            bot.send_message(message.chat.id, 
                "❌ Цена за 1 KRDS должна быть от 1000 до 100000 кредиксов!")
            return
        
        user = get_user(user_id)
        if user['krds_balance'] < amount:
            bot.send_message(message.chat.id, 
                f"❌ Недостаточно KRDS! У тебя {user['krds_balance']}")
            return
        
        with data_lock:
            order_id = str(next_order_id)
            next_order_id += 1
            
            orders[order_id] = {
                'user_id': user_id,
                'type': 'sell',
                'price_per_one': price_per_one,
                'amount': amount,
                'remaining': amount,
                'created': time.time()
            }
            save_data()
        
        text = (
            f"✅ ** ОРДЕР СОЗДАН! ** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 ID ордера: #{order_id}\n"
            f"💎 Продажа: {amount} KRDS\n"
            f"💰 Цена за 1 KRDS: {price_per_one} кредиксов\n"
            f"💵 Общая стоимость: {format_number(price_per_one * amount)} кредиксов\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Другие игроки могут купить по команде:\n"
            f"/купить {order_id} [количество]"
        )
        bot.send_message(message.chat.id, text)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите числа!")

@bot.message_handler(commands=['продать'])
def sell_to_bot_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, 
            "❌ Использование: /продать [количество]\n"
            "Пример: /продать 10\n"
            "💰 Цена: 3250 кредиксов за 1 KRDS")
        return
    
    try:
        amount = int(args[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Количество должно быть положительным!")
            return
        
        user = get_user(user_id)
        if user['krds_balance'] < amount:
            bot.send_message(message.chat.id, 
                f"❌ Недостаточно KRDS! У тебя {user['krds_balance']}")
            return
        
        with get_user_lock(user_id):
            price_per_one = 3250
            total = amount * price_per_one
            
            user['krds_balance'] -= amount
            user['balance'] += total
            save_data()
        
        text = (
            f"✅ ** ПРОДАЖА БОТУ ** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💎 Продано: {amount} KRDS\n"
            f"💰 Цена: {price_per_one} кредиксов/шт\n"
            f"💵 Получено: {format_number(total)} кредиксов\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 Новый баланс KRDS: {user['krds_balance']}\n"
            f"💰 Новый баланс кредиксов: {format_number(user['balance'])}"
        )
        bot.send_message(message.chat.id, text)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")

@bot.message_handler(commands=['моиордера'])
def my_orders_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    with data_lock:
        my_orders = []
        for oid, order in orders.items():
            if order.get('user_id') == user_id and order.get('remaining', 0) > 0:
                my_orders.append((oid, order))
    
    if not my_orders:
        bot.send_message(message.chat.id, "📋 У тебя нет активных ордеров.")
        return
    
    text = "📋 ** МОИ ОРДЕРА ** 📋\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for oid, order in my_orders:
        total_price = order['price_per_one'] * order['remaining']
        text += (
            f"🆔 #{oid}\n"
            f"   💎 Продажа: {order['remaining']}/{order['amount']} KRDS\n"
            f"   💰 Цена за 1: {order['price_per_one']} кредиксов\n"
            f"   💵 Общая стоимость: {format_number(total_price)} кредиксов\n"
            f"   ⏱ Создан: {datetime.fromtimestamp(order['created']).strftime('%d.%m %H:%M')}\n\n"
        )
    text += "━━━━━━━━━━━━━━━━━━━━━━\nОтменить: /отменитьордер [ID]"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['ордера'])
def all_orders_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    with data_lock:
        active_orders = {oid: o for oid, o in orders.items() if o.get('remaining', 0) > 0}
    
    if not active_orders:
        bot.send_message(message.chat.id, "📊 Нет активных ордеров на продажу.")
        return
    
    text = "📊 ** ВСЕ ОРДЕРА НА ПРОДАЖУ ** 📊\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for oid, order in active_orders.items():
        try:
            seller = bot.get_chat(int(order['user_id']))
            seller_name = f"@{seller.username}" if seller.username else seller.first_name
        except:
            seller_name = f"ID {order['user_id']}"
        
        total_price = order['price_per_one'] * order['remaining']
        text += (
            f"🆔 #{oid}\n"
            f"   👤 Продавец: {seller_name}\n"
            f"   💎 В наличии: {order['remaining']}/{order['amount']} KRDS\n"
            f"   💰 Цена за 1: {order['price_per_one']} кредиксов\n"
            f"   💵 Общая стоимость: {format_number(total_price)} кредиксов\n"
            f"   ⏱ Создан: {datetime.fromtimestamp(order['created']).strftime('%d.%m %H:%M')}\n\n"
        )
    text += "━━━━━━━━━━━━━━━━━━━━━━\nКупить: /купить [ID ордера] [количество]"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купить'])
def buy_krds_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, 
            "❌ Использование: /купить [ID ордера] [количество]\n"
            "Пример: /купить 5 3")
        return
    
    order_id = args[1]
    try:
        amount = int(args[2])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Количество должно быть положительным!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    with data_lock:
        if order_id not in orders:
            bot.send_message(message.chat.id, "❌ Ордер не найден!")
            return
        
        order = orders[order_id]
        if order.get('remaining', 0) <= 0:
            bot.send_message(message.chat.id, "❌ Ордер уже исполнен!")
            return
        
        if order['user_id'] == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя купить у самого себя!")
            return
        
        if amount > order['remaining']:
            bot.send_message(message.chat.id, 
                f"❌ Доступно только {order['remaining']} KRDS!")
            return
        
        buyer = get_user(user_id)
        seller = get_user(order['user_id'])
        
        total_cost = order['price_per_one'] * amount
        
        if buyer['balance'] < total_cost:
            bot.send_message(message.chat.id, 
                f"❌ Недостаточно кредиксов! Нужно: {format_number(total_cost)}")
            return
        
        if seller['krds_balance'] < amount:
            bot.send_message(message.chat.id, 
                "❌ У продавца недостаточно KRDS! Ордер будет удалён.")
            del orders[order_id]
            save_data()
            return
        
        # Используем упорядоченные блокировки
        lock1, lock2 = get_locks_sorted(user_id, order['user_id'])
        with lock1, lock2:
            buyer['balance'] -= total_cost
            seller['balance'] += total_cost
            buyer['krds_balance'] += amount
            seller['krds_balance'] -= amount
            
            order['remaining'] -= amount
            if order['remaining'] == 0:
                del orders[order_id]
            
            save_data()
    
    buyer_text = (
        f"✅ ** ПОКУПКА УСПЕШНА! ** ✅\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 Куплено: {amount} KRDS\n"
        f"💰 Цена за 1: {order['price_per_one']} кредиксов\n"
        f"💵 Заплачено: {format_number(total_cost)} кредиксов\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 Новый баланс KRDS: {buyer['krds_balance']}\n"
        f"💰 Новый баланс кредиксов: {format_number(buyer['balance'])}"
    )
    bot.send_message(message.chat.id, buyer_text)
    
    try:
        seller_text = (
            f"💰 ** ПРОДАЖА! ** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎉 Твой ордер #{order_id}:\n"
            f"💎 Продано: {amount} KRDS\n"
            f"💰 Цена за 1: {order['price_per_one']} кредиксов\n"
            f"💵 Получено: {format_number(total_cost)} кредиксов\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 Новый баланс KRDS: {seller['krds_balance']}\n"
            f"💰 Новый баланс кредиксов: {format_number(seller['balance'])}"
        )
        bot.send_message(int(order['user_id']), seller_text)
    except:
        pass

@bot.message_handler(commands=['отменитьордер'])
def cancel_order_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /отменитьордер [ID]")
        return
    
    order_id = args[1]
    
    with data_lock:
        if order_id not in orders:
            bot.send_message(message.chat.id, "❌ Ордер не найден!")
            return
        
        order = orders[order_id]
        if order['user_id'] != user_id:
            bot.send_message(message.chat.id, "❌ Это не твой ордер!")
            return
        
        del orders[order_id]
        save_data()
    
    bot.send_message(message.chat.id, f"✅ Ордер #{order_id} отменён!")

# ====================== ПРОМОКОДЫ ======================
@bot.message_handler(commands=['createpromo'])
def create_promo_command(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора!")
        return
    
    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, 
            "❌ Использование: /createpromo [сумма] [количество] [текст]\n"
            "Пример: /createpromo 10000 5 LUCKY")
        return
    
    try:
        amount = int(args[1])
        uses = int(args[2])
        if amount <= 0 or uses <= 0:
            bot.send_message(message.chat.id, 
                "❌ Сумма и количество должны быть положительными!")
            return
        
        with data_lock:
            if len(args) >= 4:
                promo_text = args[3].upper()
                if promo_text in promocodes:
                    bot.send_message(message.chat.id, 
                        "❌ Промокод с таким текстом уже существует!")
                    return
                code = promo_text
            else:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                while code in promocodes:
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            promocodes[code] = {
                'amount': amount,
                'uses': uses,
                'used': 0,
                'created_by': user_id,
                'created': time.time()
            }
            save_data()
        
        text = (
            f"🎟 ** ПРОМОКОД СОЗДАН! ** 🎟\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Код: {code}\n"
            f"💰 Сумма: {format_number(amount)} кредиксов\n"
            f"📊 Количество активаций: {uses}\n"
            f"⏱ Создан: {datetime.fromtimestamp(time.time()).strftime('%d.%m %H:%M')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Активировать: /promo {code}"
        )
        bot.send_message(message.chat.id, text)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите числа!")

@bot.message_handler(commands=['promo'])
def promo_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /promo [код]")
        return
    
    code = args[1].upper()
    
    with data_lock:
        if code not in promocodes:
            bot.send_message(message.chat.id, "❌ Промокод не найден!")
            return
        
        user = get_user(user_id)
        promo = promocodes[code]
        
        if code in user.get('used_promos', []):
            bot.send_message(message.chat.id, "❌ Ты уже активировал этот промокод!")
            return
        
        if promo['used'] >= promo['uses']:
            bot.send_message(message.chat.id, 
                "❌ Промокод больше недействителен (истекло количество активаций)!")
            return
        
        with get_user_lock(user_id):
            user['balance'] += promo['amount']
            if 'used_promos' not in user:
                user['used_promos'] = []
            user['used_promos'].append(code)
            promo['used'] += 1
            
            if promo['used'] >= promo['uses']:
                del promocodes[code]
            
            save_data()
    
    text = (
        f"🎁 ** ПРОМОКОД АКТИВИРОВАН! ** 🎁\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Ты получил: +{format_number(promo['amount'])} кредиксов\n"
        f"💰 Новый баланс: {format_number(user['balance'])} кредиксов\n"
        f"📊 Осталось активаций: {promo['uses'] - promo['used']}"
    )
    bot.send_message(message.chat.id, text)

# ====================== РЕФЕРАЛЬНАЯ СИСТЕМА ======================
@bot.message_handler(commands=['реф'])
def ref_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    user = get_user(user_id)
    
    text = (
        "👥 ** РЕФЕРАЛЬНАЯ СИСТЕМА ** 👥\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 Твоя ссылка:\n{ref_link}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Приглашено друзей: {user.get('referrals', 0)}\n\n"
        "🎁 ** Награда за друга: **\n"
        f"💰 +{format_number(bonus_data['referral_bonus'])} кредиксов\n"
        "💎 +5 KRDS\n\n"
        "🏆 ** Достижения: **\n"
        "▸ 10 друзей: +100,000 кредиксов\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Отправь ссылку друзьям и получай бонусы!"
    )
    bot.send_message(message.chat.id, text)

# ====================== БАЗОВЫЕ КОМАНДЫ ======================
@bot.message_handler(commands=['помощь', 'help'])
def help_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    text = (
        "📚 ** ПОМОЩЬ ПО БОТУ ** 📚\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎮 ** ИГРЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏰 Башня: башня [ставка]\n"
        "⚽ Футбол: футбол [ставка] [гол/мимо]\n"
        "🏀 Баскетбол: баскетбол [ставка] [гол/мимо]\n"
        "🔺 Пирамида: пирамида [ставка]\n"
        "💣 Мины: мины [ставка]\n"
        "🎰 Джекпот: джекпот [ставка]\n"
        "⚫️⚪️ Фишки: фишки [ставка] [black/white]\n"
        "🎲 x2/x3/x5: x2/x3/x5 [ставка]\n"
        "🔫 Русская рулетка: рулетка_рус [ставка]\n"
        "🃏 Очко: очко [ставка]\n"
        "🚀 Краш: краш [ставка]\n"
        "🎰 Слоты: слоты [ставка]\n"
        "🎲 Кости: кости [ставка] [больше/меньше] (всегда 6, множитель 1.8)\n"
        "🎰 Рулетка: рулетка_каз [ставка] [тип] [число]\n"
        "📈 Хило: хило [ставка]\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 ** KRDS СИСТЕМА **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/донат - баланс KRDS\n"
        "/сенд @ник сумма - отправить KRDS\n"
        "/продать количество - продать боту (3250/шт)\n"
        "/обменник - P2P обменник\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🐭 ** МЫШКИ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/мышки - магазин мышек\n"
        "/купитьмышку [тип] - купить мышку\n"
        "/мыши - мои мышки\n"
        "/собратьмыши - собрать доход\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏦 ** БАНК **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/банк - банковские операции\n"
        "/депозит [сумма] - положить под 5%\n"
        "/снять [сумма] - снять с депозита\n"
        "/кредит [сумма] - взять кредит\n"
        "/выплатить [сумма] - выплатить кредит\n"
        "/проценты - начислить проценты\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 ** ТЕЛЕФОН **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/телефон - твой номер\n"
        "/контакты - список контактов\n"
        "/добавить @ник - добавить контакт\n"
        "/позвонить @ник - позвонить\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎁 ** БОНУСЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/бонус - информация о бонусах\n"
        "/daily - ежедневный бонус\n"
        "/weekly - еженедельный бонус\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🐾 ** ПИТОМЦЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/питомцы - мои питомцы\n"
        "/магазинпитомцев - купить питомца\n"
        "/купитьпитомца [тип] - купить\n"
        "/покормить [тип] - покормить\n"
        "/собратьпитомцы - собрать доход\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏢 ** БИЗНЕС **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/бизнес - мой бизнес\n"
        "/магазинбизнеса - купить бизнес\n"
        "/купитьбизнес [тип] - купить\n"
        "/улучшить [тип] - улучшить\n"
        "/собратьбизнес - собрать доход\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 ** КЛАНЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/клан - информация\n"
        "/создатьклан [название] - создать клан\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💼 ** ЭКОНОМИКА **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/работа - +55 кредиксов\n"
        "/дать @ник сумма - перевод\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 ** СОЦИАЛ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "/реф - реферальная ссылка\n"
        "/топ - топ игроков\n"
        "/профиль - профиль\n"
        "/cancel - отменить игру\n"
        "/помощь - это меню\n"
    )
    bot.send_message(message.chat.id, text)

# ====================== ИЗМЕНЁННАЯ КОМАНДА /баланс ======================
@bot.message_handler(commands=['баланс'])
def balance_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return

    user = get_user(user_id)
    try:
        chat = bot.get_chat(int(user_id))
        name = chat.first_name
    except:
        name = "Игрок"

    text = (
        f"💰 {name} 💰\n"
        f"💲Твой баланс: {format_number(user['balance'])} кредиксов💲\n"
        f"⚡krds: {user['krds_balance']}⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎰 Проиграно: {format_number(user.get('total_lost', 0))}\n"
        f"☃️выиграно: {user.get('total_wins', 0)}☃️\n"
        f"💖сыграно игр: {user.get('games_played', 0)}💖\n"
        f"~~~~~~~~~~~~~~~~~~~~~~~~"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['профиль'])
def profile_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    
    clan_name = "Нет клана"
    if user.get('clan') and user['clan'] in clans:
        clan_name = clans[user['clan']]['name']
    
    deposit = user.get('bank_deposit', {}).get('amount', 0)
    loan = user.get('bank_loan', {}).get('amount', 0)
    
    text = (
        f"📱 ** ПРОФИЛЬ ** 📱\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 ID: {user_id}\n\n"
        f"💰 ** ФИНАНСЫ **\n"
        f"💸 Кредиксы: {format_number(user['balance'])}\n"
        f"💎 KRDS: {user['krds_balance']}\n"
        f"🏦 Депозит: {format_number(deposit)}\n"
        f"📉 Кредит: {format_number(loan)}\n\n"
        f"📊 ** СТАТИСТИКА ИГР **\n"
        f"🎮 Сыграно: {user.get('games_played', 0)}\n"
        f"✅ Побед: {user.get('total_wins', 0)}\n"
        f"❌ Поражений: {user.get('total_losses', 0)}\n"
        f"🔥 Стрик: {user.get('win_streak', 0)}\n\n"
        f"🐭 ** МЫШКИ **\n"
        f"Всего: {sum(user.get('mice', {}).values())} шт.\n"
        f"Доход в час: {sum(MICE_DATA[m]['income'] * count for m, count in user.get('mice', {}).items() if m in MICE_DATA)}\n\n"
        f"🐾 ** ПИТОМЦЫ **\n"
        f"Всего: {len(user.get('pets', {}))} шт.\n\n"
        f"🏪 ** БИЗНЕС **\n"
        f"Всего: {len(user.get('businesses', {}))} шт.\n\n"
        f"👥 ** СОЦИАЛ **\n"
        f"👥 Рефералов: {user.get('referrals', 0)}\n"
        f"👑 Клан: {clan_name}\n"
        f"💼 Работ: {user.get('work_count', 0)}\n\n"
        f"📱 ** ТЕЛЕФОН **\n"
        f"📞 Номер: {user.get('phone_number', 'Нет номера')}\n"
        f"👥 Контактов: {len(user.get('phone_contacts', []))}\n\n"
        f"🎁 ** БОНУСЫ **\n"
        f"📅 Дейли стрик: {user.get('daily_bonus', {}).get('streak', 0)} дней\n"
        f"📆 Викли стрик: {user.get('weekly_bonus', {}).get('streak', 0)} недель\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['топ'])
def top_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    with data_lock:
        users_list = [(uid, data) for uid, data in users.items()]
        sorted_users = sorted(users_list, key=lambda x: x[1].get('balance', 0), reverse=True)[:15]
    
    if not sorted_users:
        bot.send_message(message.chat.id, "📊 Пока нет пользователей в топе.")
        return
    
    text = "🏆 ** ТОП 15 ИГРОКОВ ** 🏆\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        try:
            user = bot.get_chat(int(uid))
            name = f"@{user.username}" if user.username else user.first_name
        except:
            name = f"ID {uid}"
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        mice_count = sum(data.get('mice', {}).values())
        pets_count = len(data.get('pets', {}))
        businesses_count = len(data.get('businesses', {}))
        
        text += (
            f"{medal} {name}\n"
            f"   💰 {format_number(data.get('balance', 0))} кредиксов\n"
            f"   💎 {data.get('krds_balance', 0)} KRDS\n"
            f"   🐭 {mice_count} мышек | 🐾 {pets_count} питомцев | 🏪 {businesses_count} бизнесов\n\n"
        )
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['донат'])
def donate_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    user = get_user(user_id)
    bot.send_message(message.chat.id, f"💎 Твой баланс KRDS: {user['krds_balance']}")

@bot.message_handler(commands=['сенд'])
def send_krds_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "❌ Использование: /сенд @ник сумма")
        return
    
    target_username = args[1].replace('@', '').lower()
    try:
        amount = int(args[2])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    with data_lock:
        target_id = username_cache.get(target_username)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        if target_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя отправить самому себе!")
            return
        
        user = get_user(user_id)
        if user['krds_balance'] < amount:
            bot.send_message(message.chat.id, 
                f"❌ Недостаточно KRDS! У тебя {user['krds_balance']}")
            return
        
        lock1, lock2 = get_locks_sorted(user_id, target_id)
        with lock1, lock2:
            target = get_user(target_id)
            user['krds_balance'] -= amount
            target['krds_balance'] += amount
            save_data()
    
    sender_name = f"@{message.from_user.username}" if message.from_user.username else f"ID {message.from_user.id}"
    
    bot.send_message(message.chat.id, 
        f"✅ Ты отправил {amount} KRDS пользователю @{target_username}")
    
    try:
        bot.send_message(int(target_id), 
            f"💰 ** ПОЛУЧЕНО KRDS! ** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 Отправитель: {sender_name}\n"
            f"💎 Сумма: +{amount} KRDS\n"
            f"💎 Новый баланс: {target['krds_balance']} KRDS")
    except:
        pass

@bot.message_handler(commands=['дать'])
def give_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "❌ Использование: /дать @ник сумма")
        return
    
    target_username = args[1].replace('@', '').lower()
    try:
        amount = int(args[2])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    
    with data_lock:
        target_id = username_cache.get(target_username)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
            return
        
        if target_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя перевести самому себе!")
            return
        
        user = get_user(user_id)
        if user['balance'] < amount:
            bot.send_message(message.chat.id, 
                f"❌ Недостаточно средств! Твой баланс: {format_number(user['balance'])}")
            return
        
        lock1, lock2 = get_locks_sorted(user_id, target_id)
        with lock1, lock2:
            target = get_user(target_id)
            user['balance'] -= amount
            target['balance'] += amount
            save_data()
    
    sender_name = f"@{message.from_user.username}" if message.from_user.username else f"ID {message.from_user.id}"
    
    bot.send_message(message.chat.id, 
        f"✅ Ты перевёл {format_number(amount)} кредиксов пользователю @{target_username}\n"
        f"💰 Новый баланс: {format_number(user['balance'])}")
    
    try:
        bot.send_message(int(target_id), 
            f"💰 ** ПОЛУЧЕНО! ** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 Отправитель: {sender_name}\n"
            f"💸 Сумма: +{format_number(amount)} кредиксов\n"
            f"💰 Новый баланс: {format_number(target['balance'])}")
    except:
        pass

@bot.message_handler(commands=['игры'])
def games_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    text = (
        "🎮 ** СПИСОК ИГР ** 🎮\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏰 Башня: башня [ставка]\n"
        "⚽ Футбол: футбол [ставка] [гол/мимо]\n"
        "🏀 Баскетбол: баскетбол [ставка] [гол/мимо]\n"
        "🔺 Пирамида: пирамида [ставка]\n"
        "💣 Мины: мины [ставка]\n"
        "🎰 Джекпот: джекпот [ставка]\n"
        "⚫️⚪️ Фишки: фишки [ставка] [black/white]\n"
        "🎲 x2/x3/x5: x2/x3/x5 [ставка]\n"
        "🔫 Русская рулетка: рулетка_рус [ставка]\n"
        "🃏 Очко: очко [ставка]\n"
        "🚀 Краш: краш [ставка]\n"
        "🎰 Слоты: слоты [ставка]\n"
        "🎲 Кости: кости [ставка] [больше/меньше] (всегда 6, множитель 1.8)\n"
        "🎰 Рулетка: рулетка_каз [ставка] [тип] [число]\n"
        "📈 Хило: хило [ставка]\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛑 Отмена игры: /cancel"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['cancel'])
def cancel_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    if cancel_user_game(user_id):
        bot.send_message(message.chat.id, "🛑 Игра отменена. Ставка возвращена.")
    else:
        bot.send_message(message.chat.id, "❌ У тебя нет активной игры.")

# ====================== ИГРА: КОСТИ ======================
def dice_game_command(message):
    """Обработчик для игры в кости (без слэша)"""
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    parts = message.text.lower().split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: кости [ставка] [больше/меньше]")
        return
    
    bet = parse_bet(parts[1])
    bet_type = parts[2]
    
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
        return
    
    if bet_type not in ('больше', 'меньше'):
        bot.send_message(message.chat.id, "❌ Выбери 'больше' или 'меньше'")
        return
    
    user = get_user(user_id)
    
    if user['balance'] < bet:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}")
        return
    
    if user.get('game') is not None:
        bot.send_message(message.chat.id, "❌ У тебя уже есть активная игра! Закончи её или отмени (/cancel)")
        return
    
    with get_user_lock(user_id):
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        
        if bet_type == 'больше':
            won = total > 6
        else:
            won = total < 6
        
        if won:
            win_amount = int(bet * 1.8 * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🎲 ** КОСТИ ** 🎲\n\n"
                f"Кости: {dice1} + {dice2} = {total}\n"
                f"Твоя ставка: {bet_type} 6\n\n"
                f"✅ ВЫИГРЫШ: x1.8\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🎲 ** КОСТИ ** 🎲\n\n"
                f"Кости: {dice1} + {dice2} = {total}\n"
                f"Твоя ставка: {bet_type} 6\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        
        save_data()
    
    bot.send_message(message.chat.id, text)

# ====================== ИГРОВОЙ ХЕНДЛЕР (ДЛЯ ТЕКСТОВЫХ КОМАНД) ======================
def game_handler(message):
    """Обрабатывает текстовые сообщения, начинающиеся с названия игры."""
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    parts = message.text.lower().split()
    game = parts[0]
    
    # TODO: реализовать остальные игры по аналогии с dice_game_command
    if game == 'кости':
        dice_game_command(message)
    else:
        # Игра не реализована, просто игнорируем (можно добавить ответ позже)
        pass

# ====================== ОБРАБОТЧИК ЗАВЕРШЕНИЯ ======================
def signal_handler(signum, frame):
    print("\n" + "="*50)
    print("⏳ Завершение работы бота...")
    cleanup_all_timers()
    save_data()
    print("✅ Данные сохранены")
    print("👋 Бот остановлен")
    print("="*50)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ====================== ЗАПУСК БОТА ======================
if __name__ == '__main__':
    load_data()
    
    # Получаем ID владельца и устанавливаем ему роль coder
    try:
        owner_chat = bot.get_chat(f"@{OWNER_USERNAME[1:]}")  # убираем @
        OWNER_ID = str(owner_chat.id)
        with data_lock:
            if OWNER_ID in users:
                users[OWNER_ID]['role'] = 'coder'
            else:
                # Создаём пользователя с ролью
                users[OWNER_ID] = get_user(OWNER_ID)
                users[OWNER_ID]['role'] = 'coder'
            save_data()
        print(f"👑 Владелец {OWNER_USERNAME} (ID: {OWNER_ID}) получил роль кодера.")
    except Exception as e:
        print(f"⚠️ Не удалось получить ID владельца: {e}")
        OWNER_ID = None
    
    # Запускаем фоновый поток для бонусов тестерам
    tester_thread = Thread(target=give_tester_bonus, daemon=True)
    tester_thread.start()
    
    print("=" * 60)
    print("✅ БОТ КАЗИНО ЗАПУЩЕН!")
    print("=" * 60)
    print("📋 СИСТЕМЫ:")
    print("  • 🐭 Мышки (пассивный доход)")
    print("  • 🐾 Питомцы (кормление, счастье)")
    print("  • 🏪 Бизнесы (покупка, улучшение)")
    print("  • 👥 Кланы (создание, управление)")
    print("  • 🏦 Банк (депозиты, кредиты)")
    print("  • 📱 Телефон (контакты, звонки)")
    print("  • 🎁 Бонусы (ежедневные, еженедельные)")
    print("  • 💎 KRDS (P2P обменник)")
    print("  • 👑 VIP-роли (админ, тестер, хелпер, кодер)")
    print("=" * 60)
    print("🎮 ИГРЫ:")
    print("  • Кости (реализована)")
    print("  • Остальные игры требуют доработки (помечены TODO)")
    print("=" * 60)
    print("🔑 АДМИН ПАНЕЛЬ: /Admin Kyniksvs1832")
    print("=" * 60)
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        cleanup_all_timers()
        save_data()