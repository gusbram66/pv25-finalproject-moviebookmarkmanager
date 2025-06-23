import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QDockWidget,
    QStatusBar, QScrollArea, QHeaderView, QAction, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class EnhancedMovieApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Movie Bookmark Manager")
        self.setGeometry(100, 100, 900, 700)
        
        self.db_conn = None
        self.db_cursor = None
        self.init_db()

        self.initUI()
        self.apply_styles()
        self.load_movies_to_table()

    def init_db(self):
        try:
            self.db_conn = sqlite3.connect("movies_final_project.db")
            self.db_cursor = self.db_conn.cursor()
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    genre TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    favorite INTEGER DEFAULT 0
                )
            """)
            self.db_conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Kesalahan Basis Data", f"Tidak dapat menginisialisasi basis data: {e}")
            sys.exit(1)

    def initUI(self):
        self.setup_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.setup_dock_widget()

        self.setup_status_bar()

        self.setup_scrollable_form(main_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Tambah Film")
        add_button.clicked.connect(self.add_movie)
        update_button = QPushButton("Perbarui Terpilih")
        update_button.clicked.connect(self.update_movie)
        delete_button = QPushButton("Hapus Terpilih")
        delete_button.clicked.connect(self.delete_movie)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        main_layout.addLayout(button_layout)

        self.movie_table = QTableWidget()
        self.movie_table.setColumnCount(5)
        self.movie_table.setHorizontalHeaderLabels(["ID", "Judul", "Genre", "Rating", "Favorit"])
        self.movie_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.movie_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.movie_table.verticalHeader().setVisible(False)
        self.movie_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) 
        self.movie_table.cellClicked.connect(self.populate_form_on_select)
        main_layout.addWidget(self.movie_table)

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu('&File')
        
        export_action = QAction('Ekspor ke CSV', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Keluar', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menu_bar.addMenu('&Help')
        about_action = QAction('Tentang', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def setup_dock_widget(self):
        dock_widget = QDockWidget("Panel Info", self)
        dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        info_label = QLabel(
            "<h3>Bantuan Aplikasi</h3>"
            "<p><b>Tambah:</b> Isi formulir dan klik 'Tambah Film'.</p>"
            "<p><b>Perbarui:</b> Klik film di tabel, ubah detail, dan klik 'Perbarui'.</p>"
            "<p><b>Hapus:</b> Pilih film dan klik 'Hapus'.</p>"
            "<p><b>Ekspor:</b> Buka File -> Ekspor ke CSV untuk menyimpan data Anda.</p>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #000000;")
        dock_widget.setWidget(info_label)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    def setup_status_bar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("NIM: F1D022052 | Nama: Ida Bagus Brahmanta Jayana")

    def setup_scrollable_form(self, main_layout):
        form_container_widget = QWidget()
        form_layout = QGridLayout(form_container_widget)
        form_layout.setSpacing(10)

        self.id_label = QLabel("N/A") 
        self.title_input = QLineEdit()
        self.genre_input = QComboBox()
        self.genre_input.addItems(["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Animation", "Documentary"])
        self.rating_input = QSpinBox()
        self.rating_input.setRange(1, 10)
        self.favorite_checkbox = QCheckBox("Tandai sebagai Favorit")

        form_layout.addWidget(QLabel("<b>ID:</b>"), 0, 0)
        form_layout.addWidget(self.id_label, 0, 1)
        form_layout.addWidget(QLabel("<b>Judul:</b>"), 1, 0)
        form_layout.addWidget(self.title_input, 1, 1)
        form_layout.addWidget(QLabel("<b>Genre:</b>"), 2, 0)
        form_layout.addWidget(self.genre_input, 2, 1)
        form_layout.addWidget(QLabel("<b>Rating:</b>"), 3, 0)
        form_layout.addWidget(self.rating_input, 3, 1)
        form_layout.addWidget(self.favorite_checkbox, 4, 1, Qt.AlignLeft)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(form_container_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(220)
        main_layout.addWidget(scroll_area)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f2f2f2;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #007bff;
                color: white;
                padding: 8px;
                border: 1px solid #0056b3;
                font-weight: bold;
                font-size: 14px;
            }
            QDockWidget {
                font-size: 12px;
                font-weight: bold;
            }
        """)
        bold_font = QFont()
        bold_font.setBold(True)
        self.id_label.setFont(bold_font)

    def add_movie(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Kesalahan Input", "Judul film tidak boleh kosong.")
            return

        genre = self.genre_input.currentText()
        rating = self.rating_input.value()
        is_favorite = 1 if self.favorite_checkbox.isChecked() else 0

        try:
            self.db_cursor.execute(
                "INSERT INTO movies (title, genre, rating, favorite) VALUES (?, ?, ?, ?)",
                (title, genre, rating, is_favorite)
            )
            self.db_conn.commit()
            self.clear_form()
            self.load_movies_to_table()
            self.statusBar().showMessage(f"Berhasil menambahkan '{title}'!", 4000)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Kesalahan Basis Data", f"Film dengan judul '{title}' sudah ada.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Kesalahan Basis Data", f"Tidak dapat menambahkan film: {e}")

    def update_movie(self):
        movie_id = self.id_label.text()
        if not movie_id.isdigit():
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Harap pilih film dari tabel untuk diperbarui.")
            return

        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Kesalahan Input", "Judul film tidak boleh kosong.")
            return
            
        genre = self.genre_input.currentText()
        rating = self.rating_input.value()
        is_favorite = 1 if self.favorite_checkbox.isChecked() else 0

        try:
            self.db_cursor.execute(
                "UPDATE movies SET title = ?, genre = ?, rating = ?, favorite = ? WHERE id = ?",
                (title, genre, rating, is_favorite, int(movie_id))
            )
            self.db_conn.commit()
            self.clear_form()
            self.load_movies_to_table()
            self.statusBar().showMessage(f"Berhasil memperbarui catatan untuk ID {movie_id}!", 4000)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Kesalahan Basis Data", f"Tidak dapat memperbarui film: {e}")

    def delete_movie(self):
        current_row = self.movie_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Kesalahan Pemilihan", "Harap pilih film untuk dihapus.")
            return

        movie_id = self.movie_table.item(current_row, 0).text()
        movie_title = self.movie_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(self, 'Konfirmasi Hapus', f"Apakah Anda yakin ingin menghapus '{movie_title}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db_cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
                self.db_conn.commit()
                self.clear_form()
                self.load_movies_to_table()
                self.statusBar().showMessage(f"Berhasil menghapus '{movie_title}'!", 4000)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Kesalahan Basis Data", f"Tidak dapat menghapus film: {e}")

    def load_movies_to_table(self):
        try:
            self.db_cursor.execute("SELECT id, title, genre, rating, favorite FROM movies ORDER BY title")
            rows = self.db_cursor.fetchall()
            self.movie_table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                self.movie_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
                self.movie_table.setItem(row_idx, 1, QTableWidgetItem(row_data[1]))
                self.movie_table.setItem(row_idx, 2, QTableWidgetItem(row_data[2]))
                self.movie_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
                favorite_str = "Ya" if row_data[4] == 1 else "Tidak"
                self.movie_table.setItem(row_idx, 4, QTableWidgetItem(favorite_str))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Kesalahan Basis Data", f"Tidak dapat memuat film: {e}")

    def populate_form_on_select(self, row, column):
        self.id_label.setText(self.movie_table.item(row, 0).text())
        self.title_input.setText(self.movie_table.item(row, 1).text())
        self.genre_input.setCurrentText(self.movie_table.item(row, 2).text())
        self.rating_input.setValue(int(self.movie_table.item(row, 3).text()))
        is_favorite = self.movie_table.item(row, 4).text() == "Ya"
        self.favorite_checkbox.setChecked(is_favorite)

    def clear_form(self):
        self.id_label.setText("N/A")
        self.title_input.clear()
        self.genre_input.setCurrentIndex(0)
        self.rating_input.setValue(self.rating_input.minimum())
        self.favorite_checkbox.setChecked(False)

    def export_to_csv(self):
        if self.movie_table.rowCount() == 0:
            QMessageBox.information(self, "Info Ekspor", "Tidak ada data untuk diekspor.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "File CSV (*.csv)")

        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    headers = [self.movie_table.horizontalHeaderItem(i).text() for i in range(self.movie_table.columnCount())]
                    writer.writerow(headers)
                    
                    for row in range(self.movie_table.rowCount()):
                        row_data = [self.movie_table.item(row, col).text() for col in range(self.movie_table.columnCount())]
                        writer.writerow(row_data)
                
                self.statusBar().showMessage(f"Data berhasil diekspor ke {path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Kesalahan Ekspor", f"Tidak dapat mengekspor data ke CSV: {e}")

    def show_about_dialog(self):
        QMessageBox.about(self, "Tentang Pengelola Film",
            "<b>Pengelola Bookmark Film</b><br><br>"
            "Aplikasi ini adalah Proyek Akhir untuk Pemrograman Visual.<br><br>"
            "<b>Pengembang:</b><br>"
            "Nama: Ida Bagus Brahmanta Jayana<br>"
            "NIM: F1D022052<br><br>"
            "© 2024"
        )

    def closeEvent(self, event):
        if self.db_conn:
            self.db_conn.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedMovieApp()
    window.show()
    sys.exit(app.exec_())
