import sys
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QWidget, QComboBox, QPushButton,
                             QTextEdit, QLabel, QFileDialog, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction


class DataVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.log_text = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Приложение для визуализации данных')
        self.setGeometry(100, 100, 1200, 800)

        self.create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel('Приложение для визуализации данных')
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        load_btn = QPushButton('Загрузить CSV файл')
        load_btn.clicked.connect(self.load_csv)
        main_layout.addWidget(load_btn)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.create_tab1()  # Статистика
        self.create_tab2()  # Графики корреляции
        self.create_tab3()  # Тепловая карта
        self.create_tab4()  # Линейный график
        self.create_tab5()  # Лог действий

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Файл')

        load_action = QAction('Загрузить CSV', self)
        load_action.triggered.connect(self.load_csv)
        file_menu.addAction(load_action)

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_tab1(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        refresh_btn = QPushButton('Обновить статистику')
        refresh_btn.clicked.connect(self.show_statistics)
        layout.addWidget(refresh_btn)

        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)

        self.tabs.addTab(tab, "Статистика")

    def create_tab2(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.corr_btn = QPushButton('Построить график корреляции')
        self.corr_btn.clicked.connect(self.plot_correlation)
        layout.addWidget(self.corr_btn)

        self.corr_info = QLabel('График откроется в отдельном окне')
        self.corr_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.corr_info)

        self.tabs.addTab(tab, "Корреляции")

    def create_tab3(self):
        """Третья вкладка - тепловая карта"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.heatmap_btn = QPushButton('Построить тепловую карту корреляции')
        self.heatmap_btn.clicked.connect(self.plot_heatmap)
        layout.addWidget(self.heatmap_btn)

        self.heatmap_info = QLabel('Тепловая карта откроется в отдельном окне')
        self.heatmap_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.heatmap_info)

        self.tabs.addTab(tab, "Тепловая карта")

    def create_tab4(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel('Выберите числовой столбец:'))
        self.column_combo = QComboBox()
        column_layout.addWidget(self.column_combo)

        self.line_plot_btn = QPushButton('Построить линейный график')
        self.line_plot_btn.clicked.connect(self.plot_line_chart)
        column_layout.addWidget(self.line_plot_btn)

        layout.addLayout(column_layout)

        self.line_info = QLabel('Линейный график откроется в отдельном окне')
        self.line_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.line_info)

        self.tabs.addTab(tab, "Линейный график")

    def create_tab5(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)

        clear_log_btn = QPushButton('Очистить лог')
        clear_log_btn.clicked.connect(self.clear_log)
        layout.addWidget(clear_log_btn)

        self.tabs.addTab(tab, "Лог действий")

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите CSV файл', '', 'CSV Files (*.csv)')

        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.add_to_log(f"Загружен CSV файл: {file_path}")
                self.add_to_log(f"Размер данных: {self.df.shape[0]} строк, {self.df.shape[1]} столбцов")

                self.update_comboboxes()

                self.display_data_in_table()
                self.show_statistics()

                QMessageBox.information(self, "Успех", "Данные успешно загружены!")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    def update_comboboxes(self):
        if self.df is not None:
            self.column_combo.clear()

            numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()
            for column in numeric_columns:
                self.column_combo.addItem(column)

    def display_data_in_table(self):
        if self.df is not None:
            df_display = self.df.head(100)

            self.data_table.setRowCount(df_display.shape[0])
            self.data_table.setColumnCount(df_display.shape[1])
            self.data_table.setHorizontalHeaderLabels(df_display.columns)

            for row in range(df_display.shape[0]):
                for col in range(df_display.shape[1]):
                    item = QTableWidgetItem(str(df_display.iat[row, col]))
                    self.data_table.setItem(row, col, item)

            self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def show_statistics(self):
        if self.df is not None:
            stats = self.df.describe(include='all').to_string()
            info_text = f"Общая информация:\n"
            info_text += f"Размер: {self.df.shape[0]} строк, {self.df.shape[1]} столбцов\n"
            info_text += f"Типы данных:\n{self.df.dtypes}\n\n"
            info_text += f"Статистика по данным:\n\n{stats}"

            self.stats_text.setText(info_text)
            self.add_to_log("Отображена статистика по данным")

    def plot_correlation(self):
        if self.df is not None:
            try:
                numeric_df = self.df.select_dtypes(include=['number'])
                if numeric_df.shape[1] < 2:
                    QMessageBox.warning(self, "Предупреждение",
                                        "Недостаточно числовых столбцов для построения корреляции")
                    return

                sns.pairplot(numeric_df)
                plt.suptitle('Графики корреляции числовых параметров', y=1.02)
                plt.tight_layout()
                plt.show()

                self.add_to_log("Построен график корреляции числовых параметров")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при построении графика корреляции: {str(e)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные")

    def plot_heatmap(self):
        if self.df is not None:
            try:
                numeric_df = self.df.select_dtypes(include=['number'])
                if numeric_df.shape[1] < 2:
                    QMessageBox.warning(self, "Предупреждение", "Недостаточно числовых столбцов для тепловой карты")
                    return

                corr_matrix = numeric_df.corr()

                plt.figure(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
                plt.title('Тепловая карта корреляции')
                plt.tight_layout()
                plt.show()

                self.add_to_log("Построена тепловая карта корреляции")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при построении тепловой карты: {str(e)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные")

    def plot_line_chart(self):
        if self.df is not None and self.column_combo.currentText():
            try:
                selected_column = self.column_combo.currentText()

                plt.figure(figsize=(12, 6))
                plt.plot(self.df[selected_column].values)
                plt.title(f'Линейный график: {selected_column}')
                plt.xlabel('Индекс')
                plt.ylabel(selected_column)
                plt.grid(True)
                plt.tight_layout()
                plt.show()

                self.add_to_log(f"Построен линейный график для столбца: {selected_column}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при построении линейного графика: {str(e)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные и выберите столбец")

    def add_to_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text += log_entry + "\n"
        self.log_text_edit.setText(self.log_text)
        self.log_text_edit.verticalScrollBar().setValue(
            self.log_text_edit.verticalScrollBar().maximum())

    def clear_log(self):
        self.log_text = ""
        self.log_text_edit.clear()
        self.add_to_log("Лог очищен")


def main():
    app = QApplication(sys.argv)
    window = DataVisualizationApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()