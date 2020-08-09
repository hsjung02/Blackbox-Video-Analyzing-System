# -*- coding: utf-8 -*-
import easygui
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc  # 한글지원
'''
import pygame
'''
def report():
    title='사고 영상 접수'
    msg='프로그램을 실행해주셔서 감사합니다.\n이 프로그램은 블랙박스 영상 분석을 통한 빠른 과실비율 판단을 위해 만들어졌으며, 손해보험협회의 자동차 과실비율 산정기준을 판단 근거로 삼고 있습니다. \n\n단, 이 프로그램이 제공하는 결과는 법적인 효력이 없으므로 참고용으로 사용하시기 바랍니다.'
    easygui.msgbox(msg,title)
    information=[]
    msg='사고 영상이 저장된 경로를 입력하세요\n(뒷 차량에서 촬영된 영상이어야 합니다)'
    fieldname='G:/example/video/important.mp4'
    information.append(easygui.enterbox(msg,title,fieldname)) #사고 영상 경로 입력받음
    if information[0]=='' or information[0]==None:
        easygui.msgbox("경로명을 입력하지 않으셨습니다. 프로그램이 종료됩니다. 다시 실행해주세요.")
        return
    msg='처리 시 필요한 파일들을 저장할 경로를 입력해주세요.'
    fieldname='G:/example/images/important'
    information[0]=[information[0],easygui.enterbox(msg,title,fieldname)]
    if information[0][1]=='' or information[0][1]==None:
        easygui.msgbox("경로명을 입력하지 않으셨습니다. 프로그램이 종료됩니다. 다시 실행해주세요.")
        return
    msg='당신의 차는 사고 당시 앞 차량이었나요? 아니면 뒷 차량이었나요?'
    if easygui.boolbox(msg,title,["앞차", "뒷차"]): you='앞차' #사고 당시 위치 관계 입력받음
    else: you='뒷차'
    information.append(you)
    checklist=['해당 사항 없음','음주 운전','무면허 운전', '졸음 운전', '과속 운전','(차선 변경 시) 방향지시등 미점등','운전 중 휴대폰 및 DMB 사용','초보운전 스티커 부착','합류되어 사라지는 도로 주행중','이유없는 급정거']
    frontplus=0
    rearplus=0
    msg="앞 차량에 해당하는 사항이 있을 경우 선택해주세요."
    checked=easygui.multchoicebox(msg,title,checklist) #앞 차량의 과실 사항 체크받음
    if checked==None: return
    if '이유없는 급정거' in checked: #이 경우 앞차의 과실비율 30% 추가
        frontplus+=30
        rearplus-=30
    if '음주 운전' in checked or '무면허 운전' in checked or '졸음 운전' in checked: #이 경우 앞차 과실비율 20% 추가
        frontplus+=20
        rearplus-=20
    if '과속 운전' in checked or '(차선 변경 시) 방향지시등 미점등' in checked or '운전 중 휴대폰 및 DMB 사용' in checked: #앞차 과실비율 10% 추가
        frontplus+=10
        rearplus-=10
    if '초보운전 스티커 부착' in checked: #이 경우 상대방의 과실비율 10% 추가
        frontplus-=10
        rearplus+=10
    information.append(checked)
    msg="뒷 차량에 해당하는 사항이 있을 경우 선택해주세요."
    checked=easygui.multchoicebox(msg,title,checklist[:-3]+['갓길 주행']) #뒷 차량의 과실 사항 체크받음
    if checked==None: return
    if '음주 운전' in checked or '무면허 운전' in checked or '졸음 운전' in checked:
        rearplus+=20
        frontplus-=20
    if '과속 운전' in checked or '운전 중 휴대폰 및 DMB 사용' in checked:
        rearplus+=10
        frontplus-=10
    if '초보운전 스티커 부착' in checked:
        rearplus-=10
        frontplus+=10
    information.append(checked)
    information+=[frontplus,rearplus]
    return information #information=[영상_경로, 앞차인지_뒷차인지, 앞차_특징, 뒷차_특징, 앞차_추가_과중, 뒷차_추가_과중]




def judge(information,cs,direc): #cs(내 차량),direc(상대방 차량)=left or right or no
    if '합류도로를 통해 합류 중' in information[2]:
        return information+[501,70,30]
    
    if '합류되어 사라지는 도로 주행중' in information[2]:
        return information+[502,60,40]
    
    if direc=='no' and '갓길 주행' in information[3]: #뒷차와 앞차의 차선이 같았고 갓길을 주행한 경우
        return information+[506,0,100]
    
    elif direc=='no':
        return information+[507,0,100]
    
    if cs=='no' and direc=='right':
        return information+[503,80,20]
    
    if cs=='no' and direc=='left':
        return information+[504,70,30]
    


