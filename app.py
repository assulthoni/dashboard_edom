import sys
import pandas as pd
from sqlalchemy import create_engine
from data import DATABASES

user = DATABASES['default']['USER']
password = DATABASES['default']['PASSWORD']
database_name = DATABASES['default']['NAME']
host = DATABASES['default']['HOST']
port = DATABASES['default']['PORT']
database_url = 'postgresql://{user}:{password}@{host}:{port}/{database_name}'.format(
    user=user,
    password=password,
    database_name=database_name,
    host=host,
    port=port
)


def sql_insertion(dataframe, table):
    engine = create_engine(database_url, echo=False)
    dataframe.to_sql(table, con=engine, if_exists='append', index=False)


def select_all(tablename):
    query = "SELECT * FROM {}".format(tablename)
    engine = create_engine(database_url, echo=False)
    return pd.read_sql_query(query, engine)


def select_by_year(tablename='nlp_api_pertanyaannumerik', yearstart='1819', yearend='1920'):
    yearstart_list = [int(yearstart[i:i + 2]) for i in range(0, len(yearstart), 2)]
    yearend_list = [int(yearend[i:i + 2]) for i in range(0, len(yearend), 2)]
    yearbetween = [i for i in range(yearstart_list[0] + 1, yearend_list[1])]
    yearbetween_list = [str(yearbetween[i]) + str(yearbetween[i + 1]) for i in range(0, len(yearbetween) - 1)]
    yearbetween_list.insert(0, yearstart)
    yearbetween_list.append(yearend)
    query = 'SELECT * FROM {} WHERE "SCHOOLYEAR" IN {}'.format(tablename, tuple(yearbetween_list))
    engine = create_engine(database_url, echo=False)
    df = pd.read_sql_query(query, engine)
    return df


def select_by_semester(tablename='nlp_api_pertanyaannumerik', yearstart='1819', yearend='1920', semester=[1, 2]):
    yearstart_list = [int(yearstart[i:i + 2]) for i in range(0, len(yearstart), 2)]
    yearend_list = [int(yearend[i:i + 2]) for i in range(0, len(yearend), 2)]
    yearbetween = [i for i in range(yearstart_list[0] + 1, yearend_list[1])]
    yearbetween_list = [str(yearbetween[i]) + str(yearbetween[i + 1]) for i in range(0, len(yearbetween) - 1)]
    yearbetween_list.insert(0, yearstart)
    yearbetween_list.append(yearend)
    # yearbetween_list = [int(i) for i in yearbetween_list]
    if len(semester) > 1:
        term = tuple(semester)
        query = 'SELECT * FROM {} WHERE "SCHOOLYEAR" IN {} AND "SEMESTER" IN {}'.format(tablename,
                                                                                        tuple(yearbetween_list),
                                                                                        term)

    else:
        term = semester[0]
        query = 'SELECT * FROM {} WHERE "SCHOOLYEAR" IN {} AND "SEMESTER" = {}'.format(tablename,
                                                                                       tuple(yearbetween_list),
                                                                                       term)
        print(query)
    engine = create_engine(database_url, echo=False)
    df = pd.read_sql_query(query, engine)
    return df

