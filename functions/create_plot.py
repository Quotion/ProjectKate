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
    time = []
    text = []
    labels = []
    all_time = 0

    for i in range(8, 21):
        if data[i] != 0:
            if i == 8:
                time.append(data[i])
                labels.append("Ема-502")
            elif i == 9:
                time.append(data[i])
                labels.append("81-702")
            elif i == 10:
                time.append(data[i])
                labels.append("81-703")
            elif i == 11:
                time.append(data[i])
                labels.append("81-707")
            elif i == 12:
                time.append(data[i])
                labels.append("81-710")
            elif i == 13:
                time.append(data[i])
                labels.append("МВМ")
            elif i == 14:
                time.append(data[i])
                labels.append("СПБ")
            elif i == 15:
                time.append(data[i])
                labels.append("81-718")
            elif i == 16:
                time.append(data[i])
                labels.append("81-720")
            elif i == 17:
                time.append(data[i])
                labels.append("81-722")
            elif i == 18:
                time.append(data[i])
                labels.append("81-740")
            elif i == 19:
                time.append(data[i])
                labels.append("81-760")
            elif i == 20:
                time.append(data[i])
                labels.append("81-760А")

    for i in time:
        all_time += i

    if all_time == 0:
        return [], []

    labels = ["{} - {}".format(f"0{v / all_time:.2%}" if (v / all_time) * 100 < 9.99 else f"{v / all_time:.2%}", n)
              for n, v in zip(labels, time)]

    time.sort(reverse=True)
    time = [x // 60 for x in time]
    labels.sort(reverse=True)

    plt.rc('xtick', labelsize=8)
    plt.rc('ytick', labelsize=8)
    plt.rc('figure', figsize=(13, 5))

    plt.bar(labels, time, width=0.5)
    plt.ylabel("Время (мин.)")

    plt.savefig('statistics.png')

    plt.close()

    for i in range(0, len(time)):
        text.append(f'{labels[i]}: {datetime.datetime.fromtimestamp(time[i]).strftime("%H:%M:%S")}')

    all_time = str(datetime.datetime.fromtimestamp(all_time).strftime("%H:%M:%S"))

    return text, all_time
