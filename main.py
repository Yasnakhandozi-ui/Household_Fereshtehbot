import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8625093110:AAFVfWohZT9N2ozDDJv8GKTqJMgQoUO_lMA"
ADMIN_ID = 8884194776
CARD_NUMBER = "6219-8618-7088-9737"
SHABA = "IR810560611828006735725201"
CARD_HOLDER = "خانم فرشته جهان تیغ"
SHOP_NAME = "فرشته"
SUPPORT_USERNAME = "@Fereshteh_Household"
DB_PATH = '/tmp/fereshteh.db'
PHOTOS_DIR = '/tmp/fereshteh_photos'

DEFAULT_PRODUCTS = [
    {"category": "جاروبرقی", "name": "جاروبرقی AEG مدل VX82-1-OKO", "description": "ساخت کشور چین تحت لیسانس آلمان\nتوان مصرفی: ۲۲۰۰ وات\nقدرت مکش: ۵۰۰ وات\nصدا: فقط ۵۷ دسی‌بل\nمصرف انرژی: گرید A\nموتور قدرتمند و کاملاً بی‌صدا\nدارای ۴ حالت مکش + حالت هوشمند\nکیسه قابل تعویض با گنجایش ۳/۵ لیتر\nطول سیم: ۹ متر\nشعاع کارکرد: ۱۲ متر\nوزن ۷/۱ کیلوگرم", "price": 35500000, "stock": "موجود", "models": "", "image_link": ""},
    {"category": "اسپرسوساز", "name": "اسپرسوساز دسینی مدل KD3040", "description": "جنس بدنه: استیل\nطول سیم: ۱۰۰ سانتی‌متر\nتوان: ۱۳۵۰ وات\nفشار بخار: ۲۰\nحجم مخزن آب: ۱/۲ لیتر\nتولید کف شیر- سیستم گرم کردن فنجان- نظافت خودکار\nقابلیت استفاده از پودر قهوه\nتنظیم میزان بخار به صورت دستی\nنوشیدنی‌های قابل تهیه: اسپرسو- کاپوچینو\nتنظیم میزان غلظت قهوه\nسیستم قطع خودکار\nتعداد نازل قهوه: یک عدد", "price": 17990000, "stock": "موجود", "models": "", "image_link": ""},
    {"category": "جارو عصایی", "name": "جارو عصایی پرتابل گلف مدل G562SV", "description": "وزن: ۲ کیلوگرم\nغیرشارژی- پرتابل\nجنس بدنه: پلاستیک فشرده ABS\nطول سیم: ۷ متر\nمخزن گرد و غبار ۵۵۰ گرم و مخزن آب ۶۰۰ میلی‌لیتر\nمیزان صدا: ۷۹ دسی‌بل\nقدرت موتور: ۱۱۰۰ وات\nفیلتر: هپا HEPA\nاقلام همراه: نازل درز، پد و فیلتر اضافه\nسیستم تی‌کشی همزمان\nطراحی آرگونومیک\nقابلیت ایستادن بدون تکیه‌گاه", "price": 9900000, "stock": "موجود", "models": "", "image_link": ""}
]

