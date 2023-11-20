import inspect
import os
import shutil
import sys

from detect_delimiter import detect
from fpdf import FPDF
import pandas as pd
from PIL import Image


"""
Some function comes from the scilpy toolbox. Please see :
https://github.com/scilus/scilpy
"""


def load_df_in_any_format(file):
    """
    Load dataset in any .csv or .xlsx format.
    :param file:    Input file to load.
    :return:
    Pandas dataframe.
    """
    _, ext = os.path.splitext(file)
    if ext == ".csv":
        df = pd.read_csv(file)
    if ext == ".xlsx":
        df = pd.read_excel(file)
    if ext == ".txt":
        with open(file, "r") as f:
            f = f.read()
            delimiter = detect(f, whitelist=["\t", ":", ";", " ", ","])
        df = pd.read_csv(file, sep=delimiter)

    return df


def add_overwrite_arg(p):
    p.add_argument(
        "-f",
        dest="overwrite",
        action="store_true",
        help="Force overwriting of existing output files.",
    )


def add_verbose_arg(p):
    p.add_argument(
        "-v",
        dest="verbose",
        action="store_true",
        help="If true, produce verbose output.",
    )


def assert_input(required, optional=None):
    """
    Function to validate the existence of an input file.
    From the scilpy toolbox : https://github.com/scilus/scilpy
    :param p:           Parser
    :param required:    Paths to assert the existence
    :param optional:    Paths to assert optional arguments
    :return:
    """

    def check(path):
        if not os.path.isfile(path):
            sys.exit("File {} does not exist.".format(path))

    if isinstance(required, str):
        required = [required]

    if isinstance(optional, str):
        optional = [optional]

    for file in required:
        check(file)
    for file in optional or []:
        if file is not None:
            check(file)


def assert_output(overwrite, required, optional=None, check_dir=True):
    """
    Validate that output exist and force the use of -f.
    From the scilpy toolbox : https://github.com/scilus/scilpy
    :param overwrite:       Overwrite argument value (true or false).
    :param required:    Required paths to assert.
    :param optional:    Optional paths to assert.
    :param check_dir:   Validate if output directory exist.
    :return:
    """

    def check(path):
        if os.path.isfile(path) and not overwrite:
            sys.exit(
                "Output file {} exists. Select the -f to force "
                "overwriting of the existing file.".format(path)
            )

        if check_dir:
            path_dir = os.path.dirname(path)
            if path_dir and not os.path.isdir(path_dir):
                sys.exit(
                    "Directory {} is not created for the output file."
                    .format(path_dir)
                )

    if isinstance(required, str):
        required = [required]
    if isinstance(optional, str):
        optional = [optional]

    for file in required:
        check(file)
    for file in optional or []:
        if file:
            check(file)


def assert_output_dir_exist(overwrite, required, optional=None,
                            create_dir=True):
    """
    Validate the existence of the output directory.
    From the scilpy toolbox : https://github.com/scilus/scilpy
    :param overwrite:       Overwrite argument value (true or false).
    :param required:        Required paths to validate.
    :param optional:        Optional paths to validate.
    :param create_dir:      Option to create the directory if it does not
                            already exist.
    :return:
    """

    def check(path):
        if not os.path.isdir(path):
            if not create_dir:
                sys.exit(
                    "Output directory {} does not exist. Use create_dir = "
                    "True.".format(path)
                )
            else:
                os.makedirs(path, exist_ok=True)
        if os.listdir(path):
            if not overwrite:
                sys.exit(
                    "Output directory {} is not empty. Use -f to overwrite the"
                    "existing content.".format(path)
                )
            else:
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(e)

    if isinstance(required, str):
        required = [required]
    if isinstance(optional, str):
        optional = [optional]

    for cur_dir in required:
        check(cur_dir)
    for opt_dir in optional or []:
        if opt_dir:
            check(opt_dir)


def get_data_dir():
    """
    Return a data directory within the CCPM repository
    :return:
    data_dir: data path
    """
    import CCPM

    module_path = inspect.getfile(CCPM)

    data_dir = os.path.join(os.path.dirname(
                            os.path.dirname(module_path)) + "/data/")

    return data_dir


class PDF(FPDF):
    """
    Class object to initialize reports to output recommendation in pdf
    format.
    """

    def header(self):
        """
        Function to automatically generate the header for pdf report (with
        logo).
        :return:    Header.
        """
        path = os.path.join(get_data_dir() + "CCPM.png")
        self.image(path, 10, 8, 33)
        self.ln(20)

    def footer(self):
        """
        Function to set footer for the pdf report.
        :return:    Footer.
        """
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Page " + str(self.page_no()), 0, 0, "C")

    def chapter_title(self, num, label):
        """
        Function to add a title for a new chapter.
        :param num:     Chapter Number.
        :param label:   Chapter Label.
        :return:        Chapter's string formatted for the pdf report.
        """
        self.set_font("Arial", "B", 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f"{num} : {label}", 0, 1, "L")
        self.ln(4)

    def chapter_body(self, string):
        """
        Function to add a text in the chapter's body.
        :param string:  String to add.
        :return:        String formatted for the pdf report.
        """
        self.set_font("Times", "", 12)
        self.multi_cell(0, 5, string)
        self.ln()

    def print_chapter(self, num, title, string, image=None):
        """
        Function to print the complete chapter and add it to the report.
        :param num:     Chapter Number.
        :param title:   Chapter Title.
        :param string:  String to include in the chapter's body.
        :param image:   Image to add in the chapter's body.
        :return:        Pdf page.
        """
        pdf_size = {"P": {"w": 210, "h": 297}, "L": {"w": 297, "h": 210}}

        if image:
            cover = Image.open(image)
            width, height = cover.size

            # Convert to mm since it is the default of pyFPDF.
            width, height = float(width * 0.264583), float(height * 0.264583)

            # Set orientation of the page depending on the image size.
            orientation = "P" if width < height else "L"

            # Validate the image size and ensure it fits inside the page.
            width = (
                width
                if width < pdf_size[orientation]["w"] - 100
                else pdf_size[orientation]["w"] - 100
            )
            height = (
                height
                if height < pdf_size[orientation]["h"] - 100
                else pdf_size[orientation]["h"] - 100
            )

        self.add_page(orientation=orientation)
        self.chapter_title(num, title)
        self.chapter_body(string)

        if image:
            if width > height:
                self.image(image, h=height)
            else:
                self.image(image, w=width)
