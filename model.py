import cv2
import mediapipe as mp
import time
import numpy as np
from pprint import pprint


def angle(u,v):
    # Angle en degrés entre u et v
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    dot_product = np.dot(u, v)
    angle = np.arccos(dot_product)
    return angle*180/np.pi

def get_vector(kp, i1, i2, depth=True):
    """vector from i1 to i2"""    
    if depth:
        return np.array([kp.pose_landmarks.landmark[i2].x-kp.pose_landmarks.landmark[i1].x,
                        kp.pose_landmarks.landmark[i2].y-kp.pose_landmarks.landmark[i1].y,
                        kp.pose_landmarks.landmark[i2].z-kp.pose_landmarks.landmark[i1].z])
    else:
        return np.array([kp.pose_landmarks.landmark[i2].x-kp.pose_landmarks.landmark[i1].x,
                         kp.pose_landmarks.landmark[i2].y-kp.pose_landmarks.landmark[i1].y])
    

class PoseModel:
    def __init__(self, depth=True):
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose()
        self.mpDraw = mp.solutions.drawing_utils
        self.depth = depth

    def extract_kp(self, image):
        """image : rgb format"""
        results = self.pose.process(image)
        return results

    def draw(self, img, results=None):
        if results is None:
            results = self.extract_kp(img)
            
        if results.pose_landmarks:
            self.mpDraw.draw_landmarks(img, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w,c = img.shape
                #print(id, lm)
                cx, cy = int(lm.x*w), int(lm.y*h)
                if lm.visibility > 0.5:
                    cv2.circle(img, (cx, cy), 6, (0,0,255), cv2.FILLED)
                #cv2.putText(img, str(id), (cx,cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        return img
            
    def extract_features(self, img, kp=None):
        if kp is None:
            kp = self.extract_kp(img)
        
        if kp.pose_landmarks is None:
            return None
        
        FEATURES = {"droit" : dict(), "gauche" : dict()}
        angles = [
                  ('droit','genou',(26,24,28)),
                  ('gauche','genou',(25,23,27)),
                  ('droit','hanche',(24,26,12)),
                  ('gauche','hanche',(23,25,11)),
                  ('droit','coude',(14,12,16)),
                  ('gauche','coude',(13,11,15)),
                  ('droit','epaule',(12,14,24)),
                  ('gauche','epaule',(11,13,23)),
                  ('droit','cheville',(28,32,26)),
                  ('gauche','cheville',(27,31,25)),
                  ]
        for side,name,p in angles:
            u = get_vector(kp, p[0], p[1], depth=self.depth)
            v = get_vector(kp, p[0], p[2], depth=self.depth)
            viz = sum([kp.pose_landmarks.landmark[i].visibility for i in p])/3
            FEATURES[side][name] = {"value" : angle(u,v), "viz" : viz}
        
        left = [11,23,25,27,29,31,13,15]
        right = [12,24,26,28,30,32,14,16]
        
        FEATURES['gauche']['avg_viz'] = sum([kp.pose_landmarks.landmark[i].visibility for i in left])/8
        FEATURES['droit']['avg_viz'] = sum([kp.pose_landmarks.landmark[i].visibility for i in right])/8
        
        return FEATURES
        



if __name__ == "__main__":
    model = PoseModel(depth=True)
    
    img = cv2.imread('test9.jpg')
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print('shape : ',img.shape)
    
    kp = model.extract_kp(imgRGB)
    print(kp.pose_landmarks)
    
    F = model.extract_features(imgRGB)
    pprint(F)
    
    img = model.draw(img, kp)
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    
    # TO DO : 
    # - Analyser une vidéo et récupérer les angles max et min d'un cycle de pédalage
    #   -> Traitement de la vidéo : utiliser plutôt le côté droit ou gauche ? (utiliser visibility)
    # - modéliser l'impact des composants du vélo sur les angles : hauteur de selle, avancement selle, cintre, longueur prolongateurs
    # - Obtenir les "normales" des features
    