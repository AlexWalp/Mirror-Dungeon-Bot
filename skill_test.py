from utils import *
PATH = pth(UI_PATH, "battle")

def find_skill3(background, known_rgb, threshold=40, min_pixels=10, max_pixels=100, sin="envy"):
    median_rgb = np.median(background, axis=(0, 1)).astype(int)
    blended_rgb = (median_rgb * 0.45 + np.array(known_rgb) * 0.55).astype(int)
    
    lower_bound = np.clip(blended_rgb - threshold, 0, 255)
    upper_bound = np.clip(blended_rgb + threshold, 0, 255)
    mask = cv2.inRange(background, lower_bound, upper_bound)

    # collecting clusters (colors that are directly connected)
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
    
    cluster_centers = []

    # some pixel value checks (colors in cluster may be disconnected)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        center = centroids[i]
        
        if min_pixels <= area <= max_pixels:
            x = int(center[0])
            x1, x2 = max(0, x-25), min(background.shape[1], x+25)
            y1, y2 = 0, 10
            
            region_mask = mask[y1:y2, x1:x2]
            similar_pixels = np.count_nonzero(region_mask)

            if 150 >= similar_pixels >= 20:
                cluster_centers.append(center)
    
    # merging neightbouring clusters
    merged = []
    while cluster_centers:
        current = cluster_centers.pop()
        group = [c for c in cluster_centers if np.linalg.norm(current - c) <= 50]
        cluster_centers = [c for c in cluster_centers if np.linalg.norm(current - c) > 50]
        merged.append(np.mean([current] + group, axis=0))
    
    # filter by color patterns
    filtered = []
    while merged:
        center = merged.pop()
        x = int(center[0])
        x1, x2 = max(0, x-30), min(background.shape[1], x+30)
        y1, y2 = 0, 10
        region_mask = mask[y1:y2, x1:x2]

        pattern = np.zeros((y2-y1, x2-x1), dtype=np.uint8)
        pattern = np.maximum(pattern, region_mask)
        try:
            if pattern.shape[1] < 33 : raise gui.ImageNotFoundException
            locateOnScreenRGBA(pth("sins", f"{sin}.png"), region=(0, 0, pattern.shape[1], 10), conf=0.85, path=PATH, screenshot=pattern)
            filtered.append(center[0])
        except gui.ImageNotFoundException:
            # print(sin)
            continue

    return filtered

# bgr values
sins = {
    "wrath"   : (  0,   0, 254),
    "gloom"   : (239, 197,  26),
    "sloth"   : ( 49, 205, 251),
    "lust"    : (  0, 108, 254),
    "pride"   : (213,  75,   1),
    "gluttony": (  1, 228, 146),
    "envy"    : (222,   1, 150),
}

for sin in sins.keys():
    stacked_image = None
    count = 0

    for filename in os.listdir("skill_data"):
        file_path = pth("skill_data", filename)

        background = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        known_bgr = sins[sin]

        clusters = find_skill3(background, known_bgr, sin=sin)
        count += len(clusters)
        
        for box in clusters:
            cv2.rectangle(background, (int(box - 3), int(2)), (int(box + 3), int(8)), color=(0, 255, 0), thickness=2)

        if stacked_image is None:
            stacked_image = background
        else:
            if background.shape[1] != stacked_image.shape[1]:
                new_width = stacked_image.shape[1]
                background = cv2.resize(background, (new_width, int(background.shape[0] * new_width / background.shape[1])))
            stacked_image = np.vstack((stacked_image, background))
    print(sin, count)
    cv2.imwrite(f"skill_detection/{sin}.png", stacked_image)

# wrath 162
# gloom 0
# sloth 0
# lust 58
# pride 13
# gluttony 0
# envy 155