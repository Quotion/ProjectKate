<<<<<<< HEAD
from pprint import pprint

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# 1 "ема-502": "ema_502",
# 2 "81-540":  "lvz_540",
# 3 "81-540.2": "lvz_540_2",
# 4 "81-702": "d_702",
# 5 "81-703": "e_703",
# 6 "81-707": "ezh_707",
# 7 "81-710": "ezh3_710",
# 8 "81-717-мвм": "msk_717",
# 9 "81-717-лвз": "lvz_717",
# 10 "81-717.5к": "lvz_717_5k",
# 11 "81-717.5а": "msk_717_5a",
# 12 "81-717.5м": "msk_717_5m",
# 13 "81-717.5п": "msk_717_5p",
# 14 "81-717j": "j717",
# 15 "81-718": "tisu_718",
# 16 "81-720": "yauza_720",
# 17 "81-720а": "yauza_720_a",
# 18 "81-722-new": "ubik_722_new",
# 19 "81-722": "ubik_722",
# 20 "81-722.1": "ubik_722_1",
# 21 "81-722.3": "ubik_722_3",
# 22 "81-740": "mvm_740",
# 23 "81-760": "oka_760",
# 24 "81-760a": "oka_760a"


def get_time_train(data, train):

    all_time, label, time = 0, list(), list()

    for info in data:
        if "ема-502" == train:
            time.append(info.ema_502)
            label.append(info.date)
            all_time += info.ema_502
        elif "81-540" == train:
            time.append(info.lvz_540)
            label.append(info.date)
            all_time += info.lvz_540
        elif "81-540.2" == train:
            time.append(info.lvz_540_2)
            label.append(info.date)
            all_time += info.lvz_540_2
        elif "81-702" == train:
            time.append(info.d_702)
            label.append(info.date)
            all_time += info.d_702
        elif "81-703" == train:
            time.append(info.e_703)
            label.append(info.date)
            all_time += info.e_703
        elif "81-707" == train:
            time.append(info.ezh_707)
            label.append(info.date)
            all_time += info.ezh_707
        elif "81-710" == train:
            time.append(info.ezh3_710)
            label.append(info.date)
            all_time += info.ezh3_710
        elif "81-717-мвм" == train:
            time.append(info.msk_717)
            label.append(info.date)
            all_time += info.msk_717
        elif "81-717-лвз" == train:
            time.append(info.lvz_717)
            label.append(info.date)
            all_time += info.lvz_717
        elif "81-717.5к" == train:
            time.append(info.lvz_717_5k)
            label.append(info.date)
            all_time += info.lvz_717_5k
        elif "81-717.5а" == train:
            time.append(info.msk_717_5a)
            label.append(info.date)
            all_time += info.msk_717_5a
        elif "81-717.5м" == train:
            time.append(info.msk_717_5m)
            label.append(info.date)
            all_time += info.msk_717_5m
        elif "81-717.5п" == train:
            time.append(info.msk_717_5p)
            label.append(info.date)
            all_time += info.msk_717_5p
        elif "81-717j" == train:
            time.append(info.j717)
            label.append(info.date)
            all_time += info.j717
        elif "81-718" == train:
            time.append(info.tisu_718)
            label.append(info.date)
            all_time += info.tisu_718
        elif "81-720" == train:
            time.append(info.yauza_720)
            label.append(info.date)
            all_time += info.yauza_720
        elif "81-720а" == train:
            time.append(info.yauza_720_a)
            label.append(info.date)
            all_time += info.yauza_720_a
        elif "81-722-new" == train:
            time.append(info.ubik_722_new)
            label.append(info.date)
            all_time += info.ubik_722_new
        elif "81-722" == train:
            time.append(info.ubik_722)
            label.append(info.date)
            all_time += info.ubik_722
        elif "81-722.1" == train:
            time.append(info.ubik_722_1)
            label.append(info.date)
            all_time += info.ubik_722_1
        elif "81-722.3" == train:
            time.append(info.ubik_722_3)
            label.append(info.date)
            all_time += info.ubik_722_3
        elif "81-740" == train:
            time.append(info.mvm_740)
            label.append(info.date)
            all_time += info.mvm_740
        elif "81-760" == train:
            time.append(info.oka_760)
            label.append(info.date)
            all_time += info.oka_760
        elif "81-760а" == train:
            time.append(info.oka_760a)
            label.append(info.date)
            all_time += info.oka_760a

    return all_time, label, time


async def create_figure(data, train):
    text = list()
    all_time, label, time = get_time_train(data, train)

    if all_time == 0:
        return None

    for i in range(0, len(time)):
        text.append(f'{label[i]} вы играли за пультом {datetime.datetime.utcfromtimestamp(time[i]).strftime("%H:%M:%S")}')

    pprint(time)
    pprint(label)

    plt.plot_date(label, time, marker="o")
    plt.title(f'График времени проведенного за пультом {train.upper()}', fontsize=10)
    plt.ylabel("Время в сек.")
    plt.xlabel("Дата")
    plt.gcf().autofmt_xdate()
    plt.grid(alpha=0.8)

    plt.savefig('stuff/statistics.png')

    plt.close()

    all_time = str(datetime.timedelta(seconds=all_time))

    if all_time.find("days") != -1:
        all_time = all_time.replace("days", "дн")
    else:
        all_time = all_time.replace("day", "дн")

    if all_time.find("weeks") != -1:
        all_time = all_time.replace("weeks", "нед")
    else:
        all_time = all_time.replace("week", "нед")

