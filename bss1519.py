# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 00:01:46 2018

@author: Hyun Seo
"""

import cv2
import numpy as np
import math

def frame(filename, portal): 
    vid=cv2.VideoCapture(filename) #비디오 보기
    count=0
    while True:
        yes, image=vid.read() #영상을 사진 단위로 받아오기
        if not yes: #영상이 끝나면
            break
        count+=1
        cv2.imwrite(portal+'/'+str(count)+'.png',image) #지정된 경로에 저장
        if count==200:
            break


def info(filename): #[총 프레임 수, fps, 가로, 세로 길이] 리턴
    vid=cv2.VideoCapture(filename)
    temp=[]
    temp.append(int(vid.get(cv2.CAP_PROP_FRAME_COUNT))) #총 프레임 수
    temp.append(int(vid.get(cv2.CAP_PROP_FPS))) #fps
    temp.append(int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))) #가로
    temp.append(int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))) #세로
    return temp



def sub(a,b):
    if a>=b:
        return int(a-b)
    return int(b-a)




def grayscale(img): # 흑백이미지로 변환
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def canny(img, low_threshold, high_threshold): # Canny 알고리즘
    return cv2.Canny(img, low_threshold, high_threshold)

def gaussian_blur(img, kernel_size): # 가우시안 필터
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def region_of_interest(img, vertices, color3=(255,255,255), color1=255): # ROI 셋팅

    mask = np.zeros_like(img) # mask = img와 같은 크기의 빈 이미지

    if len(img.shape) > 2: # Color 이미지(3채널)라면 :
        color = color3
    else: # 흑백 이미지(1채널)라면 :
        color = color1

    # vertices에 정한 점들로 이뤄진 다각형부분(ROI 설정부분)을 color로 채움
    cv2.fillPoly(mask, vertices, color)

    # 이미지와 color로 채워진 ROI를 합침
    ROI_image = cv2.bitwise_and(img, mask)
    return ROI_image


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap): # 허프 변환
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    #line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    #draw_lines(line_img, lines)

    return lines



def doit(newmap,frcount,ROI_range):
    chaseon=[]
    for i in range(1,frcount+1):
        image = cv2.imread(newmap+"/"+str(i)+'.png') # 이미지 읽기
        height, width = image.shape[:2] # 이미지 높이, 너비


        gray_img = grayscale(image) # 흑백이미지로 변환


        blur_img = gaussian_blur(gray_img, 3) # Blur 효과

        canny_img = canny(blur_img, 50, 160) # Canny edge 알고리즘

        vertices = np.array([ROI_range], dtype=np.int32)
        ROI_img = region_of_interest(canny_img, vertices)


        line_arr = hough_lines(ROI_img, 1, 1 * np.pi/180, 30, 10, 20) # 허프 변환   #[x1, y1, x2, y2]
        line_arr = np.squeeze(line_arr)

        # 기울기 구하기
        slope_degree = (np.arctan2(line_arr[:,1] - line_arr[:,3], line_arr[:,0] - line_arr[:,2]) * 180) / np.pi

        # 수평 기울기 제한
        line_arr = line_arr[np.abs(slope_degree)<160]
        slope_degree = slope_degree[np.abs(slope_degree)<160]
        # 수직 기울기 제한
        line_arr = line_arr[np.abs(slope_degree)>95]
        slope_degree = slope_degree[np.abs(slope_degree)>95]
        # 필터링된 직선 버리기
        L_lines, R_lines = line_arr[(slope_degree>0),:], line_arr[(slope_degree<0),:]
        L_lines, R_lines = L_lines[:,None], R_lines[:,None]
        for j in L_lines:
            for k in j:
                for l in k:
                    l=int(l)
        for j in R_lines:
            for k in j:
                for l in k:
                    l=int(l)
        temp1=[list(j) for j in L_lines]+[list(j) for j in R_lines]
        rrealtemp=[]
        temp2=[]
        for j in temp1:
            for k in j:
                for l in k:
                    rrealtemp.append(int(l))
                temp2.append(rrealtemp)
                rrealtemp=[]
        chaseon.append(temp2)
    return chaseon  #3차


def gradient(a): #기울기
    g=(a[3]-a[1])/(a[2]-a[0])   #delta y/ delta x
    return g


def analcoc(chaseon):
    count=0
    for j in chaseon:
        for i in j:
            if i==[]:
                continue
            a=gradient(i)
            if abs(a)>math.tan(1.48): #차선의 기울기가 85도를 넘어가면
                count+=1
                if count==5: #5프레임 이상 지속되면
                    return 'yes'
    return 'no'  #차선 변경이 없었다


def SAM_572(search_range,newmap,aV,a):  #search_range=[[a1,b1],[a2,b1],[a3,b2],[a4,b2],[기울기, y절편],[기울기, y절편]]
    av=aV
    temp1=[0,0,0]  #왼쪽
    temp2=[0,0,0]  #오른쪽
    temp=[]
    left=search_range[4]
    right=search_range[5]
    img=cv2.imread(newmap+"/"+str(a)+".png")  #이미지 불러오기
    for k in range(search_range[0][1],search_range[2][1]): #각각의 행
        for j in range(int((k-left[1])/left[0]),int(((k-left[1])/left[0]+int(k-right[1])/right[0])//2)):#왼쪽 부분
            for h in range(3):
                temp1[h]+=int(img[k][j][h]) #BGR값 모두 합하기
        for j in range(int(((k-left[1])/left[0]+(k-right[1])/right[0])/2),int((k-right[1])/right[0]+1)): #오른쪽 부분
            for h in range(3):
                temp2[h]+=int(img[k][j][h]) #BGR값 모두 합하기
    for h in range(3):
        temp1[h]=temp1[h]//((search_range[1][0]-search_range[0][0]+search_range[3][0]-search_range[2][0])*(search_range[2][1]-search_range[0][1])//4)  #평균 내기
        temp2[h]=temp2[h]//((search_range[1][0]-search_range[0][0]+search_range[3][0]-search_range[2][0])*(search_range[2][1]-search_range[0][1])//4)
    temp.append(temp1)
    temp.append(temp2)
    av.append(temp)
    return av




def hoit(search_range,newmap,av,inf):
    left_count=0
    right_count=0
    av=SAM_572(search_range,newmap,av,1)
    start=av[1]  #처음 내 앞의 상
    for i in range(2,inf[0]+1):
        av=SAM_572(search_range,newmap,av,i)
        if sub(av[i][0][0],start[0][0])+sub(av[i][0][1],start[0][1])+sub(av[i][0][2],start[0][2])>=40: #BGR 값의 변화
            left_count+=1 
        if sub(av[i][1][0],start[1][0])+sub(av[i][1][1],start[1][1])+sub(av[i][1][2],start[1][2])>=40: #BGR값의 변화
            right_count+=1
        if sub(av[i][0][0],start[0][0])+sub(av[i][0][1],start[0][1])+sub(av[i][0][2],start[0][2])<40 and left_count!=0:
            left_count=0
        if sub(av[i][1][0],start[1][0])+sub(av[i][1][1],start[1][1])+sub(av[i][1][2],start[1][2])<40 and right_count!=0:
            right_count=0
        if left_count>=3 and right_count>=3:
            return ('no',i)
        if left_count==5:
            return ('left',i)
        if right_count==5:
            return ('right',i)
    return ('no',0)
    
def makesr(chaseon,ROI_range,inf):
    search_range=[0,0,0,0]
    left=[0,0] #기울기, y절편   #왼쪽 차선
    right=[0,0] #오른쪽 차선
    left[0]=gradient(chaseon[0][0])  #왼쪽 기울기
    right[0]=gradient(chaseon[0][-1])  #오른쪽 기울기
    left[1]=chaseon[0][0][1]-left[0]*chaseon[0][0][0]
    right[1]=chaseon[0][-1][1]-right[0]*chaseon[0][-1][0]
    b1=ROI_range[0][1]+inf[3]//12  #도로인 첫 y지점에서 적당히 밑으로
    a1=(b1-left[1])/left[0]  #왼쪽 차선에 접하게
    a2=(b1-right[1])/right[0]  #오른쪽 차선에 접하게
    b2=ROI_range[3][1]-inf[3]//12   #도로인 마지막 y지점에서 적당히 위
    a3=(b2-left[1])/left[0]  #왼쪽 차선에 접하게
    a4=(b2-right[1])/right[0]  #오른쪽 차선에 접하게
    
    
    search_range[0]=[a1,b1]
    search_range[1]=[a2,b1]
    search_range[2]=[a3,b2]
    search_range[3]=[a4,b2]
    search_range.append(left)
    search_range.append(right)
    
    road=[0,0,0,0]
    y2=ROI_range[3][1]-inf[3]//30
    y1=ROI_range[3][1]-inf[3]//15
    x1=(y1-left[1])/left[0]+20  #왼쪽 차선에 접하게
    x2=(y1-right[1])/right[0]-20  #오른쪽 차선에 접하게
    x3=(y2-left[1])/left[0]+20  #왼쪽 차선에 접하게
    x4=(y2-right[1])/right[0]-20  #오른쪽 차선에 접하게
    road[0]=[x1,y1]
    road[1]=[x2,y1]
    road[2]=[x3,y2]
    road[3]=[x4,y2]
    
    return (search_range,road)

def roadcolor(newmap,road):
    cnt=1
    road_color=[0,0,0]
    while True:
        img=cv2.imread(newmap+'/'+str(cnt)+'.png')
        for i in range(road[2][0]+5,road[3][0]-5):
            road_color[0]+=img[i][road[2][1]][0]
            road_color[1]+=img[i][road[2][1]][1]
            road_color[2]+=img[i][road[2][1]][2]
        road_color[0]=road_color[0]//(road[3][0]-road[2][0])
        road_color[1]=road_color[0]//(road[3][0]-road[2][0])
        road_color[2]=road_color[0]//(road[3][0]-road[2][0])
        if road_color[0]<150 and road_color[1]<150 and road_color[2]<150:
            return road_color
        cnt+=1
        

    
    
    
    
    
    
    
    
    
    
    
    
 
