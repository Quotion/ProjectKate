thanks = "Спасибо, что добавили меня на сервер {}!\n" \
         "Я с удовольствием поработую на ваш сервер, но мне нужно указать какие каналы, для чего нужны.\n" \

channels = "Я не смогу ничего сделать пока вы не укажите каналы!" \
           "\nКаналы, которые стоит указать:" \
           "\n1. Основной канал: `{0}основной <хайлайт канала>`" \
           "\n2. Канал новостей: `{0}новости <хайлайт канала>`" \
           "\n3. Канал логов: `{0}логи <хайлайт канала>`"

so_many_channels = "{}, очень интересно конечно, что вы ввели 2 канала, но мне нужен только 1."

not_enough_channels = "{}, вы ничего не ввели в качетсве аргумента. `{}<канал> <хайлайт канала>`"

command_not_found = "{}, команды ***{}*** не существует. Возможно вы допустили ошибку в слове команды."

not_enough_words = "{}, не достаточно аргументов в команде."

account_create = "{}, ваш аккаунт создан, пожалуйста повторите команду."

error_json_info = "{}, при заходе на сервер, у меня произошла ошибка. Сейчас она исправлена. Повторите команду."

channel_saved = "{}, канал *{}* сохранён как канал для {}"

please_confirm = "{}, пожалуйста убедитесь, что в этот канал никто не сможет писать, а также ставить реакции! " \
                 "\nВ противном случае, обновление статуса может работать неверно."

status_already_exist = "Статус для серверов уже доступен!\n" \
                       "Просто введите ip сервера и наслаждайтесь.\n" \
                       "Если же вы хотите поменять канал введите <**удалить_статус**> и введите его занаво."

status_info = "{}, чтобы вывести информацию по серверу введите\n**{}ip <ip>:<port>**"

server_not_valid = "{} сервер, ip которого вы ввели, сейчас не доступен. " \
                   "\nЕсли вы уверены, что ip ({}) введен верно, то просто введите всё тоже самое, " \
                   "но в конце через пробел добавтье 1."

ip_exist = "{} такой ip уже есть."

nothing_to_delete = "{}, вы пытаетесь удалить, то что не существует."

something_went_wrong_ip = "Хммм... {}, вы ввели некоректные данные. Пример: **{}ip <ip>:<port>**"

no_private_message = "К сожалению, этой командой нельзя пользоваться в личных сообщениях. Пожалуйста учтите это!"

unknown_error = "Хм, похоже, это что-то за гранью предусмотренного системой:\n"

something_went_wrong = "Что-то пошло не так. Возможные причины:" \
                       "\n1) системная ошибка" \
                       "\n2) непредусмотренного исключения" \
                       "\n3) бот решил отдохнуть."

profile_create = "{}, ваш профиль только что был создан. Пожалуйста, повторите команду."

missing_permission = "{}, у вас недостаточно прав, чтобы использовать эту команду."

message_not_found = "{}, похоже сообщения не хватает." \
                    "\nЭто произошло из-за того что кто-то удалил сообщение (возможно по другой причине)." \
                    "\nПовторите ввод ip, и вывод статуса восстановится."

just_a_command = "{}, похоже, что вы ввели только команду (без данных). Пример: **{}<команда> <число>**"

not_a_number = "{}, вы ввели не число! Пример: **{}<команда> <число>**"

more_than_have = "{}, вы ввели значение {} больше, чем имеете."

not_correct = "{}, вы ввели неверное значение рейтинга."

roulette_ended = "Рулетка на сегодня для Вас, {}, оконечна!"

rating_sale = "{}, вы получили {} {} по {} за штуку."

swaps = "{} поменял **{}** {} на **{}** {}"

wrong_ban_data = '{}, что-то тут не так.\nПример: **Катерина бан <SteamID или Discord> <время в минутах> <причина>**.' \
                 '\nЕсли причину не указать, она автоматически получится **"reason"**'

time_not_right = "{}, время которое вы ввели, не точное."

steamid_not_exist = "{}, похоже, что введеное вами SteamID или Discord игрока нету в базе данных."

ban_message = "{}, вы забанили игрока.\nSteamID (Discord) забаненого - {}\nВремя до окончания бана: {} мин." \
              "\nПричина: {}."

already_in_ban = "{}, этот игрок уже в бане."

not_synchronized = "{}, игрок, {}, не синхронизирован с базой данных."

unban_message = "{}, вы разбаниои игрока.\nSteamID (Discord) разабненого: {}\nДата разбана: {}."

successful_find = "{}, игрок успешно найден.\nДля проверки введите эту же команду."

not_in_ban = "{}, игрок, SteamID (Discord) которого {}, не забанен."

successful_added = "{}, ваш SteamID успешно добавлен и синхронизирован."

steamid_not_in_bd = "К сожалению, такого SteamID в базе данных нет. Либо вы не заходили на сервера, либо указываете " \
                    "SteamID с ошибкой."

