from peewee import Model, CharField, PostgresqlDatabase, IntegerField, BooleanField, TextField
import settings
psql_db = PostgresqlDatabase(
    settings.DB_NAME,
    host=settings.DB_HOST,
    password=settings.DB_PASS,
    user=settings.DB_USER
)


class BaseModel(Model):
    class Meta:
        database = psql_db


class Users(BaseModel):
    email = CharField()
    price = IntegerField()
    url = TextField()
    mail_send = BooleanField(default=False)