def select_kuantitatif_table(tablename='nlp_api_pertanyaannumerik', yearstart='1819', yearend='1920', semester=[1, 2]):
    yearstart_list = [int(yearstart[i:i + 2]) for i in range(0, len(yearstart), 2)]
    yearend_list = [int(yearend[i:i + 2]) for i in range(0, len(yearend), 2)]
    yearbetween = [i for i in range(yearstart_list[0] + 1, yearend_list[1])]
    yearbetween_list = [str(yearbetween[i]) + str(yearbetween[i + 1]) for i in range(0, len(yearbetween) - 1)]
    yearbetween_list.insert(0, yearstart)
    yearbetween_list.append(yearend)
    if len(semester) > 1:
        term = tuple(semester)
        query = '''select "SCHOOLYEAR", "SEMESTER", "LECTURERCODE", "SUBJECTNAME", "CLASS", "QUESTIONCATEGORY", "QUESTION",
               Sangat_puas,
               Puas,
               Tidak_puas,
               Sangat_tidak_puas,
               case
               when
               (Sangat_puas + Puas + Tidak_puas + Sangat_tidak_puas) = 0 then 0
               else
               (Sangat_puas * 4 + Puas * 3 + Tidak_puas * 2 + Sangat_tidak_puas * 1) / cast(Sangat_puas + Puas + Tidak_puas + Sangat_tidak_puas as real) * 25
               end as skor
               from
               (select "SCHOOLYEAR", "SEMESTER", "LECTURERCODE", "SUBJECTNAME",
                "CLASS", "QUESTIONCATEGORY",
                "QUESTION",
                count(case when "ANSWER" = 'Puas' then 1 end) as Puas,
                count(case when "ANSWER" = 'Sangat puas' then 1 end) as sangat_puas,
                count(case when "ANSWER" = 'Sangat tidak puas' then 1 end) as Sangat_tidak_puas,
                count(case when "ANSWER" = 'Tidak puas' then 1 end) as Tidak_puas
                from {} WHERE "SCHOOLYEAR" IN {} AND "SEMESTER" IN {}
                group by "SCHOOLYEAR", "SEMESTER", "LECTURERCODE", "SUBJECTNAME",
                "CLASS", "QUESTIONCATEGORY",
                "QUESTION") as tab'''.format(tablename,
                                                                                                tuple(yearbetween_list),
                                                                                                term)

    else:
        term = semester[0]
        query = '''select "SCHOOLYEAR", "SEMESTER", "LECTURERCODE", "SUBJECTNAME", "CLASS", "QUESTIONCATEGORY", "QUESTION",
               Sangat_puas,
               Puas,
               Tidak_puas,
               Sangat_tidak_puas,
               case
               when
               (Sangat_puas + Puas + Tidak_puas + Sangat_tidak_puas) = 0 then 0
               else
               (Sangat_puas * 4 + Puas * 3 + Tidak_puas * 2 + Sangat_tidak_puas * 1) / cast(Sangat_puas + Puas + Tidak_puas + Sangat_tidak_puas as real) * 25
               end as skor
               from
               (select "SCHOOLYEAR", "SEMESTER", "LECTURERCODE", "SUBJECTNAME",
                "CLASS", "QUESTIONCATEGORY",
                "QUESTION",
                count(case when "ANSWER" = 'Puas' then 1 end) as Puas,
                count(case when "ANSWER" = 'Sangat puas' then 1 end) as sangat_puas,
                count(case when "ANSWER" = 'Sangat tidak puas' then 1 end) as Sangat_tidak_puas,
                count(case when "ANSWER" = 'Tidak puas' then 1 end) as Tidak_puas
                from {} WHERE "SCHOOLYEAR" IN {} AND "SEMESTER" = {}
                group by "SCHOOLYEAR", "SEMESTER", "LECTURERCODE", "SUBJECTNAME",
                "CLASS", "QUESTIONCATEGORY",
                "QUESTION") as tab '''.format(tablename,
                                                                                                tuple(yearbetween_list),
                                                                                                term)
        print(query)
    engine = create_engine(database_url, echo=False)
    df = pd.read_sql_query(query, engine)
    return df
def select_by_dosen(tablename='nlp_api_pertanyaannumerik', dosen=['MSN', 'ENA']):
    if len(dosen) > 1:
        dosen_list = tuple(dosen)
        query = 'SELECT * FROM {} WHERE "LECTURERCODE" IN {}'.format(tablename, dosen_list)
    else:
        dosen_list = dosen[0]
        query = 'SELECT * FROM {} WHERE "LECTURERCODE" = {}'.format(tablename, dosen_list)
    engine = create_engine(database_url, echo=False)
    df = pd.read_sql_query(query, engine)
    return df
if __name__ == '__main__':
    print(select_kuantitatif_table())
