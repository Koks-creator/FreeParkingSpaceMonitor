import cv2
import numpy as np
import pickle

with open('CarParkPosKrzywe2', 'rb') as f:
    pos_list = pickle.load(f)

# Wymiary jednego miejsca parkingowe na obrazku
width, height = 107, 48


def check_parking_space(img_processed):
    h, w = 0, 0
    free_space_counter = 0

    for index, pos in enumerate(pos_list):
        if type(pos) == tuple:
            x, y, w, h = pos

            img_crop = img_processed[y:y+h, x:x+w]

        else:
            height, width, _ = img.shape

            pos_region = np.array([pos[0], pos[1], pos[2], pos[3]], np.int32)

            mask = np.zeros((height, width), np.uint8)
            cv2.polylines(mask, [pos_region], True, 255, 2)
            cv2.fillPoly(mask, [pos_region], 255)
            img_processed_cropped = cv2.bitwise_and(img_processed, img_processed, mask=mask)
            x = np.min(pos_region[:, 0])
            x2 = np.max(pos_region[:, 0])
            y = np.min(pos_region[:, 1])
            y2 = np.max(pos_region[:, 1])

            # Wycinanie
            img_crop = img_processed_cropped[y:y2, x:x2]

            # cv2.imshow(str(index), mask)
        count = cv2.countNonZero(img_crop)
        cv2.putText(img, str(count), (x, y + h - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)

        #500
        if count < 600:
            color = (0, 200, 0)
            thickness = 5
            free_space_counter += 1
        else:
            color = (0, 0, 200)
            thickness = 2

        if type(pos) == tuple:
            cv2.rectangle(img, (x, y), (pos[0] + w, pos[1] + h), color, thickness)
        else:
            cv2.polylines(img, [pos], True, color, 4)
    cv2.putText(img, f"Free: {free_space_counter}/{len(pos_list)}", (48, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)


cap = cv2.VideoCapture("Videos\ParkingKrzywy.mp4")

frame_size = (int(cap.get(3)), int(cap.get(4)))
print(frame_size)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

start_rec = False
out = cv2.VideoWriter(f"Parking.mp4", fourcc, 20, (frame_size))
while True:

    # Resetowanie filmu
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    img = cv2.resize(img, (1280, 720))
    if success is False:
        break

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    img_median = cv2.medianBlur(img_threshold, 5)
    kernel = np.ones((3, 3), np.int8)
    img_dilate = cv2.dilate(img_median, kernel, iterations=1)

    check_parking_space(img_dilate)
    if start_rec:
        print("nagrywam")
        out.write(img)
    cv2.imshow("Res", img)
    # cv2.imshow("Res blur", img_blur)
    # cv2.imshow("Res thresh", img_threshold)
    # cv2.imshow("img_median", img_median)
    # cv2.imshow("img_dilate", img_dilate)
    key = cv2.waitKey(30)

    if key == ord("r"):
        print("df")
        start_rec = True

    if key == ord("q"):
        break

    if key == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()