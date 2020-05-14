# build_request_parser - SD2 Build Request parser

Parses Build Request excel sheet and uploads DNA parts and their respective information to SynBioHub

## Installing build_request_parser

```
$ git clone https://gitlab.sd2e.org/rmoseley/build_request_parser.git
$ cd build_request_parser
$ conda env create -f conda_env.yml
$ source activate br_parser
```

## Running build_request_parser.py in the command line
#### For submitting the SynBioHub Staging Server
```
$ python build_request_parser.py -br <path_to_build_request> -u <sd2e_username> -p <sd2e_password>
```
#### For submitting the SynBioHub Staging Server
```
$ python build_request_parser.py -br <path_to_build_request> -u <sd2e_username> -p <sd2e_password> -s False
```

## Running BuildRequest_SBH_upload notebook
Notebook can be used for testing submissions as it is set up to submit to SynBioHub Staging server.
To use, you must:
- add sd2e username and password
- add path to a Build Request excel sheet