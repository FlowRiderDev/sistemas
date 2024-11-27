from camera import *
from hand import *
from servo import *
import serial
import time

# Configuração da porta serial (ajuste a porta para a sua configuração)
arduino = serial.Serial(port='COM4', baudrate=9600, timeout=1)  # Substitua COM4 pela porta correta
time.sleep(2)  # Aguarde o Arduino inicializar

def enviar_comando_arduino(movements):
    if len(movements) != 7:
        print("Erro: A lista deve ter exatamente 7 elementos.")
        return

    # Converter lista para string no formato esperado pelo Arduino
    comando = ','.join(map(str, movements)) + '\n'
    arduino.write(comando.encode())
    time.sleep(0.1)
    resposta = arduino.readline().decode('utf-8').strip()
    print("Resposta do Arduino:", resposta)

# Inicializar o banco de dados
init_db()

# Capturar vídeo
cap = capture_video()

# Tempo de iteração
iterate = 0.1
movement = [0, 0, 30]
claw = False


# Centralizar a mão
for frame in cap:
    # Exibir vídeo com crosshair
    display_video_with_crosshair([frame])

    numerate_pixels(frame)
    map_pixels_to_quadrants_and_store(frame)

    # Pausa no loop
    time.sleep(1)
    print("Centralize sua mão")
    # Verificar se 'q' foi pressionado
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Loop principal
for frame in cap:
    # Exibir vídeo com crosshair
    display_video_with_crosshair([frame])  # Enviar o frame como uma lista para iterar

    # Verificar as mãos
    if is_left_hand_in_frame(frame):
        print("Left hand detected")
    elif is_right_hand_in_frame(frame):
        movement = get_right_hand_landmark_0_coordinates_with_z(frame)
        claw = is_right_hand_open(frame)
        print(movement)
        print(claw)
        servo_movements = calculate_servo_movements(movement, claw)
        enviar_comando_arduino(servo_movements)
        print(f"Servo Movements: {servo_movements}")

    else:
        print("No hands detected")

    # Pausa no loop
    time.sleep(iterate)

    # Verificar se 'q' foi pressionado
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar a câmera e destruir as janelas
cv2.destroyAllWindows()
