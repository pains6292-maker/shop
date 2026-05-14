import json
import os
import telebot
from telebot import types
from telebot.types import MessageEntity

TOKEN = '8790777836:AAHAaqO1Ly4oD4Gpy30jiFDvRQ6rvCmwwWo'
bot = telebot.TeleBot(TOKEN)

# ==================== Настройки Админа ====================
ADMIN_IDS = [7974493661] # Ваш Telegram ID

DATA_FILE = 'shop_data.json'

# Базовые товары
products_availability = {
    'google_ai_pro': True,
    'google_ai_ultra': True
}

custom_products = {}
custom_product_counter = 0
payment_methods = {}

# Раздел "Халява"
freebie_items = {}
freebie_counter = 0
freebies_enabled = True # Флаг отображения кнопки Халява в главном меню

# Режим технического обслуживания и Режим Призрака
maintenance_mode = False
ghost_mode = True # По умолчанию админ-призрак включен

# Отслеживание активных сообщений бота для зачистки чата { "chat_id": message_id }
active_bot_messages = {}

# ==================== Заводские настройки дизайна ====================
DEFAULT_UI_TEXTS = {
    'welcome': {
        'text': "добро пожаловать в cryrae shop ✨", 
        'entities': [MessageEntity(type="custom_emoji", offset=31, length=1, custom_emoji_id="5429541997398486546")]
    },
    'browse_title': {'text': "🛍️ Наши товары", 'entities': None},
    'how_it_works': {
        'text': "❓ *Как работает наш магазин:*\n\n1. Выберите нужный товар и срок подписки.\n2. Нажмите кнопку оплаты и переведите сумму по указанным реквизитам.\n3. После оплаты ваша заявка будет моментально обработана.\n\n✨ *Всё просто и безопасно!*", 
        'entities': None
    },
    'freebies': {
        'text': "🎁 *Халява и бонусы*\n\nЗдесь публикуются актуальные промокоды, скидки и информация о бесплатных раздачах.\n\nВыберите интересующий вас бонус ниже:",
        'entities': None
    }
}

DEFAULT_UI_BUTTONS = {
    'browse': "🛍️ Наши товары",
    'how_it_works': "❓ Как это работает",
    'freebies': "🎁 Халява"
}

DEFAULT_PRODUCT_TEXTS = {
    '18_months': {'text': "google ai pro на 18 месяцев\n\nполучи доступ к :\n\npro версиям gemini\n5тб облачной памяти\nгенерируй видео с veo3 ( 1000 кредитов ежемесячно )\nгенерируй музыку и изучай новые темы в приложении Gemini.\n\nстоимость : 500.000 сум\nгарантия - 6 месяцев", 'entities': None},
    '12_months': {'text': "google ai pro на 12 месяцев\n\nполучи доступ к :\n\npro версиям gemini\n5тб облачной памяти\nгенерируй видео с veo3 ( 1000 кредитов ежемесячно )\nгенерируй музыку и изучай новые темы в приложении Gemini.\n\nстоимость : 250.000 сум\nгарантия - 6 месяцев", 'entities': None},
    '4_months': {'text': "google ai pro на 4 месяца\n\nполучи доступ к :\n\npro версиям gemini\n5тб облачной памяти\nгенерируй видео с veo3 ( 1000 кредитов ежемесячно )\nгенерируй музыку и изучай новые темы в приложении Gemini.\n\nстоимость : 110.000 сум\nгарантия - все 4 месяца", 'entities': None},
    '1_month_ultra': {'text': "google ai ultra на 1 месяц\n\nполучи доступ к :\n\npro версиям gemini\n5тб облачной памяти\nгенерируй видео с veo3 ( 25000 кредитов ежемесячно )\nгенерируй музыку и изучай новые темы в приложении Gemini.\n\nстоимость : 250.000 сум\nгарантия - весь 1 месяц", 'entities': None}
}

# Текущий дизайн при старте
ui_texts = {k: {'text': v['text'], 'entities': v['entities']} for k, v in DEFAULT_UI_TEXTS.items()}
ui_buttons = DEFAULT_UI_BUTTONS.copy()
product_texts = {k: {'text': v['text'], 'entities': v['entities']} for k, v in DEFAULT_PRODUCT_TEXTS.items()}


# ==================== Логика Сохранения и Загрузки (JSON) ====================
def serialize_entities(entities):
    if not entities:
        return None
    res = []
    for e in entities:
        res.append({
            'type': e.type,
            'offset': e.offset,
            'length': e.length,
            'url': e.url,
            'language': e.language,
            'custom_emoji_id': e.custom_emoji_id
        })
    return res

