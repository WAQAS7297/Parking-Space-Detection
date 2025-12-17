
# AI-Powered Parking Space Detection (Semester Project)

This project detects **occupied vs free parking spaces** in a video feed using **OpenCV**, based on the classic parking-lot monitoring idea.

It is built on top of the `ParkingLot-master` codebase, cleaned and organized for use as a **final semester project**.

## 1. Project Overview

- Input: 
  - A static image of a parking lot (used to define parking slots).
  - A video of the same scene (cars entering and leaving).
- User first **marks the 4 corners of each parking space** once.
- The system then plays the video and automatically:
  - Detects motion in each slot region.
  - Marks **occupied spaces in RED**.
  - Marks **free spaces in GREEN**.

You can use this as:
- A base for **Smart City** traffic / parking analytics.
- A demo of **computer vision**, background subtraction and region-based analysis.

## 2. Folder Structure

```text
Parking_Space_Detection_Project/
  requirements.txt
  README.md
  src/
    main.py
    motion_detector.py
    coordinates_generator.py
    drawing_utils.py
    colors.py
    assets/
      images/
        parking_lot_1.png
        parking_lot_2.png
      videos/
        parking_lot_1.mp4
        parking_lot_2.mp4
      data/
        .keep       # coordinate files will be saved here
```

## 3. How to Run (Step-by-Step)

> **Prerequisite:** Python 3.8+ and `pip` installed.

### 3.1. Create virtual environment (optional but recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate
```

### 3.2. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### 3.3. Step 1 – Generate parking slot coordinates

Run coordinate generator **once** for a chosen image:

```bash
cd src
python main.py --image assets/images/parking_lot_1.png --data assets/data/coordinates_1.yml --video assets/videos/parking_lot_1.mp4 --start-frame 1
