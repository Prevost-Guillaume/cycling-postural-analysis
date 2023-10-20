"""
Le but de ce fichier est de dégager les features moyennes (angles, ratios, etc.) de la position des cyclistes pro
"""
import cv2
import pickle
from model import PoseModel


def extract_features_from_video(filename):
    model = PoseModel(depth=True)
    vid = cv2.VideoCapture(filename)
    
    FEATURES = []
    frame = 1
    while frame is not None:
        ret, frame = vid.read()
        if frame is not None:
            kp = model.extract_kp(frame)
            frame = model.draw(frame, kp)
            F = model.extract_features(frame, kp)
            FEATURES.append(F)
            frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
            cv2.imshow('frame', frame)
        
        
        if cv2.waitKey(1) & 0xFF == ord('q') or frame is None: 
            break 
    
    vid_name = filename.split('/')[-1].split('.')[0]
    with open(f'features/features_{vid_name}.p','wb') as f:
        pickle.dump(FEATURES, f)



if __name__ == "__main__":
    filename = 'datas/Test_TT.mp4'
    extract_features_from_video(filename)