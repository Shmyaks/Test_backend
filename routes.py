from datetime import date
from main import app
from database import Doc, Session, Rubric, get_db, Elastic
from models import DocModel, RubricModel, SuccessModel, DocsModels
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from fastapi import Depends, HTTPException, status


@app.post("/create", tags=["docs"], response_model=DocModel, response_class=ORJSONResponse)
def get_news(text: str, rubrics: list, date: date, db: Session = Depends(get_db)):
    """Создание документа"""

    doc = Doc(text=text, date=date)
    db.add(doc)
    doc.rubrics.extend([Rubric(name=name) for name in rubrics])
    db.commit()
    print(Elastic.create(doc.id, body_params={'text': text}))

    return doc


@app.get("/search", tags=["docs"], response_class=ORJSONResponse, response_model=DocsModels)
def get_news(db: Session = Depends(get_db), text: str = None, limit: int = 20):
    """Базовый поиск документ по запросу"""

    body = {
        "query": {
            "match": {
                "text": text
                }
            }
        }

    search = Elastic.search(body_params=body)
    id = [doc['_id'] for doc in search['hits']['hits']]
    docs = db.query(Doc).filter(Doc.id.in_(id)).order_by(
        Doc.date.desc()).limit(limit).all()

    return {'docs': docs}


@app.get("/doc/{id}", tags=["docs"], response_class=ORJSONResponse, response_model=DocModel)
def get_news(id: int, db: Session = Depends(get_db)):
    """Выдача документа по id"""

    return db.query(Doc).filter(Doc.id == id).first()


@app.delete("/doc/{id}", tags=["docs"], response_model=SuccessModel)
def get_news(id: int, db: Session = Depends(get_db)):
    """Удаления документа по id"""

    doc = db.query(Doc).filter(Doc.id == id).first()
    db.delete(doc)
    Elastic.delete(id=id)
    db.commit()

    return ORJSONResponse(content=SuccessModel)
