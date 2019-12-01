import Common
import os
from tqdm import tqdm

dataset_rows = ["LineNumber", "ID", "Hash", "UserNSID", "UserNickname", "DateTaken", "DateUploaded",
                "CaptureDevice", "Title", "Description", "UserTags", "MachineTags", "Longitude", "Latitude",
                "LongLatAcc", "PageURL", "DownloadURL", "LicenseName", "LicenseURL", "ServerIdentifier",
                "FarmIdentifier", "Secret", "OriginalSecret", "OriginalExtension", "Video"]
places_row = ["ID", "PlacesInfo"]


def join_labels_to_yfcc(labels_dir, yfcc_dir, dataset=None, places=None):
    """ Joins the Open Images labels to the YFCC100M datasets specified, outputting the result in the same directory
        with the file ending "-extended.csv" instead of ".csv"

    Parameters
    ----------
    labels_dir : str
        Path to the directory of CSV labels files
    yfcc_dir : str
        Directory where the YFCC files are stored
    dataset : bool
        Whether to extend with the dataset file, by default true
    places : bool
        Whether to extend with the places file, by default true
    """

    dataset = True if dataset is None else dataset
    places = True if places is None else places

    print("Building dictionary mapping Flickr ID to OpenImages ID")
    rows_by_flickr_id = {}
    order = {}
    matches = set()
    for subset in ["train", "validation", "test"]:
        print("Loading {}".format(subset))
        labels_file = "{}-images-{}with-rotation.csv".format(subset, "with-labels-" if subset == "train" else "")
        labels_path = os.path.join(labels_dir, labels_file)
        open_images = Common.load_csv_as_dict(labels_path)
        rows_by_flickr_id[subset] = {}
        order[subset] = []
        for row in tqdm(open_images):
            static_url = row["OriginalURL"]
            flickr_id = Common.extract_image_id_from_flickr_static(static_url)
            order[subset].append(flickr_id)
            rows_by_flickr_id[subset][flickr_id] = row
            if dataset:
                for col_name in dataset_rows:
                    if col_name != "ID":
                        rows_by_flickr_id[subset][flickr_id][col_name] = ''
            if places:
                for col_name in places_row:
                    if col_name != "ID":
                        rows_by_flickr_id[subset][flickr_id][col_name] = ''

    if dataset:
        print("Matching Open Images to YFCC100M Dataset")
        yfcc100m_dataset = Common.load_csv_as_dict(os.path.join(yfcc_dir, "yfcc100m_dataset"), fieldnames=dataset_rows,
                                                   delimiter="\t")
        join_matches(rows_by_flickr_id, matches, yfcc100m_dataset)

    if places:
        print("Matching Open Images to YFCC100M Places")
        yfcc100m_places = Common.load_csv_as_dict(os.path.join(yfcc_dir, "yfcc100m_places"), fieldnames=places_row,
                                                  delimiter="\t")
        join_matches(rows_by_flickr_id, matches, yfcc100m_places)

    print("Writing results to file")
    fieldnames = list(rows_by_flickr_id["train"][order["train"][0]].keys())
    for subset in ["train", "validation", "test"]:
        labels_file = "{}-images-{}with-rotation.csv".format(subset, "with-labels-" if subset == "train" else "")
        labels_path = os.path.join(labels_dir, labels_file)
        w = Common.new_csv_as_dict(labels_path.replace(".csv", "-extended.csv"), fieldnames)
        rows = [rows_by_flickr_id[subset][flickr_id] for flickr_id in order[subset] if flickr_id in matches]
        w.writeheader()
        w.writerows(rows)


def join_matches(rows_by_flickr_id, matches, yfcc100m):
    for row in tqdm(yfcc100m):
        flickr_id = row["ID"]
        for subset in ["train", "validation", "test"]:
            if rows_by_flickr_id[subset].get(flickr_id):
                for col_name in row.keys():
                    if col_name != "ID":
                        rows_by_flickr_id[subset][flickr_id][col_name] = row[col_name]
                matches.add(flickr_id)