def deserialize_entities(data_list):
    if not data_list:
        return None
    res = []
    for d in data_list:
        res.append(MessageEntity(
            type=d.get('type'),
            offset=d.get('offset'),
            length=d.get('length'),
            url=d.get('url'),
            user=None,
            language=d.get('language'),
            custom_emoji_id=d.get('custom_emoji_id')
        ))
    return res

def save_data():
    data = {
        'products_availability': products_availability,
        'custom_product_counter': custom_product_counter,
        'payment_methods': payment_methods,
        'ui_buttons': ui_buttons,
        'active_bot_messages': active_bot_messages,
        'freebie_counter': freebie_counter,
        'freebies_enabled': freebies_enabled,
        'maintenance_mode': maintenance_mode,
        'ghost_mode': ghost_mode,
        'ui_texts': {},
        'product_texts': {},
        'custom_products': {},
        'freebie_items': {}
    }
    
    for k, v in ui_texts.items():
        data['ui_texts'][k] = {'text': v['text'], 'entities': serialize_entities(v['entities'])}
        
    for k, v in product_texts.items():
        data['product_texts'][k] = {'text': v['text'], 'entities': serialize_entities(v['entities'])}
        
    for k, v in custom_products.items():
        data['custom_products'][k] = {
            'name': v['name'],
            'active': v['active'],
            'desc': {'text': v['desc']['text'], 'entities': serialize_entities(v['desc']['entities'])}
        }
        
    for k, v in freebie_items.items():
        data['freebie_items'][k] = {
            'name': v['name'],
            'desc': {'text': v['desc']['text'], 'entities': serialize_entities(v['desc']['entities'])}
        }
        
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    global products_availability, custom_product_counter, payment_methods
    global ui_buttons, ui_texts, product_texts, custom_products, active_bot_messages
    global freebie_items, freebie_counter, freebies_enabled, maintenance_mode, ghost_mode
    
    if not os.path.exists(DATA_FILE):
        return
        
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        products_availability.update(data.get('products_availability', {}))
        custom_product_counter = data.get('custom_product_counter', 0)
        freebie_counter = data.get('freebie_counter', 0)
        freebies_enabled = data.get('freebies_enabled', True)
        maintenance_mode = data.get('maintenance_mode', False)
        ghost_mode = data.get('ghost_mode', True)
        payment_methods.update(data.get('payment_methods', {}))
        ui_buttons.update(data.get('ui_buttons', {}))
        active_bot_messages.update(data.get('active_bot_messages', {}))
        
        if 'ui_texts' in data:
            for k, v in data['ui_texts'].items():
                ui_texts[k] = {'text': v['text'], 'entities': deserialize_entities(v['entities'])}
                
        if 'product_texts' in data:
            for k, v in data['product_texts'].items():
                product_texts[k] = {'text': v['text'], 'entities': deserialize_entities(v['entities'])}
                
        if 'custom_products' in data:
            custom_products.clear()
            for k, v in data['custom_products'].items():
                custom_products[k] = {
                    'name': v['name'],
                    'active': v['active'],
                    'desc': {'text': v['desc']['text'], 'entities': deserialize_entities(v['desc']['entities'])}
                }
                
        if 'freebie_items' in data:
            freebie_items.clear()
            for k, v in data['freebie_items'].items():
                freebie_items[k] = {
                    'name': v['name'],
                    'desc': {'text': v['desc']['text'], 'entities': deserialize_entities(v['desc']['entities'])}
                }
        print("База данных успешно загружена!")
    except Exception as e:
        print(f"Ошибка при загрузке базы: {e}")

load_data()


# ==================== Функция чистой отправки (Single Message) ====================
def send_clean_message(chat_id, text, reply_markup=None, entities=None, parse_mode=None):
    chat_str = str(chat_id)
    
    if chat_str in active_bot_messages:
        try:
            bot.delete_message(chat_id, active_bot_messages[chat_str])
        except Exception:
            pass

    msg = bot.send_message(chat_id, text, reply_markup=reply_markup, entities=entities, parse_mode=parse_mode)
    active_bot_messages[chat_str] = msg.message_id
    save_data()
    return msg

def delete_user_message(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass


# ==================== Вспомогательные функции ====================
def get_main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(ui_buttons['browse'], callback_data='browse'),
        types.InlineKeyboardButton(ui_buttons['how_it_works'], callback_data='how_it_works')
    )
    if freebies_enabled:
        markup.add(types.InlineKeyboardButton(ui_buttons['freebies'], callback_data='freebies'))
    return markup

def send_ui_message(chat_id, key, reply_markup=None):
    data = ui_texts.get(key, {'text': "Текст не найден", 'entities': None})
    send_clean_message(chat_id, data['text'], entities=data['entities'], reply_markup=reply_markup)

