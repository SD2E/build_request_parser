#!/usr/bin/env python
"""
by: Robert C. Moseley

Python function for parsing a SD2 Build Request excel sheet

Usage for submitting to SynBioHub Staging server:
python build_request_parser.py -br <path_to_build_request> -u <sd2e_username> -p <sd2e_password>

Usage for submitting to SynBioHub Production server:
python build_request_parser.py -br <path_to_build_request> -u <sd2e_username> -p <sd2e_password> -s False
"""
import pandas as pd
import argparse
import sbol2 as sbol

sbol.Config.setOption('sbol_typed_uris', False)

def sbh_login(SBH_USER, SBH_PASSWORD, spoof_bool, parts_doc):

    # submit to staging server
    if spoof_bool:
        sbh_server = sbol.PartShop('https://hub-staging.sd2e.org')
        sbh_server.spoof("https://hub.sd2e.org")
        sbol.setHomespace('https://hub-staging.sd2e.org/user/sd2e/{collection}'.format(
            collection=parts_doc.displayId))
    # submit to production server
    else:
        sbh_server = sbol.PartShop('https://hub.sd2e.org')
        sbol.setHomespace('https://hub.sd2e.org/user/sd2e/{collection}'.format(
            collection=parts_doc.displayId))

    sbh_server.login(SBH_USER, SBH_PASSWORD)

    return sbh_server


def make_parts_doc(build_request):

    # create SBOL document
    parts_doc = sbol.Document()

    collection_name = build_request.loc['Collection Name:'].iloc[:1][1].values[0]
    parts_doc.name = collection_name
    parts_doc.displayId = '_'.join(collection_name.split(' '))
    collection_desc = build_request.loc['Design Description':].iloc[1:2].index[0]
    parts_doc.description = collection_desc

    return parts_doc


def parse_parts_to_sbh(build_request, ontology_terms, parts_doc):

    # parse excel doc for only parts and create parts dataframe
    parts_df = build_request.loc['Part Name':'Composite DNA Parts']
    parts_df.columns = parts_df.iloc[0]
    parts_df = parts_df.drop(parts_df.index[0])
    parts_df = parts_df.loc[parts_df.index.dropna()]
    parts_df = parts_df.drop(['Composite DNA Parts'])

    # iterate over parts dataframe
    for part_name, part_info in parts_df.iterrows():
        part_displayid = '_'.join(part_name.split(' '))
        # create part component definition
        part_cd = sbol.ComponentDefinition(part_displayid, sbol.BIOPAX_DNA)
        part_cd.name = part_name
        part_cd.description = part_info['Description (Optional)']

        # check if Role for part is given
        if not pd.isnull(part_info['Role']):
            if part_info['Role'] in ontology_terms.index:
                # grab role uri from ontology term excel sheet
                role_uri = ontology_terms.loc[part_info['Role']].values[0]
                part_cd.roles = part_cd.roles + [role_uri]

        # check if Sequence for part is given
        if not pd.isnull(part_info['Sequence']):
            # add sequence information to part component definition
            part_seq = sbol.Sequence('{}_sequence'.format(part_cd.displayId), part_info['Sequence'])
            part_cd.sequence = part_seq

        # TODO: Fix adding Source information
        # This doesn't seem to work
        # check if Source for part is given
        if not pd.isnull(part_info['Source (Optional)']):
            # add source information to part component definition
            part_source = part_info['Source (Optional)']
            part_cd.Source = part_source

        parts_doc.addComponentDefinition(part_cd)


if __name__ == '__main__':
    """
    build_request_parser requires as input a build Request excel sheet.  
    Command-line parameters which are required include:
        -br, --build_request_excel: the path and file of the Build Request excel sheet
        -u, --sbh_username: SD2 username for accessing SynBioHub servers
        -p, --sbh_password: SD2 password for accessing SynBioHub servers
    Command-line parameters which may be optionally specified include:
        -s, --spoof: bool specifying which server to use: True = Staging Server, False = Production Server 
                    (default: True)
    """

    arg_parser = argparse.ArgumentParser(prog='Build Request Parser',
                                         description='Parses Build Request excel document for DNA parts and submits to SynBioHub')

    # - command-line arguments -
    arg_parser.add_argument('-br', '--build_request_excel',
                        action='store',
                        required=True,
                        help='full path to build request excel document')
    arg_parser.add_argument('-u', '--sbh_username',
                        action='store',
                        required=True,
                        help='SD2 SynBioHub username')
    arg_parser.add_argument('-p', '--sbh_password',
                        action='store',
                        required=True,
                        help='SD2 SynBioHub password')
    arg_parser.add_argument('-s', '--spoof',
                        action='store',
                        type=bool,
                        default=True,
                        help='Default submits DNA parts to SynBioHub staging server. Set to False to submit to SynBioHub production server.')
    args = arg_parser.parse_args()

    path_to_build_request = args.build_request_excel
    SBH_USER = args.sbh_username
    SBH_PASSWORD = args.sbh_password
    spoof_bool = args.spoof

    # Load and parse build request
    build_excel = pd.ExcelFile(path_to_build_request)
    build_request = pd.read_excel(build_excel, 'Design', index_col=0, header=None)
    ontology_terms = pd.read_excel(build_excel, 'Ontology Terms', index_col=0)

    # create parts Document
    parts_doc = make_parts_doc(build_request)

    # connect to SBH server and set Homespace
    sbh_server = sbh_login(SBH_USER, SBH_PASSWORD, spoof_bool, parts_doc)

    # parse build request and add parts to parts Document
    parse_parts_to_sbh(build_request, ontology_terms, parts_doc)

    # submit parts Document to SBH server
    sbh_server.submit(parts_doc, sbol.getHomespace(), 1)
