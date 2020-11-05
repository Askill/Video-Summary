#python
import cv2
import imageio
import time
writer = imageio.get_writer("./x23.mp4", fps=20)
        
url = "http://50.227.41.1/mjpg/video.mjpg"
i = 0
cap = cv2.VideoCapture(url)
while True :
    try:
        if i < 10:
            i+=1
            continue
        
        
        result, frame = cap.read()
        
        if result == False: 
            print("Error in cap.read()") # this is for preventing a breaking error 
            # break;
            time.sleep(1) 
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        writer.append_data(frame)
        i+=1

        if i > 20*60*60:
            break
    except Exception as e:

        cap.release()
        cv2.destroyAllWindows()
        writer.close()