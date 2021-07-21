import logging
from typing import Any, Dict, List, Optional, Tuple

from . import button_menu, utils

STAGES_DICTIONARY: Dict[str, Any] = dict()
AUDIO_URL_TEMPLATE: str = ""


class Transition(object):
    def __init__(self, to_id: str, main_text: str, synonims: List[str]):
        self.to_id = to_id
        self.main_text = main_text
        self.synonims = [
            utils.prepare_phrase(main_text[0]),
        ] + utils.prepare_phrases_list(synonims)

    def must_go(self, selection_text: str) -> bool:
        for word in selection_text.split(" "):
            if word in self.synonims:
                return True

        return False


class Stage(object):
    id: str
    texts: Optional[Tuple[str, str]]
    audio_url: Optional[str]
    transitions: List[Transition]
    default_transition: str

    def __init__(
        self,
        id: str,
        texts: Optional[Tuple[str, str]],
        has_sound: bool,
        transitions: List[Transition],
        default_transition: str,
    ) -> None:

        global AUDIO_URL_TEMPLATE
        self.id = id
        self.texts = texts

        if has_sound:
            self.audio_url = AUDIO_URL_TEMPLATE.format(file_name=self.id)
        else:
            self.audio_url = None

        self.transitions = transitions

        if (transitions is not None) and (len(transitions) > 1):
            bmb = button_menu.ButtonsMenuBuilder()
            for transition in transitions:
                bmb.add_button(transition.main_text[0])
            self.buttons = bmb.get_to_send()
        else:
            self.buttons = None

        self.default_transition = default_transition

    def is_end(self) -> bool:
        return (self.transitions is None) and (self.default_transition is None)

    def is_unconditional(self) -> bool:
        return (self.transitions is None) and (self.default_transition is not None)

    def get_next_stage(self, user_response: Optional[str] = None) -> "Stage":
        global STAGES_DICTIONARY
        if not self.is_unconditional():
            for transition in self.transitions:
                if user_response is not None:
                    user_response_str: str = user_response
                if transition.must_go(user_response_str):
                    return STAGES_DICTIONARY[transition.to_id]

        return STAGES_DICTIONARY[self.default_transition]

    def add_to_dict(self, dictionary) -> None:
        global STAGES_DICTIONARY
        if self.id in STAGES_DICTIONARY:
            logging.info(f"WARNING! {self.id} is already in target dictionary")
        dictionary[self.id] = self

    def add_response_text_and_tts(
        self, current_response: List[str], play_audio: bool = True
    ) -> None:

        if play_audio and self.audio_url is not None:
            current_response[1] += f' <speaker audio_url="{self.audio_url}"> '

        if self.texts is not None:
            current_response[0] += f"{self.texts[0]}"
            current_response[1] += f"\n{self.texts[1]}"


ROOT_STAGE: Optional[Any] = None


