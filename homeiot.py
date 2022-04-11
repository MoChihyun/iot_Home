from re import L
from signal import pause
from time import sleep
import requests
import json
import sounddevice as sd
import soundfile as sf
from io import BytesIO
from gpiozero import LED,Servo,Button
from pydub import AudioSegment
from pydub.playback import play
import sys

# 클래스화는 다음에 할게요 

button=Button(21,bounce_time=0.07)
servo=Servo(19,min_pulse_width=0.0004,max_pulse_width=0.0024)
red=LED(16)

def recognize():
    global is_success,result

    fs=16000
    seconds=5


    myrecording=sd.rec(int(seconds*fs),samplerate=fs,channels=1)
    sd.wait()

    mem_wav=BytesIO()
    sf.write(mem_wav,myrecording,fs,format="wav")

    print(mem_wav.tell())
    audio=mem_wav.seek(0)

    kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"

    rest_api_key='db7d3e117257f54d58bf7347d49b91b9'

    headers={
        "Content_Type": "applicatioin/octet-stream",
        "X-DSS-Service": "DICTATION",
        "Authorization": "KakaoAK " +rest_api_key,

    }
    # with open('converted.wav','rb') as fp:
    #     audio=fp.read()
    #이것만 교체
    res=requests.post(kakao_speech_url,headers=headers,data=mem_wav)

    print(res.text)

    result_json_string=res.text[
        res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1

    ]
    result=json.loads(result_json_string)
    print(result)
    print(result['value'])

    is_success=True
    start=res.text.find('{"type":"finalResult"')
    end=res.text.rindex('}')+1

    if start==-1:
        start=res.text.find('{"type":"errorCalled"')
        is_success=False

    result_json_string=res.text[start:end]
    result=json.loads(result_json_string)
    return is_success, result

# 음성인식처리

API_KEY='0333a09d025f1976cbb5177a5f6c9b9a'

def get_weather(city='Seoul'):
    URL=f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={API_KEY}&lang=kr'
    print(URL)

    weather={}

    res=requests.get(URL)
    if res.status_code==200:
        result=res.json()
        weather['main']=result['weather'][0]['main']
        weather['description']=result['weather'][0]['description']

        print(result['weather'][0]['description'])
        icon=result['weather'][0]['icon']
        weather['icon'] = f'http://openweathermap.org/img/w/{icon}.png' 
        weather['etc'] = result['main']

    else:
        print('error',res.status_code)

    return weather

weather = get_weather()
print(json.dumps(weather, indent=4, ensure_ascii=False))
weather
# 날씨처리



# print(round(float(weather["etc"]["temp_min"]-273),1))

URL = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
HEADERS={

    "content-Type":"application/xml",
    "Authorization": "KakaoAK db7d3e117257f54d58bf7347d49b91b9"
}
def make_text(text,name="MAN_READ_CALM"):
    return f"""
    <speak>
        <voice name="{name}">{text}</voice>
    </speak>
    """



# 음성합성







# button.when_pressed=recognize
while True:
    button.wait_for_press()
    recognize()
    if is_success:
        print('인식결과',result['value'])
        print(type(result['value']))

        if(result['value']=="문 열어"):
            servo.min()
            sleep(1)
            
            print("문열게요")
            # result['value']="초기화"
            # print(result['value'])
            
        elif(result['value']=="문 닫아"):
            servo.max()
            sleep(1)
            
            print("문 닫을게요")
        elif(result['value']=="전등 켜"):
            print("전등 킬게요")
            red.on()
            sleep(1)
        elif(result['value']=="전등 꺼"):
            print("전등 끌게요")
            red.off()
            sleep(1)

        elif(result['value']=="날씨 알려줘"):
            text=f'''오늘 날씨는 {weather["description"]} 최저온도는 {round(float(weather["etc"]["temp_min"]-273),1)} 도
            최고온도는 {round(float(weather["etc"]["temp_max"]-273),1)} 도입니다 
            또한 습도는 {weather['etc']['humidity']} 입니다. 좋은 하루 되세요
            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)

        elif(result['value']=="종료해"):
            break

        elif(result['value']!="문 열어" or result['value']!="문 닫아" or result['value']!="전등 켜" or result['value']!="전등 꺼" or result['value']!="날씨 알려줘" or result['value']!="종료해"):
            # result['value']="초기화"
            
            text=f'''죄송합니다 다시 말씀해주세요
            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)



        # elif(result['value']=="초기화"):
        #     continue

        
    else:
        print("인식실패:",result['value'])

# 클래스화는 다음에 할게요