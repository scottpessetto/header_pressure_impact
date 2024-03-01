from process_data import process, welltests
from pull_data import pull_tags

well_list = [
    "MPG-02",
    "MPG-14",
    "MPG-16",
    "MPG-18",
    "MPH-08",
    "MPH-16",
    "MPH-18",
    "MPH-19",
    "MPI-06",
    "MPI-20",
    "MPI-38",
    "MPI-15",
    "MPI-17",
    "MPI-27",
    "MPI-29",
    "MPI-31",
    "MPI-33",
    "MPI-36",
    "MPI-40",
    "MPJ-06",
    "MPJ-10",
    "MPJ-28",
    "MPJ-29",
    "MPJ-27",
]

# pull scada data
tag_dict = pull_tags.gen_tag_dict()
tag_list = pull_tags.get_tags(well_list, tag_dict)
raw_data = pull_tags.query_tag(tag_list)
raw_data.to_pickle("header_data.pkl")

# process scada