def init(audio_url_template):
    global STAGES_DICTIONARY, ROOT_STAGE, AUDIO_URL_TEMPLATE
    AUDIO_URL_TEMPLATE = audio_url_template

    # --------------------------------001--------------------------------
    Stage(
        "001",
        (
            "А что бы ты ей посоветовал? Скажи: дракон или звездочёт?",
            "А что бы ты ей посоветовал? Скажи: \n дракон или звездочёт?",
        ),
        True,
        [
            Transition("101", ("ЗВЕЗДОЧЁТ", "ЗВЕЗДОЧЁТ"), ["звездочётом"]),
            Transition("102", ("ДРАКОН", "ДРАКОН"), ["драконом", "переговоры"]),
        ],
        "101",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------101--------------------------------
    Stage(
        "101",
        (
            "Скажи принцессе: В дорогу? Или в библиотеку?",
            "Скажи принц+ессе: \n В дор+огу? Или в библиотеку?",
        ),
        True,
        [
            Transition(
                "201",
                ("БИБЛИОТЕКА", "БИБЛИОТЕКА"),
                ["библиотеку", "библиотека", "библиотеке", "книги"],
            ),
            Transition("304", ("ДОРОГА", "ДОРОГА"), ["дорогу", "дорога", "путь"]),
        ],
        "201",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------102--------------------------------
    Stage(
        "102",
        (
            "Скажи принцессе: В дорогу? Или в библиотеку?",
            "Скажи принц+ессе: \n В дор+огу? Или в библиотеку?",
        ),
        True,
        [
            Transition(
                "201",
                ("БИБЛИОТЕКА", "БИБЛИОТЕКА"),
                ["библиотеку", "библиотека", "библиотеке", "книги"],
            ),
            Transition("305", ("ДОРОГА", "ДОРОГА"), ["дорогу", "дорога", "путь"]),
        ],
        "201",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------201--------------------------------
    Stage(
        "201",
        (
            "Назови слово: История? Чудовища? Огонь?",
            "Назови слово: \nИстория? Чудовища? Огонь?",
        ),
        True,
        [
            Transition(
                "301", ("ИСТОРИЯ", "ИСТОРИЯ"), ["история", "колдовство", "колдовства"],
            ),
            Transition(
                "302", ("ЧУДОВИЩЕ", "ЧУДОВИЩЕ"), ["чудовищ", "чудовища", "описание"]
            ),
            Transition("303", ("ОГОНЬ", "ОГОНЬ"), ["магические", "формы"]),
        ],
        "301",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------301-305--------------------------------
    Stage("301", None, True, None, "306").add_to_dict(STAGES_DICTIONARY)
    Stage("302", None, True, None, "306").add_to_dict(STAGES_DICTIONARY)
    Stage("303", None, True, None, "306").add_to_dict(STAGES_DICTIONARY)
    Stage("304", None, True, None, "306").add_to_dict(STAGES_DICTIONARY)
    Stage("305", None, True, None, "306").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------306--------------------------------
    Stage(
        "306",
        (
            "Скажи: Охотники? Купцы? Или рудокопы?",
            "Скажи: \n Охотники? Купцы? Или рудокопы?",
        ),
        True,
        [
            Transition(
                "409",
                ("ОХОТНИКИ", "ОХОТНИКИ"),
                ["охотник", "охотниками", "охотникам", "лучник"],
            ),
            Transition("410", ("КУПЦЫ", "КУПЦЫ"), ["купец", "купцам", "купцами"]),
            Transition(
                "411",
                ("РУДОКОПЫ", "РУДОКОПЫ"),
                ["рудокоп", "рудокопам", "описание", "писарем", "писарь"],
            ),
        ],
        "410",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------409--------------------------------
    Stage("409", None, True, None, "551").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------410--------------------------------
    Stage(
        "410",
        (
            "Скажи: Бежать? Или помогать торговцу?",
            "Скаж+и: \n Беж+ать? Или помог+ать торг+овцу?",
        ),
        True,
        [
            Transition(
                "501",
                ("БЕЖАТЬ", "БЕЖАТЬ"),
                ["бежать в лес", "убежать", "убегать", "побеждать", "лес"],
            ),
            Transition(
                "502",
                ("ПОМОГАТЬ", "ПОМОГАТЬ"),
                ["помочь торговцу", "помочь", "торговцу", "помощь"],
            ),
        ],
        "502",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------501-502--------------------------------
    Stage("501", None, True, None, "551").add_to_dict(STAGES_DICTIONARY)
    Stage("502", None, True, None, "552").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------411--------------------------------
    Stage(
        "411",
        ("Посоветуй: Брошку? Или кинжал?", "Посоветуй: \nБр+ошку? Или кинж+ал?"),
        True,
        [
            Transition("504", ("КИНЖАЛ", "КИНЖАЛ"), [],),
            Transition("505", ("БРОШКА", "БРОШКА"), ["брошка", "брошку", "брошь"],),
        ],
        "505",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------504-505--------------------------------
    Stage("504", None, True, None, "553").add_to_dict(STAGES_DICTIONARY)
    Stage("505", None, True, None, "554").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------551--------------------------------
    Stage(
        "551",
        (
            "Что ей ответить? У неё только одна попытка. Назови нужное число!",
            "Что ей ответить? У неё только одна попытка. Назови нужное число!",
        ),
        True,
        [
            Transition("601", ("ШЕСТЬ", "ШЕСТЬ"), ["6"],),
            Transition(
                "602",
                ("ОДНА", "ОДНА"),
                [
                    "ТРИ",
                    "ЧЕТЫРЕ",
                    "ПЯТЬ",
                    "СЕМЬ",
                    "ВОСЕМЬ",
                    "ДЕВЯТЬ",
                    "ДЕСЯТЬ",
                    "ОДИННАДЦАТЬ",
                    "ДВЕНАДЦАТЬ",
                    "ТРИНАДЦАТЬ",
                    "ЗНАЮ",
                    "МОГУ",
                    "ОТВЕТА",
                    "1",
                ],
            ),
            Transition("602", ("ДВЕ", "ДВЕ"), ["2", "ДВА"]),
        ],
        "602",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------601--------------------------------
    Stage(
        "601",
        ("Скажи: Дверца? Или бойница?", "Скажи: \nДверца? Или бойница?",),
        True,
        [
            Transition("801", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("802", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
        ],
        "801",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------602--------------------------------
    Stage(
        "602",
        ("Скажи: Дверца? Или бойница?", "Скажи: \nДверца? Или бойница?",),
        True,
        [
            Transition("801", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("802", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
        ],
        "801",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------552--------------------------------
    Stage(
        "552",
        (
            "Что ей ответить? У неё только одна попытка. Назови нужное число!",
            "Что ей ответить? У неё только одна попытка. Назови нужное число!",
        ),
        True,
        [
            Transition("603", ("ШЕСТЬ", "ШЕСТЬ"), ["6"],),
            Transition(
                "604",
                ("ОДНА", "ОДНА"),
                [
                    "1",
                    "ТРИ",
                    "ЧЕТЫРЕ",
                    "ПЯТЬ",
                    "СЕМЬ",
                    "ВОСЕМЬ",
                    "ДЕВЯТЬ",
                    "ДЕСЯТЬ",
                    "ОДИННАДЦАТЬ",
                    "ДВЕНАДЦАТЬ",
                    "ТРИНАДЦАТЬ",
                    "ЗНАЮ",
                    "МОГУ",
                    "ОТВЕТА",
                ],
            ),
            Transition("604", ("ДВЕ", "ДВЕ"), ["2", "ДВА"]),
        ],
        "604",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------603--------------------------------
    Stage(
        "603",
        ("Скажи: Дверца? Или бойница?", "Скажи: \nДверца? Или бойница?",),
        True,
        [
            Transition("801", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("802", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
        ],
        "801",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------604--------------------------------
    Stage(
        "604",
        ("Скажи: Дверца? Или бойница?", "Скажи: \nДверца? Или бойница?",),
        True,
        [
            Transition("801", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("802", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
        ],
        "801",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------553--------------------------------
    Stage(
        "553",
        (
            "Посоветуй, что ей отдать? Ковёр-самолёт? Или брошку?",
            "Посоветуй, что ей отдать? Ковёр-самолёт? Или брошку?",
        ),
        True,
        [
            Transition(
                "605",
                ("КОВЁР-САМОЛЁТ", "КОВЁР-САМОЛЁТ"),
                ["ковёр", "самолёт", "ковром", "самолётом"],
            ),
            Transition("606", ("БРОШКА", "БРОШКА"), ["брошка", "брошку", "брошь"],),
        ],
        "606",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------605--------------------------------
    Stage(
        "605",
        ("Скажи: Бойница? Или подземный ход?", "Скажи: \nБойница? Или подземный ход?",),
        True,
        [
            Transition("802", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
            Transition(
                "805",
                ("ПОДЗЕМНЫЙ ХОД", "ПОДЗЕМНЫЙ ХОД"),
                ["подземный", "подземным", "ход", "ходом", "подземелье"],
            ),
        ],
        "805",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------606--------------------------------
    Stage("606", None, True, None, "554").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------554--------------------------------
    Stage(
        "554",
        (
            "Назови ответ! Первая? Вторая? Никакая?",
            "Назови ответ! Первая? Вторая? Никакая?",
        ),
        True,
        [
            Transition("607", ("НИКАКАЯ", "НИКАКАЯ"), ["одна"],),
            Transition("608", ("ПЕРВАЯ", "ПЕРВАЯ"), []),
            Transition("608", ("ВТОРАЯ", "ВТОРАЯ"), []),
        ],
        "608",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------607--------------------------------
    Stage(
        "607",
        ("Скажи: Ворота? Дверца? Бойница?", "Скажи: \nВорота? Дверца? Бойница?",),
        True,
        [
            Transition("701", ("ВОРОТА", "ВОРОТА"), [],),
            Transition("807", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("808", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
        ],
        "701",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------608--------------------------------
    Stage(
        "608",
        ("Скажи: Ворота? Дверца? Бойница?", "Скажи: \nВорота? Дверца? Бойница?",),
        True,
        [
            Transition("701", ("ВОРОТА", "ВОРОТА"), [],),
            Transition("807", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("808", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"],),
        ],
        "701",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------701--------------------------------
    Stage(
        "701",
        ("Скажи: Дверца? Или бойница?", "Скажи: \nДверца? Или бойница?",),
        True,
        [
            Transition("807", ("ДВЕРЦА", "ДВЕРЦА"), ["дверцу"],),
            Transition("808", ("БОЙНИЦА", "БОЙНИЦА"), ["бойницу", "башня", "башне"]),
        ],
        "807",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------801-802,805--------------------------------
    Stage("801", None, True, None, "851").add_to_dict(STAGES_DICTIONARY)
    Stage("802", None, True, None, "851").add_to_dict(STAGES_DICTIONARY)
    Stage("805", None, True, None, "851").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------851--------------------------------
    Stage(
        "851",
        (
            "На кого посмотреть принцессе? На гнома? На короля-отца? На звездочёта? На Дракона?",
            "На кого посмотреть принцессе? На гнома? На короля-отца? На звездочёта? На Дракона?",
        ),
        True,
        [
            Transition(
                "901", ("ГНОМ", "ГНОМ"), ["гнома", "рождественский", "рождественского"],
            ),
            Transition(
                "902", ("ОТЕЦ", "ОТЕЦ"), ["отца", "папа", "папу", "король", "короля"]
            ),
            Transition("903", ("ЗВЕЗДОЧЁТ", "ЗВЕЗДОЧЁТ"), ["звездочёта"]),
            Transition("904", ("ДРАКОН", "ДРАКОН"), ["дракона"]),
        ],
        "901",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------901-904--------------------------------
    Stage("901", None, True, None, "951").add_to_dict(STAGES_DICTIONARY)
    Stage("902", None, True, None, "951").add_to_dict(STAGES_DICTIONARY)
    Stage("903", None, True, None, "951").add_to_dict(STAGES_DICTIONARY)
    Stage("904", None, True, None, "951").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------951--------------------------------
    Stage(
        "951",
        (
            "Что тебе кажется правильнее: Сжечь? Оставить?",
            "Что тебе кажется правильнее: \nСжечь? Оставить?",
        ),
        True,
        [
            Transition("1001", ("СЖЕЧЬ", "СЖЕЧЬ"), ["жечь"],),
            Transition("1002", ("ОСТАВИТЬ", "ОСТАВИТЬ"), ["оставлять"]),
        ],
        "1002",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------1001-1002--------------------------------
    Stage("1001", None, True, None, "1051").add_to_dict(STAGES_DICTIONARY)
    Stage("1002", None, True, None, "1051").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------1051--------------------------------
    Stage(
        "1051",
        (
            "Может быть, ты подскажешь ей? Куда ей идти?",
            "Может быть, ты подскажешь ей? Куда ей идти?",
        ),
        True,
        [
            Transition(
                "1101",
                ("ЗЕРКАЛО", "ЗЕРКАЛО"),
                [
                    "зеркалу",
                    "блюдо",
                    "блюду",
                    "серебряное",
                    "серебряному",
                    "каменный",
                    "каменному",
                    "звездочёт",
                    "звездочёту",
                    "звездочётом",
                ],
            ),
            Transition(
                "1102",
                ("ГНОМ", "ГНОМ"),
                [
                    "гномы",
                    "гному",
                    "гномам",
                    "мешки",
                    "подарки",
                    "подарками",
                    "подарков",
                    "сани",
                    "мороз",
                    "санта",
                    "санта-клаус",
                    "плоская",
                ],
            ),
        ],
        "1102",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------1101-1102--------------------------------
    Stage("1101", None, True, None, None).add_to_dict(STAGES_DICTIONARY)
    Stage("1102", None, True, None, None).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------807-808--------------------------------
    Stage("807", None, True, None, "952").add_to_dict(STAGES_DICTIONARY)
    Stage("808", None, True, None, "952").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------952--------------------------------
    Stage(
        "952",
        (
            "Что тебе кажется правильнее: Сжечь? Оставить?",
            "Что тебе кажется правильнее: \nСжечь? Оставить?",
        ),
        True,
        [
            Transition("1003", ("СЖЕЧЬ", "СЖЕЧЬ"), ["жечь"],),
            Transition("1004", ("ОСТАВИТЬ", "ОСТАВИТЬ"), ["оставлять"]),
        ],
        "1004",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------1003-1004--------------------------------
    Stage("1003", None, True, None, "1052").add_to_dict(STAGES_DICTIONARY)
    Stage("1004", None, True, None, "1052").add_to_dict(STAGES_DICTIONARY)

    # --------------------------------1052--------------------------------
    Stage(
        "1052",
        (
            "Если ты заметил то, чего она не заметила, скажи ей слово, то единственное слово, которое поможет.",
            "Если ты заметил то, чего она не заметила, скажи ей слово, то единственное слово, которое поможет.",
        ),
        True,
        [
            Transition(
                "1103",
                ("ФЕНИКС", "ФЕНИКС"),
                [
                    "феникса",
                    "лук",
                    "лука",
                    "колчан",
                    "колчане",
                    "стрелы",
                    "стрелами",
                    "перья",
                    "перьями",
                ],
            ),
        ],
        "1105",
    ).add_to_dict(STAGES_DICTIONARY)

    # --------------------------------1103,1105--------------------------------
    Stage("1103", None, True, None, None).add_to_dict(STAGES_DICTIONARY)
    Stage("1105", None, True, None, None).add_to_dict(STAGES_DICTIONARY)

    # ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT-ROOT

    ROOT_STAGE = STAGES_DICTIONARY["001"]


def get_stage_by_id(id: str) -> Stage:
    global STAGES_DICTIONARY
    return STAGES_DICTIONARY[id]


def get_root_stage() -> Optional[Stage]:
    global ROOT_STAGE
    return ROOT_STAGE
