import numpy as np
import cv2
from scipy import ndimage, signal
from scipy.fft import fft2, fftshift
import matplotlib.pyplot as plt
from skimage import filters, feature, measure
from skimage.metrics import structural_similarity as ssim
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
import os


class ImageQualityAnalyzer:
    def __init__(self):
        self.image = None
        self.image_gray = None
        self.results = {}

    def load_image(self, image_path):
        """Загрузка изображения"""
        try:
            self.image = cv2.imread(image_path)
            if self.image is None:
                raise ValueError("Не удалось загрузить изображение")
            self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            return True
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return False

    def calculate_image_scale(self, physical_size_mm, sensor_size_mm):
        """Расчет масштаба изображения"""
        height, width = self.image_gray.shape
        scale_x = physical_size_mm[0] / width
        scale_y = physical_size_mm[1] / height

        # Масштабный коэффициент
        scale_factor = min(scale_x, scale_y)

        self.results['scale'] = {
            'scale_x': scale_x,
            'scale_y': scale_y,
            'scale_factor': scale_factor,
            'pixel_size_mm': (scale_x, scale_y)
        }

        return self.results['scale']

    def calculate_spatial_frequency_response(self):
        """Расчет пространственной частотной характеристики (MTF)"""
        try:
            # Поиск резких краев для расчета MTF
            edges = feature.canny(self.image_gray, sigma=1.0)

            # Находим горизонтальные и вертикальные края
            horizontal_edges = np.sum(edges, axis=1)
            vertical_edges = np.sum(edges, axis=0)

            # Расчет MTF для горизонтальных краев
            if len(horizontal_edges) > 0 and np.max(horizontal_edges) > 0:
                edge_line = np.where(horizontal_edges == np.max(horizontal_edges))[0][0]
                edge_profile = self.image_gray[edge_line, :]

                # Дифференцирование для получения функции рассеяния линии (LSF)
                lsf = np.diff(edge_profile.astype(float))

                if len(lsf) > 0:
                    # Преобразование Фурье для получения MTF (используем 1D FFT)
                    mtf = np.abs(np.fft.fft(lsf))
                    mtf = mtf / np.max(mtf) if np.max(mtf) > 0 else mtf  # Нормализация

                    # Частоты
                    frequencies = np.fft.fftfreq(len(mtf))

                    # Берем только положительные частоты
                    positive_freq_idx = frequencies >= 0
                    freq_positive = frequencies[positive_freq_idx]
                    mtf_positive = mtf[positive_freq_idx]

                    self.results['mtf'] = {
                        'frequencies': freq_positive,
                        'mtf_values': mtf_positive,
                        'mtf_50': self._find_mtf_value(freq_positive, mtf_positive, 0.5),
                        'mtf_10': self._find_mtf_value(freq_positive, mtf_positive, 0.1)
                    }
                else:
                    # Если не удалось получить LSF, создаем базовую MTF
                    self.results['mtf'] = {
                        'frequencies': np.array([0]),
                        'mtf_values': np.array([1.0]),
                        'mtf_50': None,
                        'mtf_10': None
                    }
            else:
                # Если края не найдены, создаем базовую MTF
                self.results['mtf'] = {
                    'frequencies': np.array([0]),
                    'mtf_values': np.array([1.0]),
                    'mtf_50': None,
                    'mtf_10': None
                }
        except Exception as e:
            print(f"Ошибка в расчете MTF: {e}")
            # Создаем базовую MTF в случае ошибки
            self.results['mtf'] = {
                'frequencies': np.array([0]),
                'mtf_values': np.array([1.0]),
                'mtf_50': None,
                'mtf_10': None
            }

        return self.results.get('mtf', {})

    def _find_mtf_value(self, frequencies, mtf_values, threshold):
        """Поиск частоты, при которой MTF достигает заданного значения"""
        try:
            idx = np.where(mtf_values <= threshold)[0]
            if len(idx) > 0:
                return frequencies[idx[0]]
            return None
        except:
            return None

    def calculate_sharpness(self):
        """Расчет резкости изображения"""
        # Метод 1: Градиентная резкость (Tenengrad)
        grad_x = cv2.Sobel(self.image_gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(self.image_gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
        tenengrad = np.mean(gradient_magnitude ** 2)

        # Метод 2: Лапласиан вариация
        laplacian = cv2.Laplacian(self.image_gray, cv2.CV_64F)
        laplacian_variance = np.var(laplacian)

        # Метод 3: Нормализованная вариация
        normalized_variance = np.var(self.image_gray) / np.mean(self.image_gray)

        self.results['sharpness'] = {
            'tenengrad': tenengrad,
            'laplacian_variance': laplacian_variance,
            'normalized_variance': normalized_variance
        }

        return self.results['sharpness']

    def calculate_resolution(self):
        """Расчет разрешающей способности"""
        try:
            height, width = self.image_gray.shape

            # Теоретическая разрешающая способность (предел Найквиста)
            nyquist_freq_x = width / 2
            nyquist_freq_y = height / 2

            # Эффективная разрешающая способность через анализ текстуры
            # Используем локальную стандартную девиацию как меру детализации
            try:
                # Попробуем использовать rank.variance если доступен
                from skimage.filters import rank
                disk_element = np.ones((5, 5), dtype=np.uint8)
                texture_map = rank.variance(self.image_gray, disk_element)
                effective_resolution = np.mean(texture_map)
            except (ImportError, AttributeError):
                # Альтернативный метод через локальное стандартное отклонение
                from scipy import ndimage
                kernel = np.ones((5, 5)) / 25
                local_mean = ndimage.convolve(self.image_gray.astype(float), kernel)
                local_variance = ndimage.convolve((self.image_gray.astype(float) - local_mean) ** 2, kernel)
                effective_resolution = np.mean(np.sqrt(local_variance))

            # Разрешение в пикселях на миллиметр (если доступен масштаб)
            resolution_info = {
                'width_pixels': int(width),
                'height_pixels': int(height),
                'total_pixels': int(width * height),
                'nyquist_frequency': (float(nyquist_freq_x), float(nyquist_freq_y)),
                'effective_resolution': float(effective_resolution)
            }

            if 'scale' in self.results:
                scale = self.results['scale']
                resolution_info['dpi_x'] = 25.4 / scale['scale_x']  # DPI
                resolution_info['dpi_y'] = 25.4 / scale['scale_y']

            self.results['resolution'] = resolution_info

        except Exception as e:
            print(f"Ошибка в расчете разрешения: {e}")
            # Создаем базовую информацию о разрешении
            height, width = self.image_gray.shape
            self.results['resolution'] = {
                'width_pixels': int(width),
                'height_pixels': int(height),
                'total_pixels': int(width * height),
                'nyquist_frequency': (float(width / 2), float(height / 2)),
                'effective_resolution': 0.0
            }

        return self.results['resolution']

    def analyze_discretization_artifacts(self):
        """Анализ искажений от дискретизации"""
        try:
            # Алиасинг - поиск артефактов в частотной области
            fft_image = np.fft.fft2(self.image_gray)
            fft_shifted = np.fft.fftshift(fft_image)
            magnitude_spectrum = np.log(np.abs(fft_shifted) + 1)

            # Оценка алиасинга через анализ высокочастотных компонент
            height, width = magnitude_spectrum.shape
            center_y, center_x = height // 2, width // 2

            # Анализ углов спектра (где обычно проявляется алиасинг)
            quarter_h, quarter_w = height // 4, width // 4

            if quarter_h > 0 and quarter_w > 0:
                corner_regions = [
                    magnitude_spectrum[:quarter_h, :quarter_w],  # Верхний левый
                    magnitude_spectrum[:quarter_h, -quarter_w:],  # Верхний правый
                    magnitude_spectrum[-quarter_h:, :quarter_w],  # Нижний левый
                    magnitude_spectrum[-quarter_h:, -quarter_w:]  # Нижний правый
                ]

                aliasing_measure = np.mean([np.mean(region) for region in corner_regions if region.size > 0])
            else:
                aliasing_measure = 0.0

            # Квантование - анализ гистограммы
            hist, bins = np.histogram(self.image_gray, bins=256, range=(0, 255))

            # Оценка квантования через энтропию
            hist_normalized = hist / np.sum(hist)
            hist_positive = hist_normalized[hist_normalized > 0]

            if len(hist_positive) > 0:
                entropy = -np.sum(hist_positive * np.log2(hist_positive))
            else:
                entropy = 0.0

            # Поиск пустых уровней (признак грубого квантования)
            empty_levels = np.sum(hist == 0)
            quantization_quality = 1 - (empty_levels / 256)

            self.results['discretization_artifacts'] = {
                'aliasing_measure': float(aliasing_measure),
                'entropy': float(entropy),
                'empty_levels': int(empty_levels),
                'quantization_quality': float(quantization_quality),
                'magnitude_spectrum': magnitude_spectrum
            }

        except Exception as e:
            print(f"Ошибка в анализе артефактов дискретизации: {e}")
            # Создаем базовые значения в случае ошибки
            self.results['discretization_artifacts'] = {
                'aliasing_measure': 0.0,
                'entropy': 0.0,
                'empty_levels': 0,
                'quantization_quality': 1.0,
                'magnitude_spectrum': np.zeros((10, 10))
            }

        return self.results['discretization_artifacts']

    def calculate_noise_parameters(self):
        """Расчет параметров шума"""
        try:
            # Оценка шума через медианную фильтрацию
            median_filtered = cv2.medianBlur(self.image_gray, 5)
            noise = self.image_gray.astype(float) - median_filtered.astype(float)

            noise_std = np.std(noise)
            noise_mean = np.mean(noise)

            # Signal-to-Noise Ratio
            signal_power = np.mean(self.image_gray.astype(float) ** 2)
            noise_power = np.mean(noise ** 2)

            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
            else:
                snr = float('inf')

            self.results['noise'] = {
                'noise_std': float(noise_std),
                'noise_mean': float(noise_mean),
                'snr_db': float(snr) if not np.isinf(snr) else 999.0,
                'noise_image': noise
            }

        except Exception as e:
            print(f"Ошибка в расчете шума: {e}")
            # Создаем базовые значения шума
            self.results['noise'] = {
                'noise_std': 0.0,
                'noise_mean': 0.0,
                'snr_db': 999.0,
                'noise_image': np.zeros_like(self.image_gray)
            }

        return self.results['noise']

    def calculate_contrast_parameters(self):
        """Расчет параметров контраста"""
        try:
            # Michelson контраст
            max_intensity = np.max(self.image_gray)
            min_intensity = np.min(self.image_gray)
            if (max_intensity + min_intensity) > 0:
                michelson_contrast = (max_intensity - min_intensity) / (max_intensity + min_intensity)
            else:
                michelson_contrast = 0.0

            # RMS контраст
            mean_intensity = np.mean(self.image_gray)
            rms_contrast = np.sqrt(np.mean((self.image_gray - mean_intensity) ** 2))

            # Локальный контраст - альтернативный метод
            try:
                # Попробуем использовать rank.enhance_contrast если доступен
                from skimage.filters import rank
                disk_element = np.ones((9, 9), dtype=np.uint8)
                local_contrast = rank.enhance_contrast(self.image_gray, disk_element)
                local_contrast_mean = np.mean(local_contrast)
            except (ImportError, AttributeError):
                # Альтернативный метод расчета локального контраста
                from scipy import ndimage
                # Локальный контраст через локальное стандартное отклонение
                kernel = np.ones((9, 9)) / 81
                local_mean = ndimage.convolve(self.image_gray.astype(float), kernel)
                local_std = np.sqrt(ndimage.convolve((self.image_gray.astype(float) - local_mean) ** 2, kernel))
                local_contrast_mean = np.mean(local_std)

            self.results['contrast'] = {
                'michelson_contrast': float(michelson_contrast),
                'rms_contrast': float(rms_contrast),
                'local_contrast_mean': float(local_contrast_mean),
                'intensity_range': (int(min_intensity), int(max_intensity)),
                'mean_intensity': float(mean_intensity)
            }

        except Exception as e:
            print(f"Ошибка в расчете контраста: {e}")
            # Создаем базовые значения контраста
            max_intensity = np.max(self.image_gray)
            min_intensity = np.min(self.image_gray)
            mean_intensity = np.mean(self.image_gray)

            self.results['contrast'] = {
                'michelson_contrast': 0.0,
                'rms_contrast': float(np.std(self.image_gray)),
                'local_contrast_mean': 0.0,
                'intensity_range': (int(min_intensity), int(max_intensity)),
                'mean_intensity': float(mean_intensity)
            }

        return self.results['contrast']

    def perform_full_analysis(self, physical_size_mm=None, sensor_size_mm=None):
        """Выполнение полного анализа изображения"""
        if self.image is None:
            raise ValueError("Изображение не загружено")

        print("Выполняется анализ качества изображения...")

        try:
            # Масштаб (если предоставлены размеры)
            if physical_size_mm and sensor_size_mm:
                print("- Расчет масштаба...")
                self.calculate_image_scale(physical_size_mm, sensor_size_mm)

            # Основные параметры
            print("- Расчет MTF...")
            self.calculate_spatial_frequency_response()

            print("- Расчет резкости...")
            self.calculate_sharpness()

            print("- Расчет разрешения...")
            self.calculate_resolution()

            print("- Анализ артефактов дискретизации...")
            self.analyze_discretization_artifacts()

            print("- Расчет параметров шума...")
            self.calculate_noise_parameters()

            print("- Расчет параметров контраста...")
            self.calculate_contrast_parameters()

            print("Анализ завершен!")

        except Exception as e:
            print(f"Ошибка во время анализа: {e}")
            # Добавляем хотя бы базовую информацию об изображении
            if 'resolution' not in self.results:
                height, width = self.image_gray.shape
                self.results['resolution'] = {
                    'width_pixels': width,
                    'height_pixels': height,
                    'total_pixels': width * height
                }
            raise

        return self.results

    def save_results(self, filename):
        """Сохранение результатов в JSON файл"""
        # Подготавливаем данные для сериализации
        results_serializable = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                results_serializable[key] = {}
                for k, v in value.items():
                    # Преобразуем numpy массивы и типы в сериализуемые форматы
                    if isinstance(v, np.ndarray):
                        if k != 'magnitude_spectrum' and k != 'noise_image':  # Исключаем большие массивы
                            results_serializable[key][k] = v.tolist()
                    elif isinstance(v, (np.integer, np.floating)):
                        results_serializable[key][k] = float(v)
                    elif v is not None and not isinstance(v, np.ndarray):
                        results_serializable[key][k] = v
            else:
                if isinstance(value, (np.integer, np.floating)):
                    results_serializable[key] = float(value)
                elif not isinstance(value, np.ndarray):
                    results_serializable[key] = value

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_serializable, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            raise

    def generate_report(self):
        """Генерация текстового отчета"""
        if not self.results:
            return "Анализ не выполнен"

        report = "ОТЧЕТ ПО АНАЛИЗУ КАЧЕСТВА ИЗОБРАЖЕНИЯ\n"
        report += "=" * 50 + "\n\n"

        # Разрешение
        if 'resolution' in self.results:
            res = self.results['resolution']
            report += f"РАЗРЕШЕНИЕ:\n"
            report += f"  Размер: {res['width_pixels']} x {res['height_pixels']} пикселей\n"
            report += f"  Общее количество пикселей: {res['total_pixels']:,}\n"
            if 'dpi_x' in res:
                report += f"  DPI: {res['dpi_x']:.1f} x {res['dpi_y']:.1f}\n"
            report += f"  Эффективное разрешение: {res['effective_resolution']:.2f}\n\n"

        # Резкость
        if 'sharpness' in self.results:
            sharp = self.results['sharpness']
            report += f"РЕЗКОСТЬ:\n"
            report += f"  Tenengrad: {sharp['tenengrad']:.2f}\n"
            report += f"  Лапласиан вариация: {sharp['laplacian_variance']:.2f}\n"
            report += f"  Нормализованная вариация: {sharp['normalized_variance']:.4f}\n\n"

        # Контраст
        if 'contrast' in self.results:
            contrast = self.results['contrast']
            report += f"КОНТРАСТ:\n"
            report += f"  Контраст Майкельсона: {contrast['michelson_contrast']:.4f}\n"
            report += f"  RMS контраст: {contrast['rms_contrast']:.2f}\n"
            report += f"  Средний локальный контраст: {contrast['local_contrast_mean']:.2f}\n"
            report += f"  Диапазон интенсивности: {contrast['intensity_range'][0]} - {contrast['intensity_range'][1]}\n\n"

        # Шум
        if 'noise' in self.results:
            noise = self.results['noise']
            report += f"ШУМ:\n"
            report += f"  Стандартное отклонение шума: {noise['noise_std']:.2f}\n"
            report += f"  Среднее значение шума: {noise['noise_mean']:.2f}\n"
            report += f"  SNR: {noise['snr_db']:.2f} дБ\n\n"

        # Артефакты дискретизации
        if 'discretization_artifacts' in self.results:
            artifacts = self.results['discretization_artifacts']
            report += f"АРТЕФАКТЫ ДИСКРЕТИЗАЦИИ:\n"
            report += f"  Мера алиасинга: {artifacts['aliasing_measure']:.2f}\n"
            report += f"  Энтропия: {artifacts['entropy']:.2f} бит\n"
            report += f"  Качество квантования: {artifacts['quantization_quality']:.4f}\n"
            report += f"  Пустые уровни: {artifacts['empty_levels']}/256\n\n"

        return report


class ImageQualityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор качества изображения")
        self.root.geometry("800x600")

        self.analyzer = ImageQualityAnalyzer()
        self.setup_gui()

    def setup_gui(self):
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить изображение", command=self.load_image)
        file_menu.add_command(label="Сохранить результаты", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Основная рамка
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="Загрузить изображение",
                   command=self.load_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Анализировать",
                   command=self.analyze_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Показать отчет",
                   command=self.show_report).pack(side=tk.LEFT)

        # Область для результатов
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка с изображением
        self.image_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.image_frame, text="Изображение")

        self.image_label = ttk.Label(self.image_frame, text="Изображение не загружено")
        self.image_label.pack(expand=True)

        # Вкладка с результатами
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Результаты")

        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL,
                                  command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_image(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("Все файлы", "*.*")
            ]
        )

        if filename:
            if self.analyzer.load_image(filename):
                self.display_image(filename)
                messagebox.showinfo("Успех", "Изображение загружено успешно!")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение")

    def display_image(self, filename):
        # Загружаем и масштабируем изображение для отображения
        image = Image.open(filename)
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # Сохраняем ссылку

    def analyze_image(self):
        if self.analyzer.image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        try:
            # Выполняем анализ
            self.analyzer.perform_full_analysis()

            # Отображаем результаты
            report = self.analyzer.generate_report()
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, report)

            messagebox.showinfo("Успех", "Анализ завершен!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе: {str(e)}")

    def show_report(self):
        if not self.analyzer.results:
            messagebox.showwarning("Предупреждение", "Сначала выполните анализ")
            return

        # Переключаемся на вкладку с результатами
        self.notebook.select(self.results_frame)

    def save_results(self):
        if not self.analyzer.results:
            messagebox.showwarning("Предупреждение", "Нет результатов для сохранения")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )

        if filename:
            try:
                self.analyzer.save_results(filename)
                messagebox.showinfo("Успех", "Результаты сохранены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")


def main():
    """Главная функция программы"""
    root = tk.Tk()
    app = ImageQualityGUI(root)
    root.mainloop()


if __name__ == "__main__":
    # Можно использовать как с GUI, так и напрямую
    import sys

    if len(sys.argv) > 1:
        # Консольный режим
        image_path = sys.argv[1]

        analyzer = ImageQualityAnalyzer()
        if analyzer.load_image(image_path):
            results = analyzer.perform_full_analysis()
            print(analyzer.generate_report())

            # Сохраняем результаты
            output_file = image_path.rsplit('.', 1)[0] + '_analysis.json'
            analyzer.save_results(output_file)
            print(f"\nРезультаты сохранены в {output_file}")
        else:
            print("Ошибка загрузки изображения")
    else:
        # GUI режим
        main()