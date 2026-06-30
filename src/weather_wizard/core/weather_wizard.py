import cv2 
import mediapipe as mp
import numpy as np
import random

from weather_wizard.utils.gesture_detector import GestureDetector
from weather_wizard.core.particle_system import Particle

class WeatherWizard:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        #initialize camera
        print("Attempting to open camera...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise ValueError("Failed to open camera! Please check camera permissions.")
        print("Camera opened successfully!")

        #Initialize components
        success, image = self.cap.read()
        self.height, self.width = image.shape[:2]
        self.particle_system = Particle(self.width, self.height)
        self.gesture_detector = GestureDetector(self.mp_hands)

        #Initialize state
        self.particles = []
        self.max_particles = 100
        self.current_effect = None

        #Define colors
        self.RAIN_COLOR = (200, 200, 255)
        self.SNOW_COLOR = (255, 255, 255)
        self.LIGHTNING_COLOR = (255, 255, 100)

    def run(self):
        """Main loop for the Weather Wizard application""" 
        while True:
            # Read frame from camera
            success, image = self.cap.read()
            if not success:
                print("Failed to read from camera")
                break

            # Flip the image horizontally for a later selfie-view display
            image = cv2.flip(image, 1)

            # Convert the BGR image to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Process the image and get hand landmarks
            results = self.hands.process(rgb_image)

            #Draw hand landmarks and detect gestures
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

                    #Detect gesture and update current effect
                    gesture = self.gesture_detector.detect_gesture(hand_landmarks)
                    if gesture:
                        self.current_effect = gesture

                        # Get index finger tip position for particle creation
                        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        x_pos = int(index_tip.x * self.width)

                        # Create new particle at finger position
                        if len(self.particles) < self.max_particles:
                            self.particles.append(
                                self.particle_system.create_particle(gesture, x_pos)
                            )
            # Update and draw particles
            self._update_particles(image)

            # Show the image
            cv2.imshow('Weather Wizard', image)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

    def _update_particles(self, image):
        """Update and draw all particles"""
        new_particles = []
        overlay = np.zeros_like(image)

        for particle in self.particles:
            if particle['type'] == "rain":
                # Update rain particle position
                particle['y'] += particle['speed']
                if particle['y'] < self.height:
                    cv2.line(
                        overlay,
                        (int(particle['x']), int(particle['y'])),
                        (int(particle['x']), int(particle['y'] - 30)),
                        self.RAIN_COLOR,
                        3
                    )
                    new_particles.append(particle)

            elif particle['type'] == "snow":
                # Update snow particle position
                particle['y'] += particle['speed']
                particle['x'] += particle['drift']
                if 0 < particle['y'] < self.height and 0 < particle['x']:
                    cv2.circle(
                        overlay,
                        (int(particle['x']), int(particle['y'])),
                        15,
                        self.SNOW_COLOR,
                        -1
                    )
                    new_particles.append(particle)

            elif particle['type'] == "lightning":
                # Update lightning particle position
                particle['lifetime'] -= 0.2
                if particle['lifetime'] > 0:
                    # Draw the main lightning bolt
                    for i in range(len(particle['branches']) - 1):
                        start = particle['branches'][i]
                        end = particle['branches'][i + 1]

                        #ensure points are within screen bounds
                        start_x = max(0, min(self.width, int(start[0])))
                        start_y = max(0, min(self.width, int(start[1])))
                        end_x = max(0, min(self.width, int(end[0])))
                        end_y = max(0, min(self.height, int(end[1])))

                        # Draw main bolt
                        cv2.line(overlay,
                                (start_x, start_y),
                                (end_x, end_y),
                                self.LIGHTNING_COLOR, 4)

                        # Add branches with 30% probability
                        if random.random() < 0.3:
                            branch_end_x = end_x + random.randint(-40, 40)
                            branch_end_y = end_y + random.randint(-20, 20)
                            branch_end_x = max(0, min(self.width, branch_end_x))
                            branch_end_y = max(0, min(self.height, branch_end_y))
                            cv2.line(overlay, 
                                    (end_x, end_y),
                                    (branch_end_x, branch_end_y),
                                    self.LIGHTNING_COLOR, 2)

                    # Add flash effect when lightning is fresh
                    if particle['lifetime'] > 4:
                        flash_overlay = np.full_like(overlay, 255)
                        overlay = cv2.addWeighted(overlay, 1, flash_overlay, particle['flash_intensity'])

                    new_particles.append(particle)
        
        # Blend the weather effects with the original image
        result = cv2.addWeighted(image, 1, overlay, 0.7, 0)
        image[:] = result[:]
        self.particles = new_particles
 


