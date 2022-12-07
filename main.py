# -*- coding: utf-8 -*-
import bss1518, bss1519
import easygui,cv2



###########입력 및 기본적 가공################
data=bss1518.report() #영상 접수 함수


ix, iy= -1, -1
search_range=[]

def draw_rec(event, x, y, flags, param): #이 함수는 모듈화 시 오류가 발생하여 main.py에 넣었습니다.
	global ix, iy, drawing, mode, search_range, img
	if event==cv2.EVENT_LBUTTONDOWN: #마우스 좌클릭이 감지되면
		ix,iy=x,y
		if len(search_range)==0:
			search_range.append([x*2,y*2])
		elif [x,y]!=search_range[-1]:
			search_range.append([x*2,y*2]) #마우스의 x,y좌표값을 search_range에 append
	if len(search_range)==2:
		cv2.rectangle(img,tuple([search_range[0][0]//2,search_range[0][1]//2]),tuple([search_range[1][0]//2,search_range[1][1]//2]),(0,255,0),-1) #탐색에 필요한 두 기준점이 잡히면 그것으로 직사각형 그림
        
def draw_rec2(event, x, y, flags, param): #이 함수는 모듈화 시 오류가 발생하여 main.py에 넣었습니다.
	global ix, iy, drawing, mode, ROI_range, img
	if event==cv2.EVENT_LBUTTONDOWN: #마우스 좌클릭이 감지되면
		ix,iy=x,y
		if len(ROI_range)==0:
			ROI_range.append([x*2,y*2])
		elif [x,y]!=ROI_range[-1]:
			ROI_range.append([x*2,y*2]) #마우스의 x,y좌표값을 ROI_range에 append
	if len(ROI_range)==2:
		cv2.rectangle(img,tuple([ROI_range[0][0]//2,ROI_range[0][1]//2]),tuple([ROI_range[1][0]//2,ROI_range[1][1]//2]),(0,255,0),-1) #탐색에 필요한 두 기준점이 잡히면 그것으로 직사각형 그림
#img = np.zeros((720, 1280, 3), np.uint8)
        
file=data[0][0]
newmap=data[0][1]
inf=bss1519.info(file)
'''
bss1519.frame(file,newmap)
'''


ROI_range=[]
img=cv2.imread(newmap+"/1.png")
img=cv2.resize(img,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
cv2.namedWindow('ROI range')
cv2.setMouseCallback('ROI range',draw_rec2)
print('마우스로 영상을 탐색할 두 기준점을 찍은 후, 직사각형이 그려지면 esc키를 누르세요.')
while 1:
	cv2.imshow('ROI range',img)
	k=cv2.waitKey(1) & 0xFF
	if k==27: break #esc키를 누르면 종료
cv2.destroyAllWindows()

ROI_range=[ROI_range[0],[0,0],[0,0],ROI_range[1]]
ROI_range[1]=[ROI_range[3][0],ROI_range[0][1]]
ROI_range[2]=[ROI_range[0][0],ROI_range[3][1]]
###############영상 가공 및 값 추출#################

av=['sam']
tempchaseon=bss1519.doit(newmap,5,ROI_range)  #5프레임 정도 미리 차선 따놓기

search_range, =bss1519.makesr(tempchaseon,ROI_range,inf)  #내 차선에 내접하는 사다리꼴 만들

direction,frcount=bss1519.hoit(search_range,newmap,av,inf)  #두 차의 위치관계 #left or right
img=cv2.imread(newmap+"/1.png")

chaseon=bss1519.doit(newmap,frcount,ROI_range)  #차선 리스트

cs=bss1519.analcoc(chaseon)      #내가 차선 변경 하였는지 #yes or no


     

###############판단 및 출력#####################
data=bss1518.judge(data,cs,direction) #판단 함수 #data=['D:/test.mp4','앞차',['무면허 운전'],['해당 사항 없음'],20,-20,502,40,60]

bss1518.show(data) #그래프 및 설명 출력 함수
