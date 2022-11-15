import datetime
import json
import pathlib
import subprocess
import textwrap

import markdown
import pandas as pd
import upath

extensions = ['markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.fenced_code', 'admonition', 'def_list']
current_dir = pathlib.Path(__file__).parent.absolute()


fts_columns = ['cities', 'time']

current_dir = pathlib.Path(__file__).parent.absolute()
data_dir = current_dir / 'data' / 'cmip6-downscaling'


def configure_full_text_search(*, database, tables, columns):
    for table in tables:
        command = f"sqlite-utils enable-fts --replace {database} {table} {' '.join(columns)}"
        subprocess.check_output(command, shell=True)


def make_metadata(*, tables, cities, time_min, time_max):
    db_tables = {}
    for table in tables:

        _, _, model, scenario, _, timescale, downscaling_method, variable, _ = table.split('.')
        text = textwrap.dedent(
            f"""
            ## Overview

            Every CSV file you download will contain a timeseries of one variable (`tasmax`, `tasmin`, or `pr`).
            You can specify a time range or selection of cities by typing those in the box below.
            For example, you can type in “New York City” to access data only for that city.
            The list of available cities is included below. Download the file below by scrolling down to the bottom
            of the page and clicking “Download”.


            ## Metadata

            - **General Circulation Model (GCM)**: {model}
            - **Scenario**: {scenario}
            - **Frequency**: {timescale}
            - **Temporal extent**: {time_min} to {time_max}
            - **Downscaling method**: {downscaling_method}
            - **Variable**: {variable}

            ---

            **Available cities**:

            {', '.join(cities)}

            ---

            """
        )

        db_tables[table] = {'description_html': markdown.markdown(text, extensions=extensions), 'facets': ['cities']}

    cmip6_text = textwrap.dedent(
        f'''

    ## Overview

    This page allows you to download timeseries of climate data at 107 cities around the globe in CSV format.
    The data is from a collection of downscaled climate projections based upon results from the Coupled Model
    Intercomparison Project Phase 6 (CMIP6). This collection of datasets includes results from multiple downscaling
    methods to support uncertainty estimation. See [here](https://carbonplan.org/research/cmip6-downscaling-explainer)
    for more details on the dataset and methods


    ## Metadata

    - **Variables**: daily minimum and maximum temperature, precipitation
    - **Spatial coverage**: global
    - **Temporal resolution**: daily, plus monthly and annual aggregations
    - **Last updated**: {datetime.datetime.now(datetime.timezone.utc).strftime("%B %d, %Y at %H:%M (UTC)")}
    - **License**: CC-BY-4.0
    - **Available formats**: CSVs (point locations)
    - **Tags**: `climate`, `risks`

    ## Relevant resources

    - **Explainer article**: [https://carbonplan.org/research/cmip6-downscaling-explainer](https://carbonplan.org/research/cmip6-downscaling-explainer)
    - **Map tool**: [https://carbonplan.org/research/cmip6-downscaling](https://carbonplan.org/research/cmip6-downscaling)

    '''
    )

    cmip6_html = markdown.markdown(cmip6_text, extensions=extensions)

    meta = {
        'title': 'Downscaled CMIP6 Data',
        'description_html': cmip6_html,
        'tables': db_tables,
    }

    metadata = {
        'title': 'CarbonPlan data',
        'license': 'CC Attribution 4.0 License',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'description_html': (
            'This is a public catalog of datasets related to carbon removal and climate solutions. '
            'At CarbonPlan, we maintain this data catalog for our own use and as a resource to the '
            'rest of the research community.'
        ),
        'source': 'carbonplan/data',
        'source_url': 'https://carbonplan.org/data',
        'about': 'carbonplan/data',
        'about_url': 'https://carbonplan.org/data',
        'databases': {
            'cmip6-downscaling': meta,
        },
    }
    with open(current_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)


if __name__ == '__main__':
    root = upath.UPath('s3://carbonplan-share/datasette/cmip6-downscaling')

    files = sorted(root.glob('*.csv.gz'))[:2]
    tables = [file.stem for file in files]
    paths = [f'https://carbonplan-share.s3.us-west-2.amazonaws.com/datasette/cmip6-downscaling/{file.name}' for file in files]
    command = f"csvs-to-sqlite {' '.join(paths)} cmip6-downscaling.db"
    # subprocess.check_output(command, shell=True)
    configure_full_text_search(database='cmip6-downscaling.db', tables=tables, columns=fts_columns)

    # # Optimize index usage and optimize database
    command = 'sqlite-utils analyze-tables cmip6-downscaling.db --save'
    subprocess.check_output(command, shell=True)
    command = 'sqlite-utils vacuum cmip6-downscaling.db'
    subprocess.check_output(command, shell=True)

    # Make metadata

    df = pd.read_csv(files[0])
    cities = sorted(df.cities.unique().tolist())
    time_min = df.time.min()
    time_max = df.time.max()
    make_metadata(tables=tables, cities=cities, time_min=time_min, time_max=time_max)
