#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import cv2
import mediapipe as mp
import numpy as np
import ffmpeg
from sys import exit
# from the tkinter library
from tkinter import *
# import filedialog module
from tkinter import filedialog


# In[2]:
def process_video(video_path):

    if video_path == "":
        label_file_explorer.configure(text="Please select a video file to extract content.")
        label_file_explorer.update()
        return

    body_part = v.get()

    face = hand = body = False

    if body_part == "1":
        body = True
    elif body_part == "2":
        hand = True
    else:
        face = True

    filename = os.path.splitext(os.path.basename(video_path))[0]
    dirname = os.path.dirname(video_path)

     # Change label contents
    label_file_explorer.configure(text="Extracting content from "+filename)
    label_file_explorer.update()

    savepath = dirname+"/material_"+filename

    try:
        os.mkdir(savepath)
    except OSError as error:
        pass

    #read video
    vid_01 = cv2.VideoCapture(video_path)
    fps = int(vid_01.get(cv2.CAP_PROP_FPS))

    #read audio
    #player = MediaPlayer(video_path)
    input_ = ffmpeg.input(video_path, r=fps)
    audio = input_.audio#.filter("aecho", 0.8, 0.9, 1000, 0.3)

    ######## cv2.namedWindow("output", cv2.WINDOW_NORMAL)

    #create mediapipe tool
    if face:
        mp_face_mesh = mp.solutions.face_mesh
        face =  mp_face_mesh.FaceMesh(max_num_faces=1,
                                      min_detection_confidence=0,
                                      min_tracking_confidence=0)
    elif hand:
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(max_num_hands=2)
    else:
        mpPose = mp.solutions.pose
        pose = mpPose.Pose(
            min_detection_confidence=0)

    mpDraw = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    #store kp
    kps = []
    kp = []

    i = 0

    images = []
    video_store = False

    while(vid_01.isOpened()):

        ret, frame = vid_01.read()
        #audio_frame, val = player.get_frame()

        if ret == True:
            video_store = True
            imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape

            empty_frame = np.zeros([h,w,3],dtype=np.uint8)
            empty_frame.fill(255)

            if face:
                results = face.process(imgRGB)
                if results.multi_face_landmarks:
                    for faceLms in results.multi_face_landmarks:
                        kp = []
                        for id_, lm in enumerate(faceLms.landmark):
                            kp.append([lm.x, lm.y])

                        mpDraw.draw_landmarks(empty_frame, faceLms, mp_face_mesh.FACEMESH_TESSELATION,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                        mpDraw.draw_landmarks(empty_frame, faceLms, mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                        kps.append(kp)

            elif hand:
                results = hands.process(imgRGB)
                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        kp = []
                        kp_bbox = []
                        for id_, lm in enumerate(handLms.landmark):
                            kp.append([lm.x,lm.y])
                            cx, cy = int(lm.x*w), int(lm.y*h)
                            kp_bbox.append([cx, cy])

                        mpDraw.draw_landmarks(empty_frame, handLms, mpHands.HAND_CONNECTIONS,
                            mpDraw.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2),
                            mpDraw.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2))


                        kps.append(kp)
            else:
                results = pose.process(imgRGB)
                if results.pose_landmarks:
                    for poseLms in results.pose_landmarks.landmark:
                        kp.append([poseLms.x, poseLms.y])

                    mpDraw.draw_landmarks(
                        empty_frame,
                        results.pose_landmarks,
                        mpPose.POSE_CONNECTIONS,
                        mpDraw.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2))

                    kps.append(kp)

            """#handling audio part
            if val != 'eof' and audio_frame is not None:
                #audio
                img, t = audio_frame
            """
            frame_name = filename +'_frame_'+str(i)+'.jpg'
            frame_img_path = savepath+'/'+frame_name
            cv2.imwrite(frame_img_path, empty_frame)
            images.append(empty_frame)

            i+=1
            #cv2.imshow("output", empty_frame)
            k = cv2.waitKey(20)
            # 113 is ASCII code for q key
            if k == 113:
                break
        else:
            break

    vid_01.release()
    ####### cv2.destroyAllWindows()

    #store keypoints
    try:
        textfile = open(savepath+"/keypoints.txt", "w")
        for element in kps:
            textfile.write('\n'.join(str(kp_) for kp_ in element))
        textfile.close()
    except IOError:
        label_file_explorer.configure(text="Could not write keypoints file, an error occured.")
        label_file_explorer.update()
        print("Could not write keypoints file, an error occured.")
    #fps=25
    #store video
    if video_store == True:
        video = cv2.VideoWriter(savepath+"/kps_video_silent.avi", 0, fps, (w, h))
        for image in images:
            video.write(image)

        input_ = ffmpeg.input(savepath+"/kps_video_silent.avi", r= fps)
        video = input_.video#.hflip()
        try:
            out, err = ffmpeg.output(audio, video, savepath+"/kps_video_sound.avi").run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            print(e)
    label_file_explorer.configure(text="Material extraction done successfuly!")
    label_file_explorer.update()
    return kps

# file explorer window
def browseFiles():
    global filename
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Video files",
                                                        "*.mp4"),
                                                       ("all files",
                                                        "*.*")))

    # Change label contents
    label_file_explorer.configure(text="File Opened: "+filename)
    return filename



# Create the root window
window = Tk()

# Set window title
window.title('MUSIC - Material Using Skeletons Inferred from musical Composition')

# Set window size
window.geometry("800x500")

#Set window background color
window.config(background = "white")

# Create a File Explorer label
label_file_explorer = Label(window,
                            text = "Select a video file and press Extract skeleton from sequence",
                            width = 100, height = 4,
                            fg = "blue")

filename = ""

button_explore = Button(window,
                        text = "Browse Files",
                        command = lambda: browseFiles())


cadre1 = Frame(window)

# Tkinter string variable
# able to store any string value
v = StringVar(window, "1")

# Dictionary to create multiple buttons
values = {"Body" : "1",
          "Hands" : "2",
          "Face" : "3"}

# Loop is used to create multiple Radiobuttons
# rather than creating each button separately
for (text, value) in values.items():
    Radiobutton(cadre1, text = text, variable = v,
                value = value).pack(side = LEFT,padx=5,pady=5)

button_extract = Button(cadre1,
                        text = "Extract skeleton from sequence",
                        command = lambda: process_video(filename))

button_exit = Button(window,
                     text = "Exit",
                     command = exit)

label_file_explorer.pack(side = TOP, ipady = 5)
button_explore.pack(side = TOP, padx=5,pady=5)
cadre1.pack(side=TOP)
button_extract.pack(padx=5,pady=5)
button_exit.pack(padx=5,pady=5)

# Let the window wait for any events
window.mainloop()
