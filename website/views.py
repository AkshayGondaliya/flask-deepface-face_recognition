from flask import Blueprint, render_template, request,redirect, url_for, flash, Response, send_from_directory
from flask_login import login_required, current_user
from deepface import DeepFace
import numpy as np
import time
import csv
from flask import current_app

import cv2
import os
from werkzeug.utils import secure_filename

# libraries to be imported to send email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import numpy as np

views = Blueprint('views', __name__)

#Global variables
flag = 0
flag2 = 0
cam_name = 0
recog_cam_name = 0

#Deep face attributes
metrics = ["cosine", "euclidean", "euclidean_l2"]
models = [
  "VGG-Face", 
  "Facenet", 
  "Facenet512", 
  "OpenFace", 
  "DeepFace", 
  "DeepID", 
  "ArcFace", 
  "Dlib", 
  "SFace",
]


sender_email = "iriscamadmn@gmail.com"
msg = MIMEMultipart()
msg['From'] = sender_email

# rectangle attributes
rectangle_color = (0, 255, 0)
rectangle_thickness = 2

# font attributes to write a person name on the rectangle box
font_type = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (0, 0, 255)  
font_thickness = 2

# send email to person.
def send_mail(person_name, image_name,reciever_mail, attendance_time):
    
    msg['To'] = reciever_mail
    print(reciever_mail)
    if person_name != "UNKNOWN":
        print("wait sending mail to employee")
        msg['Subject'] = "Attendance Is Done"
        body = "hello dear {} your attendance has been noted successfully at {}. you can find your image of recognition bellow. 'thak you'.".format(person_name,attendance_time)
        attachment = open(os.path.join(current_app.config['RECOGNITION_FOLDER'] , image_name), "rb")
    else:
        print("wait sending mail to unknown person")
        msg['Subject'] = "Intruder detected"
        body = "hello dear unknown person has been captured at {}. you can find your image of recognition bellow. 'thak you'.".format(attendance_time)
        attachment = open(os.path.join(current_app.config['UNKNOWN_FOLDER'] , image_name), "rb")
     
    msg.attach(MIMEText(body, 'plain'))
    
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % image_name)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender_email, "prewhizepmjfvbuw")
    text = msg.as_string()
    s.sendmail(sender_email, reciever_mail, text)
    s.quit()
    print("mail sent")

#sending mail for unauthorized oerson
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def recognize_unknown(frame,notification_mail):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    if type(faces)=="tuple":
        print("no face in frame")
    else:

        for (x,y,w,h) in faces:
            start_location = (x, y-5)
            bbox_color = (0,0,255)
            cv2.rectangle(frame,(x,y),(x+w,y+h),bbox_color, rectangle_thickness)
            cv2.putText(frame, "UNKNOWN", start_location, font_type, font_scale, font_color, font_thickness, cv2.LINE_AA)
            attendance_time = time.strftime("%Y%m%d-%I%M%S%p")
            image_name = attendance_time+".jpg"
            cv2.imwrite(os.path.join(current_app.config['UNKNOWN_FOLDER'] , image_name), frame)
            person_name = "UNKNOWN"
            reciever_mail = notification_mail
            print("unknown face is recognized")

            send_mail(person_name, image_name,reciever_mail, attendance_time)

# generating encodings
def model_training():

    # print(os.listdir(current_app.config['UPLOAD_FOLDER']))
    # result = DeepFace.find(img_path = str(os.listdir(current_app.config['UPLOAD_FOLDER'])[0]), db_path = current_app.config['UPLOAD_FOLDER'], enforce_detection=False)
    # print(result[0]['identity'])
    result = DeepFace.find(img_path = "akshay.jpg", db_path = current_app.config['UPLOAD_FOLDER'], enforce_detection=False, 
                           model_name = models[0], distance_metric = metrics[2])

    return result

