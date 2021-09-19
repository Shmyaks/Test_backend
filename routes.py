from datetime import date
import random
from main import app
from database import Doc, Session, Rubric, get_db, Elastic
from models import DocModel, SuccessModel, DocsModels
from fastapi.responses import ORJSONResponse
from fastapi import Depends
import requests


@app.post("/create", tags=["docs"], response_model=DocModel, response_class=ORJSONResponse)
def create_docs(text: str, rubrics: list, date: date, db: Session = Depends(get_db)):
    """Создание документа"""

    doc = Doc(text=text, date=date)
    db.add(doc)
    doc.rubrics.extend([Rubric(name=name) for name in rubrics])
    db.commit()
    Elastic.create(doc.id, body_params={'text': text})

    return doc


@app.get("/search", tags=["docs"], response_class=ORJSONResponse, response_model=DocsModels)
def get_docs(db: Session = Depends(get_db), text: str = None, limit: int = 20):
    """Базовый поиск документ по запросу. (Сортировка по date)
        * text = None выдача документов без поиска текста в документе.
    """

    filter = (None == None)
    if text is not None:
        body = {
            "query": {
                "match": {
                    "text": text
                }
            }
        }

        search = Elastic.search(body_params=body)
        id = [doc['_id'] for doc in search['hits']['hits']]
        filter = (Doc.id.in_(id))

    docs = db.query(Doc).filter(filter).order_by(
        Doc.date.desc()).limit(limit).all()

    return {'docs': docs}


@app.get("/doc/{id}", tags=["docs"], response_class=ORJSONResponse, response_model=DocModel)
def get_doc(id: int, db: Session = Depends(get_db)):
    """Выдача документа по id"""

    return db.query(Doc).filter(Doc.id == id).first()


@app.delete("/doc/{id}", tags=["docs"], response_model=SuccessModel, response_class=ORJSONResponse)
def delete_doc(id: int, db: Session = Depends(get_db)):
    """Удаления документа по id"""

    doc = db.query(Doc).filter(Doc.id == id).first()
    db.delete(doc)
    Elastic.delete(id=id)
    db.commit()

    return {'message': 'Success'}


@app.post("/tests/create", tags=["Tests"], response_model=DocsModels, response_class=ORJSONResponse)
def test_create_docs(db: Session = Depends(get_db), count: int = 10):
    """Создание рандомных документов"""

    rubrics = ["Первая рубрика", "Вторая рубрика", "Третья рубрика"]
    random_date = [date(2005, 9, 10), date(2005, 9, 11), date(
        2005, 9, 12), date(2005, 9, 13), date(2005, 9, 14), date(2005, 9, 15)]
    docs = []
    for i in range(count):
        text = requests.get("https://fish-text.ru/get").json()
        doc = Doc(
            text=text['text'], date=random_date[random.randint(0, len(random_date)-1)])
        db.add(doc)
        doc.rubrics.extend([Rubric(name=name) for name in rubrics])
        db.commit()
        Elastic.create(doc.id, body_params={'text': text['text']})
        docs.append(doc)

    return {'docs': docs}
