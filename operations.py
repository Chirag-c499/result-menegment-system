# operations.py
from models import *
from datetime import date

def add_subject(sub_code, name):
    return Subject.create(sub_code=sub_code, name=name)

def declare_result(student, result_data):
    result = Result.create(student=student, declaration_date=date.today())
    for item in result_data:
        subject = Subject.get(Subject.id == item['subject_id'])
        ResultItem.create(result=result, subject=subject,
                          marks_obtained=item['marks'], total_marks=item['total'])
    return result
