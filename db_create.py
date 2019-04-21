from app import models, engine

models.Base.metadata.create_all(engine)