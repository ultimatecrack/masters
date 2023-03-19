# Data Handling
import logging
import pickle
import numpy as np
from pydantic import BaseModel

# Server
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Modeling
import lightgbm

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:80",
    "http://localhost:8000",
    "http://127.0.0.1",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# Initialize logging
my_logger = logging.getLogger()
my_logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, filename='sample.log')

# Initialize files
import joblib
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
        
from sklearn.feature_extraction.text import CountVectorizer
corpus = joblib.load(open('corpos', 'rb'))
cv = CountVectorizer(max_features = 1500)
cv.fit_transform(corpus).toarray()
        
classifier = joblib.load(open('review_classifier', 'rb'))

class Data(BaseModel):
    satisfaction_level: str
        
        
@app.post("/predict")
def predict(data: Data):
    try:
        data_dict = data.dict()
        to_predict = data_dict['satisfaction_level']
        
        new_review = to_predict
        new_review = re.sub('[^a-zA-Z]', ' ', new_review)
        new_review = new_review.lower()
        new_review = new_review.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        
        
        new_review = [ps.stem(word) for word in new_review if not word in set(all_stopwords)]
        new_review = ' '.join(new_review)
        new_corpus = [new_review]
        new_X_test = cv.transform(new_corpus).toarray()
        new_y_pred = classifier.predict(new_X_test)
        #my_logger.error(data)
        #return {"prediction": 1}
        if(new_y_pred == 1):
            result = 'Positive'
        else:
            result = 'Negative'
            
        return {"prediction": result}
    except:
        my_logger.error("Something went wrong!")
        return {"prediction": "error"}
