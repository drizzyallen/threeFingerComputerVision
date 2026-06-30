class GestureDetector:
    def __init__(self, mp_hands):
        self.mp_hands = mp_hands

    def detect_gesture(self, hand_landmarks):
        """Analyze hand landmarks to determine weather effect"""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
        ring_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y

        if index_tip < index_pip and middle_tip > middle_pip and ring_tip > ring_pip:
            return "rain"
        elif index_tip < index_pip and middle_tip < middle_pip and ring_tip > ring_pip:
            return "snow"
        elif index_tip < index_pip and middle_tip < middle_pip and ring_tip < ring_pip:
            return "lightning"
        

        return None