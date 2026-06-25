IMAGE_POOL = [
    "https://images.pexels.com/photos/931162/pexels-photo-931162.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1128782/pexels-photo-1128782.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1330219/pexels-photo-1330219.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/104827/carnation-flower-pink-carnation-104827.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2111192/pexels-photo-2111192.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1470166/pexels-photo-1470166.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/931173/pexels-photo-931173.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/3408744/pexels-photo-3408744.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/265036/pexels-photo-265036.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2893685/pexels-photo-2893685.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/247917/pexels-photo-247917.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/169193/pexels-photo-169193.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/772808/pexels-photo-772808.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1464200/pexels-photo-1464200.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2962196/pexels-photo-2962196.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1027454/pexels-photo-1027454.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1080/flowers-nature-flora-beautiful.jpg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/931162/pexels-photo-931162.jpeg?auto=compress&cs=tinysrgb&w=800",
]

TITLES = [
    "Цветы Лета",
    "Акция 101 и 151 Рубиновая Роза",
    "Премиальные Пионы",
    "Персиковый Жемчуг",
    "Лето в Милане",
    "Красочные кенийские розы",
    "Восторг Любви",
    "Акция Орхидеи Ультрамарин",
    "Амальфи",
    "Комплимент",
    "Пионы и розы мисти",
    "Акция Милые Хризантемы",
    "Хит Просто Любовь",
    "Головокружительная Корзина Пионов",
    "Цветы и макаронс в коробке",
    "Прага",
    "Цветущая сакура",
    "Букет из 15 зелено-розовых роз в крафте Кения 40 см.",
    "Тайна Орхидеи",
    "Букет Девушка – Весна",
    "Корзина \"Гранд\"",
    "Жозефина",
    "Южный бриз",
    "Акция Корзина 251 Рубиновая Роза",
    "Арабская Сказка",
    "Букет «Клеопатра»",
    "Лунная Серенада",
    "Ангельские Пионы",
    "Сад Моне",
    "Мисти земляника",
    "Любимые Подсолнухи",
    "Райская Оранжерея",
    "Новый Космическая Страсть",
    "Стаккато",
    "Бархатное Сердце",
    "Богемный Шик",
    "7 Роз 60 см Эквадорские Персиковые Шиммер",
    "Море Нежности",
    "Букет «Моя вселенная»",
    "Букет из роскошных пионов , гортензий и маттиолы Для самой милой",
    "Монобукет из красных пионов",
    "Розовый зефир",
    "Хит Белые Пионы",
    "Небесный сапфир",
    "Пионовидные Мисти Баблс",
    "Солнечное Настроение",
    "Фрида Кало",
    "Красные Розы Эквадор",
    "Сумочка с орхидеями и эвкалиптом",
    "Адажио",
    "Ласковый Свет",
    "Букет «Великолепная»",
    "Цветущая Нежность",
    "Букет из 11 роз разных цветов Россия 60 см.",
    "Дуо Пионы и Гортензия",
    "Коллаж из чувств",
    "Цветы в коробке «Белый берег»",
    "Страстные Красные Розы",
    "сочный букет из красных пионов и гортензий",
    "Люблю Тебя",
]

CATEGORY_RULES = [
    ("basket", ["корзин", "корзина"], [13, 14, 15]),
    ("box", ["коробк", "сумочка"], [14, 15, 11]),
    ("orchid", ["орхид"], [6, 16, 9]),
    ("peony", ["пион"], [0, 9, 11]),
    ("rose", ["роз"], [2, 8, 17]),
    ("yellow", ["подсолн", "солнеч", "лето"], [3, 7, 14]),
    ("white", ["бел", "нежн", "светл"], [1, 10, 11]),
    ("lilac", ["сирен", "лаванд", "фиолет", "ультрамар"], [5, 9, 11]),
    ("blue", ["синий", "сапфир", "космич", "бриз"], [6, 16, 18]),
    ("autumn", ["хризант", "оранж", "осен", "бриз"], [4, 10, 18]),
    ("mixed", ["микс", "комплимент", "коллаж", "клеопатра", "стаккато", "богем", "адажио", "великолепная", "нежность"], [7, 11, 0]),
]


