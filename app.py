from flask import Flask, abort, request, render_template
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
stop = set(stopwords.words('english'))
stop.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}',''])
from nltk.stem import WordNetLemmatizer

food_data = pd.read_csv('food_choices.csv')
res_data = pd.read_csv('zomato.csv', encoding='latin-1')
res_data = res_data.loc[(res_data['Country Code'] == 1) & (res_data['City'] == 'New Delhi'), :]
res_data = res_data.loc[res_data['Longitude'] != 0, :]
res_data = res_data.loc[res_data['Latitude'] != 0, :]
res_data = res_data.loc[res_data['Latitude'] < 29] # clearing out invalid outlier
res_data = res_data.loc[res_data['Rating text'] != 'Not rated']
res_data['Cuisines'] = res_data['Cuisines'].astype(str)

def search_comfort(mood):
  lemmatizer = WordNetLemmatizer()
  foodcount = {}
  for i in range(124):
    temp = [temps.strip().replace('.','').replace(',','').lower() for temps in str(food_data["comfort_food_reasons"][i]).split(' ') if temps.strip() not in stop ]
    if mood in temp:
      foodtemp = [lemmatizer.lemmatize(temps.strip().replace('.','').replace(',','').lower()) for temps in str(food_data["comfort_food"][i]).split(',') if temps.strip() not in stop ]
      for a in foodtemp:
        if a not in foodcount.keys():
          foodcount[a] = 1 
        else:
          foodcount[a] += 1
  sorted_food = []
  sorted_food = sorted(foodcount, key=foodcount.get, reverse=True)
  return sorted_food

def find_my_comfort_food(mood):
  topn = []
  topn = search_comfort(mood) #function create dictionary only for particular mood
  return topn[:3]

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
  return render_template('index.html')

@app.route('/find', methods=['GET'])
def find_restaurant():
  mood = request.args.get('mood')
  result = find_my_comfort_food(mood)
  result_str = 'You should eat {}, {}, or {}.'.format(result[0], result[1], result[2])
  food_to_cuisine_map = {
    "pizza": "pizza",
    "ice cream": "ice cream",
    "chicken wings": "mughlai",
    "chinese": "chinese",
    "chip": "bakery",
    "chocolate": "bakery",
    "candy": "bakery",
    "mcdonalds": "burger",
    "burger": "burger",
    "cooky": "bakery",
    "mac and cheese": "american",
    "pasta": "italian",
    "soup": "chinese",
    "dark chocolate": "bakery",
    "terra chips" : "bakery",
    "reese's cups(dark chocolate)": "bakery"
  }
  restaurants_list = []
  for item in result:
    restaurants = res_data[res_data.Cuisines.str.contains(food_to_cuisine_map[item], case=False)].sort_values(by='Aggregate rating', ascending=False).head(3)
    restaurants_list.append(restaurants.iloc[0])
    restaurants_list.append(restaurants.iloc[1])
    restaurants_list.append(restaurants.iloc[2])
  return render_template('result.html', result = result_str, mood = mood, restaurants1 = restaurants_list[:3], restaurants2 = restaurants_list[3:6], restaurants3 = restaurants_list[6:])
