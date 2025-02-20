# Search by Image

An intelligent image matching application that helps users find original images in a large collection by comparing them with modified versions. This tool is particularly useful for managing and organizing image collections where modified versions exist alongside originals.

![image](https://github.com/user-attachments/assets/50c7a9d4-a4b5-4ac7-99f3-fc04882199c9)


## Overview

Search by Image is designed to solve the common problem of finding original images when you have a modified version. It uses advanced image comparison algorithms to analyze similarities between images and identify potential matches, making it easier to organize and manage large image collections.

## Features

### Core Functionality
- **Smart Image Comparison**: Uses OpenCV for efficient image matching
- **Batch Processing**: Search through entire folders of images
- **Real-time Progress**: Live updates on search progress
- **Similarity Scoring**: Detailed scoring system for matches
- **Automatic File Management**: Copies matched files to specified directory

### User Interface
- **Clean GUI Design**: Simple and intuitive interface
- **Progress Tracking**: Visual progress bar
- **Results Table**: Detailed view of all comparisons
- **File Selection**: Easy-to-use file and folder pickers
- **Error Handling**: Clear error messages and notifications

### Technical Features
- **Format Support**: Compatible with PNG, JPG, JPEG, and BMP
- **Resource Efficient**: Optimized for minimal system resource usage
- **Windows Integration**: Native Windows look and feel with taskbar icon
- **No Installation Required**: Standalone executable

## How It Works

1. **Image Selection**
   - Select the modified image you want to find the original for
   - Choose the folder containing potential original images
   - Select an output folder for matched images

2. **Processing**
   - The application analyzes the selected image
   - Compares it with all images in the selected folder
   - Computes similarity scores for each comparison

3. **Results**
   - Displays real-time comparison results
   - Shows similarity scores for each image
   - Automatically copies the best match to the output folder

## System Requirements

- Operating System: Windows 10/11
- Memory: Minimum 4GB RAM recommended
- Storage: 100MB free space
- No special hardware requirements

## Installation

1. Download the latest release from the releases page
2. Extract the ZIP file if provided
3. Run the executable file directly - no installation needed

## Usage Guide

1. **Starting the Application**
   - Double-click `Search_by_Image.exe`
   - The main interface will appear

2. **Selecting Files**
   - Click "Select Modified Image" to choose your modified image
   - Click "Select Search Folder" to specify the folder with original images
   - Click "Select Output Folder" to choose where matches should be saved

3. **Running a Search**
   - Click "Start Search" after selecting all required paths
   - Watch the progress bar for search status
   - Review results in the comparison table

4. **Reviewing Results**
   - The best match will be displayed at the bottom
   - All comparisons are listed in the table
   - Matched file is automatically copied to the output folder

## Troubleshooting

Common issues and solutions:
- **Program won't start**: Ensure Windows is up to date
- **Slow performance**: Reduce the number of images in the search folder
- **No matches found**: Check if image formats are supported

## Technical Details

- Built with Python 3.9
- Uses OpenCV for image processing
- PyQt5 for the graphical interface
- Optimized binary size using UPX compression

## Future Plans

Planned features for future releases:
- Multiple image comparison modes
- Batch processing for multiple modified images
- Advanced filtering options
- Custom similarity thresholds

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Daghriry/Search-by-image/tags).

## Author

**Mohammed Daghriry** 
- Twitter: [@Daghriry](https://x.com/Daghriry)
- GitHub: [Daghriry](https://github.com/Daghriry)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the OpenCV community for their excellent computer vision library
- PyQt team for the GUI framework
- All contributors and testers

## Project Repository

[https://github.com/Daghriry/Search-by-image](https://github.com/Daghriry/Search-by-image)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
