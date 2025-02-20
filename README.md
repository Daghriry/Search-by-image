# Search by Image

An intelligent image matching application that uses GPU-accelerated processing to find original images from a collection based on a modified version. Built with PyQt5 and PyTorch.

![image](https://github.com/user-attachments/assets/64826ff0-e5b0-432c-84d3-a7ac9914b8fd)


## Features

- **GPU Acceleration**: Utilizes CUDA for faster image processing when available
- **User-friendly GUI**: Easy-to-use interface for selecting images and folders
- **Real-time Progress**: Shows processing progress and similarity scores
- **Automatic File Management**: Saves matched images to specified output folder
- **Multi-format Support**: Handles common image formats (PNG, JPG, JPEG, BMP)
- **Similarity Scoring**: Uses cosine similarity for accurate image matching
- **Results Table**: Displays detailed comparison results for all processed images

## Requirements

- Python 3.8+
- PyQt5
- PyTorch
- torchvision
- Pillow
- CUDA (optional, for GPU acceleration)

## Installation

Install dependencies:
```bash
pip install PyQt5 torch torchvision Pillow numpy
```

## Usage

1. Launch the application:
```bash
python main.py
```

2. Select the modified image you want to find the original for
3. Choose the folder containing potential original images
4. Select an output folder for the matched image
5. Click "Start Search" to begin the process

## How It Works

1. **Image Loading**: Loads and preprocesses images using PyTorch's transformation pipeline
2. **Feature Extraction**: Converts images to tensors and normalizes them
3. **Similarity Computation**: Uses cosine similarity to compare image features
4. **Result Processing**: Identifies and copies the best matching image
5. **GPU Acceleration**: Automatically utilizes CUDA if available

## Performance Notes

- GPU acceleration can significantly improve processing speed
- Performance depends on the number and size of images
- Recommended to use GPU for large image collections

## Contact

Twitter: [@Daghriry](https://x.com/Daghriry)

Project Link: [https://github.com/Daghriry/Search-by-image](https://github.com/Daghriry/Search-by-image)
