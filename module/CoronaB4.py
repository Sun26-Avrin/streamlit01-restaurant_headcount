import bs4
import urllib.request as ul
import datetime
import pandas as pd
import os
def get_incDec(startdate='yesterday',enddate='yesterday',download=False) :
  if (startdate=='yesterday') and (enddate=='yesterday') :
    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    startDate = yesterday.strftime('%Y%m%d')
    endDate = startDate

    url = f"http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson?serviceKey=MfaA52VnJwmTOj%2F0hHVoOt1GOHvOpXvBxcwzvC1%2FJOpxSoxgpkUSBynYPEbmt67vvUdSCFERj%2F7ZSJ%2FmoiZaFA%3D%3D&pageNo=1&numOfRows=10&startCreateDt={startDate}&endCreateDt={endDate}"
    request = ul.Request(url)
    response = ul.urlopen(request)
    text = response.read()
    xml = bs4.BeautifulSoup(text, 'lxml-xml')
    item = xml.findAll('item')    

    for i in item :
      if '대구' in str(i) :
        incDec = i.find("incDec").text
    #print('Im there!')
    return incDec 

  else :
    #try :
    datetime.datetime.strptime(startdate,'%Y%m%d')
    datetime.datetime.strptime(enddate,'%Y%m%d')
    startDate = startdate
    endDate = enddate

    url = f"http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson?serviceKey=MfaA52VnJwmTOj%2F0hHVoOt1GOHvOpXvBxcwzvC1%2FJOpxSoxgpkUSBynYPEbmt67vvUdSCFERj%2F7ZSJ%2FmoiZaFA%3D%3D&pageNo=1&numOfRows=10&startCreateDt={startDate}&endCreateDt={endDate}"
    request = ul.Request(url)
    response = ul.urlopen(request)
    text = response.read()
    xml = bs4.BeautifulSoup(text, 'lxml-xml')
    item = xml.findAll('item') 

    incDec = {}
    for i in item :
        if '대구' in str(i) :
          incDec[i.find("stdDay").text] = (i.find("incDec").text)
    #print('Im here!') 

    if(download == True) :
      if os.path.exists("./CoronaCSV") == False :
        os.mkdir("./CoronaCSV")
      csv = pd.DataFrame(list(incDec.items()),columns=['날짜','코로나확진자수'])
      filename = "./CoronaCSV/대구코로나확진자수_"
      filename+=startDate
      filename+="_"
      filename+=endDate
      filename+=".csv"
      csv.to_csv(filename)

    return incDec

    # except :
    #   print('날짜형식이 올바르지 않습니다. 권장예시 : "20200801"')
    #   return -1


    
  



  




if __name__ == '__main__' :
  release=1
  while (release) :
    print("  ## 이 프로그램은 코로나 대구 확진자수를 출력하며, 이를 csv파일로 저장할 수 있습니다.")
    print("  ** 선택지를 선택하여 주십시오")
    print("")
    print("  1. 어제 대구 확진자 수")
    print("  2. 일정기간 내 대구 확진자 수")
    choice = input("  $ 입력 :")

    if (choice == '1') :
      print("")
      print("  어제일자 코로나 대구 확진자 수 : ",get_incDec())
      release=0
    elif (choice == '2') :
      print("  startDate 및 endDate를 입력해야합니다. ")
      print("  입력예시 : 20200801")
      print("")
      startdate = input("  startDate를 입력해주세요 : ")
      print("")
      enddate = input("  endDate를 입력해주세요 : ")
      print("")
      print("  csv파일로 다운로드 하시겠습니까? 다운로드를 원하신다면 y를 입력해주세요 ")
      print("  동의하지 않으신다면 아무키를 눌러주세요 ")
      downconfig = input("  입력 : ")
      release=0

      if (downconfig == 'y') or (downconfig == 'Y') :
        get_incDec(startdate=startdate, enddate=enddate,download=True)
        print('')
        print('')
        print('  # 다운로드가 완료되었습니다. CoronaCSV폴더를 확인해주세요.')
        print('')
      else :
        get_incDec(startdate=startdate, enddate=enddate)
        print('  # 리턴값이 반환되었습니다.')
        print('')

    else :
      print("")
      print("  선택지를 잘못 입력하셨습니다. ")
      print('')
      continue


  

  import os
  os.system('pause')
