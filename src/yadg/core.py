import logging
from datatree import DataTree

from dgbowl_schemas.yadg.dataschema import DataSchema
from yadg import dgutils
from yadg.extractors import extract_from_path

logger = logging.getLogger(__name__)


def process_schema(dataschema: DataSchema, strict_merge: bool = False) -> DataTree:
    """
    The main processing function of yadg.

    Takes in a :class:`DataSchema` object and returns a single :class:`DataTree` created
    from the :class:`DataSchema`.

    """
    if strict_merge:
        concatmode = "identical"
    else:
        concatmode = "drop_conflicts"

    while hasattr(dataschema, "update"):
        dataschema = dataschema.update()

    root = DataTree()
    root.attrs = {
        "yadg_provenance": "yadg process",
        "yadg_process_date": dgutils.now(asstr=True),
        "yadg_process_DataSchema": dataschema.model_dump_json(),
    }
    root.attrs.update(dgutils.get_yadg_metadata())

    for si, step in enumerate(dataschema.steps):
        logger.info(f"Processing step {si}.")

        # Backfill default timezone, locale, encoding.
        if step.extractor.timezone is None:
            step.extractor.timezone = dataschema.step_defaults.timezone

        if step.extractor.locale is None:
            step.extractor.locale = dataschema.step_defaults.locale
        if step.extractor.encoding is None:
            step.extractor.encoding = dataschema.step_defaults.encoding

        if step.tag is None:
            step.tag = f"{si}"

        todofiles = step.input.paths()
        vals = None
        if len(todofiles) == 0:
            logger.warning(f"No files processed by step '{step.tag}'.")
            vals = {}
        for tf in todofiles:
            logger.info(f"Processing file '{tf}'.")
            tasks = extract_from_path(path=tf, extractor=step.extractor).to_dict()
            fvals = {}
            for name, dset in tasks.items():
                # The root datatree node may sometimes carry metadata, even if
                # there are no variables - we don't add 'uts' to those.
                if name == "/" and len(dset.variables) == 0:
                    fvals[name] = dset
                # Otherwise, we want to process any 'step.externaldate' commands
                else:
                    fvals[name] = dgutils.complete_uts(
                        dset, tf, step.externaldate, step.extractor.timezone
                    )
                # Remove metadata entries we know will differ between different files.
                for k in {"yadg_extract_date", "yadg_extract_filename"}:
                    if k in fvals[name].attrs:
                        del fvals[name].attrs[k]

            vals = dgutils.merge_dicttrees(vals, fvals, concatmode)

        stepdt = DataTree.from_dict({} if vals is None else vals)
        stepdt.name = step.tag
        stepdt.parent = root
    return root
