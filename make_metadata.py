import json
import pathlib


def run():

    current_dir = pathlib.Path(__file__).parent.absolute()
    data_dir = current_dir / 'data'
    files = sorted(data_dir.glob('*.csv.gz'))
    tables = {file.stem: {'description_html': '', 'source_url': ''} for file in files}

    metadata = {
        'title': 'CarbonPlan data',
        'license': 'CC Attribution 4.0 License',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'source': 'carbonplan/cmip6-downscaling on GitHub',
        'source_url': 'https://github.com/carbonplan/cmip6-downscaling/blob/main/datasets.md',
        'about': 'carbonplan/cmip6-downscaling',
        'about_url': 'https://github.com/carbonplan/cmip6-downscaling/blob/main/datasets.md',
        'databases': {
            'cmip6-downscaling': {
                'title': 'CMIP6 Downscaled data',
                'tables': tables,
            }
        },
    }
    with open(current_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)


if __name__ == '__main__':
    run()
