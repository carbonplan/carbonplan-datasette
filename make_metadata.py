import json
import pathlib
import textwrap

import markdown
import pandas as pd


def cmip6_meta(current_dir):
    data_dir = current_dir / 'data' / 'cmip6-downscaling'
    files = sorted(data_dir.glob('*.csv.gz'))
    tables = {}
    for file in files:
        name = file.stem
        # CMIP.CCCma.CanESM5.historical.r1i1p1f1.day.DeepSD-BC.pr
        key = pathlib.Path(name).stem
        _, _, model, scenario, member_id, timescale, downscaling_method, variable = key.split('.')
        df = pd.read_csv(file)
        text = textwrap.dedent(
            f"""
            ## Overview

            In this dataset, downscaling results are provided for the world's top 100 most populous cities.

            ## Metadata

            - **General Circulation Model (GCM)**: {model}
            - **Scenario**: {scenario}
            - **Frequency**: {timescale}
            - **Temporal extent**: {df.time.min()} to {df.time.max()}
            - **Downscaling method**: {downscaling_method}
            - **Variable**: {variable}

            <br>
            The full dataset is available on [Microsoft Azure](https://cpdataeuwest.blob.core.windows.net/cp-cmip/version1/data/{downscaling_method}/{key}.zarr)
            in [Zarr](https://zarr.readthedocs.io/en/stable/) format and can be accessed via Python.

            A code snippet showing how to access the full dataset using Python is shown below:

            ```python
            import xarray as xr
            ds = xr.open_dataset('https://cpdataeuwest.blob.core.windows.net/cp-cmip/version1/data/{downscaling_method}/{key}.zarr', engine='zarr', chunks={{}})
            ```

            """
        )

        tables[name] = {
            'description_html': markdown.markdown(text, extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'admonition']),
            'source_url': f'https://cpdataeuwest.blob.core.windows.net/cp-cmip/version1/data/{downscaling_method}/{key}.zarr',
            'source': 'Microsoft Azure',
        }

    cmip6_text = textwrap.dedent(
        '''

    ## Overview

    This page allows you to download downscaled climate change timeseries at 107 cities around the globe in CSV format.

    Downscaled climate projections from the Coupled Model Intercomparison Project Phase 6 (CMIP6) for climate impacts
    analysis and planning.This dataset includes results from multiple downscaling methods to
    support uncertainty estimation.


    ## Metadata

    - **Variables**: daily minimum and maximum temperature, precipitation
    - **Spatial coverage**: global
    - **Temporal resolution**: daily, plus monthly and annual aggregations
    - **Last updated**: 2022-09-01
    - **License**: CC-BY-4.0
    - **Available formats**: CSVs (point locations)
    - **Tags**: `climate`, `risks`

    ## Relevant resources

    - **Explainer article**: [https://carbonplan.org/research/cmip6-downscaling-explainer](https://carbonplan.org/research/cmip6-downscaling-explainer)
    - **Map tool**: [https://carbonplan.org/research/cmip6-downscaling](https://carbonplan.org/research/cmip6-downscaling)

    '''
    )

    cmip6_html = markdown.markdown(cmip6_text, extensions=['markdown.extensions.tables'])

    return {
        'title': 'Downscaled CMIP6 Data',
        'description_html': cmip6_html,
        'tables': tables,
    }


def cdr_database_meta():
    tables = {'projects': {'description_html': '', 'source_url': ''}}
    text = textwrap.dedent(
        '''
    ## Overview

    These are reports on public Carbon Dioxide Removal project proposals. Built for transparency.

    ## Metadata

    - **Last updated**: 2022-09-01
    - **Tags**: `cdr`

    ## Relevant resources

    - **Web tool**: [https://carbonplan.org/research/cdr-database](https://carbonplan.org/research/cdr-database)

    '''
    )
    return {
        'title': 'CDR Database',
        'description_html': markdown.markdown(text, extensions=['markdown.extensions.tables']),
        'tables': tables,
    }


def run():

    current_dir = pathlib.Path(__file__).parent.absolute()

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
            'cmip6-downscaling': cmip6_meta(current_dir),
            # 'cdr-database': cdr_database_meta(),
        },
    }
    with open(current_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)


if __name__ == '__main__':
    run()
