import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import PercentFormatter


def calculate_discrete_illumination(l_ap, l_sh, a, E1, E2, num_pixels=20):
    """
    Рассчитывает дискретные значения освещенности для матрицы фотодиодов


    Параметры:
    l_ap - ширина апертуры фотодиода (в мкм)
    l_sh - шаг дискретизации (в мкм)
    a - положение границы перехода освещенности (в мкм)
    E1, E2 - уровни освещенности в % (0-100)
    num_pixels - размер матрицы (num_pixels x num_pixels)

    Возвращает:
    Матрицу значений освещенности в %
    """
    # Рассчитываем номер фотодиода, через который проходит граница
    n_a = int((a + l_sh / 2) // l_sh)

    # Создаем матрицу освещенности
    E_matrix = np.zeros((num_pixels, num_pixels))

    for n in range(num_pixels):
        for m in range(num_pixels):
            # Для всех фотодидов кроме n_a освещенность постоянна
            if n < n_a - 1:
                E_matrix[n, m] = E1
            elif n > n_a - 1:
                E_matrix[n, m] = E2
            else:
                # Для фотодиода n_a рассчитываем освещенность
                delta = l_sh * n_a - a  # lш∙na - a

                if delta >= l_ap / 2:
                    E_matrix[n, m] = E2
                elif delta <= -l_ap / 2:
                    E_matrix[n, m] = E1
                else:
                    # Случай когда -l_ap/2 < delta < l_ap/2
                    E_matrix[n, m] = ((l_ap / 2 - delta) * E1 +
                                      (l_ap / 2 + delta) * E2) / l_ap

    return E_matrix


def visualize_illumination(E_matrix, l_ap, l_sh, a, E1, E2):
    """
    Визуализирует матрицу освещенности

    Параметры:
    E_matrix - матрица значений освещенности
    l_ap, l_sh, a, E1, E2 - параметры для отображения в заголовке
    """
    num_pixels = E_matrix.shape[0]

    # Создаем фигуру с двумя subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(
        f'Дискретизация освещенности:\nl_ap={l_ap} мкм, l_sh={l_sh} мкм, a={a} мкм, E1={E1}%, E2={E2}%')

    # Графическое представление
    norm = colors.Normalize(vmin=0, vmax=100)
    im = ax1.imshow(E_matrix.T, cmap='gray', norm=norm, origin='lower',
                    extent=[0, num_pixels, 0, num_pixels])
    ax1.set_title('Графическое представление')
    ax1.set_xlabel('Номер пикселя по горизонтали (n)')
    ax1.set_ylabel('Номер пикселя по вертикали (m)')
    ax1.set_xticks(np.arange(0, num_pixels + 1, 1))
    ax1.set_yticks(np.arange(0, num_pixels + 1, 1))

    # Добавляем цветовую шкалу
    cbar = fig.colorbar(im, ax=ax1, format=PercentFormatter())
    cbar.set_label('Освещенность (%)')

    # Табличное представление
    ax2.axis('off')

    # Создаем данные для таблицы с номерами строк и столбцов
    cell_text = np.round(E_matrix.T, 1)
    row_labels = [str(i + 1) for i in range(num_pixels)]
    col_labels = [str(i + 1) for i in range(num_pixels)]

    table = ax2.table(cellText=cell_text,
                      rowLabels=row_labels,
                      colLabels=col_labels,
                      loc='center',
                      cellLoc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax2.set_title('Табличное представление (%)')

    plt.tight_layout()
    plt.show()


def validate_parameters(l_ap, l_sh, a, num_pixels):
    """
    Проверяет параметры на соответствие ограничениям
    """
    if not (1 <= l_ap <= 10 and 1 <= l_sh <= 10):
        raise ValueError("l_ap и l_sh должны быть в диапазоне 1-10 мкм")
    if l_ap > l_sh:
        raise ValueError("l_ap должна быть ≤ l_sh")
    if not (l_sh < a < (num_pixels - 1) * l_sh):
        raise ValueError(f"a должно быть в диапазоне {l_sh}..{(num_pixels - 1) * l_sh} мкм")


def main():
    # Параметры по умолчанию
    l_ap = 5.0  # ширина апертуры в мкм
    l_sh = 7.0  # шаг дискретизации в мкм
    a = 70.0  # положение границы перехода в мкм
    E1 = 20  # освещенность 1 в %
    E2 = 80  # освещенность 2 в %
    num_pixels = 20  # размер матрицы

    try:
        # Проверяем параметры
        validate_parameters(l_ap, l_sh, a, num_pixels)

        # Рассчитываем матрицу освещенности
        E_matrix = calculate_discrete_illumination(l_ap, l_sh, a, E1, E2, num_pixels)

        # Визуализируем результаты
        visualize_illumination(E_matrix, l_ap, l_sh, a, E1, E2)

    except ValueError as e:
        print(f"Ошибка в параметрах: {e}")


if __name__ == "__main__":
    main()