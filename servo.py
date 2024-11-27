# Variável global para armazenar a última posição da mão
last_position = None

# Sensibilidade para cada eixo (define o divisor para calcular os passos)
sensitivity_x = 5  # Ajuste a sensibilidade do eixo X
sensitivity_y = 5  # Ajuste a sensibilidade do eixo Y
sensitivity_z = 5  # Ajuste a sensibilidade do eixo Z

def calculate_servo_movements(current_position, hand_open):
    """
    Calcula os movimentos necessários para os servos motores imitarem a posição da mão
    e retorna uma lista de tamanho 7.

    Lista:
        Posição 0: 0 (mão aberta) ou 1 (mão fechada)
        Posição 1: 1 (x aumenta) ou 0 (x diminui)
        Posição 2: Número de passos do servo no eixo X
        Posição 3: 1 (y aumenta) ou 0 (y diminui)
        Posição 4: Número de passos do servo no eixo Y
        Posição 5: 1 (z aumenta) ou 0 (z diminui)
        Posição 6: Número de passos do servo no eixo Z

    Args:
        current_position (tuple): Coordenadas atuais (x, y, z) da mão.
        hand_open (bool): Estado da mão (True para aberta, False para fechada).

    Returns:
        list: Lista de tamanho 7 representando o estado e movimentos dos servos.
    """
    global last_position

    # Definir estado da mão (0 para aberta, 1 para fechada)
    hand_state = 0 if hand_open else 1

    # Verificar se já temos uma posição anterior
    if last_position is None:
        last_position = current_position
        # Retorna lista inicial com todos os movimentos zerados
        return [hand_state, 0, 0, 0, 0, 0, 0]

    # Calcular as diferenças entre a posição atual e a última
    delta_x = current_position[0] - last_position[0]
    delta_y = current_position[1] - last_position[1]
    delta_z = current_position[2] - last_position[2]

    # Calcular direção e número de passos para cada eixo
    direction_x = 1 if delta_x >= 0 else 0
    steps_x = int(abs(delta_x) / sensitivity_x)

    direction_y = 1 if delta_y >= 0 else 0
    steps_y = int(abs(delta_y) / sensitivity_y)

    direction_z = 1 if delta_z >= 0 else 0
    steps_z = int(abs(delta_z) / sensitivity_z)

    # Atualizar a última posição
    last_position = current_position

    # Montar e retornar a lista
    return [hand_state, direction_x, steps_x, direction_y, steps_y, direction_z, steps_z]
