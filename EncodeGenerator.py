import cv2
import face_recognition
import pickle
import os
from supabase import create_client, Client

url = "https://rahngoowmsqgkozdomhx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhaG5nb293bXNxZ2tvemRvbWh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzOTU0MTgsImV4cCI6MjA1OTk3MTQxOH0.3gD4NKLSz2HMckdhO045IVHDOUR4edqV9TNeTwHdRgA"
bucket_name = "schoolattendance"

supabase: Client = create_client(url, key)


# Import student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Image files:", pathList)

imgList = []
studentIds = []

for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    imgList.append(img)
    studentIds.append(os.path.splitext(path)[0])

    # Upload to Supabase Storage
    file_path = os.path.join(folderPath, path)
    with open(file_path, "rb") as f:
        res = supabase.storage.from_(bucket_name).upload(path, f, {"content-type": "image/png"})
        print(f"Uploaded {path}: {res}")

print("Student IDs:", studentIds)

# Encode the images
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("No face found in an image.")
    return encodeList

print("Encoding Started ....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete.")

# Save encodings locally
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("Encodings File Saved.")

