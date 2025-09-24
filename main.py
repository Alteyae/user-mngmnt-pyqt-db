import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
import mysql.connector


# Database setup || You can use sqlite just change this code or connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3307
    )
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    conn.commit()
    conn.database = "test_db"

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        age INT NOT NULL
    )
    """)
    conn.commit()

except mysql.connector.Error as e:
    print(f"Database connection error: {e}")
    sys.exit()


class AnimatedButton(QPushButton):
    """Custom animated button with hover effects"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("animatedButton")
        
    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)


class ModernDatabaseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_user_id = None
        self.setupUI()
        self.loadExternalStyles()
        self.load_data()

    def setupUI(self):
        """Setup the user interface"""
        self.setWindowTitle("User Management")
        self.setGeometry(100, 100, 800, 600)
        self.setObjectName("mainWindow")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(main_layout)

        # Header section
        self.setupHeader(main_layout)
        
        # Input section
        self.setupInputSection(main_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)
        
        # Table section
        self.setupTableSection(main_layout)

    def setupHeader(self, layout):
        """Setup header with title and subtitle"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        # Main title
        title = QLabel("User Management System")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("© Altheae Owe")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)

    def setupInputSection(self, layout):
        """Setup input form section"""
        # Input container
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(15)
        
        # Form title
        form_title = QLabel("Add New User")
        form_title.setObjectName("sectionTitle")
        input_layout.addWidget(form_title)
        
        # Input fields layout
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(15)
        
        # Name input
        name_container = QVBoxLayout()
        name_label = QLabel("Full Name")
        name_label.setObjectName("inputLabel")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("modernInput")
        self.name_input.setPlaceholderText("Enter full name...")
        name_container.addWidget(name_label)
        name_container.addWidget(self.name_input)
        
        # Age input
        age_container = QVBoxLayout()
        age_label = QLabel("Age")
        age_label.setObjectName("inputLabel")
        self.age_input = QLineEdit()
        self.age_input.setObjectName("modernInput")
        self.age_input.setPlaceholderText("Enter age...")
        age_container.addWidget(age_label)
        age_container.addWidget(self.age_input)
        
        # CRUD Button for CRUD Functionality
        button_container = QVBoxLayout()
        button_spacer = QLabel("")  

        # Button layout
        buttons_layout = QHBoxLayout()

        self.add_button = AnimatedButton("Add User")
        self.add_button.clicked.connect(self.add_user)

        self.update_button = AnimatedButton("Update User")
        self.update_button.clicked.connect(self.update_user)
        self.update_button.setEnabled(False)

        self.delete_button = AnimatedButton("Delete User")
        self.delete_button.clicked.connect(self.delete_user)
        self.delete_button.setEnabled(False)

        self.clear_button = AnimatedButton("Clear")
        self.clear_button.clicked.connect(self.clear_form)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_button)

        button_container.addWidget(button_spacer)
        button_container.addLayout(buttons_layout)
        
        fields_layout.addLayout(name_container, 2)
        fields_layout.addLayout(age_container, 1)
        fields_layout.addLayout(button_container, 1)
        
        input_layout.addLayout(fields_layout)
        layout.addWidget(input_container)

    def setupTableSection(self, layout):
        """Setup table section"""
        # Table Section
        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        
        table_layout = QVBoxLayout(table_container)
        table_layout.setSpacing(10)
        
        
        table_title = QLabel("Users Database")
        table_title.setObjectName("sectionTitle")
        table_layout.addWidget(table_title)
        
    
        self.table = QTableWidget()
        self.table.setObjectName("modernTable")
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Connect table selection signal
        self.table.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

    def loadExternalStyles(self):
        """Load QSS styles from external file"""
        try:
            # Look for styles file in same directory
            style_file = os.path.join(os.path.dirname(__file__), 'modern_styles.qss')
            
            if os.path.exists(style_file):
                with open(style_file, 'r', encoding='utf-8') as f:
                    qss = f.read()
                self.setStyleSheet(qss)
                print("External QSS file loaded successfully!")
            else:
                print(f"QSS file not found at: {style_file}")
                print("Using fallback inline styles...")
                self.loadFallbackStyles()
                
        except Exception as e:
            print(f"Error loading QSS file: {e}")
            print("Using fallback inline styles...")
            self.loadFallbackStyles()

    def loadFallbackStyles(self):
        """Fallback styles if external QSS file is not found"""
        fallback_qss = """
        #mainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #73877b, stop:0.3 #839788, stop:1 #bdbbb6);
            color: #2c3e30;
        }
        
        #mainTitle {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e30;
        }
        
        #subtitle {
            font-size: 14px;
            color: #4a5a4f;
        }
        
        #sectionTitle {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e30;
        }
        
        #inputContainer, #tableContainer {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(245, 228, 215, 0.9), 
                stop:1 rgba(229, 209, 208, 0.8));
            border: 2px solid rgba(115, 135, 123, 0.3);
            border-radius: 12px;
            padding: 25px;
        }
        
        #modernInput {
            background: rgba(245, 228, 215, 0.7);
            border: 2px solid rgba(189, 187, 182, 0.5);
            border-radius: 8px;
            padding: 12px 16px;
            color: #2c3e30;
        }
        
        #modernInput:focus {
            border: 2px solid #73877b;
        }
        
        #animatedButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #73877b, stop:1 #839788);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            color: #f5e4d7;
            font-weight: 600;
        }
        
        #modernTable {
            background: rgba(245, 228, 215, 0.8);
            color: #2c3e30;
            border: 2px solid rgba(115, 135, 123, 0.3);
            border-radius: 8px;
        }
        """
        self.setStyleSheet(fallback_qss)

    def load_data(self):
        """Load data from database into table"""
        try:
            cursor.execute("SELECT * FROM users ORDER BY id DESC")
            records = cursor.fetchall()
            self.table.setRowCount(len(records))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["ID", "Name", "Age"])

            for row_idx, row_data in enumerate(records):
                for col_idx, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)
                    
        except mysql.connector.Error as e:
            self.showError("Database Error", f"Error fetching data: {e}")

    def add_user(self):
        """Add new user to database"""
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        
        if not name or not age:
            self.showWarning("Input Required", "Please enter both name and age")
            return

        try:
            age_int = int(age)
            if age_int < 0 or age_int > 150:
                self.showWarning("Invalid Age", "Age must be between 0 and 150")
                return
                
            cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", (name, age_int))
            conn.commit()
            
           
            self.load_data()

          
            self.showInfo("Success", f"User '{name}' added successfully!")
            
        except ValueError:
            self.showWarning("Invalid Input", "Age must be a valid number")
        except mysql.connector.Error as e:
            self.showError("Database Error", f"Error inserting data: {e}")

        # Clear form after successful add
        self.clear_form()

    def showError(self, title, message):
        """Show error message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def showWarning(self, title, message):
        """Show warning message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def showInfo(self, title, message):
        """Show info message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def on_table_selection_changed(self, selected, _):
        """Handle table selection changes"""
        if selected.indexes():
            # Get selected row
            row = selected.indexes()[0].row()

            # Get user ID from first column
            id_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            age_item = self.table.item(row, 2)

            if id_item and name_item and age_item:
                self.selected_user_id = int(id_item.text())

                # Fill form with selected data
                self.name_input.setText(name_item.text())
                self.age_input.setText(age_item.text())

                # Enable update and delete buttons
                self.update_button.setEnabled(True)
                self.delete_button.setEnabled(True)
        else:
            self.selected_user_id = None
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def clear_form(self):
        """Clear form inputs and reset selection"""
        self.name_input.clear()
        self.age_input.clear()
        self.selected_user_id = None
        self.table.clearSelection()
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def update_user(self):
        """Update selected user in database"""
        if not self.selected_user_id:
            self.showWarning("No Selection", "Please select a user to update")
            return

        name = self.name_input.text().strip()
        age = self.age_input.text().strip()

        if not name or not age:
            self.showWarning("Input Required", "Please enter both name and age")
            return

        try:
            age_int = int(age)
            if age_int < 0 or age_int > 150:
                self.showWarning("Invalid Age", "Age must be between 0 and 150")
                return

            cursor.execute("UPDATE users SET name = %s, age = %s WHERE id = %s",
                         (name, age_int, self.selected_user_id))
            conn.commit()

            # Reload data and clear form
            self.load_data()
            self.clear_form()

            # Show success
            self.showInfo("Success", f"User updated successfully!")

        except ValueError:
            self.showWarning("Invalid Input", "Age must be a valid number")
        except mysql.connector.Error as e:
            self.showError("Database Error", f"Error updating data: {e}")

    def delete_user(self):
        """Delete selected user from database"""
        if not self.selected_user_id:
            self.showWarning("No Selection", "Please select a user to delete")
            return

        # Get user name for confirmation
        name = self.name_input.text().strip()

        # Confirmation dialog
        reply = QMessageBox.question(self, 'Confirm Delete',
                                   f"Are you sure you want to delete user '{name}'?\n\nThis action cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor.execute("DELETE FROM users WHERE id = %s", (self.selected_user_id,))
                conn.commit()

                # Reload data and clear form
                self.load_data()
                self.clear_form()

                # Show success
                self.showInfo("Success", f"User '{name}' deleted successfully!")

            except mysql.connector.Error as e:
                self.showError("Database Error", f"Error deleting data: {e}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  
    
    # Set application properties
    app.setApplicationName("Modern User Management")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("ModernApps")
    
    window = ModernDatabaseApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()