from source.utils.utils import *

def ck_boss(region, comp, image):
    red_mask = cv2.inRange(image, np.array([0, 0, 180]), np.array([50, 50, 255]))
    return LocateGray.check(PTH["boss"], red_mask, region=region, wait=False, comp=comp, conf=0.6)

region = (0, 0, 282, 275)
v_list = [0.8, 0.9, 1]

def detector(image_path, image_name, comp):
    i = int(os.path.splitext(image_name)[0][-1])
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # boss
    if i == 1 and ck_boss(region, comp, image):
        return "boss"
    # other fight
    elif LocateRGB.check(PTH["coin"], region=region, wait=False, comp=comp, image=image):
        if LocateRGB.check(PTH["gift"], region=region, wait=False, comp=comp, image=image):
            if      LocateGray.check(PTH[f"risk0"], region=region, wait=False, comp=comp, v_comp=v_list[i], image=image, conf=0.8) or \
               any([LocateGray.check(PTH[f"risk1"], region=region, wait=False, comp=comp*(1-0.14*j), v_comp=v_list[i], image=image, conf=0.8) for j in range(2)]) or \
               any([LocateGray.check(PTH[f"risk2"], region=region, wait=False, comp=comp*(1-0.14*j), image=image, conf=0.8) for j in range(2)]):
                return "risk"
            elif any([LocateGray.check(PTH[f"focus{j}"], region=region, wait=False, comp=comp, v_comp=v_list[i], image=image, conf=0.85) for j in range(2)]) or \
                 any([LocateGray.check(PTH[f"focus{j+2}"], region=region, wait=False, comp=comp, image=image, conf=0.85) for j in range(2)]):
                return "focused"
            else:
                return "abno"
        else:
            return "fight"
    # event
    elif any([LocateGray.check(PTH[f"event{j}"], region=region, wait=False, comp=comp, v_comp=v_list[i], image=image) for j in range(2)]) or \
              LocateGray.check(PTH[f"event2"], region=region, wait=False, comp=comp, image=image):
        return "event"
    # shop
    elif LocateGray.check(PTH[f"shop0"], region=region, wait=False, comp=comp, v_comp=v_list[i], image=image, conf=0.8) or \
         LocateGray.check(PTH[f"shop1"], region=region, wait=False, comp=comp, image=image, conf=0.8):
        return "shop"
    return "empty"

# settings:
# dataset_path = "C:/Users/Seldon/Desktop/dataset2"
# comp = 0.86
dataset_path = "C:/Users/Seldon/Desktop/dataset"
comp = 1

counter = 0
correct = 0
errors = 0
for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.lower().endswith(".png"):
            counter += 1
            full_path = os.path.join(root, file)
            output = detector(full_path, file, comp)
            parent_name = os.path.basename(os.path.dirname(full_path))

            if output in str(parent_name):
                correct += 1
                continue
            else:
                errors += 1
                print(f"Wrong detection with folder {parent_name} file {file}, detected {output}")

print(f"Accuracy: {correct/counter*100:.2f} %")
print(f"Errors: {errors}")