def init_db():
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, description TEXT, price INTEGER, stock_status TEXT DEFAULT 'موجود', image_link TEXT, models TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, product_name TEXT, model TEXT, quantity INTEGER, total_price INTEGER, name TEXT, phone TEXT, address TEXT, postal_code TEXT, tracking_code TEXT, status TEXT DEFAULT 'در انتظار تأیید')''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, question TEXT, answer TEXT, status TEXT DEFAULT 'open')''')
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        for p in DEFAULT_PRODUCTS:
            c.execute("INSERT INTO products (category, name, description, price, stock_status, image_link, models) VALUES (?, ?, ?, ?, ?, ?, ?)", (p['category'], p['name'], p['description'], p['price'], p['stock'], p['image_link'], p['models']))
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM products ORDER BY category")
    cats = [row[0] for row in c.fetchall()]
    conn.close()
    return cats

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏠 مشاهده محصولات", callback_data='products')],
        [InlineKeyboardButton("🔍 جستجوی محصول", callback_data='search')],
        [InlineKeyboardButton("📦 استعلام موجودی", callback_data='stock')],
        [InlineKeyboardButton("💰 قیمت روز", callback_data='price')],
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data='order')],
        [InlineKeyboardButton("🚚 شرایط ارسال", callback_data='shipping')],
        [InlineKeyboardButton("🛡️ گارانتی", callback_data='warranty')],
        [InlineKeyboardButton("💬 ارتباط با پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("❓ پرسش از پشتیبانی", callback_data='question')],
        [InlineKeyboardButton("🚚 پیگیری سفارش", callback_data='track')],
    ]
    await update.message.reply_text(f"🏠 به فروشگاه {SHOP_NAME} خوش اومدی!\n\nلطفاً یکی از گزینه‌ها رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    cats = get_categories()
    if not cats: await query.message.reply_text("✖️ هنوز محصولی اضافه نشده."); return
    keyboard = [[InlineKeyboardButton(f"📦 {cat}", callback_data=f"cat_{cat}")] for cat in cats]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_home')])
    await query.message.reply_text("📂 دسته‌بندی محصولات:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    cat = query.data.replace('cat_', '')
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, name, image_link FROM products WHERE category = ?", (cat,))
    products = c.fetchall(); conn.close()
    if not products: await query.message.reply_text("✖️ محصولی در این دسته پیدا نشد."); return
    for pid, name, img in products:
        if img and os.path.exists(img):
            with open(img, 'rb') as photo: await query.message.reply_photo(photo=photo, caption=f"📦 {name}")
        else: await query.message.reply_text(f"📦 {name}")

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("🔍 لطفاً نام محصول مورد نظرت رو وارد کن:"); context.user_data['mode'] = 'search'

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    term = update.message.text
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT name, description, image_link FROM products WHERE name LIKE ?", (f'%{term}%',))
    results = c.fetchall(); conn.close()
    if not results: await update.message.reply_text("✖️ محصولی با این نام پیدا نشد."); return
    for name, desc, img in results:
        text = f"📦 {name}\n\n📝 {desc}"
        if img and os.path.exists(img):
            with open(img, 'rb') as photo: await update.message.reply_photo(photo=photo, caption=text)
        else: await update.message.reply_text(text)

async def stock_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("📦 لطفاً نام محصول رو وارد کن:"); context.user_data['mode'] = 'stock'

async def handle_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT stock_status FROM products WHERE name LIKE ?", (f'%{name}%',))
    r = c.fetchone(); conn.close()
    if r:
        s = r[0]
        if s == "موجود": await update.message.reply_text("✅ موجود است.")
        elif s == "محدود": await update.message.reply_text("⚠️ تعداد محدود باقی مانده است.")
        else: await update.message.reply_text("❌ ناموجود است.")
    else: await update.message.reply_text("✖️ محصول پیدا نشد.")

async def price_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("💰 لطفاً نام محصول رو وارد کن:"); context.user_data['mode'] = 'price'

async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT price FROM products WHERE name LIKE ?", (f'%{name}%',))
    r = c.fetchone(); conn.close()
    if r: await update.message.reply_text(f"💰 قیمت روز: {r[0]:,} تومان")
    else: await update.message.reply_text("✖️ محصول پیدا نشد.")

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("🛒 لطفاً نام محصولی که می‌خوای سفارش بدی رو وارد کن:")
    context.user_data['mode'] = 'order_name'; context.user_data['order'] = {}

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text; context.user_data['order']['product_name'] = name
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT models FROM products WHERE name LIKE ?", (f'%{name}%',))
    r = c.fetchone(); conn.close()
    if r and r[0]:
        models = r[0].split(','); keyboard = []
        for m in models:
            m = m.strip(); keyboard.append([InlineKeyboardButton(m, callback_data=f"model_{m}")])
        await update.message.reply_text("🎨 لطفاً مدل/رنگ رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data['mode'] = 'order_model'
    else:
        await update.message.reply_text("🔢 لطفاً تعداد مورد نظر رو وارد کن:"); context.user_data['mode'] = 'order_qty'

async def order_model_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    model = query.data.replace('model_', ''); context.user_data['order']['model'] = model
    await query.message.reply_text("🔢 لطفاً تعداد مورد نظر رو وارد کن:"); context.user_data['mode'] = 'order_qty'

async def order_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text); context.user_data['order']['quantity'] = qty
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT price FROM products WHERE name LIKE ?", (f"%{context.user_data['order']['product_name']}%",))
        r = c.fetchone(); conn.close()
        if r:
            total = r[0] * qty; context.user_data['order']['total_price'] = total
            card_formatted = f"{CARD_NUMBER[:4]}-{CARD_NUMBER[4:8]}-{CARD_NUMBER[8:12]}-{CARD_NUMBER[12:]}"
            await update.message.reply_text(f"💰 مبلغ قابل پرداخت: {total:,} تومان\n\n💳 شماره کارت:\n`{card_formatted}`\n👤 به نام: {CARD_HOLDER}\n\n🏦 شبا:\n`{SHABA}`\n\n📸 لطفاً تصویر فیش واریزی رو بفرست.", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 کپی شماره کارت", callback_data=f"copy_{card_formatted}")]]))
            context.user_data['mode'] = 'receipt'
    except: await update.message.reply_text("✖️ لطفاً عدد وارد کن.")

async def copy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer("✅ شماره کارت کپی شد!", show_alert=True)

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: await update.message.reply_text("📝 لطفاً نام و نام خانوادگی خودت رو وارد کن:"); context.user_data['mode'] = 'info_name'
    else: await update.message.reply_text("✖️ لطفاً عکس فیش رو بفرست.")

async def info_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['name'] = update.message.text
    await update.message.reply_text("📱 شماره موبایل:"); context.user_data['mode'] = 'info_phone'

async def info_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['phone'] = update.message.text
    await update.message.reply_text("📍 آدرس کامل:"); context.user_data['mode'] = 'info_address'

async def info_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['address'] = update.message.text
    await update.message.reply_text("📮 کد پستی:"); context.user_data['mode'] = 'info_postal'

async def info_postal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['postal_code'] = update.message.text
    o = context.user_data['order']
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, username, product_name, model, quantity, total_price, name, phone, address, postal_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (update.message.from_user.id, update.message.from_user.username or "", o['product_name'], o.get('model', ''), o['quantity'], o['total_price'], o['name'], o['phone'], o['address'], o['postal_code']))
    order_id = c.lastrowid; conn.commit(); conn.close()
    await update.message.reply_text("✅ سفارش شما ثبت شد.\n\nپشتیبانی حداکثر تا چند ساعت آینده با شما تماس می‌گیرد و پس از تأیید سفارش، کد رهگیری برای شما ارسال خواهد شد.")
    context.user_data['mode'] = None
    await context.bot.send_message(ADMIN_ID, f"🛒 سفارش جدید (کد: {order_id}):\n\n👤 {o['name']}\n📱 {o['phone']}\n📍 {o['address']}\n📮 {o['postal_code']}\n\n📦 {o['product_name']}\n🎨 {o.get('model', 'ندارد')}\n🔢 تعداد: {o['quantity']}\n💰 مبلغ: {o['total_price']:,} تومان\n\nبرای ثبت کد رهگیری: /tracking {order_id} کد_رهگیری")

async def shipping_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("🚚 شرایط ارسال:\n\n📦 ارسال به سراسر ایران\n🚛 از طریق پست یا تیپاکس\n⏱ زمان: ۱ تا ۴ روز کاری\n🆓 هزینه ارسال: رایگان")

async def warranty_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("🛡️ گارانتی:\n\n✅ ضمانت اصالت کالا\n📅 ۶ ماه گارانتی\n🔄 شرایط تعویض در صورت مشکل\n📞 پشتیبانی پس از خرید")

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text(f"💬 برای ارتباط مستقیم با پشتیبانی، به آیدی زیر پیام بده:\n\n{SUPPORT_USERNAME}")

async def question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("❓ سؤالت رو بنویس:"); context.user_data['mode'] = 'question'

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO questions (user_id, username, question) VALUES (?, ?, ?)", (update.message.from_user.id, update.message.from_user.username or "", update.message.text))
    qid = c.lastrowid; conn.commit(); conn.close()
    await context.bot.send_message(ADMIN_ID, f"❓ سؤال از @{update.message.from_user.username or update.message.from_user.id}:\n\n{update.message.text}\n\nبرای پاسخ: /answer {qid} متن_پاسخ")
    await update.message.reply_text("✅ سوال شما ثبت شد.\nبه زودی پشتیبانی به شما پاسخ خواهد داد.\nاز صبر و شکیبایی شما ممنونم.")

async def track_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.message.reply_text("🚚 لطفاً کد رهگیری سفارشت رو وارد کن:"); context.user_data['mode'] = 'track'

async def handle_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT product_name, status FROM orders WHERE tracking_code = ?", (code,))
    r = c.fetchone(); conn.close()
    if r: await update.message.reply_text(f"📦 محصول: {r[0]}\n📋 وضعیت: {r[1]}")
    else: await update.message.reply_text("✖️ کد رهگیری نامعتبره.")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    keyboard = [
        [InlineKeyboardButton("➕ افزودن محصول", callback_data='adm_add')],
        [InlineKeyboardButton("📋 لیست محصولات", callback_data='adm_list')],
        [InlineKeyboardButton("💰 تغییر قیمت", callback_data='adm_price_menu')],
        [InlineKeyboardButton("📦 تغییر موجودی", callback_data='adm_stock_menu')],
        [InlineKeyboardButton("🖼️ افزودن عکس", callback_data='adm_photo')],
        [InlineKeyboardButton("📋 سفارشات", callback_data='adm_orders')],
        [InlineKeyboardButton("❓ پرسش‌ها", callback_data='adm_questions')],
    ]
    await update.message.reply_text("⚙️ پنل مدیریت فروشگاه فرشته:", reply_markup=InlineKeyboardMarkup(keyboard))

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        parts = update.message.text.replace('/add ', '').split('|')
        category, name, desc, price = parts[0].strip(), parts[1].strip(), parts[2].strip(), int(parts[3].strip())
        stock = parts[4].strip() if len(parts) > 4 else "موجود"
        models = parts[5].strip() if len(parts) > 5 else ""
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("INSERT INTO products (category, name, description, price, stock_status, models) VALUES (?, ?, ?, ?, ?, ?)", (category, name, desc, price, stock, models))
        pid = c.lastrowid; conn.commit(); conn.close()
        await update.message.reply_text(f"✅ محصول اضافه شد!\n🆔 کد: {pid}\n📂 دسته: {category}")
    except: await update.message.reply_text("✖️ فرمت: /add دسته | نام | توضیحات | قیمت | موجودی | مدل‌ها")

async def set_photo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        pid = int(update.message.text.split()[1]); context.user_data['photo_for'] = pid
        await update.message.reply_text("📸 عکس رو بفرست."); context.user_data['mode'] = 'set_photo'
    except: await update.message.reply_text("✖️ مثال: /setphoto 1")

async def set_photo_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        pid = context.user_data.get('photo_for')
        if pid:
            photo = update.message.photo[-1]; file = await context.bot.get_file(photo.file_id)
            path = f'{PHOTOS_DIR}/product_{pid}.jpg'; await file.download_to_drive(path)
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("UPDATE products SET image_link = ? WHERE id = ?", (path, pid)); conn.commit(); conn.close()
            await update.message.reply_text("✅ عکس ذخیره شد!"); context.user_data['mode'] = None

async def change_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        parts = update.message.text.replace('/price ', '').split('|')
        pid, new_price = int(parts[0].strip()), int(parts[1].strip())
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, pid)); conn.commit(); conn.close()
        await update.message.reply_text(f"✅ قیمت به {new_price:,} تومان تغییر کرد.")
    except: await update.message.reply_text("✖️ مثال: /price 1 | 36000000")

async def change_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        parts = update.message.text.replace('/stock ', '').split('|')
        pid, status = int(parts[0].strip()), parts[1].strip()
        if status not in ['موجود', 'محدود', 'ناموجود']: await update.message.reply_text("✖️ فقط: موجود / محدود / ناموجود"); return
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("UPDATE products SET stock_status = ? WHERE id = ?", (status, pid)); conn.commit(); conn.close()
        await update.message.reply_text(f"✅ موجودی به «{status}» تغییر کرد.")
    except: await update.message.reply_text("✖️ مثال: /stock 1 | ناموجود")

async def set_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        parts = update.message.text.split(' ', 2); oid, code = int(parts[1]), parts[2]
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT user_id, product_name FROM orders WHERE id = ?", (oid,))
        order = c.fetchone()
        if order:
            c.execute("UPDATE orders SET tracking_code = ?, status = 'ارسال شده' WHERE id = ?", (code, oid)); conn.commit()
            await context.bot.send_message(order[0], f"✅ سفارش شما تأیید شد!\n\n📦 محصول: {order[1]}\n🚚 کد رهگیری: {code}")
            await update.message.reply_text("✅ کد رهگیری ثبت و برای مشتری ارسال شد.")
        else: await update.message.reply_text("✖️ سفارش پیدا نشد.")
        conn.close()
    except: await update.message.reply_text("✖️ مثال: /tracking 1 12345678")

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        parts = update.message.text.split(' ', 2); qid, answer = int(parts[1]), parts[2]
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT user_id FROM questions WHERE id = ?", (qid,))
        r = c.fetchone()
        if r:
            c.execute("UPDATE questions SET answer = ?, status = 'closed' WHERE id = ?", (answer, qid)); conn.commit()
            await context.bot.send_message(r[0], f"✅ پاسخ پشتیبانی:\n\n{answer}")
            await update.message.reply_text("✅ پاسخ ارسال شد.")
        else: await update.message.reply_text("✖️ سؤال پیدا نشد.")
        conn.close()
    except: await update.message.reply_text("✖️ مثال: /answer 1 سلام وقت بخیر")

async def adm_add_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("➕ /add دسته | نام | توضیحات | قیمت | موجودی | مدل‌ها")

async def adm_list_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, category, name, price, stock_status FROM products")
    products = c.fetchall(); conn.close()
    if not products: await update.callback_query.message.reply_text("✖️ هنوز محصولی ثبت نشده."); return
    text = "📋 لیست محصولات:\n\n"
    for p in products: text += f"🆔 {p[0]} | 📂 {p[1]}\n📦 {p[2]}\n💰 {p[3]:,} تومان | 📦 {p[4]}\n\n"
    await update.callback_query.message.reply_text(text)

async def adm_price_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(); await update.callback_query.message.reply_text("💰 /price کد_محصول | قیمت_جدید")

async def adm_stock_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(); await update.callback_query.message.reply_text("📦 /stock کد_محصول | موجود/محدود/ناموجود")

async def adm_photo_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(); await update.callback_query.message.reply_text("🖼️ /setphoto کد_محصول\nسپس عکس رو بفرست.")

async def adm_orders_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.from_user.id != ADMIN_ID: return
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, name, product_name, total_price, status FROM orders ORDER BY id DESC LIMIT 10")
    orders = c.fetchall(); conn.close()
    if not orders: await query.message.reply_text("✖️ هنوز سفارشی ثبت نشده."); return
    text = "📋 آخرین سفارشات:\n\n"
    for o in orders: text += f"🆔 {o[0]} | 👤 {o[1]}\n📦 {o[2]} | 💰 {o[3]:,} | {o[4]}\n\n"
    await query.message.reply_text(text)

async def adm_questions_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.from_user.id != ADMIN_ID: return
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, username, question FROM questions WHERE status = 'open' ORDER BY id DESC")
    qs = c.fetchall(); conn.close()
    if not qs: await query.message.reply_text("✖️ سؤال بازی وجود نداره."); return
    text = "❓ سؤالات باز:\n\n"
    for q in qs: text += f"🆔 {q[0]} | 👤 @{q[1]}\n💬 {q[2]}\n\n"
    text += "برای پاسخ: /answer کد_سؤال متن_پاسخ"
    await query.message.reply_text(text)

async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    keyboard = [
        [InlineKeyboardButton("🏠 مشاهده محصولات", callback_data='products')],
        [InlineKeyboardButton("🔍 جستجوی محصول", callback_data='search')],
        [InlineKeyboardButton("📦 استعلام موجودی", callback_data='stock')],
        [InlineKeyboardButton("💰 قیمت روز", callback_data='price')],
        [InlineKeyboardButton("🛒 ثبت سفارش", callback_data='order')],
        [InlineKeyboardButton("🚚 شرایط ارسال", callback_data='shipping')],
        [InlineKeyboardButton("🛡️ گارانتی", callback_data='warranty')],
        [InlineKeyboardButton("💬 ارتباط با پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("❓ پرسش از پشتیبانی", callback_data='question')],
        [InlineKeyboardButton("🚚 پیگیری سفارش", callback_data='track')],
    ]
    await query.message.reply_text(f"🏠 به فروشگاه {SHOP_NAME} خوش اومدی!\n\nلطفاً یکی از گزینه‌ها رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    handlers = {'search': handle_search, 'price': handle_price, 'stock': handle_stock, 'order_name': order_name, 'order_qty': order_qty, 'receipt': receipt, 'info_name': info_name, 'info_phone': info_phone, 'info_address': info_address, 'info_postal': info_postal, 'track': handle_track, 'question': handle_question, 'set_photo': set_photo_msg}
    if mode in handlers: await handlers[mode](update, context)

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin))
    app.add_handler(CommandHandler('add', add_product))
    app.add_handler(CommandHandler('setphoto', set_photo_cmd))
    app.add_handler(CommandHandler('price', change_price))
    app.add_handler(CommandHandler('stock', change_stock))
    app.add_handler(CommandHandler('tracking', set_tracking))
    app.add_handler(CommandHandler('answer', answer_question))
    app.add_handler(CallbackQueryHandler(show_categories, pattern='^products$'))
    app.add_handler(CallbackQueryHandler(show_category_products, pattern='^cat_'))
    app.add_handler(CallbackQueryHandler(search_start, pattern='^search$'))
    app.add_handler(CallbackQueryHandler(price_start, pattern='^price$'))
    app.add_handler(CallbackQueryHandler(stock_start, pattern='^stock$'))
    app.add_handler(CallbackQueryHandler(order_start, pattern='^order$'))
    app.add_handler(CallbackQueryHandler(order_model_select, pattern='^model_'))
    app.add_handler(CallbackQueryHandler(copy_card, pattern='^copy_'))
    app.add_handler(CallbackQueryHandler(shipping_info, pattern='^shipping$'))
    app.add_handler(CallbackQueryHandler(warranty_info, pattern='^warranty$'))
    app.add_handler(CallbackQueryHandler(support_start, pattern='^support$'))
    app.add_handler(CallbackQueryHandler(question_start, pattern='^question$'))
    app.add_handler(CallbackQueryHandler(track_start, pattern='^track$'))
    app.add_handler(CallbackQueryHandler(back_home, pattern='^back_home$'))
    app.add_handler(CallbackQueryHandler(adm_add_info, pattern='^adm_add$'))
    app.add_handler(CallbackQueryHandler(adm_list_btn, pattern='^adm_list$'))
    app.add_handler(CallbackQueryHandler(adm_price_info, pattern='^adm_price_menu$'))
    app.add_handler(CallbackQueryHandler(adm_stock_info, pattern='^adm_stock_menu$'))
    app.add_handler(CallbackQueryHandler(adm_photo_info, pattern='^adm_photo$'))
    app.add_handler(CallbackQueryHandler(adm_orders_list, pattern='^adm_orders$'))
    app.add_handler(CallbackQueryHandler(adm_questions_list, pattern='^adm_questions$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.add_handler(MessageHandler(filters.PHOTO, handle_msg))
    print("✅ ربات فروشگاه فرشته آماده‌ست!")
    import os as _os
    _port = int(_os.environ.get("PORT", 8080))
    app.run_polling(port=_port)

if __name__ == '__main__':
    main()
