import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                           QProgressBar, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWinExtras import QtWin
import cv2
import numpy as np


class ImageProcessor(QThread):
    progress_updated = pyqtSignal(int)
    result_found = pyqtSignal(str, float)
    comparison_update = pyqtSignal(str, float)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, modified_image_path, folder_path, output_folder):
        super().__init__()
        self.modified_image_path = modified_image_path
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.target_size = (224, 224)  # Standard size for comparison

    def preprocess_image(self, image_path):
        """Load and preprocess image for comparison"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Resize
            img = cv2.resize(img, self.target_size)
            
            # Convert to grayscale for better comparison
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            return gray
        except Exception as e:
            self.error_occurred.emit(f"Error preprocessing image {image_path}: {str(e)}")
            return None

    def compute_similarity(self, img1, img2):
        """Compute similarity between two images using multiple metrics"""
        try:
            # Compute structural similarity (SSIM)
            score = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)[0][0]
            
            # Normalize score to 0-1 range
            score = (score + 1) / 2
            
            return score
        except Exception as e:
            self.error_occurred.emit(f"Error computing similarity: {str(e)}")
            return 0.0

    def copy_best_match(self, source_path):
        """Copy the best matching image to output folder"""
        try:
            os.makedirs(self.output_folder, exist_ok=True)
            original_filename = os.path.basename(source_path)
            dest_path = os.path.join(self.output_folder, original_filename)
            
            # Handle duplicate filenames
            base, ext = os.path.splitext(original_filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(self.output_folder, f"{base}_{counter}{ext}")
                counter += 1
            
            shutil.copy2(source_path, dest_path)
            return dest_path
        except Exception as e:
            self.error_occurred.emit(f"Error copying file: {str(e)}")
            return None

    def run(self):
        """Main processing function"""
        try:
            # Load and preprocess modified image
            modified_img = self.preprocess_image(self.modified_image_path)
            if modified_img is None:
                raise Exception("Failed to load modified image")

            best_match = None
            best_score = -1
            supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
            
            # Get list of image files
            image_files = [f for f in os.listdir(self.folder_path) 
                         if f.lower().endswith(supported_extensions)]
            total_files = len(image_files)
            
            if total_files == 0:
                raise Exception("No supported images found in the folder")
            
            # Process each image
            for idx, filename in enumerate(image_files):
                try:
                    current_path = os.path.join(self.folder_path, filename)
                    
                    # Skip if it's the same file
                    if os.path.abspath(current_path) == os.path.abspath(self.modified_image_path):
                        continue
                    
                    # Process comparison image
                    current_img = self.preprocess_image(current_path)
                    if current_img is not None:
                        score = self.compute_similarity(modified_img, current_img)
                        self.comparison_update.emit(filename, score)
                        
                        if score > best_score:
                            best_score = score
                            best_match = current_path
                    
                    # Update progress
                    progress = int((idx + 1) / total_files * 100)
                    self.progress_updated.emit(progress)
                    
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    continue

            # Handle results
            if best_match:
                copied_path = self.copy_best_match(best_match)
                if copied_path:
                    self.result_found.emit(copied_path, best_score)
                else:
                    self.error_occurred.emit("Failed to copy best match")
            else:
                self.error_occurred.emit("No valid matches found")
                
        except Exception as e:
            self.error_occurred.emit(str(e))

class ImageFinderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set app ID for Windows taskbar
        if hasattr(QtWin, 'setCurrentProcessExplicitAppUserModelID'):
            QtWin.setCurrentProcessExplicitAppUserModelID('SearchByImage')
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle('Search by Image')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('ico.ico'))

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Image selection buttons
        btn_layout = QHBoxLayout()
        
        self.btn_select_image = QPushButton('Select Modified Image')
        self.btn_select_image.clicked.connect(self.select_modified_image)
        btn_layout.addWidget(self.btn_select_image)
        
        self.btn_select_folder = QPushButton('Select Search Folder')
        self.btn_select_folder.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.btn_select_folder)
        
        self.btn_select_output = QPushButton('Select Output Folder')
        self.btn_select_output.clicked.connect(self.select_output_folder)
        btn_layout.addWidget(self.btn_select_output)
        
        layout.addLayout(btn_layout)

        # Path display
        self.lbl_image_path = QLabel('Modified Image: Not selected')
        self.lbl_folder_path = QLabel('Search Folder: Not selected')
        self.lbl_output_path = QLabel('Output Folder: Not selected')
        layout.addWidget(self.lbl_image_path)
        layout.addWidget(self.lbl_folder_path)
        layout.addWidget(self.lbl_output_path)

        # Search button
        self.btn_search = QPushButton('Start Search')
        self.btn_search.clicked.connect(self.start_search)
        self.btn_search.setEnabled(False)
        layout.addWidget(self.btn_search)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(['Filename', 'Similarity Score'])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)

        # Best match display
        self.lbl_best_match = QLabel('Best Match: None')
        layout.addWidget(self.lbl_best_match)

        self.modified_image_path = None
        self.folder_path = None
        self.output_folder = None

        self.setWindowIcon(QIcon('ico.ico'))  # Set window icon

    def select_modified_image(self):
        """Open file dialog to select the modified image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select Modified Image', '',
            'Images (*.png *.jpg *.jpeg *.bmp)'
        )
        if file_path:
            self.modified_image_path = file_path
            self.lbl_image_path.setText(f'Modified Image: {file_path}')
            self.update_search_button()

    def select_folder(self):
        """Open folder dialog to select the search directory"""
        folder_path = QFileDialog.getExistingDirectory(
            self, 'Select Search Folder'
        )
        if folder_path:
            self.folder_path = folder_path
            self.lbl_folder_path.setText(f'Search Folder: {folder_path}')
            self.update_search_button()

    def select_output_folder(self):
        """Open folder dialog to select the output directory"""
        folder_path = QFileDialog.getExistingDirectory(
            self, 'Select Output Folder'
        )
        if folder_path:
            self.output_folder = folder_path
            self.lbl_output_path.setText(f'Output Folder: {folder_path}')
            self.update_search_button()

    def update_search_button(self):
        """Enable search button if all paths are selected"""
        self.btn_search.setEnabled(
            bool(self.modified_image_path and self.folder_path and self.output_folder)
        )

    def start_search(self):
        """Initialize and start the image processing thread"""
        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.btn_search.setEnabled(False)
        
        self.processor = ImageProcessor(self.modified_image_path, self.folder_path, self.output_folder)
        self.processor.progress_updated.connect(self.update_progress)
        self.processor.result_found.connect(self.show_best_match)
        self.processor.comparison_update.connect(self.add_comparison_result)
        self.processor.error_occurred.connect(self.show_error)
        self.processor.finished.connect(self.search_finished)
        self.processor.start()

    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)

    def add_comparison_result(self, filename, score):
        """Add a new comparison result to the table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem(filename))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{score:.4f}"))

    def show_best_match(self, path, score):
        """Display the best matching image path and score"""
        self.lbl_best_match.setText(
            f'Best Match: {path}\nSimilarity Score: {score:.4f}'
        )

    def show_error(self, message):
        """Display error message"""
        QMessageBox.critical(self, "Error", message)

    def search_finished(self):
        """Reset UI state after search completion"""
        self.btn_search.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    ex = ImageFinderGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
