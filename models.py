from peewee import *
from uuid import uuid4

# Database connection
db = SqliteDatabase("result_management.db")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    name = CharField()
    email = CharField(unique=True)
    roll_no = CharField(unique=True)
    image = CharField()
    password = CharField()
    user_type = CharField(default="user")  # 'user' or 'admin'

class Subject(BaseModel):
    sub_code = CharField(unique=True)
    sub_name = CharField()

class Result(BaseModel):
    student = ForeignKeyField(User, backref="results")
    declaration_date = DateField()

class ResultItem(BaseModel):
    result = ForeignKeyField(Result, backref="items", on_delete="CASCADE")
    subject = ForeignKeyField(Subject, on_delete="CASCADE")
    marks_obtained = IntegerField()
    total_marks = IntegerField()

    

# Create tables
db.connect()
db.create_tables([User, Subject, Result, ResultItem])
