import cv2

def capture_video():
    # Capture video from webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Flip the frame horizontally (left-right)
        frame = cv2.flip(frame, 1)

        yield frame

    # Release the capture when done
    #cap.release()
    #cv2.destroyAllWindows()

# Now your other functions remain the same and use the flipped frame
def display_video_with_crosshair(cap):
    for frame in cap:
        # Get the frame dimensions (height, width)
        height, width, _ = frame.shape

        # Define the center of the frame
        center_x = width // 2
        center_y = height // 2

        # Draw a vertical red line (centered on the X-axis)
        cv2.line(frame, (center_x, 0), (center_x, height), (0, 0, 255), 2)

        # Draw a horizontal red line (centered on the Y-axis)
        cv2.line(frame, (0, center_y), (width, center_y), (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow('Webcam with Crosshair', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def capture_frame(cap):
    # Capture a single frame from the video stream
    for frame in cap:
        return frame
    
    