import nbformat
from nbconvert import PythonExporter
from pathlib import Path
from optparse import OptionParser
from typing import Optional

usage = "usage: %prog [options]"
parser = OptionParser(usage)

parser.add_option(
    "-s",
    "--source_folder",
    action="store",
    type="string",
    dest="notebook_folder",
    help=(
        "folder containing notebooks to convert, "
        "or can be path to a specific notebook"
    ),
)
parser.add_option(
    "-o",
    "--out_folder",
    action="store",
    type="string",
    dest="out_folder",
    help="folder to create converted files",
)

parser.add_option(
    "-f",
    "--notebook-name",
    action="store",
    type="string",
    dest="file_name",
    help="specify a specific notebook in the folder to process",
)


def convert_notebook_to_python(notebook_path, out_path):

    with open(notebook_path) as fh:
        nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
    cells = nb.get("cells")
    if cells is None:
        return

    cells_to_convert = []

    for cell in cells:
        if "execution_count" in cell:
            cell["execution_count"] = None
            cell["outputs"] = []
        skip = False
        if "metadata" in cell:
            if "tags" in cell["metadata"]:
                if "do_not_convert" in cell["metadata"]["tags"]:
                    skip = True
        if not skip:
            cells_to_convert.append(cell)

    nb["cells"] = cells_to_convert

    exporter = PythonExporter()
    source, meta = exporter.from_notebook_node(nb)

    lines = source.splitlines()
    clean_source = "\n".join((line for line in lines if line != "# In[ ]:")) + "\n"

    with open(out_path, "w", encoding="utf8") as fh:
        fh.writelines(clean_source)


def process_folder(
    folder_path: Path, out_folder: Path, folder_glob: Optional[str] = None
):
    if not folder_glob:
        folder_glob = "*.ipynb"
    p = folder_path.glob(folder_glob)
    files = [x for x in p if x.is_file()]
    for f in files:
        new_name = out_folder.joinpath(f.stem + ".py")
        print(f"processing {f} to {new_name}")
        convert_notebook_to_python(f, new_name)


def main():
    (options, args) = parser.parse_args()

    print(options)
    print(args)

    print(f"Cwd:{Path.cwd()}")

    if not options.notebook_folder:
        parser.print_help()
        parser.error("options -s is required")

    notebooks_folder = options.notebook_folder

    out_folder = notebooks_folder
    if options.out_folder:
        out_folder = options.out_folder

    if not Path(notebooks_folder).exists():
        print(f"The path {notebooks_folder} does not exist")
        return None
    if not Path(out_folder).exists():
        print(f"The path {out_folder} does not exist")
        return None

    process_folder(Path(notebooks_folder), Path(out_folder), options.file_name)


if __name__ == "__main__":
    # process_folder(
    #    Path("./axiomapy/examples"), Path("./axiomapy/examples/converted_notebooks/")
    # )
    main()
