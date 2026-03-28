# 2nd Semester CGPA Calculator

A Streamlit app to calculate your 2nd semester GPA and overall CGPA, with shared history storage.

## Features

- Input 1st semester GPA and credits
- Input scores for 2nd semester courses and labs
- Automatic grade calculation based on your grading scale
- CGPA calculation combining both semesters
- Shared history of all calculations (stored in Firebase Firestore)

## Setup and Deployment

### 1. Set up Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Enable Firestore Database
4. Go to Project Settings > Service Accounts
5. Generate a new private key (JSON) - download it
6. For local development, place the JSON file as `serviceAccountKey.json` in the project root

### 2. Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Connect your GitHub repo (push this code to GitHub first)
3. In Streamlit Cloud, go to your app settings
4. Add the Firebase service account JSON as a base64-encoded secret:
   - Key: `FIREBASE_SERVICE_ACCOUNT_B64`
   - Value: Base64 encoded JSON (see step 3 below)

### 3. Add Firebase Secret (Base64 Encoded)

1. Open your Firebase service account JSON file
2. Copy the entire JSON content
3. Base64 encode it:
   - **Online**: Use [base64encode.org](https://www.base64encode.org/)
   - **PowerShell**: `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Content 'ServiceAccountKey.json' -Raw)))`
4. In Streamlit Cloud → App Settings → Secrets, add:
   ```
   FIREBASE_SERVICE_ACCOUNT_B64 = "PASTE_THE_BASE64_STRING_HERE"
   ```
5. Click **"Save"** → App redeploys automatically

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place `serviceAccountKey.json` in the project root

3. Run:
   ```bash
   streamlit run gpa.py
   ```
### 4. Added Docker Containerization 

1. Added Dockerfile and .dockerignore
2. Ran the commands - had issues
3. Containerized - now i can share it via containers.

## Free Tier Limits

- **Firebase Firestore**: 1GB storage, 50K reads/day, 20K writes/day (free)
- **Streamlit Cloud**: Unlimited apps, but resource limits apply

## Courses and Credits

### Theory Courses
- OOP: 3 credits
- Database: 3 credits
- Linear Algebra: 3 credits
- Computer Network: 2 credits
- Digital Logic Design: 2 credits

### Labs
- OOP Lab: 1 credit
- Database Lab: 1 credit
- Computer Network Lab: 1 credit
- Digital Logic Design Lab: 1 credit

## Grading Scale

- 85+ : A (4.0)
- 80-84: A- (3.66)
- 75-79: B+ (3.33)
- 71-74: B (3.00)
- 68-70: B- (2.66)
- 64-67: C+ (2.33)
- 61-63: C (2.00)
- 58-60: C- (1.66)
- 54-57: D+ (1.33)
- 50-53: D (1.00)
- <50: F (0.00)

link : https://cgpacalculation.streamlit.app
