from Select import Select
import os
from tqdm import tqdm
from Common import Common


class Statistics:
    def __init__(self, image_level=None):
        """ Builds the object

        Parameters
        ----------
        image_level : bool
            Whether using image-level dataset, set to False if using bounding boxes, by default is True
        """

        self.image_level = True if image_level is None else image_level
        self.common = Common(self.image_level)

    def get_class_counts(self, root_dir, human_readable=None):
        """ Returns the counts of each class for the training, validation, and test sets

        Parameters
        ----------
        root_dir : str
            Root directory containing csv files and new folder
        human_readable : bool
            Whether the dictionary should use the class labels as keys or human descriptions, default is True

        Returns
        -------
        dict of str -> dict of str -> int
            Top level dictionary is keyed by labels or human descriptions, second level is train, validation, or test,
            the value of the second level dictionary is the counts for that labels subset
        """

        human_readable = True if human_readable is None else human_readable
        class_counts = {}
        for subset in ["train", "validation", "test"]:
            print("Loading CSVs for {}".format(subset))
            image_labels_file = self.common.get_image_labels_file(subset)
            image_labels_path = os.path.join(root_dir, image_labels_file)
            c = Common.load_csv_as_dict(image_labels_path)
            for row in tqdm(c):
                label_name = row["LabelName"]
                if not class_counts.get(label_name):
                    class_counts[label_name] = {}
                if not class_counts[label_name].get(subset):
                    class_counts[label_name][subset] = 0
                class_counts[label_name][subset] += 1
        if human_readable:
            label_to_human_label = Select.class_names_to_human_names(
                os.path.join(root_dir, self.common.get_classes_description_file()))
            for label in label_to_human_label.keys():
                class_counts[label_to_human_label[label]] = class_counts[label]
                del class_counts[label]
        return class_counts

    def number_of_images(self, root_dir, per_subset=None):
        """ Returns the count of all images

        Parameters
        ----------
        root_dir : str
            Root directory containing csv files and new folder
        per_subset : bool
            Whether to give stats per subset or for the whole dataset, by default the whole dataset

        Returns
        -------
        int
            Count of all images
        """

        per_subset = False if per_subset is None else per_subset

        counts = {}
        for subset in ["train", "validation", "test"]:
            counts[subset] = 0
            print("Loading CSVs for {}".format(subset))
            image_ids_file = self.common.get_image_ids_file(subset)
            image_ids_path = os.path.join(root_dir, image_ids_file)
            counts[subset] += len(Select.get_image_names(image_ids_path))
        if not per_subset:
            counts = sum(counts.values())
        return counts

    def download_space_required(self, root_dir):
        """ Returns the space required in bytes to download all training, validation, and test files

        Parameters
        ----------
        root_dir : str
            Root directory containing csv files and new folder

        Returns
        -------
        int
            Bytes required to download all training, validation, and test files
        """

        size = 0
        for subset in ["train", "validation", "test"]:
            image_ids_file = self.common.get_image_ids_file(subset)
            print("Reading {}".format(subset))
            c = Common.load_csv_as_dict(os.path.join(root_dir, image_ids_file))
            for row in tqdm(c):
                size += int(row["OriginalSize"])
        return size
