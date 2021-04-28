
import pandas as pd
import json
import sys
import os




def raw_menu_To_df(filepath, download = False) :
  df = pd.read_excel(filepath,index_col=0)
  before = df.shape[1]
  df=df.reset_index()
  after = df.shape[1]
  col_list = []
  for i in range(after) :
    col_list.append(i)

  df.columns= col_list

  lunch_idx = df[df[1].str.contains('중식') == True].index.tolist()
  lunch_idx.pop(-1)

  lunch_idx2 = df[df[1].str.contains('중식') == True].index.tolist()
  lunch_idx2.pop(0)

  for i in df.columns.tolist() :
    df[i]=df[i].apply(str)

  # 혹시나 있을 공백처리
  for i in df.columns.tolist() :
    df[i]=df[i].apply(lambda x: x.strip())

  cnt=0
  menu_list = []
  for i,j in zip(lunch_idx, lunch_idx2) :
    #print(i,j) # 실제 접근해야하는 인덱스는 i-1, j-1임
       
    #정규인덱스
    temp = df[i-1:j-1].to_numpy()
    temp_menu_list = []
    for item in temp :
      for k in item :
        if k != 'nan' :
          if k not in '중식\n' :
            temp_menu_list.append(k)

    menu_list.append(temp_menu_list)

    # 마지막인덱스
    if (j == lunch_idx2[-1]) : 
      temp2 = df[j-1:].to_numpy()
      temp2_list =[]
      for item2 in temp2 :
        for k2 in item2 :
          if k2 != 'nan' :
            if k2 not in '중식\n' :
              temp2_list.append(k2)
      menu_list.append(temp2_list)


    # 자동패딩
    df3 = pd.DataFrame(data=menu_list)
      
    # 날짜형식 다른것 
    ch_idx = df3[df3[0].str.contains('일') == True].index.tolist()
    for chidx in ch_idx :
      raw = df3.at[chidx,0]
      raw = raw.split(' ')
      elem = raw[0].split('-')
      
      target = ''
      for idx,i in enumerate(elem) :
        if (int(i)>12) :
          target += "20" + str(i)
        else :
          if (len(str(i)) != 1 ) :
            target += str(i)
          else : 
            target += "0" +str(i)

        if (idx==2) :
          target+=" 00:00:00"
        else :
          target+="-"
      
      #2019-08-05 00:00:00

      df3.at[chidx,0] = target

      if (download == True) :
        if os.path.exists("./MenuCSV") == False :
          os.mkdir("./MenuCSV")
        df3.to_csv('./MenuCSV/created.csv')

  return df3




