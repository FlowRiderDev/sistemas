import cv2
import mediapipe as mp
import sqlite3

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

# Initialize drawing utility for landmarks
mp_drawing = mp.solutions.drawing_utils

# Initialize the database
def init_db():
    conn = sqlite3.connect('pixels.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Pixels
                 (pixel_number INTEGER, x_coordinate INTEGER, y_coordinate INTEGER)''')
    conn.commit()
    conn.close()

# 1- Function to check if the right hand is in the screen
def is_right_hand_in_frame(frame):
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.multi_handedness:
        for hand_handedness in results.multi_handedness:
            if hand_handedness.classification[0].label == 'Right':
                return True
    return False

# 2- Function to check if the left hand is in the screen
def is_left_hand_in_frame(frame):
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.multi_handedness:
        for hand_handedness in results.multi_handedness:
            if hand_handedness.classification[0].label == 'Left':
                return True
    return False

# 3- Function to numerate the individual pixels
def numerate_pixels(frame):
    height, width, _ = frame.shape
    pixel_number = 1
    pixel_map = {}

    for y in range(height):
        for x in range(width):
            pixel_map[pixel_number] = (x, y)
            pixel_number += 1

    return pixel_map

# 4- Function to map pixels into quadrants (100x100) and store them in the database
def map_pixels_to_quadrants_and_store(frame):
    # Initialize the database if empty
    init_db()

    conn = sqlite3.connect('pixels.db')
    c = conn.cursor()

    # Check if the database is empty
    c.execute('SELECT COUNT(*) FROM Pixels')
    result = c.fetchone()

    if result[0] == 0:
        # Database is empty, proceed to store the pixels
        height, width, _ = frame.shape
        pixel_map = numerate_pixels(frame)

        # Define the center of the screen as (0, 0)
        center_x = width // 2
        center_y = height // 2

        # Adjust the scaling to ensure the range is from -100 to 100
        scale_x = 200 / (width - 1)  # Mapping width to 200 units (-100 to 100)
        scale_y = 200 / (height - 1) # Mapping height to 200 units (-100 to 100)

        for pixel_number, (x, y) in pixel_map.items():
            # Convert coordinates to scaled Cartesian plane
            cartesian_x = int((x - center_x) * scale_x)
            cartesian_y = int((center_y - y) * scale_y)  # Invert Y axis to match Cartesian plane orientation

            # Insert into the database
            c.execute('INSERT INTO Pixels (pixel_number, x_coordinate, y_coordinate) VALUES (?, ?, ?)',
                      (pixel_number, cartesian_x, cartesian_y))

        conn.commit()

    conn.close()

# 5- Function to get the coordinates of landmark 0 for the right hand using pixels.db
def get_right_hand_landmark_0_coordinates(frame):
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if results.multi_hand_landmarks:
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Check if it's the right hand
            if hand_handedness.classification[0].label == 'Right':
                # Get the pixel location of landmark 0 (the wrist)
                landmark_0 = hand_landmarks.landmark[0]
                height, width, _ = frame.shape

                # Convert normalized coordinates to pixel coordinates
                pixel_x = int(landmark_0.x * width)
                pixel_y = int(landmark_0.y * height)

                # Access the database to get the corresponding Cartesian coordinates
                conn = sqlite3.connect('pixels.db')
                c = conn.cursor()

                c.execute('SELECT x_coordinate, y_coordinate FROM Pixels WHERE pixel_number = ?', 
                          (pixel_y * width + pixel_x,))
                result = c.fetchone()
                
                conn.close()

                if result:
                    # Return the Cartesian coordinates (x, y)
                    return result[0], result[1]
                else:
                    print("Error: Pixel not found in the database.")
                    return None
    
    return None
import math
import math

# 6- Function to calculate z based on the distance between landmarks 0 and 1
def get_right_hand_landmark_0_z_coordinate(frame):
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if results.multi_hand_landmarks:
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Check if it's the right hand
            if hand_handedness.classification[0].label == 'Right':
                # Get the pixel coordinates of landmark 0 and 1
                height, width, _ = frame.shape
                landmark_0 = hand_landmarks.landmark[0]
                landmark_1 = hand_landmarks.landmark[1]

                # Convert normalized coordinates to pixel coordinates
                x0, y0 = int(landmark_0.x * width), int(landmark_0.y * height)
                x1, y1 = int(landmark_1.x * width), int(landmark_1.y * height)

                # Calculate the Euclidean distance between landmarks 0 and 1
                distance = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

                # Define the maximum and minimum distances for scaling z
                max_distance = math.sqrt(width ** 2 + height ** 2)  # Full screen distance at z = 0
                min_distance = 3  # Decreased minimum distance at z = 1000 (smaller distance means z will max out quicker)

                # Scale the distance to a z value between 0 and 1000
                if distance <= min_distance:
                    z_value = 1000
                else:
                    z_value = int(1000 * (max_distance - distance) / (max_distance - min_distance))
                    z_value = max(0, min(1000, z_value))  # Ensure z_value is clamped between 0 and 1000

                return z_value
    
    return None

# 7- Function to get the full x, y, z coordinates for landmark 0 of the right hand
def get_right_hand_landmark_0_coordinates_with_z(frame):
    # Get x, y coordinates using the previous function
    coordinates = get_right_hand_landmark_0_coordinates(frame)
    
    if coordinates:
        # Get the z-coordinate using the new method
        z_value = get_right_hand_landmark_0_z_coordinate(frame)
        
        if z_value is not None:
            # Return the combined x, y, z coordinates
            return coordinates[0], coordinates[1], (z_value - 900)
    
    return None

# 8- Function to determine if the right hand is open or closed
def is_right_hand_open(frame):
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Check if it's the right hand
            if hand_handedness.classification[0].label == 'Right':
                # Get the y-coordinates of the fingertips and their base points
                fingertips = [hand_landmarks.landmark[i] for i in [8, 12, 16, 20]]
                finger_bases = [hand_landmarks.landmark[i] for i in [5, 9, 13, 17]]

                # Determine if the hand is open by checking if the fingertips are further from the wrist than their bases
                hand_open = all(tip.y < base.y for tip, base in zip(fingertips, finger_bases))

                return hand_open

    return False

if __name__ == "__main__":
    # Example usage of the functions
    cap = cv2.VideoCapture(0)
    init_db()  # Initialize the database

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if is_right_hand_in_frame(frame):
            print("Right hand detected")
            hand_open = is_right_hand_open(frame)
            if hand_open:
                print("Right hand is open")
            else:
                print("Right hand is closed")

            full_coordinates = get_right_hand_landmark_0_coordinates_with_z(frame)
            if full_coordinates:
                print(f"Landmark 0 coordinates (x, y, z): {full_coordinates}")
        if is_left_hand_in_frame(frame):
            print("Left hand detected")

        map_pixels_to_quadrants_and_store(frame)

        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
