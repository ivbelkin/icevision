import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET


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
                self.add_box(image_id, **box.attrib)

            for polygon in image.iter("polygon"):
                polygon.attrib["occluded"] = bool(int(polygon.attrib["occluded"]))
                points = list(map(lambda x: list(map(float, x.split(","))),
                                  polygon.attrib["points"].split(";")))
                self.add_polygon(image_id, points, polygon.attrib["label"], polygon.attrib["occluded"])

            if "width" in image.attrib and "height" in image.attrib:
                self._set_size(image_id, image.attrib["width"], image.attrib["height"])

            if "name" in image.attrib:
                self._set_name(image_id, image.attrib["name"])

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
                xml.SubElement(
                    image_elem,
                    "box",
                    {k: str(box[k]) for k in ["xtl", "ytl", "xbr", "ybr"]},
                    label=box["label"],
                    occluded=str(int(box["occluded"]))
                )

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

    def add_box(self, image_id, xtl, ytl, xbr, ybr, label, occluded=False):
        self._images[image_id]["boxes"].append({
            "xtl": xtl, "ytl": ytl, "xbr": xbr, "ybr": ybr, "label": label, "occluded": occluded
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

    def _set_size(self, image_id, width, height):
        """Don't call outside the class!"""
        assert self._loaded_from
        image = self._images[image_id]
        image["width"] = width
        image["height"] = height

    def get_image_ids(self):
        return sorted(self._images.keys())

    def get_name(self, image_id):
        return self._images[image_id]["name"]

    def _set_name(self, image_id, name):
        """Don't call outside the class!"""
        assert self._loaded_from
        self._images[image_id]["name"] = name

    def get_labels(self):
        return self._labels