class Menu_Processing :
  def __init__(self, metadatadf, feature_len  ,mappingJsonDict) :
    self.metadata=metadatadf.columns.tolist()[:feature_len]
    
    #self.df = df
    #self.menu_col = menu_col
    #self.food_kind = self.init_food_kind()
    #self.food_kind_origin = food_kind
    self.food_kind_meta = {}
    
    #self.comp = {}
    self.mapping_metadata = mappingJsonDict


    
  def init_food_kind_from_df(self,df,menu_col) :
    self.df = df
    self.menu_col = menu_col

    food_kind=[]
    for i in menu_col :
      for j in df[i].unique().tolist() :
        #공백삭제
        temp=j.strip()
        food_kind.append(temp)
    food_kind = set(food_kind)
    
    #
    self.food_kind = list(food_kind) 
    self.food_kind_origin = list(food_kind)
    #
    self.none, self.before = self.jung_jae()
    #return list(food_kind)

  def init_food_kind_from_userInput(self,userinput) :
    #공백삭제
    fdlist = userinput.strip()
    fdlist = userinput.split("/")


    self.food_kind = list(set(fdlist))
    self.food_kind_origin = list(set(fdlist))
    self.none, self.before = self.jung_jae()


  def converted_foodlist(self) :
    return [i for i in self.food_kind_meta.values()]

  def count_match_phoneme(self,str1,str2) :
    return len(set(str1).intersection(str2))

  def isinclude(self,str1,str2) :
    if str1 in str2 :
      return 1000
    #elif str2 in str1 :
      #return 1000
    else :
      return 0
  def isinclude_prop(self,str1,str2) :
    if str1 in str2 :
      return len(str1)/len(str2)
    elif str2 in str1 :
      return len(str2)/len(str1)/1.5
    else :
      return 0

  def count_phoneme(self,str1,str2) :
    return len(set(str1).intersection(str2))

  def jung_jae(self) :
    # 잡데이터 제거
    remove_list = []
    for i,food in enumerate(self.food_kind) :
      if (food.find('<'))!=-1 :
        remove_list.append(food)
      elif (food.find('-'))!=-1 :
        remove_list.append(food)
      elif (food.find('데이'))!=-1 :
        remove_list.append(food)
      elif (food.find('D'))!=-1 :
        remove_list.append(food)
      elif (food.find('k'))!=-1 :
        remove_list.append(food)
      elif (food.find('K'))!=-1 :
        remove_list.append(food)
      elif (food.find('총'))!=-1 :
        remove_list.append(food)

    none={}
    before_jungjae = {}
    for i in remove_list :
      self.food_kind.remove(i)
      none[i] = 'None'
      before_jungjae[i]= 'None'
    

    # '/','&' 데이터 -> 메인메뉴데이터로 변경(메인메뉴가 보통 제일앞에 위치함)
    for i,food in enumerate(self.food_kind) :
      before = food
      if '양념장' in food :
          self.food_kind[i]=self.food_kind[i].replace('양','')
          self.food_kind[i]=self.food_kind[i].replace('념','')
          self.food_kind[i]=self.food_kind[i].replace('장','')
      if (food.find('/'))!=-1 :
        #print("변경전 : ",self.food_kind[i])
        self.food_kind[i] = (self.food_kind[i].split("/")[0])
        before_jungjae[before] = self.food_kind[i].split("/")[0]
        #print("변경후 : ",self.food_kind[i])
      if (food.find('&'))!=-1 :
        #print("변경전 : ",self.food_kind[i])
        if self.food_kind[i].split("&")[0] == '' :
          self.food_kind[i] = (self.food_kind[i].split("&")[1])
          before_jungjae[before] = (self.food_kind[i].split("&")[1])
          #print("변경후 : ",self.food_kind[i])
          continue
        self.food_kind[i] = (self.food_kind[i].split("&")[0])
        before_jungjae[before] = (self.food_kind[i].split("&")[0])
        #print("변경후 : ",self.food_kind[i])

    bf_re = {v: k for k,v in before_jungjae.items()}  
    return none,bf_re

    # for i in self.menu_col :
    #   self.df[i]=self.df[i].apply(lambda x: 'None' if x in remove_list else x)
    #for i in self.menu_col :
      #print(df[df[i].str.contains('데이')][i].unique())    


  def matchto_metadata(self,showmapping=False):
    self.food_kind_meta = {}
    # 새메뉴 하나씩뽑고
    for idx,newdata in enumerate(self.food_kind) :
      score_dict = {}
      if (newdata == 'None') or (newdata =='') :
        continue

      if newdata in self.mapping_metadata.keys() :
        self.food_kind_meta[newdata]=self.mapping_metadata[newdata]
        continue
      # Skip 조건
      #if 

      # 기존 메뉴에 매핑
      # 기존 메뉴 하나씩 뽑고
      for metadata in self.metadata :
        #print(newdata,'type',type(newdata))
        #print("meta",metadata,'type',type(metadata))
        

        #해당 문자열이 포함되면
        if self.isinclude(newdata,metadata) :
          # &가 포함된 다중메뉴이면
          if '&' in metadata :
            best_score=0
            for item in metadata.split('&') :
              score = self.isinclude(item,newdata)
              if(score > best_score) :
                best_score = score
            score_dict[metadata]=best_score

          # 단일메뉴이면
          else :
            score_dict[metadata]=self.isinclude(newdata,metadata)

        # 포함안되면
        else :
          score_dict[metadata] = self.count_phoneme(newdata,metadata) #/ len(metadata)

      score_dict = sorted(score_dict.items(),key=(lambda x:x[1]), reverse=True)  #내림차순 정렬
      #print(score_dict)

      # 이번에는 비율기반으로
      same_score=[]
      for item in score_dict :
        #print("#score_dict Type is :",type(score_dict))
        #print(list(item),"#item Type is :",type(item))

        # 베스트점수
        if item[1] >= score_dict[0][1] : 
          if score_dict[0][1] == 0 :
            break
          #print(newdata,"##",item[0],item[1],"##",score_dict[0][1])
          same_score.append(list(item))
      
      # 특정단어 매핑현황관찰
      #if('김가루' in score_dict[0][0] ) :
        #print("newdata : ",newdata, "#",score_dict[0],score_dict[1],score_dict[2])
        
      if len(same_score) >= 2 : #비교대상이있다면
        b_s2=0
        for idx2,food_name in enumerate(same_score) :
          a=self.isinclude_prop(newdata,food_name[0])
          b=self.count_phoneme(newdata,food_name[0])/len(food_name[0])
          if (a>b) :
            #print(same_score, "#Type is :",type(same_score))
            same_score[idx2][1] = a
          else : 
            #print(same_score, "#Type is :",type(same_score))
            same_score[idx2][1] = b
            #print(same_score)
        #self.comp[newdata]=same_score

        c = sorted(list(same_score), key=lambda x:x[1],reverse=True)
        self.food_kind[idx]= c[0][0]
      else :
        best = score_dict[0][1]
        if best == 0 :
          self.food_kind[idx] = newdata + " (DB에 존재하지않음)"#+"score : "+ str(best)

        else :
          self.food_kind[idx]= score_dict[0][0]
      
      # 모든데이터 scoredict 관찰
      print(newdata, "=>", score_dict[:2])
      
      # 모든데이터 변화현황보기
      if(showmapping) :
        print(newdata, "=>", self.food_kind[idx])






      # best = score_dict[0][1] # 가장높은점수가 0점이라면,
      # #print(best)
      
      
      
      # if best == 0 :
      #   self.food_kind[idx] = newdata + " (DB에 존재하지않음) score:"+ str(best)

      # else :
      #   #베스트스코어가 같은것끼리 리스트를 묶어 다시 한번 돌려줌 , 이번에는 비율로 점수계산





      #   self.food_kind[idx]= score_dict[0][0]#최대유사한 메뉴으로 교체
      if newdata in self.before.keys() :
        self.food_kind_meta[self.before[newdata]] = self.food_kind[idx]
      else : 
        self.food_kind_meta[newdata]=self.food_kind[idx]

      # # none 데이터 삽입
      # for key,val in self.none.items() :
      #   self.food_kind_meta[key]=val




if __name__ == '__main__' :
  print("")
  print('  ## 아래의 선택지 중 실행시킬 번호를 입력하세요.')
  print("")
  print(" 1. 두레비앙 식단 rawdata를 형식에 맞는 csv파일로 바꾸어줍니다.")
  usr_input = input('입력 : ')

  if usr_input == '1' :
    print("")
    print("  # 변환할 식단데이터는 실행되는 프로그램과 같은 폴더에 있어야 합니다.")
    print("  # 두레비앙 식단데이터는 보통 엑셀(xlsx)파일 입니다")
    print("")
    print(" 변환할 식단데이터의 파일명(확장자포함)을 입력해주세요.")
    filepath = input("입력 : ")
    raw_menu_To_df(filepath,download= True)
    print("")
    print(" *변환된 csv 파일이 생성되었습니다.")
    print(" *파일명은 'created.csv' 입니다.")
    print('')
    
  else : 
    print(' 프로그램이 종료됩니다.')
    print('')

