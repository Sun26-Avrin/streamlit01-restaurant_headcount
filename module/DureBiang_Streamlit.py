import random
import streamlit as st
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
#import jellyfish
import json
import datetime
import DureBiang_Input_Processor as Sun
#from PIL import Image
import CoronaB4
import webbrowser
import matplotlib.pyplot as plt
import seaborn as sns
import random

def corona_normalization(corona) :
  if corona>90 :
    return random.randrange(108,126)
  else :
    return random.randrange(1,7) 

#df엔 중식인원 드롭한 df넣어야함

def get_trainX_from_dfwithoutY(df, foodlist, month, weekday, corona ,feature_len = 291) :

  food_vec = np.array([0]*(df.shape[1])).reshape(1, df.shape[1])
  now = datetime.datetime.now()
  
  #정제된 푸드인풋 벡터화
  for idx,food in enumerate(foodlist) :
    if food not in df.columns.tolist()[:feature_len] :
      continue
      #print(food," not in columns")
    else :
      food_vec[0][df.columns.tolist().index(food)]=1
  #코로나 벡터화
  food_vec[0][feature_len] = corona_normalization(corona) 
  #월(month) 벡터화
  food_vec[0][feature_len+month] = 1
  
  
  food_vec[0][feature_len+12+weekday]=1

  return food_vec