=======
from pprint import pprint

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# 1 "ема-502": "ema_502",
# 2 "81-540":  "lvz_540",
# 3 "81-540.2": "lvz_540_2",
# 4 "81-702": "d_702",
# 5 "81-703": "e_703",
# 6 "81-707": "ezh_707",
# 7 "81-710": "ezh3_710",
# 8 "81-717-мвм": "msk_717",
# 9 "81-717-лвз": "lvz_717",
# 10 "81-717.5к": "lvz_717_5k",
# 11 "81-717.5а": "msk_717_5a",
# 12 "81-717.5м": "msk_717_5m",
# 13 "81-717.5п": "msk_717_5p",
# 14 "81-717j": "j717",
# 15 "81-718": "tisu_718",
# 16 "81-720": "yauza_720",
# 17 "81-720а": "yauza_720_a",
# 18 "81-722-new": "ubik_722_new",
# 19 "81-722": "ubik_722",
# 20 "81-722.1": "ubik_722_1",
# 21 "81-722.3": "ubik_722_3",
# 22 "81-740": "mvm_740",
# 23 "81-760": "oka_760",
# 24 "81-760a": "oka_760a"


def get_time_train(data, train):

    all_time, label, time = 0, list(), list()

    for info in data:
        if "ема-502" == train:
            time.append(info.ema_502)
            label.append(info.date)
            all_time += info.ema_502
        elif "81-540" == train:
            time.append(info.lvz_540)
            label.append(info.date)
            all_time += info.lvz_540
        elif "81-540.2" == train:
            time.append(info.lvz_540_2)
            label.append(info.date)
            all_time += info.lvz_540_2
        elif "81-702" == train:
            time.append(info.d_702)
            label.append(info.date)
            all_time += info.d_702
        elif "81-703" == train:
            time.append(info.e_703)
            label.append(info.date)
            all_time += info.e_703
        elif "81-707" == train:
            time.append(info.ezh_707)
            label.append(info.date)
            all_time += info.ezh_707
        elif "81-710" == train:
            time.append(info.ezh3_710)
            label.append(info.date)
            all_time += info.ezh3_710
        elif "81-717-мвм" == train:
            time.append(info.msk_717)
            label.append(info.date)
            all_time += info.msk_717
        elif "81-717-лвз" == train:
            time.append(info.lvz_717)
            label.append(info.date)
            all_time += info.lvz_717
        elif "81-717.5к" == train:
            time.append(info.lvz_717_5k)
            label.append(info.date)
            all_time += info.lvz_717_5k
        elif "81-717.5а" == train:
            time.append(info.msk_717_5a)
            label.append(info.date)
            all_time += info.msk_717_5a
        elif "81-717.5м" == train:
            time.append(info.msk_717_5m)
            label.append(info.date)
            all_time += info.msk_717_5m
        elif "81-717.5п" == train:
            time.append(info.msk_717_5p)
            label.append(info.date)
            all_time += info.msk_717_5p
        elif "81-717j" == train:
            time.append(info.j717)
            label.append(info.date)
            all_time += info.j717
        elif "81-718" == train:
            time.append(info.tisu_718)
            label.append(info.date)
            all_time += info.tisu_718
        elif "81-720" == train:
            time.append(info.yauza_720)
            label.append(info.date)
            all_time += info.yauza_720
        elif "81-720а" == train:
            time.append(info.yauza_720_a)
            label.append(info.date)
            all_time += info.yauza_720_a
        elif "81-722-new" == train:
            time.append(info.ubik_722_new)
            label.append(info.date)
            all_time += info.ubik_722_new
        elif "81-722" == train:
            time.append(info.ubik_722)
            label.append(info.date)
            all_time += info.ubik_722
        elif "81-722.1" == train:
            time.append(info.ubik_722_1)
            label.append(info.date)
            all_time += info.ubik_722_1
        elif "81-722.3" == train:
            time.append(info.ubik_722_3)
            label.append(info.date)
            all_time += info.ubik_722_3
        elif "81-740" == train:
            time.append(info.mvm_740)
            label.append(info.date)
            all_time += info.mvm_740
        elif "81-760" == train:
            time.append(info.oka_760)
            label.append(info.date)
            all_time += info.oka_760
        elif "81-760а" == train:
            time.append(info.oka_760a)
            label.append(info.date)
            all_time += info.oka_760a

    return all_time, label, time


async def create_figure(data, train):
    text = list()
    all_time, label, time = get_time_train(data, train)

    if all_time == 0:
        return None

    for i in range(0, len(time)):
        text.append(f'{label[i]} вы играли за пультом {datetime.datetime.utcfromtimestamp(time[i]).strftime("%H:%M:%S")}')

    pprint(time)
    pprint(label)

    plt.plot_date(label, time, marker="o")
    plt.title(f'График времени проведенного за пультом {train.upper()}', fontsize=10)
    plt.ylabel("Время в сек.")
    plt.xlabel("Дата")
    plt.gcf().autofmt_xdate()
    plt.grid(alpha=0.8)

    plt.savefig('stuff/statistics.png')

    plt.close()

    all_time = str(datetime.timedelta(seconds=all_time))

    if all_time.find("days") != -1:
        all_time = all_time.replace("days", "дн")
    else:
        all_time = all_time.replace("day", "дн")

    if all_time.find("weeks") != -1:
        all_time = all_time.replace("weeks", "нед")
    else:
        all_time = all_time.replace("week", "нед")

>>>>>>> 75b13045fc71e61cb736d610ba0be5d6d89e8926
    return {"text": text, "time": all_time}