len_of_command = "{}, вы не ввели чего-то. Пример: **{}ранг <SteamID или Discord (можно несколько)> <ранг>"

steamid_or_discord = "{}, либо только SteamID, либо только Discord"

not_highlight = "{}, а кому ранг то ставить? Такого человека нет в базе данных."

man_not_in_bd = "{}, у игрока {} нету профиля, чтобы изменять ему роль."

profile_not_exist = "{}, вы не создали аккаунт! **{}профиль**, чтобы его создать."

steamid_already_used = "{}, похоже вы пытаетесь ввести SteamID, который уже используете или использует кто-то другой."

rank_changed = "{}, вы сменили ранг (группу) игрока на ***{}***." \
               "\nSteamID (Discord) игрока: {}"

you_not_synchronized = "{}, вы не синхронизированы с базой данных. Для того чтобы синхронизироваться вам понадобится ваш SteamID."

for_statistics = "{}, если хотите увидеть собственную статистику, посидите в кабине, хотя бы 10 секунд."

creating_bank_account = "{}, счёт №***{}*** успешно открыт."

account_exist = "{}, похоже у вас уже есть счёт в банке."

delete_bank_account = "{}, счёт №***{}*** успешно закрыт"

nothing_to_close = "{}, у Вас нет счёта в банке, поэтому и закрывать нечего."

bill_already_open = "{}, вы уже открыли счёт в другом банке."

successful_put = "{}, деньги успешно переведены в банк."

successful_get = "{}, деньги успешно сняты со счёта."

account_not_exist = "{}, чтобы узнать состояение своего счёта, его надо открыть: {}открыть_счёт"

save_name_bank = "Имя банка успешно сохранено как \"{}\""

save_name_currency = "Имя валюты успешно сохранено как \"{}\""

not_enough_money = "{}, у Вас не достаточно {} для того чтобы снять/положить их в банк."

bill_not_found = "{}, возможно:" \
                 "\n1) такого счёта не существует" \
                 "\n2) в его номере допущена ошибка"

transaction_error = "{}, оба входных параметра должны быть числами.\n" \
                    "Пример: {}перевести <номер счёта> <количество ВС>"

company_not_found = "{}, такой компании не существует."

invests_yet = "{}, вы уже инвестировали в эту компанию"

more_than_hundred = "{}, нельзя покупать больше 1000 акций, иначе это спровоцирует кризис."

successful_buy = "{}, вы приобрели акции компании {} общей стоимостью {} NEO."

not_buy_anything = "{}, вы пока не купили не одной акции"

successful_transfer = "{}, вы успешно перевели {} NEO на счёт №{}"

successful_sale = "{}, вы продали акции компании {} за {} NEO."

already_in_voice = "{}, бот уже в голосовом канале."

not_in_voice = "{}, бот не находится не в одном из голосовых каналов."

role_not_exist = "{}, такой роли не сущесвтует."

not_enough_gold = "{}, недостаточно средст." \
                  "\nVIP - 500 тыч. золотой ВС" \
                  "\nPremium - 1 млн. золотой ВС"

buying_vip = "{}, с преобритением VIP на сервере за 1 млн."

buying_premium = "{}, поздравляю Вас с преобритение самой престижной роли на сервере Premium за 10 млн."

the_same_ranks = "{}, вы собираетесь купить ранг, который у вас уже есть."

heh_mdam = "{}, вы сломали систему и купили супер администратора на сервере за 100 млн."

promo_event = ["Получите {} {} и вам станят ясно, что ничего в мире не вечно.\nПромокод - `{}`",
               "Тут мне администраторы нашептали, что стоит вам дать кое-что интересное на {} {}\nПромокод - `{}`",
               "Uno, uno, uno, dos, cuatro. Промокодами на {} {}\nПромокод - `{}`",
               "А вы знали что на провинции есть бесплатное пиво? И мы не знали. В прочем, еще есть промокод на {} {}\nПромокод - `{}`",
               "Ало Галочка, ты сейчас умрешь. У меня есть прмокод на {} {}\nВставте текст: `{}`",
               "Шифр энигмы E3: `m xas 100 ybfvod bo ulu obep ywhr xyactq wbahe.`"\
               "\n`ROTOR1`: март; `Позиция1`: 8pm; `Кольцо1`: 9pm"\
               "\n`ROTOR2`: август; `Позиция2`: 4pm; `Кольцо2`: 9am"\
               "\n`ROTOR3`: январь; `Позиция3`: 3am; `Кольцо3`: 1am"\
               "\n`Коммутационная панель`: Позиция1 + Кольцо1 + <пробел> + Позиция2 + Кольцо2 + <пробел> + Позиция3 + Кольцо3"\
               "\n{} {}\nПромокод - `{}`",
               "Сейчас никто не скажет, что промокоды это плохо. Потому что {} {} на дороге не валяются\nПромокод - `{}`",
               "Однажды, парень рассказал, что нашёл {} {}\nПлакала половина маршрутки, а этим парнем был Альберт Эйнштейн\nПромокод - `{}`",
               "А ты готов прыгнуть в пучину отчаиния за {} {}? И я нет, поэтому и не надо.\nПромокод - `{}`",
               "Плачу каждому по {} {}, кто сможет написать слово `здесь мог бы быть норанк, но его тут нет` на латинице.\nПромокод - `{}`",
               "Как насчёт того, чтобы начать обзывать норанк за {} {}?\nПромокод - `{}`"]

