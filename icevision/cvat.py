import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET
import os


class CvatDataset:

    def __init__(self):
        self._images = {}
        self._labels = []
        self._next_id = 0
        self._loaded_from = None

    def load(self, path):
        self._loaded_from = path
        tree = ET.ElementTree(file=path)
        root = tree.getroot()

        for name in root.findall("meta/task/labels/label/name"):
            self._labels.append(name.text)
        self._labels = sorted(self._labels)

        for image in root.iter("image"):
            image_id = int(image.attrib["id"])
            self.add_image(image_id)

            for box in image.iter("box"):
                box.attrib["occluded"] = bool(int(box.attrib["occluded"]))
                for k in ["xtl", "ytl", "xbr", "ybr"]:
                    box.attrib[k] = float(box.attrib[k])
                #Add conf
                conf = None
                conf_att = box.find("attribute[@name='conf']")
                if conf_att is not None:
                    conf = int(conf_att.text)

                self.add_box(image_id, conf, **box.attrib)

            for polygon in image.iter("polygon"):
                polygon.attrib["occluded"] = bool(int(polygon.attrib["occluded"]))
                points = list(map(lambda x: list(map(float, x.split(","))),
                                  polygon.attrib["points"].split(";")))
                self.add_polygon(image_id, points, polygon.attrib["label"], polygon.attrib["occluded"])

            if "width" in image.attrib and "height" in image.attrib:
                self.set_size(image_id, int(image.attrib["width"]), int(image.attrib["height"]))

            if "name" in image.attrib:
                self.set_name(image_id, image.attrib["name"])

    def dump(self, path=None):
        path = path or self._loaded_from
        assert path, "path should be specified or markup loaded from file"

        root = xml.Element("annotations")

        version = xml.SubElement(root, "version")
        version.text = "1.1"

        if self._labels:
            meta = xml.SubElement(root, "meta")
            task = xml.SubElement(meta, "task")
            labels = xml.SubElement(task, "labels")
            for lbl in self._labels:
                label = xml.SubElement(labels, "label")
                name = xml.SubElement(label, "name")
                name.text = lbl

        for image_id, image in self._images.items():
            image_attrib = {"id": str(image_id)}

            if "height" in image and "width" in image:
                image_attrib["height"] = str(image["height"])
                image_attrib["width"] = str(image["width"])

            if "name" in image:
                image_attrib["name"] = image["name"]

            image_elem = xml.SubElement(root, "image", image_attrib)

            for box in image["boxes"]:
                t_box = xml.SubElement(
                    image_elem,
                    "box",
                    {k: str(box[k]) for k in ["xtl", "ytl", "xbr", "ybr"]},
                    label=box["label"],
                    occluded=str(int(box["occluded"]))
                )
                if box['conf'] is not None:
                    t_attr = xml.SubElement(t_box, 'attribute', name="conf")
                    t_attr.text = str(box['conf'])


            for polygon in image["polygons"]:
                xml.SubElement(
                    image_elem,
                    "polygon",
                    occluded=str(int(polygon["occluded"])),
                    points=";".join(["{},{}".format(*point) for point in polygon["points"]]),
                    label=polygon["label"]
                )

        tree = xml.ElementTree(root)
        with open(path, "w") as f:
            tree.write(f, encoding="unicode")

    def add_image(self, image_id=None):
        if image_id is None:
            image_id = self._next_id
            self._next_id += 1
        else:
            self._next_id = image_id + 1

        self._images[image_id] = {
            "boxes": [],
            "polygons": []
        }

        return image_id

    def add_box(self, image_id, conf, xtl, ytl, xbr, ybr, label, occluded=False):
        self._images[image_id]["boxes"].append({
            "xtl": xtl, "ytl": ytl, "xbr": xbr, "ybr": ybr, "label": label, "occluded": occluded, "conf": conf
        })

    def add_polygon(self, image_id, points, label, occluded=False):
        self._images[image_id]["polygons"].append({
            "points": points, "label": label, "occluded": occluded
        })

    def get_boxes(self, image_id):
        return self._images[image_id]["boxes"]

    def get_polygons(self, image_id):
        return self._images[image_id]["polygons"]

    def get_size(self, image_id):
        image = self._images[image_id]
        return {"height": image["height"], "width": image["width"]}

    def set_size(self, image_id, width, height):
        image = self._images[image_id]
        image["width"] = int(width)
        image["height"] = int(height)

    def get_image_ids(self):
        return sorted(self._images.keys())

    def get_name(self, image_id):
        return self._images[image_id]["name"]

    def set_name(self, image_id, name):
        self._images[image_id]["name"] = name

    def get_labels(self):
        return self._labels

    def __len__(self):
        return len(self._images)

    def update(self, right, on="name"):
        assert on in ["name", "frame"]
        if on == "frame":
            self._images.update(right)
        elif on == "name":
            left_dict = {os.path.basename(v["name"]): v for v in self._images.values()}
            right_dict = {os.path.basename(v["name"]): v for v in right._images.values()}
            left_dict.update(right_dict)
            self._images = {i: left_dict[name] for i, name in enumerate(sorted(left_dict))}
        if self._labels:
            self._labels = list(set(self._labels).union(right._labels))
