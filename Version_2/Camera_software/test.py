
if (int(setup["Days"]) > 0) and currentDT.hour >= int_sh and currentDT.minute >= int_sm:
    print("check")
    while int(setup["Days"]) > 0:
        camera.resolution = (1280, 720)
        camera.rotation = 180

        exit = true
        while exit != false:

            camera.start_recording('clip%02d%02d.h264' % j i)
            start_section = datetime.datetime.now()
            while datetime.datetime.now() < (start_section + setup["section"]):
                camera.wait_recording(1)
                if (curtime.hour >= int(eh)) and (curtime.minute >= int(em)):
                    print("break", setup["Days"])
                    exit = true
                    break

            camera.stop_recording()

print("%d" %setup["Days"])
print("FINISH") (edited) 