def mark_attendance(data):
    csv_file = time.strftime("%Y_%m_%d")+"_.csv"
    is_csv_exist = os.path.exists(os.path.join(current_app.config['ATTENDANCE_FOLDER'],csv_file))
    fieldnames = ['User_id','User_name', 'User_email','Appearance_time']

    with open(os.path.join(current_app.config['ATTENDANCE_FOLDER'],csv_file), 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not is_csv_exist:
            writer.writeheader()
        else:
            pass
        writer.writerow(data)

def add_employee(data):
    csv_file = "emp_sheet.csv"
    is_csv_exist = os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),csv_file))
    # print(os.path.dirname(os.path.abspath(__file__)))
    # print("====>",is_csv_exist)
    fieldnames = ['User_id', 'User_name', 'User_email']

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),csv_file), 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not is_csv_exist:
            writer.writeheader()
            
        else:
            pass
        writer.writerow(data)

    return


def recognize(notification_mail):
    fieldnames = ['User_name', 'User_email','Appearance_time']
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),"emp_sheet.csv")):

        df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),"emp_sheet.csv"))
    else:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"emp_sheet.csv"), 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

    # define a video capture object
    # vid = cv2.VideoCapture("rtmp://68.178.171.178/live/stream?sign=1765517400-e391462c5a2e443ad7884e283c3466da")


    vid = cv2.VideoCapture(recog_cam_name)

    count=0

    # fps = vid.get(cv2.CAP_PROP_FPS)
    # seconds=1
    # # print("===========================>",fps)
    # multiplier = fps * seconds
    
    # rectangle attributes
    # rectangle_color = (0, 255, 0)
    # rectangle_thickness = 2

    # font attributes to write a person name on the rectangle box
    # font_type = cv2.FONT_HERSHEY_SIMPLEX
    # font_scale = 1
    # font_color = (0, 0, 255)  
    # font_thickness = 2
    while(True):
        
        # Capture the video frame
        # by frame
        count += 1
        # frameId = int(round(vid.get(0)))
        ret, frame = vid.read()

        if flag==1:
            
            pass
        else:
        
            break
        
        if frame is not None:# and frameId % multiplier == 0:

            result = DeepFace.find(img_path = np.array(frame), db_path = current_app.config['UPLOAD_FOLDER'], 
                                   enforce_detection=False,model_name = models[0],distance_metric = metrics[0])
            print(result)
            if len(result[0]["identity"]) > 0:

                # draw boundary box and show the image
                # x=result[0]["source_x"][0]
                # y=result[0]["source_y"][0]
                # w=result[0]["source_w"][0]
                # h=result[0]["source_h"][0]
                # start_location = (x, y-5)

                # cv2.rectangle(frame,(x,y),(x+w,y+h),rectangle_color, rectangle_thickness)
                person_id = str(result[0]["identity"][0].split("/")[-1].split("_")[2])
                person_name = df.loc[df['User_id']==int(person_id)]['User_name'].values[0]
                flash("{} is recognized".format(person_name),category="success")
                # cv2.putText(frame, person_name, start_location, font_type, font_scale, font_color, font_thickness, cv2.LINE_AA)

                # cv2.imshow('frame',frame)

                #save recognized person image
                # try:
                attendance_time = time.strftime("%Y_%m_%d-%I_%M_%S_%p")
                #     image_name = person_name+"_"+attendance_time+".jpg"
                #     cv2.imwrite(os.path.join(current_app.config['RECOGNITION_FOLDER'] , image_name), frame)
                # except Exception as e:
                #     print("file saving operation is failed")
                
                #send an email to recognized person
                # try:
                reciever_mail = df.loc[df['User_id']==int(person_id)]['User_email'].values[0]
                #     send_mail(person_name, image_name,reciever_mail, attendance_time)
                #     flash('email has been sent successfully.', category='success')
                # except Exception as e:
                #     flash('email service failed', category='error')

                #print all the recognized person name in one frame
                data = {'User_id':person_id,'User_name':person_name,'User_email':reciever_mail,'Appearance_time':attendance_time}
                mark_attendance(data)
                for i in range(len(result)):

                    # print(result[i]["identity"])
                    # print(result[i]["identity"][0])
                    
                    print(person_name +" "+ "is recognized")
                    # flash("{} is recognized".format(person_name),category="success")
                    print("face recognized in {} loop".format(str(count)))


            else:
                print("face not recognized in {} loop".format(str(count)))
                try:

                    recognize_unknown(frame,notification_mail)
                    flash('mail sent sucessfully', category='success')

                except Exception as e:
                    print("erro while sending mail for unknown person.  ",e)

            # cv2.imshow('frame',frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # After the loop release the cap object
    print("stop recognition")
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()
    # return True

