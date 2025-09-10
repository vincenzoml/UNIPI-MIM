# Setup Guide for Lecture 1

## Required Software Installation

### 1. Python Environment Setup

**Option A: Anaconda (Recommended)**
```bash
# Download and install Anaconda from https://www.anaconda.com/
# Create a new environment for the course
conda create -n medical-imaging python=3.9
conda activate medical-imaging
```

**Option B: Python + pip**
```bash
# Ensure Python 3.8+ is installed
python --version
# Create virtual environment
python -m venv medical-imaging-env
source medical-imaging-env/bin/activate  # On macOS/Linux
# medical-imaging-env\Scripts\activate  # On Windows
```

### 2. Essential Libraries

```bash
# Basic scientific computing
pip install numpy scipy matplotlib pandas

# Image processing
pip install opencv-python pillow scikit-image

# Medical imaging specific
pip install SimpleITK nibabel pydicom

# Machine learning
pip install scikit-learn

# Jupyter for interactive development
pip install jupyter notebook ipykernel
```

### 3. VoxLogica Installation

**Note:** VoxLogica installation instructions depend on the specific distribution. Typically:

```bash
# If available via pip
pip install voxlogica

# Or download from official repository
# Follow instructions at: [VoxLogica official repository]
```

### 4. Additional Tools

**ImageJ/FIJI (Optional but recommended)**
- Download from: https://imagej.net/software/fiji/
- Useful for manual image inspection and validation

**3D Slicer (Optional)**
- Download from: https://www.slicer.org/
- Professional medical image visualization

### 5. Test Installation

Create a test script to verify everything works:

```python
# test_installation.py
import numpy as np
import cv2
import matplotlib.pyplot as plt
import SimpleITK as sitk
import nibabel as nib

print("All libraries imported successfully!")

# Test basic functionality
test_image = np.random.rand(100, 100)
plt.figure(figsize=(5, 5))
plt.imshow(test_image, cmap='gray')
plt.title("Test Image")
plt.axis('off')
plt.savefig('test_output.png')
print("Test image created successfully!")

# Test SimpleITK
sitk_image = sitk.GetImageFromArray(test_image)
print(f"SimpleITK image size: {sitk_image.GetSize()}")

print("Setup verification complete!")
```

Run the test:
```bash
python test_installation.py
```

### 6. Sample Data

We'll provide sample medical images for the course. Create a data directory:

```bash
mkdir course_data
cd course_data
mkdir raw_images processed_images results
```

### 7. IDE Setup (Optional)

**Recommended IDEs:**
- **Jupyter Notebook:** For interactive development
- **VS Code:** With Python extension
- **PyCharm:** Professional Python IDE

**VS Code Extensions:**
- Python
- Jupyter
- Python Docstring Generator

### 8. Troubleshooting

**Common Issues:**

1. **Import errors:** Ensure you're using the correct Python environment
2. **Permission issues:** Use `pip install --user` if needed
3. **Version conflicts:** Create a fresh virtual environment
4. **macOS issues:** May need to install Xcode command line tools

**Getting Help:**
- Check library documentation
- Use course discussion forum
- Contact instructors during office hours

### 9. Verification Checklist

Before the next lecture, ensure you can:
- [ ] Import all required libraries without errors
- [ ] Create and display a simple image with matplotlib
- [ ] Load and manipulate arrays with numpy
- [ ] Run a Jupyter notebook
- [ ] Access the course data directory

### 10. Next Steps

**For Lecture 2:**
- Bring your laptop with all software installed
- Download sample medical images (links will be provided)
- Review basic Python syntax if needed
- Read about medical imaging modalities (MRI, CT, Ultrasound)

**Resources:**
- Python refresher: https://www.python.org/about/gettingstarted/
- NumPy tutorial: https://numpy.org/doc/stable/user/quickstart.html
- Medical imaging basics: Course reading materials

---

## Contact Information

**Technical Support:**
- Course TA: [contact information]
- Discussion Forum: [link]
- Office Hours: [schedule]

**Emergency Contact:**
If you cannot get the software working before the next lecture, contact us immediately so we can provide alternative solutions.