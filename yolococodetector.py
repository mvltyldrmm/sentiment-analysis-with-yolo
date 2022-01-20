import cv2,time,psycopg2,json
from config import env
import numpy as np
import os
from classes import record_data

connection = psycopg2.connect(
database=os.getenv('DATABASE'),
user=os.getenv('USER'),
password=os.getenv('PASSWORD'),
host=os.getenv('HOST'),
port=os.getenv('POST'),
)

cursor = connection.cursor()

net = cv2.dnn.readNet("my_model/emotion_yolov4_1000.weights","my_model/emotion_yolov4.cfg")
#import model
start_time = time.time()  
#start time
classes = []
with open("my_model/emotion.names","r") as f:
    classes = [line.strip()for line in f.readlines()]
    
layer_names = net.getLayerNames()
outputlayers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

colors = np.random.uniform(0,255,size=(len(classes),3))

#loading image
cap=cv2.VideoCapture(0) #0 for 1st webcam
font = cv2.FONT_HERSHEY_PLAIN
starting_time= time.time()
frame_id = 0

happy_detection = 0
sad_detection = 0

while True:
    _,frame= cap.read() # 
    frame_id+=1
    
    height,width,channels = frame.shape
    #detecting objects
    blob = cv2.dnn.blobFromImage(frame,0.00392,(320,320),(0,0,0),True,crop=False) #reduce 416 to 320    
        
    net.setInput(blob)
    outs = net.forward(outputlayers)
    #print(outs[1])

    #Showing info on screen/ get confidence score of algorithm in detecting an object in blob
    class_ids=[]
    confidences=[]
    boxes=[]
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            
            confidence = scores[class_id]

            if confidence > 0.3:
                #onject detected
                center_x= int(detection[0]*width)
                center_y= int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)

                #cv2.circle(img,(center_x,center_y),10,(0,255,0),2)
                #rectangle co-ordinaters
                x=int(center_x - w/2)
                y=int(center_y - h/2)
                #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

                boxes.append([x,y,w,h]) #put all rectangle areas
                confidences.append(float(confidence)) #how confidence was that object detected and show that percentage
                class_ids.append(class_id) #name of the object tha was detected

    indexes = cv2.dnn.NMSBoxes(boxes,confidences,0.4,0.6)

    for i in range(len(boxes)):
        if i in indexes:
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            if label == "sad":
                sad_detection +=1
            else:
                happy_detection +=1    
            confidence= confidences[i]
            color = colors[class_ids[i]]
            cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
            cv2.putText(frame,label+" "+str(round(confidence,2)),(x,y+30),font,1,(255,255,255),2)
            
    elapsed_time = time.time() - starting_time

    fps=frame_id/elapsed_time
    cv2.putText(frame,"FPS:"+str(round(fps,2)),(10,50),font,2,(0,0,0),1)
    
    cv2.imshow("Image",frame)
    key = cv2.waitKey(1) #wait 1ms the loop will start again and we will process the next frame
    
    if key == 27: #esc key stops the process
        postgres_insert_query = """ INSERT INTO records_data (id, name, description, total_time,emotion_analytics ) VALUES (%s,%s,%s,%s,%s)"""
        name = input("NAME :")
        description = input("DESCRIPTON :")
        total_time = int((time.time() - start_time))
        emotion_analytics = "Happy emotion : ", happy_detection , " Sad emotion :" ,sad_detection
        data = record_data.records_data(name, description, round(elapsed_time,1), json.dumps(emotion_analytics))                   
        record_to_insert = (str(data.uuid),data.name, data.description, data.total_time, data.emotion_analytics)
        print("Database id : ", data.uuid)
        cursor.execute(postgres_insert_query, record_to_insert)

        break;

connection.commit()  #insert db

print("Last db data : ")
cursor.execute("""select * from records_data""")
result = cursor.fetchall();
for i in result:
    print(i)
connection.close()
#db close
cap.release()    
cv2.destroyAllWindows()
#opencv close