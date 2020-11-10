import matplotlib.pyplot as plt
import datetime


# 08 - Ема-502
# 09 - Д (81-702)
# 10 - Е (81-703)
# 11 - Еж (81-707)
# 12 - Еж3 (81-710)
# 13 - Номерной МВМ (81-717)
# 14 - Номерной ЛВЗ (81-717)
# 15 - ТИСУ (81-718)
# 16 - Яуза (81-720)
# 17 - Юбилейный (81-722)
# 18 - Пришелец СПБ (81-540.2)
# 19 - ОКА (81-760)
# 20 - ОКА ("баклажан" 81-760А)


async def create_figure(data):
    time, text, labels = list(), list(), list()

    all_time = data.ema_502 + data.d_702 + data.e_703 + data.ezh_707 + data.ezh3_710 + data.mvm_717 + data.lvz_717 +\
               data.tisu_718 + data.yauza_720 + data.sbp_722 + data.alien + data.oka_760 + data.oka_760a

    if all_time == 0 or all_time < 600:
        return [], 0

    time.append(data.ema_502)
    labels.append("Ема-502")
    time.append(data.d_702)
    labels.append("81-702")
    time.append(data.e_703)
    labels.append("81-703")
    time.append(data.ezh_707)
    labels.append("81-707")
    time.append(data.ezh3_710)
    labels.append("81-710")
    time.append(data.mvm_717)
    labels.append("МВМ")
    time.append(data.lvz_717)
    labels.append("СПБ")
    time.append(data.tisu_718)
    labels.append("81-718")
    time.append(data.yauza_720)
    labels.append("81-720")
    time.append(data.sbp_722)
    labels.append("81-722")
    time.append(data.alien)
    labels.append("81-540.2")
    time.append(data.oka_760)
    labels.append("81-760")
    time.append(data.oka_760a)
    labels.append("81-760А")

    labels = ["{} - {}".format(f"0{v / all_time:.2%}" if (v / all_time) * 100 < 9.99 else f"{v / all_time:.2%}", n)
              for n, v in zip(labels, time)]

    time.sort(reverse=True)
    labels.sort(reverse=True)

    for i in range(0, len(time)):
        text.append(f'{labels[i]}: {datetime.datetime.fromtimestamp(time[i]).strftime("%H:%M:%S")}')

    time = [x // 60 for x in time]

    plt.rc('xtick', labelsize=7)
    plt.rc('ytick', labelsize=7)
    plt.rc('figure', figsize=(13, 5))

    plt.bar(labels, time, width=0.5)
    plt.ylabel("Время (мин.)")

    plt.savefig('statistics.png')

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

    return text, all_time