def main():
  st.set_page_config(layout="wide")
  now = datetime.datetime.now()
  corona_cnt=CoronaB4.get_incDec()
	
  time = str(now.year)+"년 "+ str(now.month)+ "월 "+str(now.day)+"일 "
  col1, col3 = st.beta_columns([2.5,1])
  
  # 이미지
  col3.image('../logo_final.png',
            width=180)
  
  # 폰트스타일
  st.markdown("""
    <style>
    .small-font {
        font-size:13px;
        color:#FF5733;
        text-align:center;
    }
    </style>
    """, unsafe_allow_html=True)



  st.write("""
  # ** 두레비앙 중식 식수인원 예측**

  
  """)





  my_expander = st.beta_expander(label = '사용설명서')
  my_expander.write('1. 메뉴를 입력하시고 **Ctrl+Enter** 또는 **여기**를 눌러주시면 식수인원이 예측됩니다.')
  my_expander.write('2. **과일류 샐러드**는 **과일샐러드**로 입력해주시면 더 정확히 예측이 가능합니다.')
  my_expander.write('3. **야채류 전**은 **야채전**으로 입력해주시면 더 정확히 예측이 가능합니다.')
  my_expander.write('4. **&또는 /로 구분된 메뉴**는 **대표메뉴**로 자동입력됩니다.')
  my_expander.write('5. **등록되지않은 메뉴**를 기입시 자동으로 등록된메뉴에서 찾아주나, **예측성능**은 크게 저하합니다.')
  my_expander.write('')
  my_expander.write('')

  url = 'https://sauce.foodpolis.kr/home/specialty/nutritionInfo.do?PAGE_MN_ID=SIS-030300'

  st.write("")
  if my_expander.button('영양성분을 조회하고 싶으시면 여기를 눌러주세요.'):
    my_expander.write('')
    my_expander.write("**# 소스산업화센터 영양성분조회 URL**")
    webbrowser.open_new_tab(url)
    my_expander.markdown(url,unsafe_allow_html=True)
  
  

  df_pro = pd.read_csv("../Dure_train_data_210123.csv",index_col=0)
  #drop = ['중식 인원','년']



  # json metadata
  with open('DURE_meta.json','r',encoding='utf-8') as f:
    map_json = json.load(f)

  
  


  cont = '어제 코로나 대구확진자 수 : '+str(corona_cnt)
  st.sidebar.image('../dure_logo.png',width=150)
  
  st.sidebar.write('')
  st.sidebar.write('')
  st.sidebar.write("**Today : "+time+"**")
  st.sidebar.write("**"+cont+"**")  
  corona = st.sidebar.slider('작일 코로나 대구확진자 수',1, 400)
  month = st.sidebar.slider('월',1, 12)
  weekday = st.sidebar.slider('요일',1,5)
  st.sidebar.write('')
  st.sidebar.write('**메뉴를 입력하세요. 각 메뉴를 / 로 구분해주세요.**')
  st.sidebar.markdown("<p class='small-font'><b> * 메뉴는 4개이상 입력가능</p>", unsafe_allow_html=True)

  
  n = random.sample(range(1,291),6)
  rand_menu = df_pro.columns[:291]
  rand_df = pd.DataFrame(rand_menu[n],columns=["예시 메뉴셋"])
  
  

  menu_list=st.sidebar.text_area("   예시) 밥/김치찌개/과일샐러드/코다리조림/맛살계란볶음/오이소박이")
  st.sidebar.write("")
  st.sidebar.write("")
  


  st.sidebar.table(rand_df)
  st.sidebar.markdown('<p class="small-font">페이지를 새로고침 할 때마다</p>',unsafe_allow_html=True)
  st.sidebar.markdown('<p class="small-font">예시 메뉴셋이 랜덤으로 추출됩니다</p>',unsafe_allow_html=True)
  if (menu_list) :
    df_input = df_pro.drop(['식수인원'],axis=1)
    sun = Sun.Menu_Processing(metadatadf = df_input , 
                              feature_len = 291, mappingJsonDict = map_json)
    #st.write(menu_list)
    sun.init_food_kind_from_userInput(menu_list)
    sun.matchto_metadata()
    foodlist = sun.converted_foodlist()
    X = get_trainX_from_dfwithoutY(df_input,foodlist, month, weekday, corona)


    y = df_pro['식수인원']


    if (len(foodlist) == 4) :
      data = {
              '월' : month,
              '요일' : weekday,
              '코로나' : corona,
              '메뉴1' : foodlist[0],
              '메뉴2' : foodlist[1],
              '메뉴3' : foodlist[2],
              '메뉴4' : foodlist[3]
              }
    elif (len(foodlist) == 5) :
      data = {
              '월' : month,
              '요일' : weekday,
              '코로나' : corona,
              '메뉴1' : foodlist[0],
              '메뉴2' : foodlist[1],
              '메뉴3' : foodlist[2],
              '메뉴4' : foodlist[3],
              '메뉴5' : foodlist[4]
              }
    elif (len(foodlist) == 6) : 
      data = {
              '월' : month,
              '요일' : weekday,
              '코로나' : corona,
              '메뉴1' : foodlist[0],
              '메뉴2' : foodlist[1],
              '메뉴3' : foodlist[2],
              '메뉴4' : foodlist[3],
              '메뉴5' : foodlist[4],
              '메뉴6' : foodlist[5]
              }
    elif (len(foodlist) == 7) : 
      data = {
              '월' : month,
              '요일' : weekday,
              '코로나' : corona,
              '메뉴1' : foodlist[0],
              '메뉴2' : foodlist[1],
              '메뉴3' : foodlist[2],
              '메뉴4' : foodlist[3],
              '메뉴5' : foodlist[4],
              '메뉴6' : foodlist[5],
              '메뉴7' : foodlist[6]
              }
    elif (len(foodlist) < 4)  :
      data = {'월' : month,
              '요일' : weekday,
              '메뉴' : "Menu Error(0)"}
      st.write("")
      st.write("")
      st.markdown("<div style='color:red'><b> # 메뉴 갯수가 너무 적습니다. </b>(4-7개 입력가능)</div>", unsafe_allow_html=True)
    else :
      data = {'월' : month,
              '요일' : weekday,
              '메뉴' : "Menu Error(1)"}
      st.write("")
      st.write("")
      st.markdown("<div style='color:red'><b> # 메뉴 갯수가 너무 많습니다. </b>(4-7개 입력가능)</div>", unsafe_allow_html=True)
      

    

    features = pd.DataFrame(data, index=[0])
    st.write("")
    st.write("")
    st.subheader("**입력하신 데이터입니다.**")
    st.write("")
    st.table(features)






    
  


    from tensorflow import keras 
    model = keras.models.load_model("../model.h5")

    


    predict_ = model.predict(X)


    st.write("")
    st.write("")
    st.subheader("**식수인원 예측**")
    st.write("")
    pre = pd.DataFrame(predict_, columns=["예상 중식인원"],index = ["total"])
    st.table(pre)



    ch1,ch2 = st.beta_columns([2.5,1])
    my_expander2 = st.beta_expander(label = '기존 식수인원 대비 분포도')
    my_expander2.markdown("<p class='small-font'> * 해당 분포도는 과거 데이터의 분포에서 예측식수인원이 어디에 위치하는지 보여줍니다.</div>", unsafe_allow_html=True)
    # 분포도
    fig, axes = plt.subplots(1,1)
    ax=sns.distplot(df_pro['식수인원'],hist=False,ax=axes)
    data_x, data_y = ax.lines[0].get_data()

    xi = predict_[0] 
    yi = np.interp(xi,data_x, data_y)
    axes.plot([xi],[yi], marker="o")
    axes.plot([xi,xi],[0,yi],color='r')

    axes.set_title('Total Customer Distribution', fontsize=18)
    axes.set_xlabel('Customer', fontsize=16)
    axes.set_ylabel('Density', fontsize=16)

    my_expander2.write("")
    my_expander2.write("")
    _,_,ch3,_,_ = my_expander2.beta_columns([1,1,3,1,1])
    ch3.pyplot(fig)

    
    

  









if __name__ == '__main__':
	main()
