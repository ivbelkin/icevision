import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET


class CvatDataset:

    def __init__(self):
        self._data = {}
        self._next_id = 0

    def load(self, path):
        tree = ET.ElementTree(file=path)
        root = tree.getroot()

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

    def dump(self, path):
        root = xml.Element("annotations")

        version = xml.SubElement(root, "version")
        version.text = "1.1"

        for image_id, image_data in self._data.items():
            image_elem = xml.SubElement(
                root,
                "image",
                id=str(image_id)
            )

            for box in image_data["boxes"]:
                xml.SubElement(
                    image_elem,
                    "box",
                    {k: str(box[k]) for k in ["xtl", "ytl", "xbr", "ybr"]},
                    label=box["label"],
                    occluded=str(int(box["occluded"]))
                )

            for polygon in image_data["polygons"]:
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

        self._data[image_id] = {
            "boxes": [],
            "polygons": []
        }

        return image_id

    def add_box(self, image_id, xtl, ytl, xbr, ybr, label, occluded=False):
        self._data[image_id]["boxes"].append({
            "xtl": xtl, "ytl": ytl, "xbr": xbr, "ybr": ybr, "label": label, "occluded": occluded
        })

    def add_polygon(self, image_id, points, label, occluded=False):
        self._data[image_id]["polygons"].append({
            "points": points, "label": label, "occluded": occluded
        })

    def get_boxes(self, image_id):
        return self._data[image_id]["boxes"]

    def get_polygons(self, image_id):
        return self._data[image_id]["polygons"]
