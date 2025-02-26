import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from database import Database
from datetime import datetime

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
            formal_name='Контроль качества отливок',
            app_id='org.casting.quality.control',
            app_name='CastingQC'
        )
        self.db = Database()

    def create_labeled_input(self, label_text, input_widget, width=180):
        """Создает строку с меткой и полем ввода"""
        row = toga.Box(style=Pack(direction=ROW, padding=2))
        row.add(toga.Label(label_text, style=Pack(width=width)))
        row.add(input_widget)
        return row

    def startup(self):
        # Создаем главное окно в самом начале метода
        self.main_window = toga.MainWindow(title='Контроль качества отливок')

        # Обновляем стиль для секций
        section_style = Pack(
            direction=COLUMN,
            padding=10,
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
            padding=5,
            width=200
        )

        # Обновляем стиль для меток
        label_style = Pack(
            width=180,
            color=self.COLORS['text_dim'],
            padding=(5, 10)
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
        
        # Определяем функцию обновления до её использования
        def update_accepted_count(widget):
            self.accepted_count.value = str(self.calculate_accepted())

        def create_input_with_update(placeholder):
            input_field = toga.TextInput(
                placeholder=placeholder,
                style=input_style
            )
            input_field.on_change = update_accepted_count
            return input_field

        # Основная информация
        basic_box = toga.Box(style=section_style)
        basic_box.add(toga.Label('ОСНОВНАЯ ИНФОРМАЦИЯ', style=header_style))
        
        # Создаем поля ввода
        self.casting_name = toga.TextInput(placeholder='Введите наименование', style=input_style)
        self.executor1 = toga.TextInput(placeholder='Введите ФИО исполнителя', style=input_style)
        self.executor2 = toga.TextInput(placeholder='Введите ФИО исполнителя', style=input_style)
        self.controller1 = toga.TextInput(placeholder='Введите ФИО контролера', style=input_style)
        self.controller2 = toga.TextInput(placeholder='Введите ФИО контролера', style=input_style)
        self.submitted_count = toga.TextInput(
            placeholder='Введите количество',
            style=input_style
        )
        self.acceptance_date = toga.DateInput(style=input_style)
        self.accepted_count = toga.TextInput(readonly=True, style=input_style)
        
        # Добавляем обработчик для submitted_count
        self.submitted_count.on_change = update_accepted_count
        
        basic_fields = [
            ('Наименование отливки:', self.casting_name),
            ('Исполнитель 1:', self.executor1),
            ('Исполнитель 2:', self.executor2),
            ('Контролер 1:', self.controller1),
            ('Контролер 2:', self.controller2),
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
        
        left_column.add(basic_box)
        
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
        total_defects = 0
        
        for field_data in self.second_grade_fields.values():
            value = field_data['input'].value or '0'
            total_defects += int(value if value.isdigit() else 0)
            
        for field_data in self.rework_fields.values():
            value = field_data['input'].value or '0'
            total_defects += int(value if value.isdigit() else 0)
            
        for field in self.final_defect_fields.values():
            value = field.value or '0'
            total_defects += int(value if value.isdigit() else 0)
            
        submitted = self.submitted_count.value or '0'
        return int(submitted if submitted.isdigit() else 0) - total_defects

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
            accepted_count = self.calculate_accepted()
            
            data = (
                self.casting_name.value,
                self.executor1.value,
                self.executor2.value,
                self.controller1.value,
                self.controller2.value,
                int(self.submitted_count.value or 0),
                self.acceptance_date.value.strftime('%d.%m.%Y'),
                accepted_count,
                *(int(field_data['input'].value or 0) for field_data in self.second_grade_fields.values()),
                *(int(field_data['input'].value or 0) for field_data in self.rework_fields.values()),
                *(int(field.value or 0) for field in self.final_defect_fields.values()),
                self.notes.value
            )
            
            self.db.insert_record(data)
            self.show_success_dialog()
        except Exception as e:
            self.show_error_dialog(f'Не удалось сохранить запись: {str(e)}')

def main():
    return CastingQualityControl()

if __name__ == '__main__':
    app = main()
    app.main_loop() 