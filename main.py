import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                           QProgressBar, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import torch
import torchvision.transforms as transforms
from PIL import Image
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
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def load_and_preprocess_image(self, image_path):
        try:
            with Image.open(image_path).convert('RGB') as img:
                tensor = self.transform(img).unsqueeze(0)
                return tensor.to(self.device)
        except Exception as e:
            self.error_occurred.emit(f"Error loading image {image_path}: {str(e)}")
            return None

    def compute_similarity(self, img1_tensor, img2_tensor):
        try:
            img1_tensor = img1_tensor.to(self.device)
            img2_tensor = img2_tensor.to(self.device)
            
            img1_flat = img1_tensor.view(img1_tensor.size(0), -1)
            img2_flat = img2_tensor.view(img2_tensor.size(0), -1)
            
            similarity = torch.nn.functional.cosine_similarity(img1_flat, img2_flat)
            return similarity.item()
        except Exception as e:
            self.error_occurred.emit(f"Error computing similarity: {str(e)}")
            return 0.0

    def copy_best_match(self, source_path, similarity_score):
        try:
            # Create output folder if it doesn't exist
            os.makedirs(self.output_folder, exist_ok=True)
            
            # Get original filename
            original_filename = os.path.basename(source_path)
            dest_path = os.path.join(self.output_folder, original_filename)
            
            # Handle duplicate filenames
            base, ext = os.path.splitext(original_filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(self.output_folder, f"{base}_{counter}{ext}")
                counter += 1
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            print(f"Copied best match to: {dest_path}")
            return dest_path
        except Exception as e:
            self.error_occurred.emit(f"Error copying file: {str(e)}")
            return None

    def run(self):
        try:
            print(f"Loading modified image: {self.modified_image_path}")
            modified_img_tensor = self.load_and_preprocess_image(self.modified_image_path)
            if modified_img_tensor is None:
                raise Exception("Failed to load modified image")

            best_match = None
            best_score = -1
            supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
            
            image_files = [f for f in os.listdir(self.folder_path) 
                         if f.lower().endswith(supported_extensions)]
            total_files = len(image_files)
            
            if total_files == 0:
                raise Exception("No supported images found in the folder")

            print(f"Processing {total_files} images...")
            
            for idx, filename in enumerate(image_files):
                try:
                    current_path = os.path.join(self.folder_path, filename)
                    
                    if os.path.abspath(current_path) == os.path.abspath(self.modified_image_path):
                        continue
                    
                    current_img_tensor = self.load_and_preprocess_image(current_path)
                    if current_img_tensor is not None:
                        score = self.compute_similarity(modified_img_tensor, current_img_tensor)
                        print(f"Comparing with {filename}: score = {score}")
                        
                        self.comparison_update.emit(filename, score)
                        
                        if score > best_score:
                            best_score = score
                            best_match = current_path
                    
                    progress = int((idx + 1) / total_files * 100)
                    self.progress_updated.emit(progress)
                    
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    continue

            if best_match:
                print(f"Best match found: {best_match} with score {best_score}")
                # Copy the best match to output folder
                copied_path = self.copy_best_match(best_match, best_score)
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
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Search by Image')
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Image selection area
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

        # Device info
        self.lbl_device = QLabel(f'Using: {torch.device("cuda" if torch.cuda.is_available() else "cpu")}')
        layout.addWidget(self.lbl_device)

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

    def select_modified_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select Modified Image', '',
            'Images (*.png *.jpg *.jpeg *.bmp)'
        )
        if file_path:
            self.modified_image_path = file_path
            self.lbl_image_path.setText(f'Modified Image: {file_path}')
            self.update_search_button()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, 'Select Search Folder'
        )
        if folder_path:
            self.folder_path = folder_path
            self.lbl_folder_path.setText(f'Search Folder: {folder_path}')
            self.update_search_button()

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, 'Select Output Folder'
        )
        if folder_path:
            self.output_folder = folder_path
            self.lbl_output_path.setText(f'Output Folder: {folder_path}')
            self.update_search_button()

    def update_search_button(self):
        self.btn_search.setEnabled(
            bool(self.modified_image_path and self.folder_path and self.output_folder)
        )

    def start_search(self):
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
        self.progress_bar.setValue(value)

    def add_comparison_result(self, filename, score):
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem(filename))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{score:.4f}"))

    def show_best_match(self, path, score):
        self.lbl_best_match.setText(
            f'Best Match: {path}\nSimilarity Score: {score:.4f}'
        )

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def search_finished(self):
        self.btn_search.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    ex = ImageFinderGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