def show(information): #information=[영상_경로, 앞차인지_뒷차인지, 앞차_특징, 뒷차_특징, 앞차_추가_과중, 뒷차_추가_과중, 사건유형번호, 앞차_과실비율, 뒷차_과실비율]

    front_fault=information[4]+information[7] #입력받은 앞, 뒷차의 특징을 바탕으로 최종 과실 비율 계산
    rear_fault=information[5]+information[8]
    if front_fault>=100:
        front_fault=100
        rear_fault=0
    elif rear_fault>=100:
        rear_fault=100
        front_fault=0
        
    description={501:['합류도로를 통해 진입중',
                      '주행로 주행',
                      '앞 차량은 본선도로의 주행을 방해해서는 안 될 의무가 있고, 뒷 차량은 진입하려는 자동차를 잘 살펴야 할 의무가 있습니다.'],
                 502:['합류되어 사라지는 차로 주행',
                      '합류가 예상되는 차로에서 후행',
                      '두 차량 모두 차로 감소를 예상하여 안전운전을 해야 할 의무가 있으나, 합류차인 앞 차량의 주의의무가 더 큽니다.'],
                 503:['주행로에서 추월로로 진로변경',
                      '추월로에서 직진',
                      '앞 차량이 추월선으로 진로를 변경할 때 뒷 차량의 움직임을 잘 살피지 못한 과실이 큽니다.'],
                 504:['추월로(또는 주행로)에서 주행로로 진로변경',
                      '주행로에서 직진',
                      '앞 차량의 경우 진로를 변경할 때 뒤에 따라오는 차량의 움직임을 잘 살피지 못한 과실이 큽니다.'],
                 505:['주행로에 정차',
                      '후행',
                      '일반도로와 달리 고속도로에서는 자동차의 주정차를 예상하기 어려우므로 과실 비율이 다음과 같습니다.'],
                 506:['갓길에 정차',
                      '갓길에서 후행',
                      '운전자는 자동차의 고장 등 부득이한 사유가 있는 경우를 제외하고는 정해진 차로에 따라 통행해야하며 갓길로 통행하여서는 안됩니다.'],
                 507:['주행',
                      '앞차보다 빠르게 주행',
                      '뒷 차량은 전방을 잘 살피지 못하였고 안전거리를 확보하지 않았기 때문에 일방적인 과실이 있습니다.']
                 } #사고 상황 별 설명을 담은 딕셔너리
    checklist_percent={'음주 운전':'(+20%)',
                       '무면허 운전':'(+20%)',
                       '졸음 운전': '(+20%)',
                       '과속 운전':'(+10%)',
                       '운전 중 휴대폰 및 DMB 사용':'(+10%)',
                       '(차선 변경 시) 방향지시등 미점등':'(+10%)',
                       '초보운전 스티커 부착':'(-10%)',
                       '이유없는 급정거':'(+30%)'} #각 사항 별 추가 과실 비율을 담은 딕셔너리
    
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name) #원그래프에 한글 폰트 적용
    
    x=['앞 차량', '뒷 차량'] #정의역
    if information[1]=='앞차': x[0]+='(당신의 차량)'
    else: x[1]+='(당신의 차량)'
    y=[front_fault, rear_fault] #치역    
    plt.title('<즉석 과실비율 분석 결과>',size=15) #그래프 제목
    wedges, texts, autotexts = plt.pie(y,labels=x,
                                       autopct='%1d%%', pctdistance=0.85,
                                       shadow=True, startangle=90)
    for w in wedges: # 조각 설정
        w.set_linewidth(1)
        w.set_edgecolor('w')

    for t in texts: # label 설정
        t.set_color('k')
        t.set_fontsize(12)

    for a in autotexts: # 퍼센티지 설정
        a.set_color('w')
        a.set_fontsize(12)
    plt.savefig("piegraph.png",dpi=300) #원그래프를 이미지로 저장
    plt.show() #원그래프 보여줌
    
    
    front_result_text, rear_result_text, explain = description[information[6]]
    front_result_text=x[0]+': '+front_result_text+'('+str(information[7])+'%)'
    rear_result_text=x[1]+': '+rear_result_text+'('+str(information[8])+'%)'
    explain='총 과실 => '+str(front_fault)+':'+str(rear_fault)+'   (사고 분류 유형 : '+str(information[6])+'번)'+'\n\n해설 : '+explain+'\n\n\n ** 반영비율이 같은 사항들은 하나만 과실비율에 반영됩니다.'
    if front_fault>=50: front_result_text+='* 보험료 할증 대상!'
    if rear_fault>=50: rear_result_text+='*보험료 할증 대상!'
    for i in information[2]:
        if i!='해당 사항 없음' and i!='합류되어 사라지는 도로 주행중':
            front_result_text=front_result_text+'\n  - '+i+checklist_percent[i] #앞 차량 설명에 과실 추가요소들을 추가함
    for j in information[3]:
        if j!='해당 사항 없음':
            rear_result_text=rear_result_text+'\n  - '+j+checklist_percent[j] #뒷 차량 설명에도 과실 추가요소들을 추가함
    easygui.msgbox(front_result_text+'\n\n'+rear_result_text+'\n\n'+explain) #창 띄움


#################################################################################    



















