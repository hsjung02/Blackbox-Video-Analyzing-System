# 블랙박스 영상 분석을 통한 고속도로 사고 과실 분석

## 1. 연구동기
우리나라에서 매년 발생하는 교통사고는 무려 20만 건. 지금 이 시간에도 고속도로에서는 셀 수 없이 사고가 일어나고 있다. 고속도로에서 한번 사고가 발생하면 사고가 났을 때 보험회사의 차량이 출동하기 전까지는 과실 비율을 바로 산정할 수 없다는 문제도 있다. 그 전까지 교통이 정체되는 혼란이 빚어지는 것이다. 만약 보험회사가 출동하는데 걸리는 시간인 5~10분보다 빠르게 오프라인에서 간단하게 과실을 확인할 수 있다면, 이로 인한 피해가 줄어들 것이라 생각했고 따라서 OpenCV를 이용해 블랙박스의 영상을 분석해보기로 하였다.

## 2. 흐름도
 ![흐름도](/flow_chart.png)
 
## 3. 주요 코드
### 3.1 영상을 프레임 단위로 분리
 영상 분석을 하기 위해 영상을 프레임 단위로 분리하여 저장하였다
 ```python
 def frame(filename, portal): #(파일 경로, 저장 경로)
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
  ```
### 3.2 차선 검출
 Canny edge 알고리즘을 이용해 차선을 검출하였다
 ![차선 검출](/img/chaseon.png){: height="100"}
 ```python
 def doit(inf,newmap,frcount,ROI_range):
    chaseon=[]
    for i in range(1,frcount+1):
        start_time=time.time()
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
        if i==1 or inf[0]//10*10%i==0:
            k=(frcount-i)*(time.time()-start_time)/(i)
            print(k,"초 정도 남았습니다")
    return chaseon  #3차
 ```

### 3.3 충돌 시점 결정
 차량 전방의 RGB 평균값이 급격하게 변하는 시점이 사고 시점이라 판단하였다. 전방에 차선에 접하는 사다리꼴 영역을 만들고, 그 영역 내의 RGB 평균값을 계산하였다.
 ![사다리꼴](/img/timing.png)
 ```python
 def hoit(search_range,newmap,av,inf):
    left_count=0
    right_count=0
    start=av[1]  #처음 내 앞의 상
    for i in range(1,inf[0]+1):
        av=SAM_572(search_range,newmap,av,i)
        if sub(av[i][0][0],start[0][0])+sub(av[i][0][1],start[0][1])+sub(av[i][0][2],start[0][2])>=40: #BGR 값의 변화
            left_count+=1 
        if sub(av[i][1][0],start[1][0])+sub(av[i][1][1],start[1][1])+sub(av[i][1][2],start[1][2])>=40: #BGR값의 변화
            right_count+=1
        if sub(av[i][0][0],start[0][0])+sub(av[i][0][1],start[0][1])+sub(av[i][0][2],start[0][2])<40 and left_count!=0:
            left_count=0
        if sub(av[i][1][0],start[1][0])+sub(av[i][1][1],start[1][1])+sub(av[i][1][2],start[1][2])<40 and right_count!=0:
            right_count=0
        if left_count==5:
            return ('left',i)
        if right_count==5:
            return ('right',i)
    return ('no',0)
 ```
### 3.4 차선 변경 여부 검출
 ```python
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
 ```

### 3.5 과실비율 결정
 ```python
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
 ```

### 3.6 시각화
 사용자에게 결과를 글과 그래프로 시각화하여 보여준다
 ![팝업](/img/show1.png) ![그래프](/img/show2.png)
 ```python
 def show(information): #information=[영상_경로, 앞차인지_뒷차인지, 앞차_특징, 뒷차_특징, 앞차_추가_과중, 뒷차_추가_과중, 사건유형번호, 앞차_과실비율, 뒷차_과실비율]

    front_fault=information[4]+information[7] #입력받은 앞, 뒷차의 특징을 바탕으로 최종 과실 비율 계산
    rear_fault=information[5]+information[8]
    if front_fault>=100:
        front_fault=100
        rear_fault=0
    elif rear_fault>=100:
        rear_fault=100
        front_fault=0
 ```
 
 
## 4. Member
 - 정현서 HyunSeo Jung, @BSS / [hsjung02@Github](http://github.com/hsjung02)
 - 정상 Sang Jung, @BSS / [withsang@Github](http://github.com/withsang)
