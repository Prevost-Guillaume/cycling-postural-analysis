# cycling-postural-analysis
How does AI can help cyclists ?

This tool uses AI to analyze the cyclist's position on the bike in order to extract statistics on the cyclist's position.  

## Method
The google mediapipe tool is used to extract key body points in 3D and analyze position. Visibility information for each key point is used to determine which direction the cyclist is facing.
We then extract several angles (ankle, knee, hip, shoulder, elbow)
Pedaling cycles (corresponding to one pedal revolution, starting with the foot at the top) are then extracted, and statistics on each angle are calculated:   
 - Average joint angle value  
 - The average amplitude of the angle in a pedaling cycle  
 - Average maximum angle value (extension)  
 - The average minimum value (flexion)  
These values can be compared with reference values to determine the position changes to be made.  


For example:  
 - If the angle of the knee in extension is less than the reference: raise the saddle, increase the length of the cranks.  
 - If the average elbow angle is below the reference: lower the handlebars, or stand up on the bike (unfold the elbows).  
 - If hip angle is below reference: Mount saddle, unfold elbows, move saddle forward, reduce crank length.  
 - If ankle angle amplitude is below reference: Use the ankle more in the pedaling cycle.  


## Pedaling cycle analysis
A more detailed analysis of the pedaling cycle is possible.
For this, each pedaling cycle (corresponding to one pedal revolution) is set to the same duration (using interpolation techniques) and the mean and standard deviation of the angular values of these cycles is calculated.
Using the montecarlo thresholding method, it is possible to visualize within the cycle when an angle is significantly greater or less than the reference. This is indicated by green or red highlighting. 
This visualization provides an in-depth analysis of how each joint works during a pedal stroke.
Take, for example, the following knee angle:
Analysis of joint pedaling cycles involving the ankle and knee shows an inverse correlation between the knee problem and the ankle problem during the cycle.
It would be interesting to work on __using the ankle at an almost constant angle__. This could solve the knee angle problem.
This visualization can also be used to highlight movements correlated with the pedaling cycle that should not take place (elbow or shoulder angle on a TT, for example, which translates into periodic movement of the arms when the aero position should not move).

## Limitations
 - Key points are extracted in 3D, but the algorithm works better if the cyclist on the bike is in profile.
 - As a reference position for the pedaling cycle, we used a video of a professional cyclist training on a home trainer on YouTube. It would be interesting to analyse more videos to extract more reliable angle norms (minimum, maximum, amplitude, etc.).
 - Shoulder and elbow angles are useless in the "classic" position, due to the multiple possible placements of the hands on the handlebars, but can be analyzed in the case of a time-trial position analysis. The reference should therefore be changed.