def get_back_only_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Назад в главное меню", callback_data='back_to_main'))
    return markup

def get_purchasable_items():
    items = {
        '18_months': 'Google AI Pro (18 месяцев)',
        '12_months': 'Google AI Pro (12 месяцев)',
        '4_months': 'Google AI Pro (4 месяца)',
        '1_month_ultra': 'Google AI Ultra (1 месяц)'
    }
    for p_id, p_info in custom_products.items():
        items[p_id] = p_info['name']
    return items

def get_admin_products_markup():
    markup = types.InlineKeyboardMarkup()
    pro_status = "✅ В наличии" if products_availability['google_ai_pro'] else "❌ Отключен"
    ultra_status = "✅ В наличии" if products_availability['google_ai_ultra'] else "❌ Отключен"
    
    markup.add(types.InlineKeyboardButton(f"Google AI Pro: {pro_status}", callback_data='admin_toggle_google_ai_pro'))
    markup.add(types.InlineKeyboardButton(f"Google AI Ultra: {ultra_status}", callback_data='admin_toggle_google_ai_ultra'))
    
    for p_id, p_info in list(custom_products.items()):
        status = "✅ В наличии" if p_info['active'] else "❌ Отключен"
        btn_toggle = types.InlineKeyboardButton(f"{p_info['name']}: {status}", callback_data=f"admin_toggle_{p_id}")
        btn_delete = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"admin_delete_{p_id}")
        markup.row(btn_toggle, btn_delete)
        
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='admin_main'))
    return markup

def get_admin_freebies_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "✅ Включена" if freebies_enabled else "❌ Отключена"
    markup.add(types.InlineKeyboardButton(f"Отображение в меню: {status_text}", callback_data='admin_toggle_freebies'))
    
    for f_id, f_info in list(freebie_items.items()):
        markup.add(types.InlineKeyboardButton(f"❌ Удалить: {f_info['name']}", callback_data=f"admin_freedel_{f_id}"))
        
    markup.add(types.InlineKeyboardButton("➕ Добавить раздачу", callback_data='admin_freeadd'))
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='admin_main'))
    return markup

def get_user_freebies_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for f_id, f_info in freebie_items.items():
        markup.add(types.InlineKeyboardButton(f_info['name'], callback_data=f"showfree_{f_id}"))
    markup.add(types.InlineKeyboardButton("🔙 Назад в главное меню", callback_data='back_to_main'))
    return markup

def get_payment_markup(item_id, back_callback):
    pay_markup = types.InlineKeyboardMarkup(row_width=1)
    methods = payment_methods.get(item_id, [])
    if not methods:
        pay_markup.add(types.InlineKeyboardButton("💳 Оплатить", callback_data=f"pay_{item_id}"))
    else:
        for idx, method in enumerate(methods):
            pay_markup.add(types.InlineKeyboardButton(method['name'], callback_data=f"userpay_{item_id}_{idx}"))
    pay_markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=back_callback))
    return pay_markup