promo_is_enter = "{}, промокод уже был использован"

promo_is_off = "{}, на вашем сервере промокоды не доступны!"

promo_is_active = "{}, поздравляю! Вы активировали промокод на {} {}"

promo_already_on = "{}, промокоды уже доступны у вас на сервере!"

promo_on = "{}, прокоды теперь доступны! Чтобы выключить отсылку промокодов введите {}выкл_промокоды." \
           "\n Теперь ждите пока в какой-то из каналов придёт первый промокод!"

promo_already_off = "{}, промокоды уже выключены!"

promo_off = "{}, прокоды теперь НЕ доступны! Чтобы включить отсылку промокодов введите {}вкл_промокоды."

answers_out_of_range = "{}, больше 9 вариантов добавить не возможно."

question_not_post = "{}, вы не поставили вопрос для голосования.\nПример: {}выбор `На сколько вагонов расчитанны станции Сокольнеческой линии?` `+6 вагонов` `+8 вагонов +не знаю`"

cooldown = "{}, ожидайте ещё {} сек. перед тем как повторить команду."

role_dont_exist = "{}, такой роли на РП-сессии нет."

dont_write = "{}, вы не писали заявку на РП-сессию." \
             "\nЗаполнение заявки: {}заявка `машинист` `76` `хочу кататься по 2 линии и иметь всех чикс с выхино`"

already_in_rp = "{}, вы уже записаны на РП-сессию."

you_not_right = "{}, вы указали неверные параметры."\
                "\nЗаполнение заявки: {}заявка `машинист` `76` `хочу кататься по 2 линии и иметь всех чикс с выхино`"

not_enough_words_to_rp = "{}, вы указали слишком много (или мало) параметров."\
                         "\nЗаполнение заявки: {}заявка `машинист` `76` `хочу кататься по 2 линии и иметь всех чикс с выхино`"

to_many_dch = "{}, вы указали слишком много (или мало) параметров для этой роли.\nПример: {}заявка `дцх` `1`"

success_add_dch = "{}, вы успешно добавлены на РП-сессию в роли `ДЦХ` по {}-й линии."

success_add_dscp = "{}, вы успешно добавлены на РП-сессию в роли `ДСЦП` по станции `{}`."

success_add_shunting_driver = "{}, вы успешно добавлены на РП-сессию в роли `Маневрового Машиниста` по станции: `{}`."

success_add_driver = "{}, вы успешно добавлены на РП-сессию в роли `Машиниста` состава под номером `{}`."

dch_already_taken = "{}, ДЦХ уже есть на линии."

dscp_alert = "{}, ДСЦП уже есть на такой станции или их число уже достаточно для РП-сессии."

number_already_taken = "{}, такой номер состава уже присутствует на РП-сессии."

success_delete = "{}, ваша заявка на РП-сессию удалена."

driver_shunting = "{}, в данном рп манверовый машинистов нет."

driver_shunting_already_exist = "{}, маневровых машинистов уже достаточно на РП-сессии"

line_not_exist = "{}, такой линии нет на РП-сессии."

station_not_exist = "{}, такой станции на РП-сессии нет (или допущена ошибка в её написании)"

number_should_be_number = "{}, номер состава должен быть числом, а не чем-то иным."

number_not_number = "{}, вы ввели число либо меньше 0, либо больше 1000."

attention_but_success = "{}, машинистов на РП-сессии достаточно, но вы успешно добавлены."

successfully_added_to_botban = "{}, вы успешно добавили человека в игнорируемые ботом"

text_not_found = "{}, вы не ввели текст для вывода объявления"

text_for_adverting = "Здраствуйте, уважаемые @everyone.\nВ связи с проведением РП-сессии {} объявляется открытие заявок на неё.\nРП-сессия будет проходить `{}` по МСК.\n\n"\
                     "В РП-сессии будут участвовать **{}** человек:\n`ДЦХ` на **{}** линию(-и)\n`ДСЦП` по **{}** станции(-иям)\n`Маневровые машинисты`, в количестве **{}** чел.\n`Машинисты`, желательно набрать **{}** чел.\n\n"\
                     "В ходе голосования была выбрана карта `{}`\n\n"\
                     "Следование составов будет осуществляться по `{}`\n\n"\
                     "{}\n\n"\
                     "Ниже представленны участники данной РП-сессии:\n"
