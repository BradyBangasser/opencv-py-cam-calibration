def main():
    import os, cv2, glob, sys, shutil, time, json

    # flags
    force = sys.argv.__contains__("-f")
    # tells the program to use the existing imgs in the IMG_PATH folder
    useExisting = sys.argv.__contains__("-u")
    # create a new charuco board
    create = sys.argv.__contains__("-n")

    # args
    try:
        imgSrc = int(sys.argv[sys.argv.index("-s") + 1])
    except:
        imgSrc = -1

    IMG_PATH = "calibration-imgs"
    MIN_NUMBER_OF_IMGS = 30
    NUMBER_OF_CAMERAS_TO_TRY = 5
    C_DIR = os.getcwd()

    crit = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 100, .001)
    dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
    board = cv2.aruco.CharucoBoard((8, 11), .0015, .0011, dict)

    if create:
        cv2.imwrite("board.jpg", board.generateImage((int(7 * 300), int(9 * 300)), marginSize=int(300 * .5)))
        exit() 

    currentNumberOfPictures = 0

    if not os.path.exists(IMG_PATH):
        if not useExisting: os.mkdir(IMG_PATH)
        else: raise FileNotFoundError(f"'{IMG_PATH}' doesn't exist lol")
    else:
        # if its a file
        if not os.path.isdir(IMG_PATH):
            if force:
                os.remove(IMG_PATH)
                os.mkdir(IMG_PATH)
            else:
                raise FileExistsError(f"'{IMG_PATH}' is a file")
        else:
            if not useExisting:
                if all(os.path.splitext(x)[1] == ".jpg" for x in os.listdir(IMG_PATH)): 
                    if force: 
                        try:
                            for file in os.listdir(IMG_PATH):
                                file = os.path.join(IMG_PATH, file)
                                if os.path.isfile(file): os.remove(file)
                                else: shutil.rmtree(file)
                        except:
                            
                            print("Unable to remove contents of folder")
                    else:
                        print(f"WARNING: '{IMG_PATH}' already exists, .jpgs in the folder may affect calibration")
            else: 
                currentNumberOfPictures = len(list(filter(lambda x: os.path.splitext(x)[1] == ".jpg", os.listdir(IMG_PATH))))

    os.chdir(IMG_PATH)

    camIndex = 1
    cam = cv2.VideoCapture(imgSrc if imgSrc != -1 else 0)


    while not cam.isOpened() and camIndex < NUMBER_OF_CAMERAS_TO_TRY:
        print(f"Cam index {camIndex - 1} didn't work, attempting cam index {camIndex}")
        cam = cv2.VideoCapture(camIndex)
        camIndex += 1

    if not cam.isOpened(): raise OSError("Unable to access camera")
    else:
        print(f"Connect to cam src {camIndex - 1}")

    while MIN_NUMBER_OF_IMGS - currentNumberOfPictures > 0:
        _, frame = cam.read()
        fcopy = frame
        cv2.putText(fcopy, f"{currentNumberOfPictures}/{MIN_NUMBER_OF_IMGS}", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
        cv2.imshow("out", fcopy)


        if cv2.waitKey(25) == ord(" "):
            cv2.imwrite(f"calibration_{time.strftime('%Y-%m-%d')}_{currentNumberOfPictures}.jpg", frame)
            currentNumberOfPictures += 1

    corners, obj_points = [], []

    detector = cv2.aruco.CharucoDetector(board)

    size: cv2.typing.Size = (0, 0)

    for img in glob.glob('*.jpg'):
        cvimg = cv2.imread(img)
        gimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
        size = gimg.shape

        ccorners, cids, mcorners, mids = detector.detectBoard(gimg)

        frame_points, frame_img_points = board.matchImagePoints(ccorners, cids)

        cv2.aruco.drawDetectedCornersCharuco(cvimg, ccorners, cids)

        print(f"Working: processing {img}...")

        if len(cids) >= 70:
            corners.append(frame_img_points)
            obj_points.append(frame_points)

    ret, matrix, dist, tvecs, rvecs = cv2.calibrateCamera(obj_points, corners, size, None, None)

    os.chdir(C_DIR)

    out = open("calibration.json", "w")
    out.write(json.dumps({
        "date": time.strftime('%Y-%m-%d'),
        "matrix": list(matrix.flatten().data),
        "dist": list(dist.flatten().data)
    }))

    out.close()

if __name__ == "__main__":
    main()