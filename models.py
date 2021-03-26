import peewee
import json as js

with open("stuff/config.json", "r", encoding="utf8") as file:
    json = js.load(file)
    db_config = json['database']
    db = peewee.MySQLDatabase(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        port=3306,
        charset="utf8"
    )


class DBModel(peewee.Model):
    class Meta:
        database = db


class GmodPlayer(DBModel):
    SID = peewee.CharField(max_length=25, unique=True)
    group = peewee.TextField(null=False, default="user")
    status = peewee.TextField(null=False, default="status")
    nick = peewee.TextField(null=False, default="nick")
    synch = peewee.SmallIntegerField(null=False, default=0)
    synchgroup = peewee.TextField(null=False, default="")

    class Meta:
        table_name = "ma_players"


class GmodBan(DBModel):
    SID = peewee.ForeignKeyField(GmodPlayer, field="SID",
                                 on_update="cascade", on_delete="cascade")
    ban = peewee.SmallIntegerField(default=0)
    server = peewee.SmallIntegerField(default=1)
    ban_admin = peewee.TextField(default="")
    ban_reason = peewee.TextField(default="")
    ban_date = peewee.TextField(default="")
    unban_date = peewee.TextField(default="")

    class Meta:
        table_name = "ma_bans"


class UserDiscord(DBModel):
    discord_id = peewee.BigIntegerField(unique=True)
    money = peewee.BigIntegerField(default=0)
    gold_money = peewee.BigIntegerField(default=0)
    chance_roulette = peewee.BooleanField(default=True)
    SID = peewee.CharField(max_length=32, null=True)

    class Meta:
        table_name = "ds_users"


class Rating(DBModel):
    discord = peewee.ForeignKeyField(UserDiscord, field="discord_id", on_update="cascade", on_delete="cascade")
    user = peewee.ForeignKeyField(UserDiscord, field="discord_id", on_update="cascade", on_delete="cascade")
    rating = peewee.BooleanField()
    date = peewee.DateField()


class RoleDiscord(DBModel):
    role_id = peewee.BigIntegerField(unique=True)
    discord_id = peewee.ManyToManyField(UserDiscord, backref='user_role')

    class Meta:
        table_name = "ds_roles"


class Promocode(DBModel):
    code = peewee.IntegerField(null=False, default=0)
    amount = peewee.IntegerField(null=False, default=0)
    thing = peewee.IntegerField(null=False, default=0)
    creating_admin = peewee.BooleanField(default=False)

    class Meta:
        table_name = "promocodes"


class StatusGMS(DBModel):
    ip = peewee.CharField(unique=True, max_length=24, null=False)
    name = peewee.TextField(default="Название сервера")
    message = peewee.BigIntegerField(null=False)
    collection = peewee.BigIntegerField(null=False)

    class Meta:
        table_name = "status"


class DonateUser(DBModel):
    SID = peewee.ForeignKeyField(GmodPlayer, field="SID",
                                 on_update="cascade", on_delete="cascade")
    donate = peewee.BooleanField(null=False, default=False)
    date_start = peewee.IntegerField(default=0)
    date_end = peewee.IntegerField(default=0)

    class Meta:
        table_name = "donate_user"


class AllTimePlay(DBModel):
    SID = peewee.ForeignKeyField(GmodPlayer, field="SID",
                                 on_update="cascade", on_delete="cascade", primary_key=True)
    user = peewee.IntegerField(default=0)
    driver = peewee.IntegerField(default=0)
    driver3class = peewee.IntegerField(default=0)
    driver2class = peewee.IntegerField(default=0)
    driver1class = peewee.IntegerField(default=0)
    all_time_on_server = peewee.IntegerField(null=False, default=0)

    class Meta:
        table_name = "player_group_time"
        order_by = ("all_time_on_server",)


class StatisticsDriving(DBModel):
    SID = peewee.CharField(max_length=30)
    date = peewee.DateField()
    ema_502 = peewee.IntegerField(default=0)
    lvz_540 = peewee.IntegerField(default=0)
    lvz_540_2 = peewee.IntegerField(default=0)
    lvz_540_2k = peewee.IntegerField(default=0)
    d_702 = peewee.IntegerField(default=0)
    e_703 = peewee.IntegerField(default=0)
    ezh_707 = peewee.IntegerField(default=0)
    ezh3_710 = peewee.IntegerField(default=0)
    msk_717 = peewee.IntegerField(default=0)
    lvz_717 = peewee.IntegerField(default=0)
    lvz_717_5k = peewee.IntegerField(default=0)
    msk_717_5a = peewee.IntegerField(default=0)
    msk_717_5m = peewee.IntegerField(default=0)
    lvz_717_5p = peewee.IntegerField(default=0)
    j717 = peewee.IntegerField(default=0)
    tisu_718 = peewee.IntegerField(default=0)
    yauza_720 = peewee.IntegerField(default=0)
    yauza_720_a = peewee.IntegerField(default=0)
    ubik_722_new = peewee.IntegerField(default=0)
    ubik_722 = peewee.IntegerField(default=0)
    ubik_722_1 = peewee.IntegerField(default=0)
    ubik_722_3 = peewee.IntegerField(default=0)
    mvm_740 = peewee.IntegerField(default=0)
    oka_760 = peewee.IntegerField(default=0)
    oka_760a = peewee.IntegerField(default=0)

    class Meta:
        table_name = "statistics"
        order_by = ("date",)


class RolesGmod(DBModel):
    name = peewee.TextField(null=False)
    group = peewee.TextField(null=False)


class TeamsGmodName(DBModel):
    group = peewee.TextField(unique=True, default='')
    team = peewee.TextField(unique=True, default='')


class NewYearPresents(DBModel):
    discord_id = peewee.ForeignKeyField(UserDiscord, field="discord_id",
                                        on_update="cascade", on_delete="cascade", primary_key=True)
    present = peewee.IntegerField(null=False)


RoleUser = RoleDiscord.discord_id.get_through_model()