def _category_for_title(title):
    lowered = title.lower()
    for category, keywords, _ in CATEGORY_RULES:
        if any(keyword in lowered for keyword in keywords):
            return category
    return "mixed"


def _gallery_indexes(category, seed):
    base_map = {
        "basket": [[13, 14, 18], [13, 15, 19], [14, 18, 12]],
        "box": [[14, 15, 11], [11, 15, 19], [14, 12, 18]],
        "orchid": [[6, 16, 9], [6, 18, 16], [16, 9, 6]],
        "peony": [[0, 9, 11], [0, 1, 7], [9, 11, 0]],
        "rose": [[2, 8, 17], [2, 17, 12], [2, 18, 8]],
        "yellow": [[3, 7, 14], [3, 14, 18], [3, 7, 19]],
        "white": [[1, 10, 11], [1, 11, 12], [10, 11, 1]],
        "lilac": [[5, 9, 11], [5, 11, 9], [9, 5, 18]],
        "blue": [[6, 16, 18], [6, 18, 16], [16, 6, 9]],
        "autumn": [[4, 10, 18], [4, 18, 15], [10, 4, 19]],
        "mixed": [[7, 11, 0], [7, 0, 12], [11, 7, 18]],
    }
    variants = base_map[category]
    return variants[seed % len(variants)]


def _price_for_title(title, seed):
    lowered = title.lower()
    if "корзин" in lowered or "коробк" in lowered:
        base = 3400
    elif "орхид" in lowered:
        base = 3600
    elif "пион" in lowered:
        base = 3000
    elif "роз" in lowered:
        base = 2800
    elif "подсолн" in lowered or "солнеч" in lowered:
        base = 2200
    elif "хризант" in lowered:
        base = 2400
    elif "макаронс" in lowered:
        base = 3900
    else:
        base = 2600
    return base + (seed % 5) * 180


def _description_for_category(category):
    return {
        "basket": "Подарочная цветочная композиция в корзине с объемной подачей.",
        "box": "Стильная композиция в коробке с аккуратной флористической подачей.",
        "orchid": "Элегантная композиция с акцентом на изящные орхидеи.",
        "peony": "Нежный букет с крупными пышными соцветиями и мягкой фактурой.",
        "rose": "Классический букет роз с выразительной и торжественной подачей.",
        "yellow": "Яркий солнечный букет для теплого и позитивного повода.",
        "white": "Светлая воздушная композиция в чистой и спокойной гамме.",
        "lilac": "Легкий букет в сиренево-лавандовой палитре.",
        "blue": "Необычный современный букет с холодным цветовым акцентом.",
        "autumn": "Теплая композиция с мягкими сезонными оттенками.",
        "mixed": "Авторский букет с гармоничным сочетанием нескольких оттенков.",
    }[category]


def _tags_for_category(category):
    return {
        "basket": ["корзина", "подарок", "объемный", "цветы"],
        "box": ["коробка", "подарок", "стильный", "цветы"],
        "orchid": ["орхидея", "элегантный", "премиальный", "изящный"],
        "peony": ["пионы", "нежный", "пышный", "подарок"],
        "rose": ["розы", "романтика", "классика", "подарок"],
        "yellow": ["яркий", "лето", "солнце", "букет"],
        "white": ["светлый", "нежный", "воздушный", "букет"],
        "lilac": ["сиреневый", "нежный", "лёгкий", "букет"],
        "blue": ["синий", "современный", "оригинальный", "букет"],
        "autumn": ["теплый", "осень", "уютный", "букет"],
        "mixed": ["авторский", "микс", "нежный", "подарок"],
    }[category]


def _build_demo_products():
    products = []
    for seed, title in enumerate(TITLES):
        category = _category_for_title(title)
        gallery = _gallery_indexes(category, seed)
        products.append(
            {
                "title": title,
                "price": _price_for_title(title, seed),
                "image_url": IMAGE_POOL[gallery[0]],
                "gallery_images": [IMAGE_POOL[i] for i in gallery],
                "tags": _tags_for_category(category),
                "description": _description_for_category(category),
            }
        )
    return products


PRODUCTS = _build_demo_products()
DEMO_PRODUCTS = PRODUCTS
