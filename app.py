import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from database import Database
from datetime import datetime
import math
from toga.colors import rgb
import matplotlib
matplotlib.use('Agg')  # Используем не-интерактивный бэкенд
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
from PIL import Image
import json
import os
from pathlib import Path

class SelectionManager:
    """Класс для управления списками значений"""
    def __init__(self):
        self.data_file = Path('lists_data.json')
        # Значения по умолчанию
        self.default_lists = {
            'casting_names': ['', 'Ригель', 'Вороток'],
            'executors': ['', 'Леонтьева', 'Мещерякова', 'Аюбов'],
            'controllers': ['', 'Елхова', 'Лабуткина', 'Рябова', 'Улитина']
        }
        # Загружаем сохраненные списки или используем значения по умолчанию
        self.load_lists()
        
    def load_lists(self):
        """Загружает списки из файла"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.casting_names = data.get('casting_names', self.default_lists['casting_names'])
                    self.executors = data.get('executors', self.default_lists['executors'])
                    self.controllers = data.get('controllers', self.default_lists['controllers'])
            else:
                self.casting_names = self.default_lists['casting_names'].copy()
                self.executors = self.default_lists['executors'].copy()
                self.controllers = self.default_lists['controllers'].copy()
        except Exception as e:
            print(f"Ошибка при загрузке списков: {e}")
            # В случае ошибки используем значения по умолчанию
            self.casting_names = self.default_lists['casting_names'].copy()
            self.executors = self.default_lists['executors'].copy()
            self.controllers = self.default_lists['controllers'].copy()

    def save_lists(self):
        """Сохраняет списки в файл"""
        try:
            data = {
                'casting_names': self.casting_names,
                'executors': self.executors,
                'controllers': self.controllers
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении списков: {e}")

    def add_value(self, list_type, value):
        """Добавляет новое значение в указанный список"""
        if not value or not value.strip():
            return False
            
        value = value.strip()
        target_list = getattr(self, list_type)
        
        if value not in target_list:
            target_list.append(value)
            self._sort_list(list_type)  # Сортируем список после добавления
            self.save_lists()  # Сохраняем изменения
            return True
        return False

    def remove_value(self, list_type, value):
        """Удаляет значение из указанного списка"""
        target_list = getattr(self, list_type)
        if value and value in target_list and value != '':  # Не удаляем пустое значение
            target_list.remove(value)
            self.save_lists()  # Сохраняем изменения
            return True
        return False

    def _sort_list(self, list_type):
        """Сортирует указанный список, сохраняя пустое значение в начале"""
        target_list = getattr(self, list_type)
        # Отделяем пустое значение
        empty = '' in target_list
        if empty:
            target_list.remove('')
        # Сортируем остальные значения
        target_list.sort()
        # Возвращаем пустое значение в начало
        if empty:
            target_list.insert(0, '')

    def get_list(self, list_type):
        """Возвращает отсортированный список по его типу"""
        return getattr(self, list_type)

class CastingQualityControl(toga.App):
    # Определяем светлую цветовую схему как атрибут класса
    COLORS = {
        'background': '#f0f2f5',     # Светло-серый фон
        'surface': '#ffffff',        # Белый фон для секций
        'primary': '#1976d2',        # Синий основной цвет
        'text': '#202124',          # Темно-серый текст
        'text_dim': '#5f6368',      # Приглушенный текст
        'input_bg': '#ffffff',      # Белый фон для полей ввода
    }

    def __init__(self):
        # Добавляем формальное имя приложения
        super().__init__(
            formal_name='Контроль качества отливок. Доработка. Версия 1.0',
            app_id='org.casting.quality.control',
            app_name='CastingQC'
        )
        self.db = Database()

    def create_labeled_input(self, label_text, input_widget, width=150):
        """Создает строку с меткой и полем ввода"""
        row = toga.Box(style=Pack(direction=ROW, padding=2))
        row.add(toga.Label(label_text, style=Pack(width=width)))
        row.add(input_widget)
        return row

    def startup(self):
        # Создаем главное окно в самом начале метода
        self.main_window = toga.MainWindow(title='Контроль качества отливок. Доработка. Версия 1.0')

        # Обновляем стиль для секций
        section_style = Pack(
            direction=COLUMN,
            padding=8,
            background_color=self.COLORS['surface']  # Используем self.COLORS
        )

        # Обновляем стиль для заголовков
        header_style = Pack(
            font_weight='bold',
            padding_bottom=10,
            color=self.COLORS['primary']
        )

        # Обновляем стили для полей ввода
        input_style = Pack(
            background_color=self.COLORS['input_bg'],
            color=self.COLORS['text'],
            padding=3,
            width=180
        )

        # Обновляем стиль для меток
        label_style = Pack(
            width=150,
            color=self.COLORS['text_dim'],
            padding=(3, 5)
        )

        # Обновляем стиль для кнопки
        button_style = Pack(
            padding=(10, 20),
            background_color=self.COLORS['primary'],
            color='#ffffff'
        )

        # Основной контейнер с двумя колонками
        main_box = toga.Box(style=Pack(direction=ROW, padding=10))

        # Левая колонка
        left_column = toga.Box(style=Pack(direction=COLUMN, padding=5))
        
        # Основная информация
        basic_box = toga.Box(style=section_style)
        basic_box.add(toga.Label('ОСНОВНАЯ ИНФОРМАЦИЯ', style=header_style))

        # Определяем функцию обновления до её использования
        def update_accepted_count(widget):
            self.accepted_count.value = str(self.calculate_accepted())
            self.draw_pie_chart()  # Обновляем диаграмму после обновления значения

        def validate_positive_integer(widget):
            """Проверяет и корректирует введенное значение"""
            if widget.value:
                old_value = widget.value
                new_value = ''.join(char for char in widget.value if char.isdigit())
                
                if new_value:
                    new_value = str(int(new_value))
                
                if new_value != old_value:
                    widget.value = new_value
            else:
                widget.value = ''
            
            # Просто обновляем значение, диаграмма обновится автоматически
            update_accepted_count(widget)

        # Обновляем создание полей ввода для числовых значений
        def create_input_with_update(placeholder):
            input_field = toga.TextInput(
                placeholder=placeholder,
                style=input_style
            )
            # Добавляем обработчик изменений
            input_field.on_change = validate_positive_integer
            return input_field

        # Инициализируем менеджер списков
        self.selection_manager = SelectionManager()

        # Создаем поля выбора
        def create_selection_with_button(list_type, label):
            """Создает выпадающий список с кнопкой добавления"""
            container = toga.Box(style=Pack(direction=ROW))
            
            # Создаем выпадающий список
            selection = toga.Selection(
                items=self.selection_manager.get_list(list_type),
                style=input_style
            )
            
            # Создаем кнопку добавления
            add_button = toga.Button(
                '+',
                style=Pack(width=30, padding_left=5),
                on_press=lambda w: self.show_add_value_dialog(list_type, label, selection)
            )
            
            container.add(selection)
            container.add(add_button)
            return container, selection

        # Создаем поля выбора
        casting_box, self.casting_name = create_selection_with_button('casting_names', 'наименование отливки')
        executor1_box, self.executor1 = create_selection_with_button('executors', 'исполнителя')
        executor2_box, self.executor2 = create_selection_with_button('executors', 'исполнителя')
        controller1_box, self.controller1 = create_selection_with_button('controllers', 'контролера')
        controller2_box, self.controller2 = create_selection_with_button('controllers', 'контролера')

        # Создаем остальные поля ввода
        self.submitted_count = toga.TextInput(
            placeholder='Введите количество',
            style=input_style
        )
        self.submitted_count.on_change = validate_positive_integer
        
        self.acceptance_date = toga.DateInput(style=input_style)
        
        self.accepted_count = toga.TextInput(
            readonly=True,
            style=input_style
        )

        # Обновляем basic_fields, используя боксы вместо просто полей
        basic_fields = [
            ('Наименование отливки:', casting_box),
            ('Исполнитель 1:', executor1_box),
            ('Исполнитель 2:', executor2_box),
            ('Контролер 1:', controller1_box),
            ('Контролер 2:', controller2_box),
            ('Контроль подано:', self.submitted_count),
            ('Дата приемки:', self.acceptance_date),
            ('Контроль принято:', self.accepted_count),
        ]
        
        # Создаем строки для полей с новыми стилями
        for label, field in basic_fields:
            row = toga.Box(style=Pack(direction=ROW, padding=2))
            row.add(toga.Label(
                label,
                style=label_style
            ))
            row.add(field)
            basic_box.add(row)
        
        # Создаем контейнер для основной информации и диаграммы
        info_row = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # Добавляем basic_box в левую часть
        info_row.add(basic_box)
        
        # Создаем ImageView вместо Canvas для диаграммы
        self.chart_view = toga.ImageView(
            style=Pack(
                width=300,
                height=300,
                padding=20
            )
        )
        
        # Добавляем ImageView в правую часть
        info_row.add(self.chart_view)
        
        # Добавляем info_row вместо basic_box
        left_column.add(info_row)
        
        # Второй сорт и доработка в одной строке
        defects_row = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # Второй сорт
        second_grade_box = toga.Box(style=section_style)
        second_grade_box.add(toga.Label('ВТОРОЙ СОРТ', style=header_style))
        
        self.second_grade_fields = {}
        second_grade_types = [
            ('Раковины:', 'cavities'),
            ('Зарез:', 'cut'),
            ('Прочее:', 'other')
        ]
        
        for label, key in second_grade_types:
            input_field = create_input_with_update('Введите количество')
            self.second_grade_fields[key] = {'input': input_field, 'label': label}
            second_grade_box.add(self.create_labeled_input(label, input_field))
        
        defects_row.add(second_grade_box)
        
        # Доработка
        rework_box = toga.Box(style=section_style)
        rework_box.add(toga.Label('ДОРАБОТКА', style=header_style))
        
        self.rework_fields = {}
        rework_types = [
            ('Лапы:', 'paw'),
            ('Питатель:', 'feeder'),
            ('Корона:', 'crown')
        ]
        
        for label, key in rework_types:
            input_field = create_input_with_update('Введите количество')
            self.rework_fields[key] = {'input': input_field, 'label': label}
            rework_box.add(self.create_labeled_input(label, input_field))
        
        defects_row.add(rework_box)
        left_column.add(defects_row)
        
        # Перемещаем окончательный брак в левую колонку
        final_defect_box = toga.Box(style=section_style)
        final_defect_box.add(toga.Label('ОКОНЧАТЕЛЬНЫЙ БРАК', style=header_style))

        # Создаем сетку для окончательного брака (3 колонки)
        self.final_defect_fields = {}
        defect_types = [
            # Первый столбец
            ['Недолив', 'Вырыв', 'Зарез', 'Коробление', 'Наплыв металла', 'Нарушение геометрии', 'Нарушение маркировки'],
            # Второй столбец
            ['Непроклей', 'Неслитина', 'Несоответствие внешнего вида', 'Несоответствие размеров', 'Пеномодель', 'Пористость', 'Пригар песка'],
            # Третий столбец
            ['Рыхлота', 'Раковины', 'Скол', 'Слом', 'Спай', 'Трещины', 'Прочее']
        ]

        columns_box = toga.Box(style=Pack(direction=ROW))

        for column_types in defect_types:
            column_box = toga.Box(style=Pack(
                direction=COLUMN,
                padding=(0, 10),
                width=250
            ))
            for defect_type in column_types:
                input_field = create_input_with_update('Введите количество')
                self.final_defect_fields[defect_type.lower()] = input_field
                field_box = toga.Box(style=Pack(direction=COLUMN, padding=2))
                field_box.add(toga.Label(
                    defect_type + ':',
                    style=Pack(
                        padding=(0, 5),
                        color=self.COLORS['text']
                    )
                ))
                field_box.add(input_field)
                column_box.add(field_box)
            columns_box.add(column_box)

        final_defect_box.add(columns_box)
        left_column.add(final_defect_box)  # Добавляем в левую колонку

        # Примечание и кнопка сохранения в одной строке
        bottom_row = toga.Box(style=Pack(direction=ROW, padding=5))

        # Примечание
        notes_box = toga.Box(style=section_style)
        notes_box.add(toga.Label('ПРИМЕЧАНИЕ', style=header_style))
        self.notes = toga.MultilineTextInput(style=Pack(
            height=40,
            width=650  # Уменьшаем ширину с 800 до 650
        ))
        notes_box.add(self.notes)
        bottom_row.add(notes_box)

        # Кнопка сохранения справа от примечания
        save_button = toga.Button(
            'Сохранить',
            on_press=self.save_record,
            style=Pack(
                padding=(20, 20),
                background_color=self.COLORS['primary'],
                color='#ffffff',
                width=100  # Задаем фиксированную ширину кнопки
            )
        )
        bottom_row.add(save_button)

        # Добавляем строку с примечанием и кнопкой
        left_column.add(bottom_row)

        # Удаляем правую колонку
        main_box.add(left_column)  # Добавляем только левую колонку

        # Устанавливаем контент и размер окна
        self.main_window.content = main_box
        self.main_window.size = (900, 950)  # Увеличиваем высоту с 900 до 950
        self.main_window.show()

    def calculate_accepted(self):
        """Вычисляет количество принятых деталей"""
        total_defects = 0
        
        # Подсчет дефектов второго сорта
        for field_data in self.second_grade_fields.values():
            value = field_data['input'].value
            if value and value.isdigit():
                total_defects += int(value)
            
        # Подсчет доработки
        for field_data in self.rework_fields.values():
            value = field_data['input'].value
            if value and value.isdigit():
                total_defects += int(value)
            
        # Подсчет окончательного брака
        for field in self.final_defect_fields.values():
            value = field.value
            if value and value.isdigit():
                total_defects += int(value)
            
        submitted = self.submitted_count.value
        if not submitted or not submitted.isdigit():
            return 0
            
        result = int(submitted) - total_defects
        return max(0, result)  # Не допускаем отрицательных значений

    def show_success_dialog(self):
        self.main_window.info_dialog(
            'Успех',
            'Запись успешно сохранена'
        )

    def show_error_dialog(self, message):
        self.main_window.error_dialog(
            'Ошибка',
            message
        )

    def save_record(self, widget):
        try:
            # Проверяем обязательные поля
            if not self.casting_name.value:
                raise ValueError("Необходимо указать наименование отливки")
            
            if not self.submitted_count.value or not self.submitted_count.value.isdigit():
                raise ValueError("Необходимо указать корректное количество поданных на контроль")
                
            if not self.acceptance_date.value:
                raise ValueError("Необходимо указать дату приемки")

            accepted_count = self.calculate_accepted()
            date_str = self.acceptance_date.value.strftime('%d.%m.%Y') if self.acceptance_date.value else ''
            
            # Создаем кортеж данных
            data = (
                self.casting_name.value,
                self.executor1.value,
                self.executor2.value,
                self.controller1.value,
                self.controller2.value,
                int(self.submitted_count.value or 0),
                date_str,
                accepted_count,
                *(int(field_data['input'].value or 0) for field_data in self.second_grade_fields.values()),
                *(int(field_data['input'].value or 0) for field_data in self.rework_fields.values()),
                *(int(field.value or 0) for field in self.final_defect_fields.values()),
                self.notes.value
            )
            
            self.db.insert_record(data)
            self.show_success_dialog()
                
        except ValueError as ve:
            self.show_error_dialog(str(ve))
        except Exception as e:
            self.show_error_dialog(f'Не удалось сохранить запись: {str(e)}')

    def draw_pie_chart(self):
        try:
            # Получаем значения
            total = int(self.submitted_count.value or 0)
            accepted = int(self.accepted_count.value or 0)
            
            if total > 0:
                # Очищаем все предыдущие фигуры matplotlib
                plt.clf()
                plt.close('all')
                
                # Создаем данные для диаграммы
                sizes = [accepted, total - accepted]
                labels = ['Принято', 'Брак']
                colors = ['#4BB543', '#E53935']  # Зеленый и красный
                
                # Создаем новую фигуру с фиксированным размером
                fig = plt.figure(figsize=(4, 4))  # Сохраняем ссылку на фигуру
                
                # Создаем круговую диаграмму с дополнительными параметрами
                plt.pie(
                    sizes,
                    labels=labels,
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    labeldistance=1.1,
                    pctdistance=0.6,
                    radius=0.8
                )
                
                plt.axis('equal')
                plt.tight_layout(pad=1.5)
                
                # Сохраняем в буфер памяти
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
                plt.close(fig)  # Закрываем конкретную фигуру
                
                buf.seek(0)
                image = toga.Image(buf.read())
                self.chart_view.image = image
                
        except Exception as e:
            print(f"Ошибка при создании диаграммы: {e}")
        finally:
            # Всегда закрываем буфер и фигуры
            if 'buf' in locals():
                buf.close()
            plt.close('all')

    def show_add_value_dialog(self, list_type, field_type, selection_widget):
        """Показывает диалог добавления нового значения"""
        # Создаем окно для диалога
        dialog_window = toga.Window(title=f'Добавить {field_type}')
        
        # Создаем контейнер для содержимого
        dialog_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        # Добавляем метку
        label = toga.Label(
            f'Введите новое значение для поля "{field_type}":',
            style=Pack(padding=(0, 0, 10, 0))
        )
        dialog_box.add(label)
        
        # Добавляем поле ввода
        input_field = toga.TextInput(
            style=Pack(
                flex=1,
                padding=(0, 0, 20, 0),
                height=30,
                background_color=self.COLORS['input_bg']
            )
        )
        dialog_box.add(input_field)
        
        # Добавляем кнопки
        buttons_box = toga.Box(style=Pack(direction=ROW, padding=(0, 0), alignment='center'))
        
        def on_ok(widget):
            value = input_field.value
            if self.selection_manager.add_value(list_type, value):
                # Обновляем список в виджете
                selection_widget.items = self.selection_manager.get_list(list_type)
                selection_widget.value = value
                
                # Обновляем связанные поля
                self._update_related_fields(list_type)
            
            dialog_window.close()
            
        def on_cancel(widget):
            dialog_window.close()
            
        # Стиль для кнопок
        button_style = Pack(
            padding=(10, 5),
            width=100,
            height=30,
            background_color=self.COLORS['primary'],
            color='#ffffff'
        )
        
        ok_button = toga.Button('OK', on_press=on_ok, style=button_style)
        cancel_button = toga.Button('Отмена', on_press=on_cancel, style=button_style)
        
        buttons_box.add(ok_button)
        buttons_box.add(cancel_button)
        dialog_box.add(buttons_box)
        
        # Добавляем кнопку удаления, если выбрано значение
        if selection_widget.value and selection_widget.value != '':
            def on_delete(widget):
                if self.selection_manager.remove_value(list_type, selection_widget.value):
                    selection_widget.items = self.selection_manager.get_list(list_type)
                    selection_widget.value = ''
                    self._update_related_fields(list_type)
                dialog_window.close()
            
            delete_button = toga.Button(
                'Удалить',
                on_press=on_delete,
                style=Pack(
                    padding=(20, 5),
                    width=100,
                    height=30,
                    background_color='#dc3545',  # Красный цвет для кнопки удаления
                    color='#ffffff'
                )
            )
            dialog_box.add(delete_button)
        
        # Устанавливаем содержимое окна
        dialog_window.content = dialog_box
        
        # Устанавливаем размер окна
        dialog_window.size = (400, 250)
        
        # Показываем окно
        dialog_window.show()

    def _update_related_fields(self, list_type):
        """Обновляет связанные поля при изменении списка"""
        if list_type == 'executors':
            items = self.selection_manager.get_list(list_type)
            self.executor1.items = items
            self.executor2.items = items
        elif list_type == 'controllers':
            items = self.selection_manager.get_list(list_type)
            self.controller1.items = items
            self.controller2.items = items

def main():
    return CastingQualityControl()

if __name__ == '__main__':
    app = main()
    app.main_loop() 