def get_admin_payedit_markup(item_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    methods = payment_methods.get(item_id, [])
    for idx, method in enumerate(methods):
        markup.add(types.InlineKeyboardButton(f"❌ Удалить: {method['name']}", callback_data=f"admin_paydel_{item_id}_{idx}"))
    markup.add(types.InlineKeyboardButton("➕ Добавить способ", callback_data=f"admin_payadd_{item_id}"))
    markup.add(types.InlineKeyboardButton("🔙 Назад к списку товаров", callback_data='admin_payments'))
    return markup


# ==================== /start ====================
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    delete_user_message(message)
    
    # Логика защиты: если тех. работы включены
    if maintenance_mode:
        # Если пишет админ И включен режим призрака — пускаем его в магазин
        if message.from_user.id in ADMIN_IDS and ghost_mode:
            pass
        else:
            send_clean_message(message.chat.id, "🛠 *Бот находится на техническом обслуживании.*\nПожалуйста, попробуйте позже.", parse_mode='Markdown')
            return
        
    send_ui_message(message.chat.id, 'welcome', reply_markup=get_main_menu_markup())


# ==================== Админ Панель ====================
@bot.message_handler(commands=['admin'])
def admin_panel_command(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    delete_user_message(message)
    
    if message.from_user.id not in ADMIN_IDS:
        return

    show_admin_panel(message.chat.id)

def show_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⚙️ Статус бота (Тех. работы)", callback_data='admin_status_menu'),
        types.InlineKeyboardButton("🎨 Дизайн (Тексты и Кнопки)", callback_data='admin_design_menu'),
        types.InlineKeyboardButton("📦 Управление товарами", callback_data='admin_products'),
        types.InlineKeyboardButton("💳 Управление оплатой", callback_data='admin_payments'),
        types.InlineKeyboardButton("🎁 Раздел Халява", callback_data='admin_freebies_menu'),
        types.InlineKeyboardButton("➕ Добавить новый товар", callback_data='admin_add_product'),
        types.InlineKeyboardButton("❌ Выйти", callback_data='admin_exit')
    )
    send_clean_message(chat_id, "🛠 *Панель администратора*", parse_mode='Markdown', reply_markup=markup)


# ==================== Логика Редактирования ====================
def process_edit_text(message, key):
    delete_user_message(message)
    if message.text and message.text.startswith('/'): return
    
    ui_texts[key] = {
        'text': message.text if message.text else message.caption,
        'entities': message.entities if message.entities else message.caption_entities
    }
    save_data()
    bot.answer_callback_query(active_bot_messages.get(str(message.chat.id)), "✅ Текст успешно обновлен!")
    show_admin_panel(message.chat.id)

def process_edit_button(message, key):
    delete_user_message(message)
    if message.text and message.text.startswith('/'): return
    
    ui_buttons[key] = message.text
    save_data()
    show_admin_panel(message.chat.id)

def process_edit_product_text(message, item_id):
    delete_user_message(message)
    if message.text and message.text.startswith('/'): return
    
    new_data = {
        'text': message.text if message.text else message.caption,
        'entities': message.entities if message.entities else message.caption_entities
    }
    
    if item_id in product_texts:
        product_texts[item_id] = new_data
    elif item_id in custom_products:
        custom_products[item_id]['desc'] = new_data
        
    save_data()
    show_admin_panel(message.chat.id)


# ==================== Логика добавления Халявы ====================
def process_new_freebie_name(message):
    delete_user_message(message)
    if message.text.startswith('/'): return
    
    f_name = message.text
    msg = send_clean_message(message.chat.id, f"Отлично. Теперь отправь текст/описание (промокод, ссылку или инструкцию) для кнопки «{f_name}»:\n(Премиум-эмодзи поддерживаются)")
    bot.register_next_step_handler(msg, process_new_freebie_desc, f_name)

def process_new_freebie_desc(message, f_name):
    delete_user_message(message)
    if message.text.startswith('/'): return
    
    global freebie_counter
    freebie_counter += 1
    new_f_id = f"free_{freebie_counter}"
    
    freebie_items[new_f_id] = {
        'name': f_name,
        'desc': {
            'text': message.text if message.text else message.caption,
            'entities': message.entities if message.entities else message.caption_entities
        }
    }
    save_data()
    
    markup = get_admin_freebies_markup()
    send_clean_message(message.chat.id, f"✅ Бонус «{f_name}» успешно добавлен!", reply_markup=markup)


# ==================== Логика добавления товара/оплаты ====================
def process_new_product_name(message):
    delete_user_message(message)
    if message.text.startswith('/'): return
    
    product_name = message.text
    msg = send_clean_message(message.chat.id, f"Отлично. Теперь отправь текст описания для товара «{product_name}» (любые премиум-эмодзи сохранятся):")
    bot.register_next_step_handler(msg, process_new_product_desc, product_name)

def process_new_product_desc(message, product_name):
    delete_user_message(message)
    if message.text.startswith('/'): return
    
    global custom_product_counter
    custom_product_counter += 1
    new_product_id = f"custom_{custom_product_counter}"
    
    custom_products[new_product_id] = {
        'name': product_name,
        'desc': {
            'text': message.text if message.text else message.caption,
            'entities': message.entities if message.entities else message.caption_entities
        },
        'active': True
    }
    save_data()
    show_admin_panel(message.chat.id)

def process_new_payment_name(message, item_id):
    delete_user_message(message)
    if message.text.startswith('/'): return
    
    method_name = message.text
    msg = send_clean_message(message.chat.id, f"Отлично. Теперь введите реквизиты/инструкцию для «{method_name}»:")
    bot.register_next_step_handler(msg, process_new_payment_desc, item_id, method_name)

def process_new_payment_desc(message, item_id, method_name):
    delete_user_message(message)
    if message.text.startswith('/'): return
    
    method_desc = message.text
    if item_id not in payment_methods:
        payment_methods[item_id] = []
    payment_methods[item_id].append({'name': method_name, 'desc': method_desc})
    save_data()
    
    markup = get_admin_payedit_markup(item_id)
    send_clean_message(message.chat.id, f"✅ Способ оплаты «{method_name}» успешно добавлен!", reply_markup=markup)


# ==================== Обработчик кнопок ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    # ОБЪЯВЛЕНИЕ ВСЕХ ГЛОБАЛЬНЫХ ПЕРЕМЕННЫХ СТРОГО В НАЧАЛЕ ФУНКЦИИ:
    global maintenance_mode, ghost_mode, freebies_enabled
    
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.answer_callback_query(call.id)
    
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    
    active_bot_messages[str(chat_id)] = msg_id
    save_data()

    # ------------------- Логика Админа -------------------
    if call.data.startswith('admin_') or call.data.startswith('edit_') or call.data.startswith('reset_') or call.data == 'cancel_edit':
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "❌ У вас нет доступа.", show_alert=True)
            return

        if call.data == 'admin_main':
            show_admin_panel(chat_id)

        # ---- Вкладка Статуса и Призрака ----
        elif call.data == 'admin_status_menu':
            markup = types.InlineKeyboardMarkup(row_width=1)
            m_status = "🔴 Отключен (Тех. работы)" if maintenance_mode else "🟢 Работает в штатном режиме"
            m_btn = "🟢 Включить бота" if maintenance_mode else "🔴 Отключить бота"
            g_status = "✅ Включен" if ghost_mode else "❌ Отключен"
            
            markup.add(
                types.InlineKeyboardButton(m_btn, callback_data='admin_toggle_maintenance'),
                types.InlineKeyboardButton(f"👻 Режим призрака: {g_status}", callback_data='admin_toggle_ghost'),
                types.InlineKeyboardButton("🔙 Назад", callback_data='admin_main')
            )
            bot.edit_message_text(f"⚙️ *Управление статусом бота*\n\nТекущий статус: {m_status}\n\n👻 *Режим призрака* позволяет вам (админу) полноценно тестировать меню, товары и цены через `/start` даже при включенных технических работах.", chat_id, msg_id, parse_mode='Markdown', reply_markup=markup)

        elif call.data in ['admin_toggle_maintenance', 'admin_toggle_ghost']:
            if call.data == 'admin_toggle_maintenance':
                maintenance_mode = not maintenance_mode
            else:
                ghost_mode = not ghost_mode
            save_data()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            m_status = "🔴 Отключен (Тех. работы)" if maintenance_mode else "🟢 Работает в штатном режиме"
            m_btn = "🟢 Включить бота" if maintenance_mode else "🔴 Отключить бота"
            g_status = "✅ Включен" if ghost_mode else "❌ Отключен"
            
            markup.add(
                types.InlineKeyboardButton(m_btn, callback_data='admin_toggle_maintenance'),
                types.InlineKeyboardButton(f"👻 Режим призрака: {g_status}", callback_data='admin_toggle_ghost'),
                types.InlineKeyboardButton("🔙 Назад", callback_data='admin_main')
            )
            bot.edit_message_text(f"⚙️ *Управление статусом бота*\n\nТекущий статус: {m_status}\n\n👻 *Режим призрака* позволяет вам (админу) полноценно тестировать меню, товары и цены через `/start` даже при включенных технических работах.", chat_id, msg_id, parse_mode='Markdown', reply_markup=markup)

        # ---- Меню Дизайна ----
        elif call.data == 'admin_design_menu':
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("💬 Тексты интерфейса", callback_data='admin_design_texts'),
                types.InlineKeyboardButton("📦 Описания товаров", callback_data='admin_design_prod_list'),
                types.InlineKeyboardButton("🔘 Кнопки меню", callback_data='admin_design_btns'),
                types.InlineKeyboardButton("🔙 Назад", callback_data='admin_main')
            )
            bot.edit_message_text("🎨 Что будем менять?", chat_id, msg_id, reply_markup=markup)

        elif call.data == 'admin_design_texts':
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Приветствие (/start)", callback_data='edit_txt_welcome'),
                types.InlineKeyboardButton("Заголовок 'Наши товары'", callback_data='edit_txt_browse_title'),
                types.InlineKeyboardButton("Текст 'Как это работает'", callback_data='edit_txt_how_it_works'),
                types.InlineKeyboardButton("Текст 'Халява'", callback_data='edit_txt_freebies'),
                types.InlineKeyboardButton("🔙 Назад", callback_data='admin_design_menu')
            )
            bot.edit_message_text("💬 Выбери системный текст для изменения:", chat_id, msg_id, reply_markup=markup)

        elif call.data == 'admin_design_prod_list':
            markup = types.InlineKeyboardMarkup(row_width=1)
            for item_id, name in get_purchasable_items().items():
                markup.add(types.InlineKeyboardButton(name, callback_data=f"edit_prod_txt_{item_id}"))
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='admin_design_menu'))
            bot.edit_message_text("📦 Выбери товар для изменения его текста (заголовка/описания):", chat_id, msg_id, reply_markup=markup)

        elif call.data == 'admin_design_btns':
            markup = types.InlineKeyboardMarkup(row_width=1)
            for key, name in ui_buttons.items():
                markup.add(types.InlineKeyboardButton(f"Изменить: {name}", callback_data=f"edit_btn_{key}"))
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='admin_design_menu'))
            bot.edit_message_text("🔘 Выбери кнопку для изменения:", chat_id, msg_id, reply_markup=markup)

        # Запросы на редактирование
        elif call.data.startswith('edit_txt_'):
            key = call.data.replace('edit_txt_', '')
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Сбросить (По умолчанию)", callback_data=f'reset_txt_{key}'),
                types.InlineKeyboardButton("❌ Отмена", callback_data='cancel_edit')
            )
            msg = send_clean_message(chat_id, f"📝 Отправь новый текст.\n\n*Совет:* Используй премиум-эмодзи или форматирование — бот всё запомнит!", parse_mode='Markdown', reply_markup=markup)
            bot.register_next_step_handler(msg, process_edit_text, key)

        elif call.data.startswith('edit_prod_txt_'):
            item_id = call.data.replace('edit_prod_txt_', '')
            markup = types.InlineKeyboardMarkup(row_width=1)
            if item_id in DEFAULT_PRODUCT_TEXTS:
                markup.add(types.InlineKeyboardButton("🔄 Сбросить (По умолчанию)", callback_data=f'reset_prod_txt_{item_id}'))
            markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data='cancel_edit'))
            
            msg = send_clean_message(chat_id, f"📝 Отправь новый текст/описание для этого товара:\n(Любые премиум-эмодзи будут сохранены)", reply_markup=markup)
            bot.register_next_step_handler(msg, process_edit_product_text, item_id)

        elif call.data.startswith('edit_btn_'):
            key = call.data.replace('edit_btn_', '')
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Сбросить (По умолчанию)", callback_data=f'reset_btn_{key}'),
                types.InlineKeyboardButton("❌ Отмена", callback_data='cancel_edit')
            )
            msg = send_clean_message(chat_id, f"📝 Отправь новое название для этой кнопки (без премиум-эмодзи):", reply_markup=markup)
            bot.register_next_step_handler(msg, process_edit_button, key)

        # Сброс и отмена
        elif call.data.startswith('reset_txt_'):
            key = call.data.replace('reset_txt_', '')
            ui_texts[key] = {'text': DEFAULT_UI_TEXTS[key]['text'], 'entities': DEFAULT_UI_TEXTS[key]['entities']}
            save_data()
            bot.answer_callback_query(call.id, "✅ Текст успешно сброшен!", show_alert=True)
            show_admin_panel(chat_id)

        elif call.data.startswith('reset_prod_txt_'):
            item_id = call.data.replace('reset_prod_txt_', '')
            if item_id in DEFAULT_PRODUCT_TEXTS:
                product_texts[item_id] = {'text': DEFAULT_PRODUCT_TEXTS[item_id]['text'], 'entities': DEFAULT_PRODUCT_TEXTS[item_id]['entities']}
                save_data()
                bot.answer_callback_query(call.id, "✅ Описание товара сброшено!", show_alert=True)
            show_admin_panel(chat_id)

        elif call.data.startswith('reset_btn_'):
            key = call.data.replace('reset_btn_', '')
            ui_buttons[key] = DEFAULT_UI_BUTTONS[key]
            save_data()
            bot.answer_callback_query(call.id, "✅ Название кнопки сброшено!", show_alert=True)
            show_admin_panel(chat_id)
            
        elif call.data == 'cancel_edit':
            show_admin_panel(chat_id)

        # Управление Халявой в админке
        elif call.data == 'admin_freebies_menu':
            markup = get_admin_freebies_markup()
            bot.edit_message_text("🎁 Управление разделом Халява.\nЗдесь вы можете скрывать раздел из меню, добавлять кнопки или удалять старые:", chat_id, msg_id, reply_markup=markup)

        elif call.data == 'admin_toggle_freebies':
            freebies_enabled = not freebies_enabled
            save_data()
            markup = get_admin_freebies_markup()
            bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup)

        elif call.data == 'admin_freeadd':
            msg = send_clean_message(chat_id, "📝 Введите название кнопки для новой раздачи (например, «🎁 Промокод 15%»):")
            bot.register_next_step_handler(msg, process_new_freebie_name)

        elif call.data.startswith('admin_freedel_'):
            f_id = call.data.replace('admin_freedel_', '')
            if f_id in freebie_items:
                del freebie_items[f_id]
                save_data()
                bot.answer_callback_query(call.id, "✅ Раздача удалена!", show_alert=True)
            markup = get_admin_freebies_markup()
            bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup)

        # Управление товарами
        elif call.data == 'admin_products':
            markup = get_admin_products_markup()
            bot.edit_message_text("📦 Нажмите на товар, чтобы изменить его статус, или удалите его:", chat_id, msg_id, reply_markup=markup)

        elif call.data == 'admin_add_product':
            msg = send_clean_message(chat_id, "📝 Введите название нового товара (оно будет на кнопке):")
            bot.register_next_step_handler(msg, process_new_product_name)

        elif call.data == 'admin_exit':
            try:
                bot.delete_message(chat_id, msg_id)
                active_bot_messages.pop(str(chat_id), None)
                save_data()
            except Exception:
                pass

        elif call.data.startswith('admin_toggle_'):
            item_id = call.data.replace('admin_toggle_', '')
            if item_id in products_availability:
                products_availability[item_id] = not products_availability[item_id]
            elif item_id in custom_products:
                custom_products[item_id]['active'] = not custom_products[item_id]['active']
            save_data()
            markup = get_admin_products_markup()
            bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup)
            
        elif call.data.startswith('admin_delete_'):
            item_id = call.data.replace('admin_delete_', '')
            if item_id in custom_products:
                del custom_products[item_id]
                payment_methods.pop(item_id, None)
                save_data()
                bot.answer_callback_query(call.id, "✅ Товар удален!", show_alert=True)
            markup = get_admin_products_markup()
            bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup)
            
        elif call.data == 'admin_payments':
            markup = types.InlineKeyboardMarkup(row_width=1)
            for item_id, name in get_purchasable_items().items():
                markup.add(types.InlineKeyboardButton(name, callback_data=f"admin_payedit_{item_id}"))
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='admin_main'))
            bot.edit_message_text("💳 Выберите товар для настройки способов оплаты:", chat_id, msg_id, reply_markup=markup)

        elif call.data.startswith('admin_payedit_'):
            item_id = call.data.replace('admin_payedit_', '')
            item_name = get_purchasable_items().get(item_id, "Неизвестный товар")
            markup = get_admin_payedit_markup(item_id)
            bot.edit_message_text(f"💳 Способы оплаты для *{item_name}*:", chat_id, msg_id, parse_mode='Markdown', reply_markup=markup)

        elif call.data.startswith('admin_payadd_'):
            item_id = call.data.replace('admin_payadd_', '')
            msg = send_clean_message(chat_id, "📝 Введите название кнопки для нового способа оплаты (например, «💳 Карта Uzcard»):")
            bot.register_next_step_handler(msg, process_new_payment_name, item_id)

        elif call.data.startswith('admin_paydel_'):
            parts = call.data.split('_')
            idx = int(parts[-1])
            item_id = "_".join(parts[2:-1])
            if item_id in payment_methods and len(payment_methods[item_id]) > idx:
                del payment_methods[item_id][idx]
                save_data()
                bot.answer_callback_query(call.id, "✅ Способ оплаты удален!", show_alert=True)
            markup = get_admin_payedit_markup(item_id)
            bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=markup)

        return # Завершаем выполнение админ-блока


    # ------------------- Логика Пользователя -------------------
    # Защита при тех. работах
    if maintenance_mode:
        if call.from_user.id in ADMIN_IDS and ghost_mode:
            pass
        else:
            bot.answer_callback_query(call.id, "🛠 Бот находится на техническом обслуживании.", show_alert=True)
            return

    if call.data == 'browse':
        product_markup = types.InlineKeyboardMarkup(row_width=1)
        product_markup.add(
            types.InlineKeyboardButton("google ai pro", callback_data='google_ai_pro'),
            types.InlineKeyboardButton("google ai ultra", callback_data='google_ai_ultra')
        )
        for p_id, p_info in custom_products.items():
            if p_info['active']:
                product_markup.add(types.InlineKeyboardButton(p_info['name'], callback_data=f"show_{p_id}"))

        product_markup.add(types.InlineKeyboardButton("🔙 Назад в главное меню", callback_data='back_to_main'))
        
        data = ui_texts.get('browse_title', {'text': "🛍️ Наши товары", 'entities': None})
        try:
            bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], reply_markup=product_markup)
        except Exception:
            send_ui_message(chat_id, 'browse_title', reply_markup=product_markup)

    elif call.data == 'freebies':
        if not freebies_enabled:
            bot.answer_callback_query(call.id, "❌ Данный раздел временно отключен.", show_alert=True)
            return
            
        data = ui_texts.get('freebies', {'text': "Раздел Халява", 'entities': None})
        p_mode = None if data['entities'] else 'Markdown'
        markup = get_user_freebies_markup()
        try:
            bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], parse_mode=p_mode, reply_markup=markup)
        except Exception:
            send_clean_message(chat_id, data['text'], entities=data['entities'], parse_mode=p_mode, reply_markup=markup)

    elif call.data.startswith('showfree_'):
        f_id = call.data.replace('showfree_', '')
        if f_id in freebie_items:
            data = freebie_items[f_id]['desc']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Назад к списку бонусов", callback_data='freebies'))
            try:
                bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], reply_markup=markup)
            except Exception:
                send_clean_message(chat_id, data['text'], entities=data['entities'], reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ Данный бонус больше не доступен.", show_alert=True)

    elif call.data == 'how_it_works':
        data = ui_texts.get('how_it_works', {'text': "Инструкция", 'entities': None})
        p_mode = None if data['entities'] else 'Markdown'
        try:
            bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], parse_mode=p_mode, reply_markup=get_back_only_markup())
        except Exception:
            send_clean_message(chat_id, data['text'], entities=data['entities'], parse_mode=p_mode, reply_markup=get_back_only_markup())

    elif call.data.startswith('show_custom_'):
        item_id = call.data.replace('show_', '')
        if item_id in custom_products and custom_products[item_id]['active']:
            data = custom_products[item_id]['desc']
            pay_markup = get_payment_markup(item_id, 'back_to_products')
            try:
                bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], reply_markup=pay_markup)
            except Exception:
                send_clean_message(chat_id, data['text'], entities=data['entities'], reply_markup=pay_markup)
        else:
            bot.answer_callback_query(call.id, "❌ Данный товар временно недоступен.", show_alert=True)

    elif call.data == 'google_ai_pro':
        if not products_availability['google_ai_pro']:
            bot.answer_callback_query(call.id, "❌ Данный товар временно недоступен.", show_alert=True)
            return

        options_markup = types.InlineKeyboardMarkup(row_width=1)
        options_markup.add(
            types.InlineKeyboardButton("18-months", callback_data='18_months'),
            types.InlineKeyboardButton("12-months", callback_data='12_months'),
            types.InlineKeyboardButton("4-months",  callback_data='4_months'),
            types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_products')
        )
        bot.edit_message_text("выбери нужный вариант:", chat_id, msg_id, reply_markup=options_markup)

    elif call.data == 'google_ai_ultra':
        if not products_availability['google_ai_ultra']:
            bot.answer_callback_query(call.id, "❌ Данный товар временно недоступен.", show_alert=True)
            return

        ultra_markup = types.InlineKeyboardMarkup(row_width=1)
        ultra_markup.add(
            types.InlineKeyboardButton("1-month", callback_data='1_month_ultra'),
            types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_products')
        )
        bot.edit_message_text("выбери нужный вариант:", chat_id, msg_id, reply_markup=ultra_markup)

    elif call.data in ['18_months', '12_months', '4_months', '1_month_ultra']:
        data = product_texts[call.data]
        parent = 'google_ai_pro' if call.data != '1_month_ultra' else 'google_ai_ultra'
        pay_markup = get_payment_markup(call.data, parent)
        try:
            bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], reply_markup=pay_markup)
        except Exception:
            send_clean_message(chat_id, data['text'], entities=data['entities'], reply_markup=pay_markup)

    elif call.data.startswith('userpay_'):
        parts = call.data.split('_')
        idx = int(parts[-1])
        item_id = "_".join(parts[1:-1])
        if item_id in payment_methods and len(payment_methods[item_id]) > idx:
            desc = payment_methods[item_id][idx]['desc']
            back_btn = 'back_to_products' if item_id.startswith('custom_') else item_id
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=back_btn))
            bot.edit_message_text(desc, chat_id, msg_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "❌ Способ оплаты недоступен.", show_alert=True)

    elif call.data.startswith('pay_'):
        bot.answer_callback_query(call.id, "✅ Спасибо! Оплата будет доступна в ближайшее время.", show_alert=True)

    elif call.data == 'back_to_main':
        data = ui_texts.get('welcome', {'text': "добро пожаловать в cryrae shop ✨", 'entities': None})
        try:
            bot.edit_message_text(data['text'], chat_id, msg_id, entities=data['entities'], reply_markup=get_main_menu_markup())
        except Exception:
            send_ui_message(chat_id, 'welcome', reply_markup=get_main_menu_markup())

    elif call.data == 'back_to_products':
        call.data = 'browse'
        handle_callback_query(call)


# ==================== Запуск ====================
if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)