def gen_frames():
    camera =  cv2.VideoCapture(cam_name)



    while True:
        global flag2
        success, frame = camera.read()  # read the camera frame
        if not success or flag2 != 1:
            break
        else:
            

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    camera.release()
    cv2.destroyAllWindows()

@views.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_choice = 0
    user_name = ""
    # counter = 0
    # recording = ""
    global flag
    global recog_cam_name
    global flag2
    global cam_name

    path = current_app.config['ATTENDANCE_FOLDER']
    dirs = os.listdir(path)
    temp = []
    for dir in dirs:
        temp.append({'name': dir})

    if request.method == "POST":
        user_choice = request.form.get("fname")

        if(user_choice == "1"):
            user_name = request.form.get("uname")
            user_id = request.form.get("uid")
            user_email = request.form.get("umail")
            print(user_email)
            files = request.files.getlist('uimage') 
            # file_extention = (f.filename).split(".")[-1]
            # file_name = user_name+"_"+user_email+"_."+file_extention
            # print(file_name)
            if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'],"representations_vgg_face.pkl")):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'],"representations_vgg_face.pkl"))
            try:
            # print(app.instance_path) 
                # print(current_app.config['UPLOAD_FOLDER'])   
                for file in files:
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
                flash('file save sucessfully', category='success')

            except Exception as e:
                flash('file save operation is failed', category='error')

            try:
                data={'User_id':user_id,'User_name':user_name,'User_email':user_email}
                add_employee(data)
            except Exception as e:
                pass

            # print("done step 1")
            return redirect(url_for('views.home'))

        elif(user_choice == "2"):


            if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'],"representations_vgg_face.pkl")):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'],"representations_vgg_face.pkl"))
            try:
                result = model_training()
                flash('your face encodings are generated successfully', category='success')
            except Exception as e:
                flash('there is a problem in generationg encodings', category='error')
            return redirect(url_for('views.home'))

        elif(user_choice == "3"):

            do_recognize = request.form.get("ans")
            camera_name = request.form.get("cname")
            notification_email = request.form.get("unknownmail")
            
            if do_recognize != "yes" and flag2==1:

                flag=0

                return render_template("live_feed.html", user=current_user, data=temp)
            elif do_recognize != "yes" and flag2==0:

                flag=0              

                return redirect(url_for('views.home'))
            else:
                 
                flag=1
                if camera_name=="0":
                    recog_cam_name = 0
                    recognize(notification_email)
                else:
                    recog_cam_name = camera_name
                    recognize(notification_email)
                # return render_template("recognition.html", user=current_user)

            return redirect(url_for('views.home'))
        
        elif(user_choice == "4"):

            stop_player = request.form.get("ans2")
            camera_name = request.form.get("cname")
            
            # notification_email = request.form.get("unknownmail")
            if stop_player == "yes":
                
                flag2=0
                return render_template("home.html", user=current_user, data=temp)

            else:
                 
                flag2=1
                if camera_name=="0":
                    cam_name = 0
                    return render_template("live_feed.html",user=current_user, data=temp)
                else:
                    cam_name = camera_name
                    return render_template("live_feed.html",user=current_user, data=temp)

        elif(user_choice == "5"):
            file_name = request.form.get("filename")
            return send_from_directory(current_app.config['ATTENDANCE_FOLDER'], file_name,as_attachment=True)

           
        else:
            flash('add the values and then try again', category='error')

    return render_template("home.html", user=current_user, data=temp)