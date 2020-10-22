import peewee


with open("functions/info", "r", encoding="utf8") as file:
    config = file.read().splitlines()
    db = peewee.MySQLDatabase(
        host=config[0],
        user=config[1],
        password=config[2],
        database=config[3],
        port=3306
    )


class DBModel(peewee.Model):
    class Meta:
        database = db


class GmodPlayer(DBModel):
    SID = peewee.CharField(max_length=25, unique=True)
    group = peewee.TextField(null=False)
    status = peewee.TextField(null=False)
    nick = peewee.TextField(null=False)
    synch = peewee.SmallIntegerField(null=False)
    synchgroup = peewee.TextField(null=False)

    class Meta:
        db_table = "ma_players"


class GmodBan(DBModel):
    SID = peewee.ForeignKeyField(GmodPlayer, field="SID",
                                 on_update="cascade", on_delete="cascade")
    ban = peewee.BooleanField(default=False)
    ban_admin = peewee.TextField()
    ban_reason = peewee.TextField()
    ban_date = peewee.TextField()
    unban_date = peewee.TextField()

    class Meta:
        db_table = "ma_bans"


class UserDiscord(DBModel):
    discord_id = peewee.BigIntegerField(primary_key=True)
    rating = peewee.IntegerField(default=0)
    money = peewee.BigIntegerField(default=0)
    gold_money = peewee.BigIntegerField(default=0)
    chance_roulette = peewee.BooleanField(default=True)
    SID = peewee.CharField(max_length=32, default="STEAM_0:0:0000000")
    role_id = peewee.BigIntegerField()

    class Meta:
        db_table = "ds_users"


class RolesDiscord(DBModel):
    role_id = peewee.BigIntegerField()
    discord_id = peewee.ManyToManyField(UserDiscord)

    class Meta:
        db_table = "ds_roles"


class Promocode(DBModel):
    code = peewee.IntegerField(null=False, default=0)
    amount = peewee.IntegerField(null=False, default=0)
    thing = peewee.IntegerField(null=False, default=0)
    creating_admin = peewee.BooleanField(default=False)

    class Meta:
        db_table = "promocodes"


class StatusDB(DBModel):
    ip = peewee.CharField(primary_key=True, max_length=24, null=False)
    message = peewee.BigIntegerField(null=False)
    collection = peewee.BigIntegerField(null=False)

    class Meta:
        db_table = "status"


class BanRole(DBModel):
    id_role = peewee.BooleanField()

    class Meta:
        db_table = "ban_role"
