# american-gut-rest

A RESTful(ish) interface into the unidentified American Gut data. Any invalid response, or a query requesting an unknown sample will return a 410 HTTP status. 

# Endpoints

| endpoint | description | example | result | 
| :------- | ----------- | ------- | -----: |
| `GET /`    | Endpoint detail | `curl https://api.microbio.me/american-gut/1/` | `{"foo_url": ...}`
| `GET /otu/:sample-id` | A sample specific OTU table | `curl https://api.microbio.me/american-gut/1/otu/000005636.1053788` | A [BIOM-format 1.0.0](http://biom-format.org/documentation/format_versions/biom-1.0.html) table |
| `GET /otu/:sample-id/txt` | A sample specific Excel OTU table | `curl https://api.microbio.me/american-gut/1/otu/000005636.1053788/txt` | A tab delimited string |
| `GET /otu/:sample-id/json` | A sample specific OTU table | `curl https://api.microbio.me/american-gut/1/otu/000005636.1053788/json` | A [BIOM-format 1.0.0](http://biom-format.org/documentation/format_versions/biom-1.0.html) table |
| `GET /sample` | A list of the known samples | `curl https://api.microbio.me/american-gut/1/sample/` | `["foo", "bar", ...]`
| `GET /sequence/:sample-id` | Per-sample sequences for download | `curl https://api.microbio.me/american-gut/1/sequence/000005636.1053788` | `{"fastq_url": "ftp://..."}` |

# Configuration

The following is a list of the configuration options and their default value. If the environment variable `$AGREST_CONFIG` is defined, the configuration will be sourced from there and in which case, all configuration values must be set (i.e., defaults are all or none)

| option | description | default |
| :----- | ----------- | ------: |
| `serverport` | The port the HTTP server will listen on | `8080` |
| `base_conf_dir` | The directory nginx will search for includes in | `.` |
| `db_user` | The unprivileged database user | `postgres` |
| `db_password` | The unprivileged database user password | `""` |
| `db_host` | The database host | `localhost` |
| `db_name` | The database name | `ag_rest` |
| `admin_db_user` | The privileged database user | `postgres` |
| `admin_db_password` | The privileged database user password | `""` |
| `test_environment` | A boolean flag to indicate if this is a test environment | `True` |
| `ag_biom_src` | The URL for the source BIOM file | `https://github.com/biocore/American-Gut/blob/master/data/AG/AG_100nt_even10k.biom?raw=true` |
| `ag_accession_src` | The URL for the per sample accession details | `https://github.com/biocore/American-Gut/blob/master/data/AG/accession_to_sample.json?raw=true` |
| `ag_biom_src_api` | The URL for the source BIOM file Github API to check its SHA | `ag_biom_src_api': 'https://api.github.com/repos/biocore/American-Gut/commits?path=data/AG/AG.biom` | 
