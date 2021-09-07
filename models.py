<<<<<<< HEAD
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


class GuildDiscord(DBModel):
    guild_id = peewee.IntegerField(primary_key=True)
    guild = peewee.BigIntegerField()
    tech_channel = peewee.BigIntegerField(default=0)

    class Meta:
        table_name = "guild_discord"


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
    chance_roulette = peewee.SmallIntegerField(default=3)
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
    guild_id = peewee.ForeignKeyField(GuildDiscord, on_delete="cascade", on_update="cascade")
    discord_id = peewee.ManyToManyField(UserDiscord, backref='user_role')

    class Meta:
        table_name = "ds_roles"


class Promocode(DBModel):
    id = peewee.IntegerField(primary_key=True)
    code = peewee.IntegerField(null=False, default=0)
    amount = peewee.IntegerField(null=False, default=0)
    thing = peewee.IntegerField(null=False, default=0)
    creating_admin = peewee.BooleanField(default=False)

    class Meta:
        table_name = "promocodes"


class StatusGMS(DBModel):
    id = peewee.IntegerField(primary_key=True)
    ip = peewee.CharField(max_length=24, null=False)
    name = peewee.TextField(default="Название сервера")
    guild = peewee.ForeignKeyField(GuildDiscord, on_delete="cascade", on_update="cascade")
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


class Group(DBModel):
    group_id = peewee.IntegerField(primary_key=True)
    group = peewee.CharField(max_length=32)


class PlayerGroupTime(DBModel):
    time_id = peewee.IntegerField(primary_key=True)
    player_id = peewee.ForeignKeyField(GmodPlayer, field="id", on_update="cascade", on_delete="cascade")
    group_id = peewee.ForeignKeyField(Group, field="group_id", on_update="cascade", on_delete="cascade")
    time = peewee.IntegerField()

    class Meta:
        table_name = "player_group_time"


class NewYearPresents(DBModel):
    discord_id = peewee.ForeignKeyField(UserDiscord, field="discord_id",
                                        on_update="cascade", on_delete="cascade", primary_key=True)
    present = peewee.IntegerField(null=False)


RoleUser = RoleDiscord.discord_id.get_through_model()
=======
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


class GuildDiscord(DBModel):
    guild_id = peewee.IntegerField(primary_key=True)
    guild = peewee.BigIntegerField()
    tech_channel = peewee.BigIntegerField(default=0)

    class Meta:
        table_name = "guild_discord"


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
    chance_roulette = peewee.SmallIntegerField(default=3)
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
    guild_id = peewee.ForeignKeyField(GuildDiscord, on_delete="cascade", on_update="cascade")
    discord_id = peewee.ManyToManyField(UserDiscord, backref='user_role')

    class Meta:
        table_name = "ds_roles"


class Promocode(DBModel):
    id = peewee.IntegerField(primary_key=True)
    code = peewee.IntegerField(null=False, default=0)
    amount = peewee.IntegerField(null=False, default=0)
    thing = peewee.IntegerField(null=False, default=0)
    creating_admin = peewee.BooleanField(default=False)

    class Meta:
        table_name = "promocodes"


class StatusGMS(DBModel):
    id = peewee.IntegerField(primary_key=True)
    ip = peewee.CharField(max_length=24, null=False)
    name = peewee.TextField(default="Название сервера")
    guild = peewee.ForeignKeyField(GuildDiscord, on_delete="cascade", on_update="cascade")
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


class Group(DBModel):
    group_id = peewee.IntegerField(primary_key=True)
    group = peewee.CharField(max_length=32)


class PlayerGroupTime(DBModel):
    time_id = peewee.IntegerField(primary_key=True)
    player_id = peewee.ForeignKeyField(GmodPlayer, field="id", on_update="cascade", on_delete="cascade")
    group_id = peewee.ForeignKeyField(Group, field="group_id", on_update="cascade", on_delete="cascade")
    time = peewee.IntegerField()

    class Meta:
        table_name = "player_group_time"


class NewYearPresents(DBModel):
    discord_id = peewee.ForeignKeyField(UserDiscord, field="discord_id",
                                        on_update="cascade", on_delete="cascade", primary_key=True)
    present = peewee.IntegerField(null=False)


RoleUser = RoleDiscord.discord_id.get_through_model()
>>>>>>> 75b13045fc71e61cb736d610ba0be5d6d89e8926
